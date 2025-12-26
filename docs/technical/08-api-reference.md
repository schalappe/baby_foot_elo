# API Reference

**Document Type**: Technical Reference
**Target Audience**: Backend developers, API consumers, integration partners
**Last Updated**: 2025-12-26
**Maintained By**: Development Team

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL & Versioning](#base-url--versioning)
3. [Authentication](#authentication)
4. [Common Patterns](#common-patterns)
5. [Error Handling](#error-handling)
6. [Health Check](#health-check)
7. [Players API](#players-api)
8. [Teams API](#teams-api)
9. [Matches API](#matches-api)
10. [Rate Limiting](#rate-limiting)
11. [Code Examples](#code-examples)

---

## Overview

The Baby Foot ELO REST API provides programmatic access to player rankings, team management, and match recording. All endpoints return JSON responses and follow RESTful conventions.

### Key Features

- **CRUD Operations**: Full create, read, update, delete for all entities
- **Hybrid ELO System**: Automatic ELO calculation for all matches
- **Statistics & Rankings**: Pre-calculated stats via database RPC functions
- **Filtering & Pagination**: Offset-based pagination with flexible filters
- **Batch Operations**: Efficient bulk operations for match history

---

## Base URL & Versioning

### Development
```text
http://localhost:3000/api/v1
```

### Production
```text
https://your-domain.vercel.app/api/v1
```

**API Version**: v1 (current and only version)

---

## Authentication

**Current Status**: No authentication required (open API)

**Planned**: JWT-based authentication for write operations (POST, PUT, DELETE)

---

## Common Patterns

### Request Headers

```http
Content-Type: application/json
Accept: application/json
```

### Pagination

**Pattern**: Offset-based pagination with `skip`/`offset` and `limit` parameters

**Query Parameters**:
- `skip` or `offset`: Number of items to skip (default: 0, 0-indexed)
- `limit`: Maximum items to return (default varies by endpoint)

**Example**:
```bash
GET /api/v1/players?skip=20&limit=10
# Returns players 21-30
```

### Date Filtering

**Format**: ISO 8601 datetime strings

**Query Parameters**:
- `start_date`: Filter records after this datetime (inclusive)
- `end_date`: Filter records before this datetime (inclusive)

**Example**:
```bash
GET /api/v1/matches?start_date=2025-01-01T00:00:00Z&end_date=2025-12-31T23:59:59Z
```

### Response Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| `200` | OK | Successful GET request |
| `201` | Created | Successful POST request (resource created) |
| `204` | No Content | Successful DELETE request (no response body) |
| `400` | Bad Request | Invalid request parameters or business rule violation |
| `404` | Not Found | Requested resource doesn't exist |
| `409` | Conflict | Resource already exists (duplicate) |
| `422` | Unprocessable Entity | Validation error (invalid data format) |
| `500` | Internal Server Error | Server-side error during operation |

---

## Error Handling

### Error Response Format

All errors return a JSON object with a `detail` field:

```json
{
  "detail": "Human-readable error message"
}
```

### Error Types

#### 404 Not Found
```json
{
  "detail": "Player not found: 123"
}
```

**Triggers**:
- Player/Team/Match ID doesn't exist
- Invalid entity reference

#### 409 Conflict
```json
{
  "detail": "Player with name 'John Doe' already exists"
}
```

**Triggers**:
- Duplicate player name
- Team with same player pair already exists

#### 422 Validation Error
```json
{
  "detail": "name: Name must be at least 2 characters; global_elo: ELO must be a positive number"
}
```

**Triggers**:
- Zod schema validation failures
- Invalid data types or formats
- Missing required fields

#### 400 Bad Request
```json
{
  "detail": "Winner and loser teams must be different"
}
```

**Triggers**:
- Invalid match team combinations
- Business rule violations

#### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

**Triggers**:
- Database operation failures
- Unexpected server errors

### Error Handling Wrapper

All routes use `handleApiRequest()` wrapper (`lib/api/handle-request.ts:58`) which:
1. Catches `ZodError` → 422 with formatted field errors
2. Catches `ApiError` → Custom status code with error detail
3. Catches unknown errors → 500 with generic message (logged to console)

---

## Health Check

### Check API Health

```http
GET /api/v1/health
```

**Description**: Verifies API availability

**Response**: `200 OK`
```json
{
  "status": "ok"
}
```

**Use Cases**:
- Uptime monitoring
- Load balancer health checks
- Integration testing setup

---

## Players API

### List All Players

```http
GET /api/v1/players
```

**Description**: Get all players with basic statistics

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Maximum players to return |
| `skip` | integer | 0 | Number of players to skip |

**Response**: `200 OK`
```json
[
  {
    "player_id": 1,
    "name": "Alice Johnson",
    "global_elo": 1650,
    "matches_played": 42,
    "wins": 25,
    "losses": 17,
    "win_rate": 0.595,
    "created_at": "2025-01-15T10:30:00Z",
    "last_match_at": "2025-12-20T14:22:00Z"
  }
]
```

**Implementation**: `app/api/v1/players/route.ts:15`

---

### Get Player Rankings

```http
GET /api/v1/players/rankings
```

**Description**: Get active players ranked by ELO (filtered by activity and minimum matches)

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 100 | Maximum players to return |
| `days_since_last_match` | integer | 180 | Activity window (days) |

**Filters Applied**:
- Must have **> 10 matches** (`MIN_MATCHES_FOR_RANKING`)
- Must have match within `days_since_last_match` window

**Response**: `200 OK`
```json
[
  {
    "player_id": 1,
    "name": "Alice Johnson",
    "global_elo": 1650,
    "matches_played": 42,
    "wins": 25,
    "losses": 17,
    "win_rate": 0.595,
    "created_at": "2025-01-15T10:30:00Z",
    "last_match_at": "2025-12-20T14:22:00Z",
    "rank": 1
  }
]
```

**Sorting**: Descending by `global_elo`

**Implementation**: `app/api/v1/players/rankings/route.ts:12`

---

### Create Player

```http
POST /api/v1/players
```

**Description**: Create a new player with automatic team generation for all existing players

**Request Body**:
```json
{
  "name": "Bob Smith",
  "global_elo": 1000
}
```

**Schema Validation**:
```typescript
{
  name: string (min: 1, max: 100 chars),
  global_elo?: number (positive, default: 1000)
}
```

**Response**: `201 Created`
```json
{
  "player_id": 42,
  "name": "Bob Smith",
  "global_elo": 1000,
  "matches_played": 0,
  "wins": 0,
  "losses": 0,
  "win_rate": 0,
  "created_at": "2025-12-26T15:00:00Z",
  "last_match_at": null
}
```

**Errors**:
- `409 Conflict`: Player with this name already exists
- `422 Validation Error`: Invalid name or ELO format

**Side Effects**:
- Creates teams with all existing players (N teams where N = current player count)
- All new teams start with ELO 1000

**Implementation**: `app/api/v1/players/route.ts:35` → `lib/services/players.ts:110`

---

### Get Player by ID

```http
GET /api/v1/players/{playerId}
```

**Description**: Get detailed information about a specific player

**Path Parameters**:
- `playerId` (integer, required): Player ID

**Response**: `200 OK`
```json
{
  "player_id": 1,
  "name": "Alice Johnson",
  "global_elo": 1650,
  "matches_played": 42,
  "wins": 25,
  "losses": 17,
  "win_rate": 0.595,
  "created_at": "2025-01-15T10:30:00Z",
  "last_match_at": "2025-12-20T14:22:00Z"
}
```

**Errors**:
- `404 Not Found`: Player doesn't exist
- `422 Validation Error`: Invalid player ID format

**Implementation**: `app/api/v1/players/[playerId]/route.ts:16`

---

### Update Player

```http
PUT /api/v1/players/{playerId}
```

**Description**: Update player name or ELO

**Path Parameters**:
- `playerId` (integer, required): Player ID

**Request Body**:
```json
{
  "name": "Alice Cooper",
  "global_elo": 1700
}
```

**Schema Validation**:
```typescript
{
  name?: string (min: 1, max: 100 chars),
  global_elo?: number (positive)
}
```

**Response**: `200 OK`
```json
{
  "player_id": 1,
  "name": "Alice Cooper",
  "global_elo": 1700,
  "matches_played": 42,
  "wins": 25,
  "losses": 17,
  "win_rate": 0.595,
  "created_at": "2025-01-15T10:30:00Z",
  "last_match_at": "2025-12-20T14:22:00Z"
}
```

**Errors**:
- `404 Not Found`: Player doesn't exist
- `409 Conflict`: New name conflicts with existing player
- `422 Validation Error`: Invalid data format

**Implementation**: `app/api/v1/players/[playerId]/route.ts:39`

---

### Delete Player

```http
DELETE /api/v1/players/{playerId}
```

**Description**: Delete a player (soft delete)

**Path Parameters**:
- `playerId` (integer, required): Player ID

**Response**: `204 No Content` (empty body)

**Errors**:
- `404 Not Found`: Player doesn't exist
- `422 Validation Error`: Invalid player ID format

**⚠️ Warning**: Deleting a player may affect historical match data integrity.

**Implementation**: `app/api/v1/players/[playerId]/route.ts:66`

---

### Get Player Statistics

```http
GET /api/v1/players/{playerId}/statistics
```

**Description**: Get comprehensive player statistics including ELO history and trends

**Path Parameters**:
- `playerId` (integer, required): Player ID

**Response**: `200 OK`
```json
{
  "player_id": 1,
  "name": "Alice Johnson",
  "global_elo": 1650,
  "matches_played": 42,
  "wins": 25,
  "losses": 17,
  "win_rate": 0.595,
  "created_at": "2025-01-15T10:30:00Z",
  "last_match_at": "2025-12-20T14:22:00Z",
  "elo_values": [1000, 1024, 1048, ..., 1650],
  "elo_difference": [24, 24, -16, ..., 12],
  "average_elo_change": 15.5,
  "highest_elo": 1680,
  "lowest_elo": 980,
  "recent": {
    "matches_played": 10,
    "wins": 7,
    "losses": 3,
    "win_rate": 0.7,
    "average_elo_change": 18.2,
    "elo_changes": [24, 16, -12, 20, ...]
  }
}
```

**ELO Arrays**:
- `elo_values`: Historical ELO values (chronological)
- `elo_difference`: ELO change per match (positive = gain, negative = loss)

**Recent Stats**: Last 10 matches (configurable via query params in future)

**Implementation**: `app/api/v1/players/[playerId]/statistics/route.ts:11` → RPC: `get_player_full_stats`

---

### Get Player Match History

```http
GET /api/v1/players/{playerId}/matches
```

**Description**: Get paginated match history for a player

**Path Parameters**:
- `playerId` (integer, required): Player ID

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Matches per page |
| `offset` | integer | 0 | Number of matches to skip |
| `start_date` | datetime | - | Filter matches after this date |
| `end_date` | datetime | - | Filter matches before this date |

**Response**: `200 OK`
```json
{
  "matches": [
    {
      "match_id": 101,
      "winner_team_id": 5,
      "loser_team_id": 3,
      "is_fanny": false,
      "played_at": "2025-12-20T14:22:00Z",
      "notes": "Championship final",
      "winner_team": {
        "team_id": 5,
        "player1_id": 1,
        "player2_id": 2,
        "global_elo": 1650
      },
      "loser_team": {
        "team_id": 3,
        "player1_id": 3,
        "player2_id": 4,
        "global_elo": 1450
      },
      "player_elo_change": 24,
      "new_player_elo": 1650,
      "old_player_elo": 1626
    }
  ],
  "total": 42,
  "limit": 10,
  "offset": 0
}
```

**Sorting**: Descending by `played_at` (newest first)

**Implementation**: `app/api/v1/players/[playerId]/matches/route.ts:13` → RPC: `get_player_matches_json`

---

### Get Player ELO History

```http
GET /api/v1/players/{playerId}/elo-history
```

**Description**: Get paginated ELO change history

**Path Parameters**:
- `playerId` (integer, required): Player ID

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 20 | History records to return |
| `offset` | integer | 0 | Number of records to skip |

**Response**: `200 OK`
```json
[
  {
    "match_id": 101,
    "old_elo": 1626,
    "new_elo": 1650,
    "elo_change": 24,
    "played_at": "2025-12-20T14:22:00Z"
  }
]
```

**Sorting**: Descending by `played_at`

**Implementation**: `app/api/v1/players/[playerId]/elo-history/route.ts:12`

---

## Teams API

### Get Team Rankings

```http
GET /api/v1/teams/rankings
```

**Description**: Get active teams ranked by ELO

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 200 | Maximum teams to return |
| `days_since_last_match` | integer | 180 | Activity window (days) |

**Filters Applied**:
- Must have **> 10 matches**
- Must have match within `days_since_last_match` window

**Response**: `200 OK`
```json
[
  {
    "team_id": 5,
    "player1_id": 1,
    "player2_id": 2,
    "player1": {
      "player_id": 1,
      "name": "Alice Johnson",
      "global_elo": 1650
    },
    "player2": {
      "player_id": 2,
      "name": "Bob Smith",
      "global_elo": 1580
    },
    "global_elo": 1620,
    "matches_played": 28,
    "wins": 18,
    "losses": 10,
    "win_rate": 0.643,
    "created_at": "2025-01-15T10:35:00Z",
    "last_match_at": "2025-12-20T14:22:00Z",
    "rank": 1
  }
]
```

**Sorting**: Descending by `global_elo`

**Implementation**: `app/api/v1/teams/rankings/route.ts:12`

---

### List All Teams

```http
GET /api/v1/teams
```

**Description**: Get all teams with basic statistics

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of teams to skip |
| `limit` | integer | 100 | Maximum teams to return |

**Response**: `200 OK`
```json
[
  {
    "team_id": 5,
    "player1_id": 1,
    "player2_id": 2,
    "global_elo": 1620,
    "matches_played": 28,
    "wins": 18,
    "losses": 10,
    "win_rate": 0.643,
    "created_at": "2025-01-15T10:35:00Z",
    "last_match_at": "2025-12-20T14:22:00Z"
  }
]
```

**Implementation**: `app/api/v1/teams/route.ts:15`

---

### Create Team

```http
POST /api/v1/teams
```

**Description**: Create a new team (or return existing team with same player pair)

**Request Body**:
```json
{
  "player1_id": 1,
  "player2_id": 2,
  "global_elo": 1000
}
```

**Schema Validation**:
```typescript
{
  player1_id: number (positive integer),
  player2_id: number (positive integer, different from player1_id),
  global_elo?: number (positive, default: 1000)
}
```

**Player ID Normalization**: Players are stored in canonical order (`player1_id < player2_id`)

**Response**: `201 Created`
```json
{
  "team_id": 42,
  "player1_id": 1,
  "player2_id": 2,
  "global_elo": 1000,
  "matches_played": 0,
  "wins": 0,
  "losses": 0,
  "win_rate": 0,
  "created_at": "2025-12-26T15:30:00Z",
  "last_match_at": null
}
```

**Errors**:
- `404 Not Found`: One or both players don't exist
- `409 Conflict`: Team with this player pair already exists (returns existing team)
- `422 Validation Error`: Invalid player IDs or same player specified twice

**Implementation**: `app/api/v1/teams/route.ts:35` → `lib/services/teams.ts:79`

---

### Get Team by ID

```http
GET /api/v1/teams/{teamId}
```

**Description**: Get detailed team information with player details

**Path Parameters**:
- `teamId` (integer, required): Team ID

**Response**: `200 OK`
```json
{
  "team_id": 5,
  "player1_id": 1,
  "player2_id": 2,
  "player1": {
    "player_id": 1,
    "name": "Alice Johnson",
    "global_elo": 1650
  },
  "player2": {
    "player_id": 2,
    "name": "Bob Smith",
    "global_elo": 1580
  },
  "global_elo": 1620,
  "matches_played": 28,
  "wins": 18,
  "losses": 10,
  "win_rate": 0.643,
  "created_at": "2025-01-15T10:35:00Z",
  "last_match_at": "2025-12-20T14:22:00Z"
}
```

**Errors**:
- `404 Not Found`: Team doesn't exist

**Implementation**: `app/api/v1/teams/[teamId]/route.ts:16`

---

### Delete Team

```http
DELETE /api/v1/teams/{teamId}
```

**Description**: Delete a team (soft delete)

**Path Parameters**:
- `teamId` (integer, required): Team ID

**Response**: `204 No Content`

**Errors**:
- `404 Not Found`: Team doesn't exist

**⚠️ Warning**: Deleting a team may affect historical match data integrity.

**Implementation**: `app/api/v1/teams/[teamId]/route.ts:35`

---

### Get Team Statistics

```http
GET /api/v1/teams/{teamId}/statistics
```

**Description**: Get comprehensive team statistics including ELO history

**Path Parameters**:
- `teamId` (integer, required): Team ID

**Response**: `200 OK`
```json
{
  "team_id": 5,
  "player1_id": 1,
  "player2_id": 2,
  "player1": { "player_id": 1, "name": "Alice", "global_elo": 1650 },
  "player2": { "player_id": 2, "name": "Bob", "global_elo": 1580 },
  "global_elo": 1620,
  "matches_played": 28,
  "wins": 18,
  "losses": 10,
  "win_rate": 0.643,
  "elo_values": [1000, 1024, 1048, ..., 1620],
  "elo_difference": [24, 24, -16, ..., 12],
  "average_elo_change": 22.1,
  "highest_elo": 1650,
  "lowest_elo": 980,
  "recent": {
    "matches_played": 10,
    "wins": 7,
    "losses": 3,
    "win_rate": 0.7,
    "average_elo_change": 25.3,
    "elo_changes": [24, 16, -12, ...]
  }
}
```

**Implementation**: `app/api/v1/teams/[teamId]/statistics/route.ts:11` → RPC: `get_team_full_stats_optimized`

**Note**: The RPC `get_all_teams_with_stats_optimized` is used only for multi-team queries (e.g., team rankings).

---

### Get Team Match History

```http
GET /api/v1/teams/{teamId}/matches
```

**Description**: Get paginated match history for a team with ELO changes

**Path Parameters**:
- `teamId` (integer, required): Team ID

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of matches to skip |
| `limit` | integer | 100 | Matches per page |

**Response**: `200 OK`
```json
[
  {
    "match_id": 101,
    "winner_team_id": 5,
    "loser_team_id": 3,
    "is_fanny": false,
    "played_at": "2025-12-20T14:22:00Z",
    "notes": "Championship final",
    "team_elo_change": 18,
    "new_team_elo": 1620,
    "old_team_elo": 1602
  }
]
```

**Sorting**: Descending by `played_at`

**Implementation**: `app/api/v1/teams/[teamId]/matches/route.ts:13` → RPC: `get_team_match_history`

---

## Matches API

### List Matches

```http
GET /api/v1/matches
```

**Description**: Get matches with optional filtering

**Query Parameters**:
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | integer | 0 | Number of matches to skip |
| `limit` | integer | 100 | Matches per page |
| `team_id` | integer | - | Filter by team (winner or loser) |
| `start_date` | datetime | - | Filter matches after this date |
| `end_date` | datetime | - | Filter matches before this date |
| `is_fanny` | boolean | - | Filter by fanny status |

**Response**: `200 OK`
```json
[
  {
    "match_id": 101,
    "winner_team_id": 5,
    "loser_team_id": 3,
    "winner_team": {
      "team_id": 5,
      "player1_id": 1,
      "player2_id": 2,
      "global_elo": 1620
    },
    "loser_team": {
      "team_id": 3,
      "player1_id": 3,
      "player2_id": 4,
      "global_elo": 1450
    },
    "is_fanny": false,
    "played_at": "2025-12-20T14:22:00Z",
    "notes": "Championship final"
  }
]
```

**Sorting**: Descending by `played_at`

**Implementation**: `app/api/v1/matches/route.ts:15`

---

### Create Match

```http
POST /api/v1/matches
```

**Description**: Record a new match with automatic ELO calculation and updates

**Request Body**:
```json
{
  "winner_team_id": 5,
  "loser_team_id": 3,
  "is_fanny": false,
  "played_at": "2025-12-26T16:00:00Z",
  "notes": "Championship final"
}
```

**Schema Validation**:
```typescript
{
  winner_team_id: number (positive integer),
  loser_team_id: number (positive integer, different from winner),
  is_fanny?: boolean (default: false),
  played_at: datetime (ISO 8601 string),
  notes?: string (max 500 chars)
}
```

**Response**: `201 Created`
```json
{
  "match_id": 101,
  "winner_team_id": 5,
  "loser_team_id": 3,
  "is_fanny": false,
  "played_at": "2025-12-26T16:00:00Z",
  "notes": "Championship final",
  "elo_changes": {
    "1": { "old_elo": 1626, "new_elo": 1650, "difference": 24 },
    "2": { "old_elo": 1556, "new_elo": 1580, "difference": 24 },
    "3": { "old_elo": 1466, "new_elo": 1450, "difference": -16 },
    "4": { "old_elo": 1400, "new_elo": 1367, "difference": -33 }
  }
}
```

**ELO Changes**: Keys are player IDs (as strings), values show before/after ELO and difference

**Errors**:
- `404 Not Found`: One or both teams don't exist
- `400 Bad Request`: Winner and loser teams are the same
- `422 Validation Error`: Invalid data format

**Side Effects** (9-step process):
1. Fetch winner/loser team data
2. Calculate individual ELO changes for all 4 players (hybrid system)
3. Update player ELO values in database (batch operation)
4. Update team ELO values in database (batch operation)
5. Record player ELO history (batch operation)
6. Record team ELO history (batch operation)
7. Create match record
8. Update team statistics (wins/losses)
9. Return match with ELO changes

**Implementation**: `app/api/v1/matches/route.ts:40` → `lib/services/matches.ts:135`

---

### Get Match by ID

```http
GET /api/v1/matches/{matchId}
```

**Description**: Get match details with consolidated player ELO changes

**Path Parameters**:
- `matchId` (integer, required): Match ID

**Response**: `200 OK`
```json
{
  "match_id": 101,
  "winner_team_id": 5,
  "loser_team_id": 3,
  "winner_team": {
    "team_id": 5,
    "player1_id": 1,
    "player2_id": 2,
    "player1": { "player_id": 1, "name": "Alice", "global_elo": 1650 },
    "player2": { "player_id": 2, "name": "Bob", "global_elo": 1580 },
    "global_elo": 1620
  },
  "loser_team": {
    "team_id": 3,
    "player1_id": 3,
    "player2_id": 4,
    "player1": { "player_id": 3, "name": "Charlie", "global_elo": 1450 },
    "player2": { "player_id": 4, "name": "Diana", "global_elo": 1367 },
    "global_elo": 1408
  },
  "is_fanny": false,
  "played_at": "2025-12-26T16:00:00Z",
  "notes": "Championship final",
  "elo_changes": {
    "1": { "old_elo": 1626, "new_elo": 1650, "difference": 24 },
    "2": { "old_elo": 1556, "new_elo": 1580, "difference": 24 },
    "3": { "old_elo": 1466, "new_elo": 1450, "difference": -16 },
    "4": { "old_elo": 1400, "new_elo": 1367, "difference": -33 }
  }
}
```

**Errors**:
- `404 Not Found`: Match doesn't exist

**Implementation**: `app/api/v1/matches/[matchId]/route.ts:16`

---

### Delete Match

```http
DELETE /api/v1/matches/{matchId}
```

**Description**: Delete a match record

**Path Parameters**:
- `matchId` (integer, required): Match ID

**Response**: `204 No Content`

**Errors**:
- `404 Not Found`: Match doesn't exist

**⚠️ CRITICAL WARNING**:
- **Does NOT reverse ELO changes** (matches Python implementation behavior)
- Match history records are deleted, but player/team ELO values remain unchanged
- This is intentional to maintain historical consistency
- Use with extreme caution in production environments

**Implementation**: `app/api/v1/matches/[matchId]/route.ts:33`

---

### Export Matches

```http
GET /api/v1/matches/export
```

**Description**: Export all match data as JSON (for backups, analytics, data migration)

**Query Parameters**: None

**Response**: `200 OK`
```json
[
  {
    "match_id": 1,
    "winner_team_id": 5,
    "loser_team_id": 3,
    "is_fanny": false,
    "played_at": "2025-01-20T10:00:00Z",
    "notes": null
  }
]
```

**Practical Limit**: ~100,000 matches (response size constraint)

**Use Cases**:
- Database backups
- Data analytics/reporting
- Migration to external systems
- Audit logs

**Implementation**: `app/api/v1/matches/export/route.ts:8`

---

## Rate Limiting

**Current Status**: No rate limiting implemented

**Planned**:
- 100 requests/minute per IP for GET endpoints
- 20 requests/minute per IP for POST/PUT/DELETE endpoints

---

## Code Examples

### JavaScript/TypeScript (Axios)

```typescript
import axios from 'axios';

const API_URL = 'http://localhost:3000/api/v1';

// Get player rankings
const getPlayerRankings = async (): Promise<Player[]> => {
  try {
    const response = await axios.get(`${API_URL}/players/rankings`);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API Error:', error.response?.data?.detail);
    }
    throw error;
  }
};

// Create a new match
const createMatch = async (matchData: MatchCreate): Promise<Match> => {
  try {
    const response = await axios.post(`${API_URL}/matches`, matchData);
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const detail = error.response?.data?.detail;
      if (error.response?.status === 404) {
        console.error('Team not found:', detail);
      } else if (error.response?.status === 400) {
        console.error('Invalid teams:', detail);
      }
    }
    throw error;
  }
};

// Get player statistics with pagination
const getPlayerMatches = async (
  playerId: number,
  limit: number = 10,
  offset: number = 0
): Promise<MatchHistory> => {
  const response = await axios.get(
    `${API_URL}/players/${playerId}/matches`,
    { params: { limit, offset } }
  );
  return response.data;
};
```

### Python (requests)

```python
import requests
from typing import Dict, List

API_URL = "http://localhost:3000/api/v1"

def get_player_rankings() -> List[Dict]:
    """Get ranked players."""
    response = requests.get(f"{API_URL}/players/rankings")
    response.raise_for_status()
    return response.json()

def create_match(match_data: Dict) -> Dict:
    """Create a new match."""
    try:
        response = requests.post(
            f"{API_URL}/matches",
            json=match_data,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        error_detail = e.response.json().get("detail", "Unknown error")
        if e.response.status_code == 404:
            print(f"Team not found: {error_detail}")
        elif e.response.status_code == 400:
            print(f"Invalid teams: {error_detail}")
        raise

def get_player_statistics(player_id: int) -> Dict:
    """Get comprehensive player stats."""
    response = requests.get(f"{API_URL}/players/{player_id}/statistics")
    response.raise_for_status()
    return response.json()
```

### cURL

```bash
# Get player rankings
curl -X GET "http://localhost:3000/api/v1/players/rankings?limit=10"

# Create a new player
curl -X POST "http://localhost:3000/api/v1/players" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "global_elo": 1200}'

# Create a match
curl -X POST "http://localhost:3000/api/v1/matches" \
  -H "Content-Type: application/json" \
  -d '{
    "winner_team_id": 5,
    "loser_team_id": 3,
    "is_fanny": false,
    "played_at": "2025-12-26T16:00:00Z",
    "notes": "Championship final"
  }'

# Get player match history with pagination
curl -X GET "http://localhost:3000/api/v1/players/1/matches?limit=20&offset=0"

# Get team statistics
curl -X GET "http://localhost:3000/api/v1/teams/5/statistics"

# Delete a match
curl -X DELETE "http://localhost:3000/api/v1/matches/101"

# Export all matches
curl -X GET "http://localhost:3000/api/v1/matches/export" > matches_backup.json
```

---

## Maintenance Notes

**Update this document when**:
- Adding new API endpoints
- Modifying request/response schemas
- Changing error codes or handling
- Adding authentication/authorization
- Implementing rate limiting
- Changing pagination strategy

**Related Documentation**:
- [Architecture Overview](./01-architecture-overview.md) - API layer architecture
- [Service Layer](./05-service-layer.md) - Business logic behind endpoints
- [Database Schema](./02-database-schema.md) - Database structure
- [Sequence Diagrams](./03-sequence-diagrams.md) - Request flow diagrams
- [ELO Calculation System](./04-elo-calculation-system.md) - Match result processing

---

**Last Updated**: 2025-12-26
**API Version**: v1
**Total Endpoints**: 22
