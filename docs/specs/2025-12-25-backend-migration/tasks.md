# Task Breakdown: Backend Migration (Python → TypeScript)

## Overview

Total Task Groups: 9
Total Tasks: ~45

## Task List

### Foundation Layer

#### Task Group 1: Project Setup & Dependencies

**Dependencies:** None

- [x] 1.0 Complete project setup
  - [x] 1.1 Install Zod dependency (`bun add zod`)
  - [x] 1.2 Create directory structure under `frontend/lib/` (db, errors, repositories, services, types/schemas)
  - [x] 1.3 Create directory structure under `frontend/app/api/v1/` (health, players, teams, matches)

**Acceptance Criteria:**

- All directories exist
- Zod available in package.json

---

#### Task Group 2: Database Utilities

**Dependencies:** Task Group 1

- [x] 2.0 Complete database utilities
  - [x] 2.1 Write 3 tests for retry utility (success, retry on failure, exhaust retries)
  - [x] 2.2 Create `lib/db/client.ts` — Supabase client singleton
  - [x] 2.3 Create `lib/db/retry.ts` — `withRetry()` HOF with 3 retries, 500ms delay
  - [x] 2.4 Ensure tests pass

**Acceptance Criteria:**

- Client singleton returns same instance
- Retry utility attempts 3 times with delay
- Tests pass

---

#### Task Group 3: Error Classes

**Dependencies:** Task Group 1

- [x] 3.0 Complete error handling layer
  - [x] 3.1 Write 4 tests for error classes (ApiError, NotFoundError, ConflictError, ValidationError)
  - [x] 3.2 Create `lib/errors/api-errors.ts` — Base ApiError class with statusCode and detail
  - [x] 3.3 Add NotFoundError, ConflictError, ValidationError extending ApiError
  - [x] 3.4 Add domain-specific errors: PlayerNotFoundError, TeamNotFoundError, MatchNotFoundError
  - [x] 3.5 Ensure tests pass

**Acceptance Criteria:**

- All errors have correct status codes
- Error messages are descriptive
- Tests pass

---

#### Task Group 4: Zod Schemas

**Dependencies:** Task Group 1

- [x] 4.0 Complete type definitions
  - [x] 4.1 Write 6 tests for schema validation (player create, team create with ID normalization, match create)
  - [x] 4.2 Create `lib/types/schemas/player.ts` — PlayerBase, PlayerCreate, PlayerUpdate, PlayerResponse
  - [x] 4.3 Create `lib/types/schemas/team.ts` — TeamCreate with `.refine().transform()` for ID normalization
  - [x] 4.4 Create `lib/types/schemas/match.ts` — MatchCreate, MatchResponse, MatchWithEloResponse
  - [x] 4.5 Create `lib/types/schemas/elo-history.ts` — EloHistoryCreate, EloHistoryResponse
  - [x] 4.6 Ensure tests pass

**Acceptance Criteria:**

- TeamCreate swaps player IDs to canonical order (lower ID first)
- TeamCreate rejects same player for both positions
- All response schemas include computed fields
- Tests pass

---

### Core Business Logic

#### Task Group 5: ELO Service

**Dependencies:** Task Group 4

- [x] 5.0 Complete ELO calculation service
  - [x] 5.1 Write 8 tests ported from Python `test_elo_service.py` (K-factors, win probability, pool correction)
  - [x] 5.2 Create `lib/services/elo.ts` — Define constants (K_TIER1=200, K_TIER2=100, K_TIER3=50)
  - [x] 5.3 Implement `calculateTeamElo()` and `calculateWinProbability()`
  - [x] 5.4 Implement `determineKFactor()` and `calculateEloChange()` using `Math.trunc()`
  - [x] 5.5 Implement `calculateEloChangesWithPoolCorrection()` — zero-sum correction
  - [x] 5.6 Implement `calculatePlayersEloChange()` and `calculateTeamEloChange()`
  - [x] 5.7 Implement `processMatchResult()` — main entry point
  - [x] 5.8 Ensure tests pass and verify against Python baseline values

**Acceptance Criteria:**

- All 8 ELO functions implemented
- K-factor tiers match Python exactly
- Pool correction ensures zero-sum across 4 players
- `Math.trunc()` used for int conversion
- Tests pass with identical results to Python

---

### Data Access Layer

#### Task Group 6: Repositories

**Dependencies:** Task Groups 2, 3, 4

- [ ] 6.0 Complete repository layer
  - [ ] 6.1 Write 6 integration tests for CRUD operations (create player, get player, update ELO, RPC call)
  - [ ] 6.2 Create `lib/repositories/players.ts` — createPlayer, getPlayer, updatePlayer, batchUpdateElo
  - [ ] 6.3 Create `lib/repositories/teams.ts` — createTeam, getTeam, deleteTeam, batchUpdateElo
  - [ ] 6.4 Create `lib/repositories/matches.ts` — createMatch, getMatch, getMatchesByPlayer, getMatchesByTeam
  - [ ] 6.5 Create `lib/repositories/player-elo-history.ts` — recordEloChange, getHistory
  - [ ] 6.6 Create `lib/repositories/team-elo-history.ts` — recordEloChange, getHistory
  - [ ] 6.7 Create `lib/repositories/stats.ts` — RPC calls for get_player_full_stats, get_team_full_stats
  - [ ] 6.8 Wrap all functions with `withRetry()`
  - [ ] 6.9 Ensure tests pass

