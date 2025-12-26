# Repository Layer Documentation

**Last Updated**: 2025-12-26
**Document Type**: Class Reference
**Target Audience**: Backend Developers

---

## Overview

The repository layer provides the **data access abstraction** for the Baby Foot ELO system. Repositories encapsulate all database operations, isolating the service layer from Supabase implementation details.

### Location
```text
lib/db/
├── client.ts              # Supabase client singleton
├── retry.ts               # Retry wrapper utility
└── repositories/
    ├── players.ts         # Player data access
    ├── teams.ts           # Team data access
    ├── matches.ts         # Match data access
    ├── stats.ts           # Statistics data access (RPC)
    └── elo-history.ts     # ELO history data access
```

### Design Pattern: Repository Pattern

**Purpose**: Abstract data persistence so services don't depend on Supabase specifics.

**Benefits**:
- **Testability**: Mock repositories in service tests
- **Flexibility**: Swap database without changing services
- **Single Responsibility**: One repository per entity
- **DRY**: Centralize query logic

**Key Rule**: Repositories **only** do data access. No business logic, no validation (beyond existence checks).

---

## Core Utilities

### Supabase Client (`lib/db/client.ts`)

**Purpose**: Singleton Supabase client with environment-based configuration.

**Features**:
- Automatic key resolution (publishable key preferred over anon key)
- Error handling for missing environment variables
- TypeScript Database type generation support

**Usage**:
```typescript
import { supabase } from '@/lib/db/client'

const { data, error } = await supabase.from('players').select('*')
```

**Location**: `lib/db/client.ts`

**Environment Variables**:
- `NEXT_PUBLIC_SUPABASE_URL`: Project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`: Modern publishable key (preferred)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Legacy anon key (fallback)

---

### Retry Wrapper (`lib/db/retry.ts`)

**Purpose**: Add automatic retry logic to database operations.

**Configuration**:
```typescript
const DEFAULT_RETRY_CONFIG = {
  maxRetries: 3,
  baseDelayMs: 100,
  maxDelayMs: 2000,
  backoffMultiplier: 2  // Exponential backoff
}
```

**Usage**:
```typescript
import { withRetry } from '@/lib/db/retry'

export async function getPlayer(id: number) {
  return withRetry(async () => {
    const { data, error } = await supabase
      .from('players')
      .select('*')
      .eq('player_id', id)
      .single()

    if (error) throw error
    return data
  })
}
```

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: 100ms delay
- Attempt 3: 200ms delay
- Attempt 4: 400ms delay (max: 2000ms)

**Location**: `lib/db/retry.ts:8-49`

---

## Player Repository (`lib/db/repositories/players.ts`)

**Purpose**: All data operations for the `players` table.

**Location**: `lib/db/repositories/players.ts`
**Exports**: 10 functions

---

### Core Functions

#### `createPlayer(name: string, globalElo?: number): Promise<Player>`

**Purpose**: Insert a new player into the database.

**Parameters**:
- `name` (string): Player name (must be unique)
- `globalElo` (number, optional): Starting ELO (default: 1000)

**Returns**: `Promise<Player>` - Created player object

**Throws**: Error if name already exists (unique constraint violation)

**Example**:
```typescript
const player = await createPlayer('Alice', 1000)
// → { player_id: 1, name: 'Alice', global_elo: 1000, created_at: '...' }
```

**SQL Equivalent**:
```sql
INSERT INTO players (name, global_elo) VALUES ('Alice', 1000) RETURNING *;
```

**Location**: `lib/db/repositories/players.ts:18-34`

---

#### `getPlayerById(playerId: number): Promise<Player>`

**Purpose**: Fetch a single player by ID.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<Player>` - Player object

**Throws**: `PlayerNotFoundError` if player doesn't exist

**Example**:
```typescript
const player = await getPlayerById(1)
// → { player_id: 1, name: 'Alice', global_elo: 1050, created_at: '...' }
```

**Location**: `lib/db/repositories/players.ts:43-60`

---

#### `getPlayerByName(name: string): Promise<Player | null>`

**Purpose**: Fetch a player by name (for uniqueness checking).

