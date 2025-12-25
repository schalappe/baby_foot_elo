# Specification: Backend Migration (Python → TypeScript)

## Goal

Migrate all 18 FastAPI endpoints from Python/Heroku to TypeScript/Next.js Route Handlers on Vercel, maintaining identical API contracts and ELO calculation behavior.

## User Stories

- As a frontend developer, I want API routes running on the same Vercel deployment so that I can eliminate cross-origin requests and simplify infrastructure.
- As a maintainer, I want a unified TypeScript codebase so that I don't need to context-switch between Python and TypeScript.

## Specific Requirements

**ELO Calculation Service:**

- Port all 8 ELO functions as pure TypeScript functions with no DB dependencies
- Preserve K-factor tiers exactly: K=200 (<1200), K=100 (1200-1800), K=50 (>=1800)
- Pool correction formula: `correction = -Σ(changes) / Σ(K-factors)`
- Use `Math.trunc()` for int conversion (not `Math.round()`)
- Unit tests comparing TypeScript output against Python baseline

**Type Definitions (Zod Schemas):**

- Convert Pydantic models to Zod schemas: Base → Create/Update/Response pattern
- TeamCreateSchema must validate `player1_id !== player2_id` and normalize order
- PlayerResponseSchema includes computed fields: `matches_played`, `wins`, `losses`, `win_rate`
- MatchWithEloResponse includes `elo_changes` map for all 4 players

**Database Layer:**

- Supabase client singleton using existing `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `withRetry()` higher-order function: 3 retries, 500ms delay
- No real transactions (Supabase limitation) - sequential operations with logging

**Repository Layer:**

- 6 repository files: players, teams, matches, player-elo-history, team-elo-history, stats
- All functions wrapped with retry logic
- Use existing Supabase RPC functions for complex queries (rankings, stats)

**Service Layer:**

- `matches.ts` orchestrates: validate teams → create match → calculate ELO → batch update all
- `players.ts` and `teams.ts` handle business logic validation
- Services throw custom errors; routes catch and return appropriate HTTP status

**API Route Handlers:**

- 18 endpoints across 4 domains: health, players, teams, matches
- Zod validation on all request bodies
- Consistent error response format: `{ detail: string }`
- Return 201 for created resources, 404 for not found, 409 for conflicts

**Error Handling:**

- Custom error hierarchy: ApiError → NotFoundError, ConflictError, ValidationError
- ZodError caught and returned as 422 with error details
- Unexpected errors logged and returned as 500

**Testing:**

- Unit tests for ELO service (compare against Python test cases)
- Integration tests for API routes against Supabase

## Visual Design

No visual assets provided.

## Existing Code to Leverage

**Python ELO Service — `backend/app/services/elo.py`**

- What it does: All ELO calculation logic (351 lines)
- How to reuse: Direct port to TypeScript, preserve all formulas
- Key methods: `processMatchResult()`, `calculateEloChangesWithPoolCorrection()`

**Python Repositories — `backend/app/db/repositories/`**

- What it does: CRUD operations for all entities
- How to reuse: Port to TypeScript with Supabase JS client methods
- Key methods: `createPlayerByName()`, `batchUpdatePlayersElo()`, RPC calls

**Python Pydantic Models — `backend/app/models/`**

- What it does: Request/response validation
- How to reuse: Convert to Zod schemas with same validation rules
- Key methods: `TeamCreate.validate_players()` becomes `.refine().transform()`

**Supabase RPC Functions — `supabase/*.sql`**

- What it does: Complex queries (rankings, stats, match history)
- How to reuse: Call unchanged via `supabase.rpc('function_name', params)`
- Key methods: `get_all_players_with_stats`, `get_team_match_history`

**Frontend Types — `frontend/types/`**

- What it does: TypeScript interfaces mirroring Pydantic models
- How to reuse: Reference for field names, replace with Zod-inferred types
- Key files: `player.ts`, `team.ts`, `match.ts`

## Architecture Approach

**Component Design:**

```text
Route Handlers (app/api/v1/*)
    ↓ Parse, validate, call service
Services (lib/services/*)
    ↓ Business logic, orchestration
Repositories (lib/repositories/*)
    ↓ Supabase operations, retry wrapper
Database Layer (lib/db/*)
    ↓ Client singleton, retry utility
```

**Data Flow (Create Match):**

1. Route handler validates with `MatchCreateSchema.parse(body)`
2. `matchService.createMatch()` fetches both teams
3. `eloService.processMatchResult()` calculates changes for 4 players + 2 teams
4. Repositories batch-update players, teams, and record history
5. Return `MatchWithEloResponse` with nested team data and ELO changes

**Integration Points:**

- Supabase: Reuse existing JS client from frontend
- Frontend services: Update to use relative URLs (`/api/v1/...`)
- Environment: Use existing `NEXT_PUBLIC_SUPABASE_*` variables

**Target Directory Structure:**

```text
frontend/
├── app/api/v1/
│   ├── health/route.ts
│   ├── players/
│   │   ├── route.ts                 # GET, POST
│   │   └── [playerId]/
│   │       ├── route.ts             # GET, PUT, DELETE
│   │       ├── matches/route.ts
│   │       ├── elo-history/route.ts
│   │       └── statistics/route.ts
│   ├── teams/
│   │   ├── route.ts                 # GET, POST
│   │   ├── rankings/route.ts
│   │   └── [teamId]/
│   │       ├── route.ts             # GET, DELETE
│   │       └── matches/route.ts
│   └── matches/
│       ├── route.ts                 # GET, POST
│       ├── export/route.ts
│       └── [matchId]/route.ts       # GET, DELETE
├── lib/
│   ├── db/
│   │   ├── client.ts
│   │   └── retry.ts
│   ├── errors/
│   │   └── api-errors.ts
│   ├── repositories/
│   │   ├── players.ts
│   │   ├── teams.ts
│   │   ├── matches.ts
│   │   ├── player-elo-history.ts
│   │   ├── team-elo-history.ts
│   │   └── stats.ts
│   ├── services/
│   │   ├── elo.ts
│   │   ├── players.ts
│   │   ├── teams.ts
│   │   └── matches.ts
│   └── types/
│       └── schemas/
│           ├── player.ts
│           ├── team.ts
│           ├── match.ts
│           └── elo-history.ts
└── tests/
    ├── unit/services/elo.test.ts
    └── integration/api/
```

## Out of Scope

- New features beyond existing API functionality
- Database schema changes
- Authentication/authorization implementation
- Row Level Security (RLS) configuration
- Frontend dependency upgrades
- End-to-end tests
- Rollback plan
- Backward compatibility period with Heroku
- Rate limiting middleware (defer to future)
- Cascade delete for players/teams (marked TODO in Python)
