# Sequence Diagrams

## Document Information

- **Document Type**: Technical Flow Documentation
- **Target Audience**: Developers, System Designers
- **Last Updated**: 2025-12-26
- **Maintainer**: Development Team

## Overview

This document provides detailed sequence diagrams for the critical flows in the Baby Foot ELO application. Each diagram illustrates the interaction between components during key operations.

## 1. Match Creation Flow

The match creation flow is the most complex operation in the system, involving validation, ELO calculation, and multiple database updates in an atomic transaction.

```sql
┌────────┐      ┌─────────┐      ┌──────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐
│ Client │      │  API    │      │ matches  │      │   elo   │      │  repos   │      │ Database │
│  (UI)  │      │  Route  │      │ service  │      │ service │      │          │      │          │
└────┬───┘      └────┬────┘      └────┬─────┘      └────┬────┘      └────┬─────┘      └────┬─────┘
     │               │                │                 │                │                │
     │ POST /api/v1/matches          │                 │                │                │
     │ {winner_team_id, loser_team_id, ...}           │                │                │
     ├──────────────>│                │                 │                │                │
     │               │                │                 │                │                │
     │               │ Validate with Zod               │                │                │
     │               │ MatchCreateSchema               │                │                │
     │               │────────┐       │                 │                │                │
     │               │        │       │                 │                │                │
     │               │<───────┘       │                 │                │                │
     │               │                │                 │                │                │
     │               │ createNewMatch(data)            │                │                │
     │               ├───────────────>│                 │                │                │
     │               │                │                 │                │                │
     │               │                │ Validate teams different        │                │
     │               │                │────────┐        │                │                │
     │               │                │        │        │                │                │
     │               │                │<───────┘        │                │                │
     │               │                │                 │                │                │
     │               │                │ getTeam(winner_id)              │                │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ RPC: get_team_with_stats
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │                 │                │ {team + players + stats}
     │               │                │                 │                │<───────────────┤
     │               │                │                 │                │                │
     │               │                │ winningTeam     │                │                │
     │               │                │<────────────────────────────────┤                │
     │               │                │                 │                │                │
     │               │                │ getTeam(loser_id) [parallel]    │                │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ RPC: get_team_with_stats
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │ losingTeam      │                │                │
     │               │                │<────────────────────────────────┤                │
     │               │                │                 │                │                │
     │               │                │ createMatchByTeamIds(...)       │                │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ INSERT INTO matches
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │ match_id (42)   │                │ {match_id: 42} │
     │               │                │<────────────────────────────────┤<───────────────┤
     │               │                │                 │                │                │
     │               │                │ processMatchResult(winning, losing)              │
     │               │                ├────────────────>│                │                │
     │               │                │                 │                │                │
     │               │                │                 │ Calculate team ELOs            │
     │               │                │                 │ (avg of player ELOs)           │
     │               │                │                 │────────┐       │                │
     │               │                │                 │        │       │                │
     │               │                │                 │<───────┘       │                │
     │               │                │                 │                │                │
     │               │                │                 │ Calculate win probability      │
     │               │                │                 │ 1/(1+10^((ELO_B-ELO_A)/400))   │
     │               │                │                 │────────┐       │                │
     │               │                │                 │        │       │                │
     │               │                │                 │<───────┘       │                │
     │               │                │                 │                │                │
     │               │                │                 │ For each of 4 players:         │
     │               │                │                 │ - determineKFactor(elo)        │
     │               │                │                 │ - calculateEloChange(...)      │
     │               │                │                 │────────┐       │                │
     │               │                │                 │        │       │                │
     │               │                │                 │<───────┘       │                │
     │               │                │                 │                │                │
     │               │                │                 │ Pool correction (zero-sum)     │
     │               │                │                 │ - Sum all changes              │
     │               │                │                 │ - Distribute delta by K-factor │
     │               │                │                 │────────┐       │                │
     │               │                │                 │        │       │                │
     │               │                │                 │<───────┘       │                │
     │               │                │                 │                │                │
     │               │                │ {playersChange, teamsChange}    │                │
     │               │                │<────────────────┤                │                │
     │               │                │                 │                │                │
     │               │                │ batchUpdatePlayersElo([...])    │                │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ UPDATE players SET
     │               │                │                 │                │ global_elo = CASE...
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │                 │                │ {count: 4}     │
     │               │                │<────────────────────────────────┤<───────────────┤
     │               │                │                 │                │                │
     │               │                │ batchRecordPlayerEloUpdates([...])               │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ INSERT INTO player_history
     │               │                │                 │                │ (4 rows)       │
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │                 │                │ {count: 4}     │
     │               │                │<────────────────────────────────┤<───────────────┤
     │               │                │                 │                │                │
     │               │                │ batchUpdateTeamsElo([...])      │                │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ UPDATE teams   │
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │                 │                │ {count: 2}     │
     │               │                │<────────────────────────────────┤<───────────────┤
     │               │                │                 │                │                │
     │               │                │ batchRecordTeamEloUpdates([...]) │                │
     │               │                ├────────────────────────────────>│                │
     │               │                │                 │                │                │
     │               │                │                 │                │ INSERT INTO team_history
     │               │                │                 │                │ (2 rows)       │
     │               │                │                 │                ├───────────────>│
     │               │                │                 │                │                │
     │               │                │                 │                │ {count: 2}     │
     │               │                │<────────────────────────────────┤<───────────────┤
     │               │                │                 │                │                │
     │               │                │ Format MatchWithEloResponse     │                │
     │               │                │ {match, teams, elo_changes}     │                │
     │               │                │────────┐        │                │                │
     │               │                │        │        │                │                │
     │               │                │<───────┘        │                │                │
     │               │                │                 │                │                │
     │               │ MatchWithEloResponse            │                │                │
     │               │<───────────────┤                 │                │                │
     │               │                │                 │                │                │
     │ 201 Created   │                │                 │                │                │
     │ {match + ELO changes}          │                 │                │                │
     │<──────────────┤                │                 │                │                │
     │               │                │                 │                │                │
```