**Parameters**:
- `name` (string): Player name to search

**Returns**: `Promise<Player | null>` - Player if found, null otherwise

**Note**: Does **not** throw if player doesn't exist (returns null instead).

**Example**:
```typescript
const existing = await getPlayerByName('Alice')
if (existing) {
  throw new PlayerAlreadyExistsError('Alice')
}
```

**Use Case**: Validate name uniqueness before creating/updating player.

**Location**: `lib/db/repositories/players.ts:69-87`

---

#### `getAllPlayers(): Promise<PlayerWithStatsRow[]>`

**Purpose**: Fetch all players with computed statistics using optimized RPC.

**Returns**: `Promise<PlayerWithStatsRow[]>` - Players with stats

**RPC Function**: `get_all_players_with_stats_optimized`

**Data Structure**:
```typescript
{
  player_id: number,
  name: string,
  global_elo: number,
  created_at: string,
  matches_played: number,
  wins: number,
  losses: number,
  win_rate: number,
  rank: number,
  last_match_at: string | null
}
```

**Performance**: Uses CTE-based aggregation (41x faster than N+1 queries).

**Example**:
```typescript
const players = await getAllPlayers()
// → [
//   { player_id: 1, name: 'Alice', global_elo: 1850, wins: 85, ... },
//   ...
// ]
```

**Location**: `lib/db/repositories/players.ts:96-117`

---

#### `updatePlayerElo(playerId: number, newElo: number): Promise<void>`

**Purpose**: Update a player's ELO rating.

**Parameters**:
- `playerId` (number): Player to update
- `newElo` (number): New ELO value

**Returns**: `Promise<void>`

**Throws**: Error if player doesn't exist

**Example**:
```typescript
await updatePlayerElo(1, 1124)
// Player 1's ELO updated to 1124
```

**Use Case**: Called after match creation to apply ELO changes.

**Location**: `lib/db/repositories/players.ts:126-136`

---

#### `batchUpdatePlayersElo(updates: Array<{ player_id: number, global_elo: number }>): Promise<void>`

**Purpose**: Update multiple players' ELOs in sequence.

**Parameters**:
- `updates` (array): Array of player ID + new ELO pairs

**Returns**: `Promise<void>`

**Note**: Supabase doesn't support batch updates with different values per row, so updates are performed **sequentially** in a single function call.

**Performance**: Acceptable for 4 players per match. Would be an issue for bulk operations (100+ updates).

**Example**:
```typescript
await batchUpdatePlayersElo([
  { player_id: 1, global_elo: 1624 },
  { player_id: 2, global_elo: 1424 },
  { player_id: 3, global_elo: 1184 },
  { player_id: 4, global_elo: 1067 }
])
// All 4 players updated sequentially
```

**Location**: `lib/db/repositories/players.ts:145-168`

---

#### `updatePlayer(playerId: number, updates: Partial<Player>): Promise<Player>`

**Purpose**: Update any player fields (name, ELO, etc.).

**Parameters**:
- `playerId` (number): Player to update
- `updates` (Partial<Player>): Fields to update

**Returns**: `Promise<Player>` - Updated player

**Throws**: `PlayerNotFoundError` if player doesn't exist

**Example**:
```typescript
// Update name only
const player = await updatePlayer(1, { name: 'Alice Johnson' })

// Update ELO manually (rare)
const player = await updatePlayer(1, { global_elo: 1900 })
```

**Location**: `lib/db/repositories/players.ts:177-194`

---

#### `deletePlayerById(playerId: number): Promise<void>`

**Purpose**: Delete a player from the database.

**Parameters**:
- `playerId` (number): Player to delete

**Returns**: `Promise<void>`

**Throws**: `PlayerNotFoundError` if player doesn't exist

**Cascade Behavior**: Database foreign keys handle cascade deletes to teams.

**Example**:
```typescript
await deletePlayerById(1)
// Player deleted
// All teams with player_id=1 also deleted (cascade)
```

**Location**: `lib/db/repositories/players.ts:203-220`

---

