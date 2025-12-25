# Implementation: Task Groups 6-7 (Repositories & Services)

**Date:** 2025-12-25
**Task Groups:** 6 (Repositories) and 7 (Business Logic Services)

## Summary

Implemented the complete data access layer (6 repositories) and business logic layer (3 services) for the Python to TypeScript backend migration. All repositories use the throw-first error pattern and are wrapped with `withRetry()` for resilience. The services orchestrate repository calls and implement validation rules matching the Python backend.

## Architecture Approach

**Chosen Approach: Minimal changes with throw-first repositories**

Key decisions:
1. **Throw-first pattern**: Repositories throw domain errors (e.g., `PlayerNotFoundError`) instead of returning null. This differs from Python but creates cleaner TypeScript service code.
2. **Separate lookup functions**: `getPlayerById()` and `getPlayerByName()` as distinct functions (not combined with optional params like Python).
3. **withRetry wrapper**: All repository functions wrapped at export level for automatic retry on transient failures.
4. **Stateless functions**: No classes - just exported async functions matching the Python pattern.

## Files Created

### Repositories (frontend/lib/db/repositories/)

- `players.ts` — Player CRUD: createPlayerByName, getPlayerById, getPlayerByName, getAllPlayers, updatePlayer, batchUpdatePlayersElo, deletePlayerById
- `teams.ts` — Team CRUD with player ordering: createTeamByPlayerIds, getTeamById, getTeamByPlayerIds, getAllTeams, getTeamsByPlayerId, updateTeam, batchUpdateTeamsElo, deleteTeamById
- `matches.ts` — Match operations: createMatchByTeamIds, getMatchById, getAllMatches, getMatchesByTeamId, getMatchesByPlayerId, deleteMatchById
- `player-elo-history.ts` — Player ELO history: recordPlayerEloUpdate, batchRecordPlayerEloUpdates, getPlayerEloHistory, getPlayersEloHistoryByMatchId
- `team-elo-history.ts` — Team ELO history: recordTeamEloUpdate, batchRecordTeamEloUpdates, getTeamEloHistory, getTeamsEloHistoryByMatchId
- `stats.ts` — RPC wrappers: getPlayerStats, getTeamStats

### Services (frontend/lib/services/)

- `players.ts` — Player business logic: getPlayer, getAllPlayersWithStats, createNewPlayer (with auto-team creation), updateExistingPlayer, deletePlayer, getPlayerEloHistory
- `teams.ts` — Team business logic: getTeam, getAllTeamsWithStats, getTeamsByPlayer, createNewTeam (with player validation), updateExistingTeam, deleteTeam
- `matches.ts` — Match orchestration: getMatch, getMatches, getMatchesByPlayer, createNewMatch (orchestrates ELO updates), getMatchWithPlayerElo, getMatchWithTeamElo, deleteMatch

### Tests (frontend/lib/__tests__/)

- `repositories/players.test.ts` — 6 integration tests for player CRUD
- `services/matches.test.ts` — 5 integration tests for match creation with ELO updates

## Key Details

### Repository Layer Pattern

Each repository follows this pattern:

```typescript
// Internal implementation with actual logic
async function createPlayerByNameImpl(name: string, globalElo: number): Promise<number> {
  const client = getSupabaseClient();
  const { data, error } = await client.from("players").insert(...).select().single();
  if (error) throw new PlayerOperationError(...);
  if (!data) throw new PlayerNotFoundError(...);
  return data.player_id;
}

// Export wrapped version with retry logic
export const createPlayerByName = withRetry(createPlayerByNameImpl);
```

### Match Creation Orchestration

The `createNewMatch` service orchestrates 8 sequential operations:

1. Validate winner !== loser
2. Fetch both teams with player data
3. Create match record
4. Calculate ELO changes via `processMatchResult()`
5. Batch update player ELOs
6. Record player ELO history
7. Batch update team ELOs
8. Record team ELO history

### Error Handling

- Repositories throw specific domain errors (`PlayerNotFoundError`, `TeamNotFoundError`, etc.)
- Services catch and may re-throw with additional context
- All errors extend `ApiError` with statusCode and detail

## Integration Points

### Existing Code Leveraged

- `lib/db/client.ts` — Supabase singleton
- `lib/db/retry.ts` — withRetry() HOF
- `lib/errors/api-errors.ts` — Error hierarchy
- `lib/services/elo.ts` — ELO calculation (processMatchResult)
- `lib/types/schemas/*.ts` — Zod schemas for type inference

### Supabase RPC Functions Used

- `get_all_players_with_stats` — Player rankings with computed stats
- `get_all_teams_with_stats` — Team rankings with computed stats
- `get_player_full_stats` — Single player stats
- `get_team_full_stats` — Single team stats
- `get_team_match_history` — Team match history with filtering
- `get_player_matches_json` — Player match history with filtering
- `get_all_matches_with_details` — All matches with team data

## Testing Notes

- Tests use Vitest (project's existing test framework)
- Integration tests run against real Supabase instance
- Tests create/delete their own fixtures to avoid pollution
- Player repository tests: 6 test cases
- Match service tests: 5 test cases (including ELO verification)

## Verification

Run tests with:

```bash
cd frontend && bun test
```

Expected: All tests pass against Supabase.