**Acceptance Criteria:**

- All repositories use Supabase client correctly
- RPC functions called for complex queries
- Retry wrapper applied to all operations
- Tests pass against Supabase

---

### Service Layer

#### Task Group 7: Business Logic Services

**Dependencies:** Task Groups 5, 6

- [ ] 7.0 Complete service layer
  - [ ] 7.1 Write 5 integration tests for services (create match with ELO update, delete player validation)
  - [ ] 7.2 Create `lib/services/players.ts` — getPlayerWithStats, deletePlayer (with validation)
  - [ ] 7.3 Create `lib/services/teams.ts` — getTeamWithPlayers, deleteTeam (with validation)
  - [ ] 7.4 Create `lib/services/matches.ts` — createMatch (orchestrates ELO), getMatchHistory
  - [ ] 7.5 Ensure services throw custom errors for not-found and conflict cases
  - [ ] 7.6 Ensure tests pass

**Acceptance Criteria:**

- Match creation updates all 4 player ELOs + 2 team ELOs
- Match creation records ELO history entries
- Services throw appropriate custom errors
- Tests pass

---

### API Layer

#### Task Group 8: Route Handlers

**Dependencies:** Task Group 7

- [ ] 8.0 Complete API route handlers
  - [ ] 8.1 Write 8 integration tests for key endpoints (health, create player, create team, create match)
  - [ ] 8.2 Create `app/api/v1/health/route.ts` — GET returns { status: 'ok' }
  - [ ] 8.3 Create player routes: `players/route.ts` (GET, POST), `players/[playerId]/route.ts` (GET, PUT, DELETE)
  - [ ] 8.4 Create player sub-routes: `[playerId]/matches`, `[playerId]/elo-history`, `[playerId]/statistics`
  - [ ] 8.5 Create team routes: `teams/route.ts` (GET, POST), `teams/rankings/route.ts`, `teams/[teamId]/route.ts`
  - [ ] 8.6 Create team sub-routes: `[teamId]/matches`
  - [ ] 8.7 Create match routes: `matches/route.ts` (GET, POST), `matches/export/route.ts`, `matches/[matchId]/route.ts`
  - [ ] 8.8 Add error handling wrapper to all routes (catch ZodError → 422, ApiError → statusCode, else → 500)
  - [ ] 8.9 Ensure tests pass

**Acceptance Criteria:**

- All 18 endpoints functional
- Zod validation on POST/PUT request bodies
- Consistent error response format `{ detail: string }`
- Correct HTTP status codes (201, 404, 409, 422, 500)
- Tests pass

---

### Integration & Finalization

#### Task Group 9: Frontend Integration & Testing

**Dependencies:** Task Group 8

- [ ] 9.0 Complete integration
  - [ ] 9.1 Update `frontend/services/playerService.ts` — change base URL to relative `/api/v1`
  - [ ] 9.2 Update `frontend/services/teamService.ts` — change base URL to relative `/api/v1`
  - [ ] 9.3 Update `frontend/services/matchService.ts` — change base URL to relative `/api/v1`
  - [ ] 9.4 Remove or comment out `NEXT_PUBLIC_API_URL` usage
  - [ ] 9.5 Run full development server and manually test key flows
  - [ ] 9.6 Review all tests from groups 2-8 (~30 tests)
  - [ ] 9.7 Identify and write max 5 additional tests for critical gaps
  - [ ] 9.8 Run all feature tests and verify passing

**Acceptance Criteria:**

- Frontend works with new API routes
- No CORS errors (same-origin)
- All tests pass (~35 total)
- Key user flows work: create player, create team, record match, view rankings

---

## Execution Order

1. **Task Group 1** — Project Setup
2. **Task Groups 2, 3, 4** — Foundation (can run in parallel)
3. **Task Group 5** — ELO Service (critical path)
4. **Task Group 6** — Repositories
5. **Task Group 7** — Services
6. **Task Group 8** — Route Handlers
7. **Task Group 9** — Integration & Testing

## Testing Summary

| Task Group | Tests Written | Type        |
| ---------- | ------------- | ----------- |
| 2          | 3             | Unit        |
| 3          | 4             | Unit        |
| 4          | 6             | Unit        |
| 5          | 8             | Unit        |
| 6          | 6             | Integration |
| 7          | 5             | Integration |
| 8          | 8             | Integration |
| 9          | 5 (gap fill)  | Mixed       |
| **Total**  | **~45**       |             |

## Notes

- Task Groups 2, 3, 4 have no dependencies on each other and can be implemented in parallel
- ELO service (Group 5) is the most critical — must validate against Python baseline
- Use `bun test` for running tests
- All routes should use consistent error handling pattern