#### `recordPlayerEloHistory(playerId: number, matchId: number, oldElo: number, newElo: number): Promise<void>`

**Purpose**: Record an ELO change in the history table.

**Parameters**:
- `playerId` (number): Player whose ELO changed
- `matchId` (number): Match that caused the change
- `oldElo` (number): ELO before match
- `newElo` (number): ELO after match

**Returns**: `Promise<void>`

**Data Inserted**:
```typescript
{
  player_id,
  match_id,
  old_elo,
  new_elo,
  difference: newElo - oldElo,
  date: new Date().toISOString()
}
```

**Example**:
```typescript
await recordPlayerEloHistory(1, 42, 1600, 1624)
// Inserts: { player_id: 1, match_id: 42, old_elo: 1600, new_elo: 1624, difference: 24 }
```

**Location**: `lib/db/repositories/players.ts:229-248`

---

#### `getPlayerEloHistory(playerId: number): Promise<PlayerEloHistoryRow[]>`

**Purpose**: Fetch ELO change history for a player.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<PlayerEloHistoryRow[]>` - Ordered by date descending

**Example**:
```typescript
const history = await getPlayerEloHistory(1)
// → [
//   { history_id: 100, player_id: 1, match_id: 42, old_elo: 1600, new_elo: 1624, difference: 24, date: '...' },
//   ...
// ]
```

**Location**: `lib/db/repositories/players.ts:257-274`

**Use Case**: Display ELO progression chart on player detail page.

---

## Team Repository (`lib/db/repositories/teams.ts`)

**Purpose**: All data operations for the `teams` table.

**Location**: `lib/db/repositories/teams.ts`
**Exports**: 13 functions

---

### Utility Functions

#### `normalizePlayerIds(player1Id: number, player2Id: number): [number, number]`

**Purpose**: Ensure player IDs are ordered (lower ID first).

**Parameters**:
- `player1Id` (number): First player ID
- `player2Id` (number): Second player ID

**Returns**: `[number, number]` - Tuple with min ID first

**Why?** Guarantees team uniqueness regardless of player order.

**Example**:
```typescript
normalizePlayerIds(5, 3)  // → [3, 5]
normalizePlayerIds(3, 5)  // → [3, 5]
normalizePlayerIds(7, 2)  // → [2, 7]
```

**Location**: `lib/db/repositories/teams.ts:37-45`

**Database Benefit**: Supports unique index on `(player1_id, player2_id)` without needing to check both orderings.

---

### Core Functions

#### `createTeamByPlayerIds(player1Id: number, player2Id: number, globalElo?: number): Promise<Team>`

**Purpose**: Create a new team, automatically normalizing player order.

**Parameters**:
- `player1Id` (number): First player ID
- `player2Id` (number): Second player ID
- `globalElo` (number, optional): Starting team ELO (default: 1000)

**Returns**: `Promise<Team>` - Created team

**Throws**: Error if team already exists (unique constraint)

**Process**:
1. Normalize player IDs (min first)
2. Insert team with normalized IDs
3. Return created team

**Example**:
```typescript
// These create the SAME team
const team1 = await createTeamByPlayerIds(5, 3)  // Stored as (3, 5)
const team2 = await createTeamByPlayerIds(3, 5)  // Stored as (3, 5) ← duplicate error
```

**Location**: `lib/db/repositories/teams.ts:54-76`

---

#### `getTeamById(teamId: number): Promise<Team | null>`

**Purpose**: Fetch a team by ID.

**Parameters**:
- `teamId` (number): Team identifier

**Returns**: `Promise<Team | null>` - Team if found, null otherwise

**Example**:
```typescript
const team = await getTeamById(10)
// → { team_id: 10, player1_id: 3, player2_id: 5, global_elo: 1500, ... }
```

**Location**: `lib/db/repositories/teams.ts:85-102`

---

#### `getTeamByPlayerIds(player1Id: number, player2Id: number): Promise<Team | null>`

**Purpose**: Find a team by its player pair (order-insensitive).

**Parameters**:
- `player1Id` (number): First player ID
- `player2Id` (number): Second player ID

**Returns**: `Promise<Team | null>` - Team if found, null otherwise

**Process**:
1. Normalize player IDs
2. Query by normalized IDs

**Example**:
```typescript
const team1 = await getTeamByPlayerIds(5, 3)
const team2 = await getTeamByPlayerIds(3, 5)
// Both return the same team: { team_id: 10, player1_id: 3, player2_id: 5, ... }
```

**Use Case**: Check if team exists before creating.

**Location**: `lib/db/repositories/teams.ts:111-134`

---

#### `getAllTeams(): Promise<TeamWithStatsRow[]>`

**Purpose**: Fetch all teams with computed statistics using RPC.

**Returns**: `Promise<TeamWithStatsRow[]>` - Teams with stats

**RPC Function**: `get_all_teams_with_stats_optimized`

**Data Structure**:
```typescript
{
  team_id: number,
  player1_id: number,
  player2_id: number,
  global_elo: number,
  created_at: string,
  last_match_at: string | null,
  matches_played: number,
  wins: number,
  losses: number,
  win_rate: number,
  rank: number
}
```

**Example**:
```typescript
const teams = await getAllTeams()
// → [
//   { team_id: 10, player1_id: 3, player2_id: 5, global_elo: 1750, wins: 30, ... },
//   ...
// ]
```

**Location**: `lib/db/repositories/teams.ts:143-164`

---

#### `getTeamsByPlayerId(playerId: number): Promise<TeamWithStatsRow[]>`

**Purpose**: Find all teams that include a specific player.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<TeamWithStatsRow[]>` - All teams containing this player