**Key Points**:
- **Atomic Operation**: All 9 steps succeed or entire transaction rolls back
- **Parallel Fetches**: Both teams fetched simultaneously for performance
- **Pool Correction**: Ensures zero-sum ELO across all 4 players
- **Batch Updates**: Single query updates multiple players/teams
- **Audit Trail**: History records created for all ELO changes

**Error Scenarios**:
- Validation fails → 422 Unprocessable Entity
- Team not found → 404 Not Found
- Same team winner/loser → 400 Bad Request
- Database error → 500 Internal Server Error (retried 3 times)

---

## 2. Player Rankings Retrieval Flow

This flow demonstrates how optimized RPC functions reduce query complexity and improve performance.

```bash
┌────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ Client │      │  API    │      │ players  │      │  repos   │      │ Database │
│  (UI)  │      │  Route  │      │ service  │      │          │      │          │
└────┬───┘      └────┬────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │               │                │                 │                │
     │ GET /api/v1/players/rankings?limit=100          │                │
     ├──────────────>│                │                 │                │
     │               │                │                 │                │
     │               │ getAllPlayersWithStats()        │                │
     │               ├───────────────>│                 │                │
     │               │                │                 │                │
     │               │                │ getAllPlayers() │                │
     │               │                ├────────────────>│                │
     │               │                │                 │                │
     │               │                │                 │ RPC: get_all_players_with_stats_optimized()
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │                 │                │ WITH matches_as_winner AS (
     │               │                │                 │                │   -- CTE: aggregate wins
     │               │                │                 │                │ ),
     │               │                │                 │                │ matches_as_loser AS (
     │               │                │                 │                │   -- CTE: aggregate losses
     │               │                │                 │                │ ),
     │               │                │                 │                │ aggregated_stats AS (
     │               │                │                 │                │   SELECT p.*, wins, losses,
     │               │                │                 │                │   win_rate, rank
     │               │                │                 │                │   FROM players p
     │               │                │                 │                │   LEFT JOIN wins/losses
     │               │                │                 │                │   ROW_NUMBER() for rank
     │               │                │                 │                │ )
     │               │                │                 │                │ SELECT * ORDER BY rank
     │               │                │                 │                │────────┐
     │               │                │                 │                │        │
     │               │                │                 │                │<───────┘
     │               │                │                 │                │
     │               │                │                 │ PlayerWithStatsRow[]
     │               │                │                 │<───────────────┤
     │               │                │                 │                │
     │               │                │ PlayerWithStatsRow[]            │
     │               │                │<────────────────┤                │
     │               │                │                 │                │
     │               │                │ Map to PlayerResponse[]         │
     │               │                │────────┐        │                │
     │               │                │        │        │                │
     │               │                │<───────┘        │                │
     │               │                │                 │                │
     │               │ PlayerResponse[]                │                │
     │               │<───────────────┤                 │                │
     │               │                │                 │                │
     │ 200 OK        │                │                 │                │
     │ [players with stats]           │                 │                │
     │<──────────────┤                │                 │                │
     │               │                │                 │                │
```

