# Database Schema

## Document Information

- **Document Type**: Database Design Reference
- **Target Audience**: Database Administrators, Backend Developers
- **Last Updated**: 2025-12-26
- **Maintainer**: Development Team

## Overview

The Baby Foot ELO application uses PostgreSQL (via Supabase) with a normalized relational schema optimized for ELO tracking and match history. The schema consists of 5 core tables with referential integrity enforced through foreign keys.

## Entity Relationship Diagram

```text
┌─────────────────────────────┐
│         players             │
├─────────────────────────────┤
│ player_id (PK)              │ ◄───────┐
│ name (UNIQUE)               │         │
│ global_elo                  │         │
│ created_at                  │         │
│ last_match_at               │         │
└─────────────────────────────┘         │
        ▲                               │
        │                               │
        │                               │
        │ FK                            │ FK
        │                               │
┌───────┴─────────────────────┐         │
│         teams               │         │
├─────────────────────────────┤         │
│ team_id (PK)                │         │
│ player1_id (FK) ────────────┼─────────┘
│ player2_id (FK) ────────────┼─────────┐
│ global_elo                  │         │
│ created_at                  │         │
│ last_match_at               │         │
└─────────────────────────────┘         │
        ▲                               │
        │                               │
        │ FK                            │
        │                               │
┌───────┴─────────────────────┐         │
│        matches              │         │
├─────────────────────────────┤         │
│ match_id (PK)               │         │
│ winner_team_id (FK)         │         │
│ loser_team_id (FK)          │         │
│ is_fanny                    │         │
│ played_at                   │         │
│ notes                       │         │
└─────────────────────────────┘         │
        │                               │
        │                               │
        │ FK                            │
        │                               │
        ├───────────────────────────────┤
        │                               │
┌───────▼─────────────────────┐  ┌──────▼──────────────────────┐
│    player_history           │  │     team_history            │
├─────────────────────────────┤  ├─────────────────────────────┤
│ history_id (PK)             │  │ history_id (PK)             │
│ player_id (FK) ─────────────┼──┤ team_id (FK)                │
│ match_id (FK)               │  │ match_id (FK)               │
│ old_elo                     │  │ old_elo                     │
│ new_elo                     │  │ new_elo                     │
│ date                        │  │ date                        │
└─────────────────────────────┘  └─────────────────────────────┘
```

## Table Definitions

### `players`

**Purpose**: Stores individual player information and current global ELO rating.