**Query Logic**:
```sql
SELECT * FROM teams WHERE player1_id = ? OR player2_id = ?
```

**Example**:
```typescript
const teams = await getTeamsByPlayerId(3)
// → [
//   { team_id: 10, player1_id: 3, player2_id: 5, ... },  // 3 is player1
//   { team_id: 11, player1_id: 2, player2_id: 3, ... },  // 3 is player2
//   ...
// ]
```

**Location**: `lib/db/repositories/teams.ts:173-197`

---

#### `getActiveTeamsWithStats(minMatches: number, daysSinceLastMatch: number): Promise<TeamWithStatsRow[]>`

**Purpose**: Fetch only "active" teams (recent activity + minimum matches).

**Parameters**:
- `minMatches` (number): Minimum matches required (e.g., 10)
- `daysSinceLastMatch` (number): Max days since last match (e.g., 180)

**Returns**: `Promise<TeamWithStatsRow[]>` - Active teams only

**RPC Function**: `get_active_teams_with_stats_batch`

**Filter Logic** (in SQL):
```sql
WHERE matches_played >= minMatches
  AND last_match_at >= NOW() - INTERVAL 'daysSinceLastMatch days'
```

**Example**:
```typescript
const activeTeams = await getActiveTeamsWithStats(10, 180)
// Returns only teams that:
// - Have played 10+ matches
// - Played within the last 6 months
```

**Location**: `lib/db/repositories/teams.ts:206-227`

**Use Case**: Leaderboard that shows only currently-competing teams.

---

#### `updateTeamElo(teamId: number, newElo: number): Promise<void>`

**Purpose**: Update a team's ELO rating.

**Parameters**:
- `teamId` (number): Team to update
- `newElo` (number): New ELO value

**Returns**: `Promise<void>`

**Example**:
```typescript
await updateTeamElo(10, 1780)
// Team 10's ELO updated to 1780
```

**Location**: `lib/db/repositories/teams.ts:236-246`

---

#### `batchUpdateTeamsElo(updates: Array<{ team_id: number, global_elo: number, last_match_at?: string }>): Promise<void>`

**Purpose**: Update multiple teams' ELOs and last match timestamps.

**Parameters**:
- `updates` (array): Array of team updates

**Returns**: `Promise<void>`

**Note**: Sequential updates (same Supabase limitation as players).

**Example**:
```typescript
await batchUpdateTeamsElo([
  { team_id: 10, global_elo: 1780, last_match_at: '2025-12-26T...' },
  { team_id: 11, global_elo: 1220, last_match_at: '2025-12-26T...' }
])
```