**Performance**: 41x faster than ORM approach due to:
- Single RPC call (no N+1 queries)
- Database-side aggregation with CTEs
- Pre-computed rank via `ROW_NUMBER()`

**SWR Caching** (Frontend):
```typescript
const { data } = useSWR(
  '/api/v1/players/rankings',
  getPlayers,
  { refreshInterval: 30000 } // 30s cache
);
```

---

## 3. Player Detail Page Load Flow

This flow shows how multiple API calls are coordinated to populate a detail page.

```sql
┌────────┐      ┌─────────────┐      ┌─────────┐      ┌──────────┐
│Browser │      │   SWR Hook  │      │   API   │      │ Database │
│  Page  │      │  (Frontend) │      │  Routes │      │          │
└────┬───┘      └──────┬──────┘      └────┬────┘      └────┬─────┘
     │                 │                  │                │
     │ Navigate to /players/42           │                │
     ├────────┐        │                  │                │
     │        │        │                  │                │
     │<───────┘        │                  │                │
     │                 │                  │                │
     │ Trigger 3 parallel SWR fetches    │                │
     ├────────────────>│                  │                │
     │                 │                  │                │
     │                 │ GET /api/v1/players/42/statistics│
     │                 ├─────────────────>│                │
     │                 │                  │                │
     │                 │                  │ RPC: get_player_full_stats(42)
     │                 │                  ├───────────────>│
     │                 │                  │                │
     │                 │                  │ {stats with ELO history, streaks}
     │                 │                  │<───────────────┤
     │                 │                  │                │
     │                 │ PlayerStats      │                │
     │                 │<─────────────────┤                │
     │                 │                  │                │
     │                 │ GET /api/v1/players/42/matches   │
     │                 ├─────────────────>│                │
     │                 │                  │                │
     │                 │                  │ RPC: get_player_matches_json(42)
     │                 │                  ├───────────────>│
     │                 │                  │                │
     │                 │                  │ [{match, elo_change, result}]
     │                 │                  │<───────────────┤
     │                 │                  │                │
     │                 │ Match[]          │                │
     │                 │<─────────────────┤                │
     │                 │                  │                │
     │                 │ GET /api/v1/players/42/elo-history
     │                 ├─────────────────>│                │
     │                 │                  │                │
     │                 │                  │ SELECT * FROM player_history
     │                 │                  │ WHERE player_id = 42
     │                 │                  │ ORDER BY date ASC
     │                 │                  ├───────────────>│
     │                 │                  │                │
     │                 │                  │ [{date, old_elo, new_elo}]
     │                 │                  │<───────────────┤
     │                 │                  │                │
     │                 │ EloHistory[]     │                │
     │                 │<─────────────────┤                │
     │                 │                  │                │
     │ {stats, matches, eloHistory}      │                │
     │<────────────────┤                  │                │
     │                 │                  │                │
     │ Render PlayerDetail component     │                │
     │ - Stats cards   │                  │                │
     │ - Match history │                  │                │
     │ - ELO trend chart                  │                │
     │────────┐        │                  │                │
     │        │        │                  │                │
     │<───────┘        │                  │                │
     │                 │                  │                │
```

**Parallel Fetching**: All 3 API calls fire simultaneously via SWR, reducing total load time.