**Columns**:

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `player_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for each player |
| `name` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE` | Player's display name (case-sensitive) |
| `global_elo` | `INTEGER` | `NOT NULL`, `DEFAULT 1000` | Current ELO rating (starting at 1000) |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT NOW()` | Player registration timestamp |
| `last_match_at` | `TIMESTAMP WITH TIME ZONE` | `NULL` | Timestamp of most recent match |

**Indexes**:
- Primary key on `player_id`
- Unique index on `name`
- Index on `global_elo` (for ranking queries)

**Business Rules**:
- Player names must be unique (case-sensitive comparison)
- Starting ELO is always 1000
- `last_match_at` updated automatically when player participates in a match
- Players cannot be deleted if they have match history (CASCADE rules prevent orphaned data)

**Example Row**:
```sql
INSERT INTO players (name, global_elo, created_at, last_match_at)
VALUES ('Alice', 1620, '2025-01-15 10:30:00+00', '2025-12-26 14:25:00+00');
```

---

### `teams`

**Purpose**: Stores team pairings of two players with their combined ELO rating.

**Columns**:

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `team_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for each team |
| `player1_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → players(player_id)` | First player in the team |
| `player2_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → players(player_id)` | Second player in the team |
| `global_elo` | `INTEGER` | `NOT NULL`, `DEFAULT 1000` | Current team ELO rating |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT NOW()` | Team creation timestamp |
| `last_match_at` | `TIMESTAMP WITH TIME ZONE` | `NULL` | Timestamp of team's most recent match |

**Indexes**:
- Primary key on `team_id`
- Composite index on `(player1_id, player2_id)` (for uniqueness check)
- Index on `global_elo` (for ranking queries)
- Foreign key indexes on `player1_id` and `player2_id`

**Constraints**:
- `player1_id` and `player2_id` must reference existing players
- `player1_id` ≠ `player2_id` (enforced at application level)
- No duplicate teams (same pair of players)

**Business Rules**:
- Starting team ELO is average of both players' current ELOs at creation time
- Team ELO evolves independently from player ELOs after creation
- `last_match_at` updated when team plays a match
- Teams are auto-created when new players join (one team per existing player)

**Example Row**:
```sql
INSERT INTO teams (player1_id, player2_id, global_elo, created_at, last_match_at)
VALUES (1, 2, 1514, '2025-01-15 10:35:00+00', '2025-12-26 14:25:00+00');
```

---

### `matches`

**Purpose**: Records individual matches between two teams with outcome and metadata.

**Columns**:

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `match_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for each match |
| `winner_team_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → teams(team_id)` | Team that won the match |
| `loser_team_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → teams(team_id)` | Team that lost the match |
| `is_fanny` | `BOOLEAN` | `NOT NULL`, `DEFAULT FALSE` | True if losing team scored 0 points (fanny) |
| `played_at` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL`, `DEFAULT NOW()` | When the match was played |
| `notes` | `TEXT` | `NULL` | Optional match notes or comments |

**Indexes**:
- Primary key on `match_id`
- Index on `winner_team_id`
- Index on `loser_team_id`
- Index on `played_at` (for chronological queries)
- Composite index on `(winner_team_id, played_at)` (for team match history)
- Composite index on `(loser_team_id, played_at)` (for team match history)

**Constraints**:
- `winner_team_id` and `loser_team_id` must reference existing teams
- `winner_team_id` ≠ `loser_team_id` (enforced at application level)

**Business Rules**:
- Match creation triggers ELO recalculation for all 4 players and 2 teams
- `played_at` can be backdated for historical data entry
- `is_fanny` flag may affect future ELO calculations (currently no impact)
- Deleting a match does NOT reverse ELO changes (soft delete behavior)

**Example Row**:
```sql
INSERT INTO matches (winner_team_id, loser_team_id, is_fanny, played_at, notes)
VALUES (5, 3, FALSE, '2025-12-26 14:25:00+00', 'Championship final match');
```

---

### `player_history`

**Purpose**: Audit trail of player ELO changes per match for historical analysis.

**Columns**:

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `history_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for history entry |
| `player_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → players(player_id)` | Player whose ELO changed |
| `match_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → matches(match_id)` | Match that caused the ELO change |
| `old_elo` | `INTEGER` | `NOT NULL` | Player's ELO before the match |
| `new_elo` | `INTEGER` | `NOT NULL` | Player's ELO after the match |
| `date` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL` | When the change occurred (matches `played_at`) |

**Indexes**:
- Primary key on `history_id`
- Index on `player_id` (for player ELO progression queries)
- Index on `match_id` (for match impact analysis)
- Composite index on `(player_id, date)` (for chronological player history)

**Constraints**:
- `player_id` must reference an existing player
- `match_id` must reference an existing match
- `old_elo` and `new_elo` must be positive integers

**Business Rules**:
- One entry created per player per match (4 entries total per match)
- ELO difference: `new_elo - old_elo` can be positive or negative
- Used for ELO trend charts and historical analysis
- Preserved even if match is deleted (for audit purposes)

**Example Row**:
```sql
INSERT INTO player_history (player_id, match_id, old_elo, new_elo, date)
VALUES (1, 42, 1600, 1620, '2025-12-26 14:25:00+00');
```

---

### `team_history`

**Purpose**: Audit trail of team ELO changes per match for historical analysis.

**Columns**:

| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `history_id` | `INTEGER` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for history entry |
| `team_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → teams(team_id)` | Team whose ELO changed |
| `match_id` | `INTEGER` | `NOT NULL`, `FOREIGN KEY → matches(match_id)` | Match that caused the ELO change |
| `old_elo` | `INTEGER` | `NOT NULL` | Team's ELO before the match |
| `new_elo` | `INTEGER` | `NOT NULL` | Team's ELO after the match |
| `date` | `TIMESTAMP WITH TIME ZONE` | `NOT NULL` | When the change occurred (matches `played_at`) |

**Indexes**:
- Primary key on `history_id`
- Index on `team_id` (for team ELO progression queries)
- Index on `match_id` (for match impact analysis)
- Composite index on `(team_id, date)` (for chronological team history)

**Constraints**:
- `team_id` must reference an existing team
- `match_id` must reference an existing match
- `old_elo` and `new_elo` must be positive integers

**Business Rules**:
- One entry created per team per match (2 entries total per match)
- ELO difference: `new_elo - old_elo` can be positive or negative
- Used for team ELO trend analysis
- Preserved even if match is deleted

**Example Row**:
```sql
INSERT INTO team_history (team_id, match_id, old_elo, new_elo, date)
VALUES (5, 42, 1500, 1514, '2025-12-26 14:25:00+00');
```

## RPC Functions (PostgreSQL)

The application uses custom PostgreSQL functions (RPC) for optimized data retrieval with pre-aggregated statistics. These functions are located in the `supabase/` directory and called via Supabase RPC.

### `get_all_players_with_stats_optimized`

**Purpose**: Retrieve all players with computed statistics (wins, losses, win rate, rank).

**Performance**: 41x faster than previous ORM-based approach using CTEs for pre-aggregation.

**SQL Location**: `supabase/functions/get_all_players_with_stats.sql`

**Returns**: Array of player records with:
- All `players` table columns
- `wins` (INTEGER) - Total wins across all teams
- `losses` (INTEGER) - Total losses across all teams
- `matches_played` (INTEGER) - Total matches played
- `win_rate` (DECIMAL) - Win percentage (0-100)
- `rank` (INTEGER) - Rank by ELO (1 = highest)

**Query Structure**:
```sql
WITH matches_as_winner AS (
  -- Aggregate wins per player
  SELECT player1_id, player2_id, COUNT(*) as wins
  FROM matches m
  JOIN teams t ON m.winner_team_id = t.team_id
  GROUP BY player1_id, player2_id
),
matches_as_loser AS (
  -- Aggregate losses per player
  SELECT player1_id, player2_id, COUNT(*) as losses
  FROM matches m
  JOIN teams t ON m.loser_team_id = t.team_id
  GROUP BY player1_id, player2_id
),
aggregated_stats AS (
  SELECT
    p.*,
    COALESCE(w.wins, 0) + COALESCE(l.losses, 0) as matches_played,
    CASE WHEN matches_played > 0
         THEN (COALESCE(w.wins, 0)::DECIMAL / matches_played * 100)
         ELSE 0 END as win_rate,
    ROW_NUMBER() OVER (ORDER BY p.global_elo DESC) as rank
  FROM players p
  LEFT JOIN matches_as_winner w ...
  LEFT JOIN matches_as_loser l ...
)
SELECT * FROM aggregated_stats ORDER BY rank;
```

---

### `get_all_teams_with_stats`

**Purpose**: Retrieve all teams with computed statistics (wins, losses, win rate, rank).

**SQL Location**: `supabase/functions/get_all_teams_with_stats.sql`

**Returns**: Array of team records with:
- All `teams` table columns
- Player objects (nested): `player1` and `player2` with full details
- `wins` (INTEGER)
- `losses` (INTEGER)
- `matches_played` (INTEGER)
- `win_rate` (DECIMAL)
- `rank` (INTEGER)

**Query Structure**: Similar CTE pattern to player stats with JOINs to embed player data.

---

### `get_player_matches_json`

**Purpose**: Retrieve match history for a specific player with ELO changes.

**SQL Location**: `supabase/functions/get_player_matches_json.sql`

**Parameters**:
- `player_id_param` (INTEGER) - Player to fetch matches for

**Returns**: JSON array of matches with:
- Match details (teams, date, outcome)
- Player's ELO change for that match
- Team composition (partner's name)
- Win/loss indicator

**Query Structure**:
```sql
SELECT json_build_object(
  'match_id', m.match_id,
  'played_at', m.played_at,
  'is_fanny', m.is_fanny,
  'player_elo_change', (
    SELECT new_elo - old_elo
    FROM player_history
    WHERE player_id = player_id_param AND match_id = m.match_id
  ),
  'team', json_build_object(...),
  'opponent_team', json_build_object(...),
  'result', CASE WHEN ... THEN 'WIN' ELSE 'LOSS' END
) as match_data
FROM matches m
JOIN teams winner_team ON ...
JOIN teams loser_team ON ...
WHERE winner_team.player1_id = player_id_param
   OR winner_team.player2_id = player_id_param
   OR loser_team.player1_id = player_id_param
   OR loser_team.player2_id = player_id_param