**Location**: `lib/db/repositories/teams.ts:255-277`

---

#### `deleteTeamById(teamId: number): Promise<void>`

**Purpose**: Delete a team from the database.

**Parameters**:
- `teamId` (number): Team to delete

**Returns**: `Promise<void>`

**Throws**: `TeamNotFoundError` if team doesn't exist

**Example**:
```typescript
await deleteTeamById(10)
// Team deleted
```

**Location**: `lib/db/repositories/teams.ts:286-303`

---

#### `recordTeamEloHistory(teamId: number, matchId: number, oldElo: number, newElo: number): Promise<void>`

**Purpose**: Record a team ELO change in the history table.

**Parameters**:
- `teamId` (number): Team whose ELO changed
- `matchId` (number): Match that caused the change
- `oldElo` (number): ELO before match
- `newElo` (number): ELO after match

**Returns**: `Promise<void>`

**Data Inserted**:
```typescript
{
  team_id,
  match_id,
  old_elo,
  new_elo,
  difference: newElo - oldElo,
  date: new Date().toISOString()
}
```

**Example**:
```typescript
await recordTeamEloHistory(10, 42, 1750, 1780)
// Inserts: { team_id: 10, match_id: 42, old_elo: 1750, new_elo: 1780, difference: 30 }
```

**Location**: `lib/db/repositories/teams.ts:312-331`

---

## Match Repository (`lib/db/repositories/matches.ts`)

**Purpose**: All data operations for the `matches` table.

**Location**: `lib/db/repositories/matches.ts`
**Exports**: 6 functions

---

### Core Functions

#### `createMatchByTeamIds(winnerTeamId: number, loserTeamId: number, isFanny: boolean, playedAt: string, notes?: string): Promise<number>`

**Purpose**: Insert a new match record.

**Parameters**:
- `winnerTeamId` (number): Winning team ID
- `loserTeamId` (number): Losing team ID
- `isFanny` (boolean): Was it a fanny (blowout) win?
- `playedAt` (string): ISO timestamp of match
- `notes` (string, optional): Additional notes

**Returns**: `Promise<number>` - Created match ID

**Example**:
```typescript
const matchId = await createMatchByTeamIds(10, 11, false, new Date().toISOString(), 'Championship')
// → 42 (match_id)
```

**Location**: `lib/db/repositories/matches.ts:17-41`

---

#### `getMatchById(matchId: number): Promise<Match | null>`

**Purpose**: Fetch a single match by ID.

**Parameters**:
- `matchId` (number): Match identifier

**Returns**: `Promise<Match | null>` - Match if found, null otherwise

**Example**:
```typescript
const match = await getMatchById(42)
// → {
//   match_id: 42,
//   winner_team_id: 10,
//   loser_team_id: 11,
//   is_fanny: false,
//   played_at: '2025-12-26T...',
//   notes: 'Championship'
// }
```

**Location**: `lib/db/repositories/matches.ts:50-67`

---

#### `getAllMatches(options?: MatchFilterOptions): Promise<any[]>`

**Purpose**: Fetch all matches with optional filtering using RPC.

**Parameters**:
- `options` (MatchFilterOptions, optional):
  ```typescript
  {
    start_date?: string,  // ISO date
    end_date?: string,    // ISO date
    is_fanny?: boolean
  }
  ```

**Returns**: `Promise<any[]>` - Matches with team details

**RPC Function**: `get_all_matches_with_details`

**Example**:
```typescript
// All matches
const all = await getAllMatches()

// December 2025 matches
const december = await getAllMatches({
  start_date: '2025-12-01',
  end_date: '2025-12-31'
})

// Fanny matches only
const fannies = await getAllMatches({ is_fanny: true })
```

**Location**: `lib/db/repositories/matches.ts:76-113`

---

#### `getMatchesByTeamId(teamId: number): Promise<any[]>`

**Purpose**: Get all matches for a specific team (as winner or loser).

**Parameters**:
- `teamId` (number): Team identifier

**Returns**: `Promise<any[]>` - Matches with team data