**Loading States**:
- Show skeleton loaders while data loads
- Display error alerts if any fetch fails
- Progressive rendering as each fetch completes

---

## 4. New Player Registration Flow

This flow demonstrates the cascade effect of creating a new player (auto-team creation).

```sql
┌────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ Client │      │  API    │      │ players  │      │  teams   │      │ Database │
│  Form  │      │  Route  │      │ service  │      │ service  │      │          │
└────┬───┘      └────┬────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │               │                │                 │                │
     │ POST /api/v1/players           │                 │                │
     │ {name: "Charlie"}              │                 │                │
     ├──────────────>│                │                 │                │
     │               │                │                 │                │
     │               │ Validate with PlayerCreateSchema│                │
     │               │────────┐       │                 │                │
     │               │        │       │                 │                │
     │               │<───────┘       │                 │                │
     │               │                │                 │                │
     │               │ createNewPlayer({name: "Charlie"})                │
     │               ├───────────────>│                 │                │
     │               │                │                 │                │
     │               │                │ Check uniqueness│                │
     │               │                │ getPlayerByName("Charlie")       │
     │               │                ├────────────────────────────────>│
     │               │                │                 │                │
     │               │                │                 │ SELECT * FROM players
     │               │                │                 │ WHERE name = 'Charlie'
     │               │                │                 │ ───────────────>
     │               │                │                 │                │
     │               │                │                 │ null (not found - OK)
     │               │                │<────────────────────────────────┤
     │               │                │                 │                │
     │               │                │ createPlayer({name, elo: 1000}) │
     │               │                ├────────────────────────────────>│
     │               │                │                 │                │
     │               │                │                 │ INSERT INTO players
     │               │                │                 │ (name, global_elo)
     │               │                │                 │ VALUES ('Charlie', 1000)
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │ {player_id: 3, name: "Charlie"} │
     │               │                │<────────────────────────────────┤
     │               │                │                 │                │
     │               │                │ getAllPlayers() (get existing)  │
     │               │                ├────────────────────────────────>│
     │               │                │                 │                │
     │               │                │                 │ SELECT * FROM players
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │ [{1: "Alice"}, {2: "Bob"}, {3: "Charlie"}]
     │               │                │<────────────────────────────────┤
     │               │                │                 │                │
     │               │                │ For each existing player (Alice, Bob):
     │               │                │   createTeamByPlayerIds(3, existing.id)
     │               │                ├────────────────>│                │
     │               │                │                 │                │
     │               │                │                 │ createTeamByPlayerIds(3, 1)
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │                 │ INSERT INTO teams
     │               │                │                 │ (player1_id, player2_id, elo)
     │               │                │                 │ VALUES (3, 1, 1310)
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │                 │ {team_id: 7}   │
     │               │                │                 │<───────────────┤
     │               │                │                 │                │
     │               │                │                 │ createTeamByPlayerIds(3, 2)
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │                 │ INSERT INTO teams
     │               │                │                 │ VALUES (3, 2, 1204)
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │                 │ {team_id: 8}   │
     │               │                │<────────────────┤<───────────────┤
     │               │                │                 │                │
     │               │ PlayerResponse (Charlie + auto-created teams)    │
     │               │<───────────────┤                 │                │
     │               │                │                 │                │
     │ 201 Created   │                │                 │                │
     │ {player: "Charlie"}            │                 │                │
     │<──────────────┤                │                 │                │
     │               │                │                 │                │
```

**Key Points**:
- **Uniqueness Check**: Prevents duplicate player names
- **Auto-Team Creation**: New player auto-paired with all existing players
- **Initial Team ELO**: Average of both players' current ELOs at creation time
- **Cascade Effect**: Adding 1 player creates N-1 teams (where N = total players)

**Example**: If 10 players exist, adding player 11 creates 10 new teams.

---

## 5. Match History Filtering Flow (Frontend)

This flow shows how frontend state management triggers API refetches.