ORDER BY m.played_at DESC;
```

---

### `get_team_match_history`

**Purpose**: Retrieve match history for a specific team with ELO changes.

**SQL Location**: `supabase/functions/get_team_match_history.sql`

**Parameters**:
- `team_id_param` (INTEGER) - Team to fetch matches for

**Returns**: Similar structure to player matches, but focused on team ELO changes.

---

### `get_all_matches_with_details`

**Purpose**: Retrieve all matches with full team and player details.

**SQL Location**: `supabase/functions/get_all_matches_with_details.sql` (inferred)

**Returns**: Match records with nested team/player objects for display.

---

### `get_player_full_stats`

**Purpose**: Comprehensive player statistics including ELO progression, streaks, and performance metrics.

**SQL Location**: `supabase/functions/get_player_full_stats.sql`

**Parameters**:
- `player_id_param` (INTEGER)

**Returns**: Single object with:
- Player details
- Total wins, losses, matches
- Current win streak
- Longest win streak
- Average ELO gain per win
- Average ELO loss per loss
- Recent form (last 10 matches)
- All-time high ELO

## Data Integrity Constraints

### Foreign Key Relationships

**Teams → Players**:
```sql
ALTER TABLE teams
ADD CONSTRAINT fk_player1 FOREIGN KEY (player1_id) REFERENCES players(player_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_player2 FOREIGN KEY (player2_id) REFERENCES players(player_id) ON DELETE CASCADE;
```

**Matches → Teams**:
```sql
ALTER TABLE matches
ADD CONSTRAINT fk_winner_team FOREIGN KEY (winner_team_id) REFERENCES teams(team_id) ON DELETE RESTRICT,
ADD CONSTRAINT fk_loser_team FOREIGN KEY (loser_team_id) REFERENCES teams(team_id) ON DELETE RESTRICT;
```

**History → Players/Teams/Matches**:
```sql
ALTER TABLE player_history
ADD CONSTRAINT fk_player FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_match FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE;

ALTER TABLE team_history
ADD CONSTRAINT fk_team FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE CASCADE,
ADD CONSTRAINT fk_match FOREIGN KEY (match_id) REFERENCES matches(match_id) ON DELETE CASCADE;
```

### Cascade Behavior

- **DELETE player**: Cascades to `teams` and `player_history` (removes all player data)
- **DELETE team**: Restricted if referenced by `matches` (cannot delete team with match history)
- **DELETE match**: Cascades to `player_history` and `team_history` (preserves audit trail decision made at application level)

### Unique Constraints

- `players.name` - No duplicate player names
- Implicit unique on `(teams.player1_id, teams.player2_id)` - No duplicate team pairings (enforced at application level)

## Query Performance

### Optimized Queries

1. **Player Rankings**:
```sql
SELECT * FROM get_all_players_with_stats_optimized() ORDER BY rank LIMIT 100;
```
**Performance**: O(n log n) due to CTE aggregation + sorting
**Index Usage**: Uses `players.global_elo` index

2. **Team Rankings**:
```sql
SELECT * FROM get_all_teams_with_stats() ORDER BY rank LIMIT 100;
```
**Performance**: Similar to player rankings

3. **Match History (Filtered by Date)**:
```sql
SELECT * FROM matches
WHERE played_at >= '2025-01-01' AND played_at < '2026-01-01'
ORDER BY played_at DESC
LIMIT 50;
```
**Performance**: O(log n) due to `played_at` index + LIMIT

4. **Player ELO Trend**:
```sql
SELECT old_elo, new_elo, date
FROM player_history
WHERE player_id = $1
ORDER BY date ASC;
```
**Performance**: O(m log m) where m = player's matches (uses composite index)

### Index Coverage

All foreign keys are indexed for JOIN performance:
- `teams.player1_id`, `teams.player2_id`
- `matches.winner_team_id`, `matches.loser_team_id`
- `player_history.player_id`, `player_history.match_id`
- `team_history.team_id`, `team_history.match_id`

Frequently queried columns:
- `players.global_elo` (rankings)
- `teams.global_elo` (rankings)
- `matches.played_at` (chronological queries)

## Migration Strategy

### Schema Changes

**Location**: Supabase migrations (not currently tracked in codebase)

**Process**:
1. Create migration SQL in Supabase dashboard
2. Test on development database
3. Apply to production with zero downtime (Supabase handles)

### Backwards Compatibility

- Adding columns: Use `DEFAULT` values or `NULL` to avoid breaking existing queries
- Removing columns: Deprecate in application code first, remove after 1+ deployment
- Changing RPC functions: Version them (`get_all_players_with_stats_v2`) or use optional parameters

### Data Seeding

**Initial Data**:
- Minimum 2 players required for functionality
- Teams auto-created when players added

**Example Seed**:
```sql
INSERT INTO players (name, global_elo) VALUES
  ('Alice', 1000),
  ('Bob', 1000);

-- Team auto-created by application when players registered
```

## Maintenance Notes

### When to Update This Document

- Table schema changes (new columns, constraints)
- New RPC functions added
- Index strategy changes
- Foreign key relationship modifications

### Performance Monitoring

**Slow Query Candidates**:
- Match history without date filter (full table scan)
- Player stats without RPC (N+1 queries)

**Optimization Checklist**:
- [ ] All foreign keys indexed
- [ ] Frequently filtered columns indexed
- [ ] RPC functions use CTEs for aggregation
- [ ] LIMIT clauses on large result sets
- [ ] Composite indexes on `(entity_id, date)` patterns

### Backup Strategy

- Supabase automatic backups (daily)
- Point-in-time recovery available
- Export critical data via CSV for local backup

## Related Documentation

- `01-architecture-overview.md` - System architecture context
- `03-elo-calculation-system.md` - ELO algorithm details