**RPC Function**: `get_team_match_history`

**Example**:
```typescript
const matches = await getMatchesByTeamId(10)
// → [
//   { match_id: 42, winner_team_id: 10, loser_team_id: 11, is_winner: true, ... },
//   { match_id: 43, winner_team_id: 11, loser_team_id: 10, is_winner: false, ... },
//   ...
// ]
```

**Location**: `lib/db/repositories/matches.ts:122-145`

---

#### `getMatchesByPlayerId(playerId: number, limit?: number, offset?: number): Promise<{ matches: any[], total: number }>`

**Purpose**: Get match history for a player with pagination and ELO changes.

**Parameters**:
- `playerId` (number): Player identifier
- `limit` (number, optional): Max matches to return (default: 50)
- `offset` (number, optional): Skip first N matches (default: 0)

**Returns**: Promise resolving to:
```typescript
{
  matches: any[],  // Includes player's ELO changes
  total: number    // Total match count
}
```

**RPC Function**: `get_player_matches_json`

**Special Feature**: Each match includes this player's specific ELO change.

**Example**:
```typescript
const result = await getMatchesByPlayerId(1, 10, 0)
// → {
//   matches: [
//     {
//       match_id: 42,
//       team_id: 10,
//       is_winner: true,
//       opponent_team_id: 11,
//       elo_change: 24,  // ← This player's change
//       played_at: '2025-12-26T...',
//       ...
//     },
//     ...
//   ],
//   total: 156
// }
```

**Location**: `lib/db/repositories/matches.ts:154-189`

---

#### `deleteMatchById(matchId: number): Promise<void>`

**Purpose**: Delete a match from the database.

**Parameters**:
- `matchId` (number): Match to delete

**Returns**: `Promise<void>`

**Throws**: `MatchNotFoundError` if match doesn't exist

**Example**:
```typescript
await deleteMatchById(42)
// Match removed (but ELO changes remain!)
```

**Location**: `lib/db/repositories/matches.ts:198-215`

---

## Stats Repository (`lib/db/repositories/stats.ts`)

**Purpose**: Fetch computed statistics using RPC functions.

**Location**: `lib/db/repositories/stats.ts`
**Exports**: 2 functions

---

### Core Functions

#### `getPlayerStats(playerId: number): Promise<PlayerStatsRow | null>`