```bash
┌──────────┐      ┌─────────────┐      ┌─────────┐      ┌──────────┐
│  User    │      │  Component  │      │   SWR   │      │   API    │
│ Interact │      │   State     │      │  Hook   │      │          │
└────┬─────┘      └──────┬──────┘      └────┬────┘      └────┬─────┘
     │                   │                  │                │
     │ Select date range │                  │                │
     │ (2025-01 to 2025-12)                 │                │
     ├──────────────────>│                  │                │
     │                   │                  │                │
     │                   │ Update state:    │                │
     │                   │ startDate = '2025-01-01'          │
     │                   │ endDate = '2025-12-31'            │
     │                   │────────┐         │                │
     │                   │        │         │                │
     │                   │<───────┘         │                │
     │                   │                  │                │
     │                   │ SWR key changes: │                │
     │                   │ '/api/v1/matches?start_date=2025-01-01&end_date=2025-12-31'
     │                   ├─────────────────>│                │
     │                   │                  │                │
     │                   │                  │ Trigger refetch│
     │                   │                  ├───────────────>│
     │                   │                  │                │
     │                   │                  │ GET /api/v1/matches?start_date=...
     │                   │                  │                │
     │                   │                  │ {matches filtered by date}
     │                   │                  │<───────────────┤
     │                   │                  │                │
     │                   │ Updated data     │                │
     │                   │<─────────────────┤                │
     │                   │                  │                │
     │                   │ Re-render with new matches        │
     │                   │────────┐         │                │
     │                   │        │         │                │
     │                   │<───────┘         │                │
     │                   │                  │                │
     │ Display filtered matches             │                │
     │<──────────────────┤                  │                │
     │                   │                  │                │
     │ Select player filter: "Alice"        │                │
     ├──────────────────>│                  │                │
     │                   │                  │                │
     │                   │ Update state:    │                │
     │                   │ selectedPlayer = 42               │
     │                   │────────┐         │                │
     │                   │        │         │                │
     │                   │<───────┘         │                │
     │                   │                  │                │
     │                   │ SWR key changes: │                │
     │                   │ '/api/v1/matches?start_date=...&player_id=42'
     │                   ├─────────────────>│                │
     │                   │                  │                │
     │                   │                  │ Trigger refetch│
     │                   │                  ├───────────────>│
     │                   │                  │                │
     │                   │                  │ Filtered matches for Alice
     │                   │                  │<───────────────┤
     │                   │                  │                │
     │                   │ Updated data     │                │
     │                   │<─────────────────┤                │
     │                   │                  │                │
     │ Display matches with Alice           │                │
     │<──────────────────┤                  │                │
     │                   │                  │                │
```

**SWR Automatic Features**:
- **Deduplication**: Multiple components requesting same data share single request
- **Revalidation**: Fresh data on tab focus (configurable)
- **Caching**: 30-second cache reduces API calls
- **Optimistic Updates**: UI updates before API confirms (for mutations)

---

## 6. Error Handling Flow

This flow demonstrates how errors propagate through layers and get mapped to HTTP responses.