**Purpose**: Get detailed statistics for a player.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<PlayerStatsRow | null>` - Stats or null if player doesn't exist

**RPC Function**: `get_player_full_stats_optimized`

**Data Structure**:
```typescript
{
  player_id: number,
  name: string,
  global_elo: number,
  matches_played: number,
  wins: number,
  losses: number,
  win_rate: number,
  last_match_at: string | null,
  created_at: string
}
```

**Example**:
```typescript
const stats = await getPlayerStats(1)
// → {
//   player_id: 1,
//   name: 'Alice',
//   global_elo: 1850,
//   matches_played: 120,
//   wins: 85,
//   losses: 35,
//   win_rate: 0.708,
//   last_match_at: '2025-12-26T...',
//   created_at: '2025-01-01T...'
// }
```

**Location**: `lib/db/repositories/stats.ts:15-38`

---

#### `getTeamStats(teamId: number): Promise<TeamStatsRow | null>`

**Purpose**: Get detailed statistics for a team.

**Parameters**:
- `teamId` (number): Team identifier

**Returns**: `Promise<TeamStatsRow | null>` - Stats or null if team doesn't exist

**RPC Function**: `get_team_full_stats_optimized`

**Data Structure**:
```typescript
{
  team_id: number,
  player1_id: number,
  player2_id: number,
  global_elo: number,
  matches_played: number,
  wins: number,
  losses: number,
  win_rate: number,
  last_match_at: string | null,
  created_at: string
}
```

**Example**:
```typescript
const stats = await getTeamStats(10)
// → {
//   team_id: 10,
//   player1_id: 3,
//   player2_id: 5,
//   global_elo: 1750,
//   matches_played: 45,
//   wins: 30,
//   losses: 15,
//   win_rate: 0.667,
//   last_match_at: '2025-12-26T...',
//   created_at: '2025-02-10T...'
// }
```

**Location**: `lib/db/repositories/stats.ts:47-70`

---

## ELO History Repository (`lib/db/repositories/elo-history.ts`)

**Purpose**: Access ELO change history for players and teams.

**Location**: `lib/db/repositories/elo-history.ts`
**Exports**: 2 functions

---

### Core Functions

#### `getPlayerEloHistory(playerId: number): Promise<PlayerEloHistoryRow[]>`

**Purpose**: Fetch all ELO changes for a player.

**Parameters**:
- `playerId` (number): Player identifier

**Returns**: `Promise<PlayerEloHistoryRow[]>` - Ordered by date descending

**Example**:
```typescript
const history = await getPlayerEloHistory(1)
// → [
//   { history_id: 100, player_id: 1, match_id: 42, old_elo: 1600, new_elo: 1624, difference: 24, date: '...' },
//   { history_id: 99, player_id: 1, match_id: 41, old_elo: 1580, new_elo: 1600, difference: 20, date: '...' },
//   ...
// ]
```

**Location**: `lib/db/repositories/elo-history.ts:15-32`

---

#### `getTeamEloHistory(teamId: number): Promise<TeamEloHistoryRow[]>`

**Purpose**: Fetch all ELO changes for a team.

**Parameters**:
- `teamId` (number): Team identifier

**Returns**: `Promise<TeamEloHistoryRow[]>` - Ordered by date descending

**Example**:
```typescript
const history = await getTeamEloHistory(10)
// → [
//   { history_id: 50, team_id: 10, match_id: 42, old_elo: 1750, new_elo: 1780, difference: 30, date: '...' },
//   ...
// ]
```

**Location**: `lib/db/repositories/elo-history.ts:41-58`

---

## Repository Design Patterns

### 1. Single Table per Repository

Each repository manages **exactly one table**:
- `players.ts` → `players` table
- `teams.ts` → `teams` table
- `matches.ts` → `matches` table
- History tables are split to `elo-history.ts`

### 2. Error Handling

Repositories throw **specific errors**:
```typescript
if (!player) {
  throw new PlayerNotFoundError(playerId)
}
```

They do **not** return error objects or status codes.

### 3. Retry Wrapper

All repository functions should be wrapped with `withRetry()`:

```typescript
export async function getPlayer(id: number): Promise<Player> {
  return withRetry(async () => {
    // Database operation here
  })
}
```

This provides automatic retry on transient failures.

### 4. RPC Function Calls

For complex queries with aggregations, repositories call **RPC functions**:

```typescript
const { data, error } = await supabase.rpc('get_all_players_with_stats_optimized')
```

**Benefits**:
- Single database round-trip
- Server-side computation
- Avoids N+1 query problem

### 5. Null vs Throw

**Return null**: When absence is a valid state (e.g., checking if team exists)
```typescript
const team = await getTeamByPlayerIds(1, 2)  // null if not found
```

**Throw error**: When entity must exist (e.g., fetching by ID)
```typescript
const player = await getPlayerById(1)  // throws if not found
```

### 6. Normalization at Repository Level

Team player ID normalization happens **in the repository**, not the service:

```typescript
export async function createTeamByPlayerIds(player1Id, player2Id) {
  const [p1, p2] = normalizePlayerIds(player1Id, player2Id)
  // Use normalized IDs for insert
}
```

This ensures all team creation paths automatically normalize IDs.

---

## Database Query Optimization

### Index Strategy

The database has strategic indexes to support repository queries:

**Player Queries**:
- `players_pkey`: Primary key on `player_id`
- Implicit index on `name` (unique constraint)

**Team Queries**:
- `teams_pkey`: Primary key on `team_id`
- `idx_teams_player_pair_order_insensitive`: Composite index on `(player1_id, player2_id)`
- Supports fast lookups by player pair

**Match Queries**:
- `matches_pkey`: Primary key on `match_id`
- `idx_matches_played_at`: Index on `played_at` for date filtering
- `idx_matches_winner_team_id`: Foreign key index
- `idx_matches_loser_team_id`: Foreign key index

**History Queries**:
- `idx_players_elohist_player_id`: Index on `player_id` in `players_elo_history`
- `idx_players_elohist_match_id`: Index on `match_id`
- Similar indexes for team history

### RPC Performance

RPC functions use **CTEs (Common Table Expressions)** for efficiency:

```sql
WITH player_stats AS (
  SELECT ... FROM (match aggregation) GROUP BY player_id
)
SELECT * FROM players p CROSS JOIN player_stats ps WHERE p.player_id = ps.player_id
```

This approach is **41x faster** than the naive helper-function approach.

---

## Testing Repositories

### Integration Tests

Repositories require database access, so tests are **integration tests**:

```typescript
import { createPlayer, getPlayerById } from '@/lib/db/repositories/players'