```bash
┌────────┐      ┌─────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐
│ Client │      │  API    │      │ Service  │      │  Repo    │      │ Database │
│        │      │ Wrapper │      │          │      │ (retry)  │      │          │
└────┬───┘      └────┬────┘      └────┬─────┘      └────┬─────┘      └────┬─────┘
     │               │                │                 │                │
     │ POST /api/v1/matches (invalid data)             │                │
     ├──────────────>│                │                 │                │
     │               │                │                 │                │
     │               │ Zod validation fails            │                │
     │               │────────┐       │                 │                │
     │               │        │       │                 │                │
     │               │<───────┘       │                 │                │
     │               │                │                 │                │
     │               │ throw ZodError │                 │                │
     │               │<───────────────┤                 │                │
     │               │                │                 │                │
     │               │ Catch in handleApiRequest()     │                │
     │               │────────┐       │                 │                │
     │               │        │ if (error instanceof ZodError)           │
     │               │        │   return 422 with validation details     │
     │               │<───────┘       │                 │                │
     │               │                │                 │                │
     │ 422 Unprocessable Entity       │                 │                │
     │ {errors: [{field, message}]}   │                 │                │
     │<──────────────┤                │                 │                │
     │               │                │                 │                │
     │ POST /api/v1/players/{id} (not found)           │                │
     ├──────────────>│                │                 │                │
     │               │                │                 │                │
     │               │ getPlayer(999) │                 │                │
     │               ├───────────────>│                 │                │
     │               │                │                 │                │
     │               │                │ getPlayerById(999)               │
     │               │                ├────────────────>│                │
     │               │                │                 │                │
     │               │                │                 │ SELECT ... WHERE id = 999
     │               │                │                 ├───────────────>│
     │               │                │                 │                │
     │               │                │                 │ null (no rows) │
     │               │                │                 │<───────────────┤
     │               │                │                 │                │
     │               │                │                 │ throw PlayerNotFoundError(999)
     │               │                │<────────────────┤                │
     │               │                │                 │                │
     │               │ throw PlayerNotFoundError       │                │
     │               │<───────────────┤                 │                │
     │               │                │                 │                │
     │               │ Catch in handleApiRequest()     │                │
     │               │────────┐       │                 │                │
     │               │        │ if (error instanceof NotFoundError)      │
     │               │        │   return error.statusCode (404)          │
     │               │<───────┘       │                 │                │
     │               │                │                 │                │
     │ 404 Not Found │                │                 │                │
     │ {message: "Player with ID 999 not found"}       │                │
     │<──────────────┤                │                 │                │
     │               │                │                 │                │
     │ POST /api/v1/matches (DB connection fail)       │                │
     ├──────────────>│                │                 │                │
     │               │                │                 │                │
     │               │ createNewMatch(...)             │                │
     │               ├───────────────>│                 │                │
     │               │                │                 │                │
     │               │                │ createMatchByTeamIds(...)        │
     │               │                ├────────────────>│                │
     │               │                │                 │                │
     │               │                │                 │ Attempt 1: FAIL (timeout)
     │               │                │                 ├───────────────>│
     │               │                │                 │ ✗              │
     │               │                │                 │                │
     │               │                │                 │ Wait 500ms     │
     │               │                │                 │────────┐       │
     │               │                │                 │        │       │
     │               │                │                 │<───────┘       │
     │               │                │                 │                │
     │               │                │                 │ Attempt 2: FAIL│
     │               │                │                 ├───────────────>│
     │               │                │                 │ ✗              │
     │               │                │                 │                │
     │               │                │                 │ Wait 500ms     │
     │               │                │                 │────────┐       │
     │               │                │                 │        │       │
     │               │                │                 │<───────┘       │
     │               │                │                 │                │
     │               │                │                 │ Attempt 3: FAIL│
     │               │                │                 ├───────────────>│
     │               │                │                 │ ✗              │
     │               │                │                 │                │
     │               │                │                 │ throw MatchCreationError
     │               │                │<────────────────┤                │
     │               │                │                 │                │
     │               │ throw MatchCreationError        │                │
     │               │<───────────────┤                 │                │
     │               │                │                 │                │
     │               │ Catch in handleApiRequest()     │                │
     │               │────────┐       │                 │                │
     │               │        │ if (error instanceof OperationError)     │
     │               │        │   return 500           │                │
     │               │<───────┘       │                 │                │
     │               │                │                 │                │
     │ 500 Internal Server Error      │                 │                │
     │ {message: "Failed to create match"}             │                │
     │<──────────────┤                │                 │                │
     │               │                │                 │                │
```

**Error Mapping**:
- `ZodError` → 422 Unprocessable Entity
- `NotFoundError` → 404 Not Found
- `ConflictError` → 409 Conflict
- `ValidationError` → 422 Unprocessable Entity
- `OperationError` → 500 Internal Server Error
- Unknown errors → 500 Internal Server Error

**Retry Strategy**:
- Max 3 attempts
- 500ms delay between attempts
- Preserves error type for `instanceof` checks
- Only retries transient failures (timeouts, connection errors)

---

## Maintenance Notes

### When to Update This Document

- New API endpoints added
- Major flow changes (e.g., adding transactions)
- New error types or handling strategies
- Performance optimizations affecting flow

### Related Documentation

- `01-architecture-overview.md` - Component layers context
- `02-database-schema.md` - Database interaction details
- `04-api-reference.md` - Endpoint specifications
- `03-elo-calculation-system.md` - ELO algorithm details