describe('Player Repository', () => {
  test('createPlayer inserts and returns player', async () => {
    const player = await createPlayer('TestUser', 1000)

    expect(player.player_id).toBeDefined()
    expect(player.name).toBe('TestUser')
    expect(player.global_elo).toBe(1000)
  })

  test('getPlayerById fetches existing player', async () => {
    const created = await createPlayer('Alice', 1200)
    const fetched = await getPlayerById(created.player_id)

    expect(fetched).toEqual(created)
  })
})
```

**Setup**: Tests run against local Supabase instance (started with `bun run supabase:start`).

### Mocking Repositories in Service Tests

When testing **services**, mock repositories to avoid database dependency:

```typescript
import * as playerRepo from '@/lib/db/repositories/players'

jest.mock('@/lib/db/repositories/players')

describe('Player Service', () => {
  test('createNewPlayer calls repository', async () => {
    const mockPlayer = { player_id: 1, name: 'Alice', global_elo: 1000 }
    playerRepo.createPlayer.mockResolvedValue(mockPlayer)

    const result = await createNewPlayer({ name: 'Alice' })

    expect(playerRepo.createPlayer).toHaveBeenCalledWith('Alice', 1000)
    expect(result).toEqual(mockPlayer)
  })
})
```

---

## Common Patterns

### Existence Check Before Create

```typescript
const existing = await getPlayerByName(name)
if (existing) {
  throw new PlayerAlreadyExistsError(name)
}
const player = await createPlayer(name, elo)
```

### Fetch with Fallback Error

```typescript
const player = await getPlayerById(playerId)
if (!player) {
  throw new PlayerNotFoundError(playerId)
}
return player
```

### Batch Updates (Sequential)

```typescript
for (const update of updates) {
  await updateSingleEntity(update.id, update.value)
}
```

**Note**: Acceptable for small batches (2-10 items). For large batches, consider bulk SQL.

### RPC Call with Error Handling

```typescript
const { data, error } = await supabase.rpc('function_name', { params })

if (error) {
  throw new Error(`RPC function_name failed: ${error.message}`)
}

return data
```

---

## Maintenance Notes

### Adding New Repository Functions

1. **Identify the table**: Which table does this query?
2. **Choose return type**: Entity object, array, or null?
3. **Error handling**: Throw or return null?
4. **Wrap with retry**: Use `withRetry()` wrapper
5. **Add tests**: Integration tests with local Supabase

### Performance Optimization

If a query is slow:
1. **Check indexes**: Does the query use indexed columns?
2. **Consider RPC**: Can aggregation move to SQL?
3. **Batch operations**: Can you reduce round-trips?

### Breaking Changes

**Changing repository signatures breaks services**. If you must change:
1. Create new function with new signature
2. Update all service calls
3. Remove old function
4. Update tests

---

## Summary

The repository layer is the **data access boundary** in Baby Foot ELO. It:
- Abstracts Supabase implementation details
- Provides type-safe database operations
- Centralizes query logic
- Enables service layer testing through mocking
- Optimizes queries with RPC functions and indexes

**Key Takeaway**: Repositories are **stateless data accessors**. They don't contain business logic or validation beyond existence checks.

---

**Next**: [Component Reference Documentation](./07-component-reference.md)

**Last Updated**: 2025-12-26
