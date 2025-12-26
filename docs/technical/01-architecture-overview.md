# Architecture Overview

## Document Information

- **Document Type**: Technical Architecture
- **Target Audience**: Developers, Technical Leads, Architects
- **Last Updated**: 2025-12-26
- **Maintainer**: Development Team

## System Overview

Baby Foot ELO is a full-stack web application built with Next.js 16 that manages foosball (baby-foot) championships using a hybrid ELO rating system. The application tracks individual players and teams, calculates dynamic ELO ratings after each match, and provides real-time rankings and statistics.

### Key Features

- **Hybrid ELO System**: Players have individual ELO ratings that change based on both personal and team performance
- **Zero-Sum Pool Correction**: Ensures fairness by preventing ELO inflation/deflation across matches
- **Real-Time Rankings**: Live leaderboards for both players and teams
- **Match History**: Complete audit trail with ELO change visualization
- **Team Management**: Automatic team generation when new players join
- **Statistics Dashboard**: Detailed stats including win rates, streaks, and ELO progression

## High-Level Architecture

```bash
┌─────────────────────────────────────────────────────────────┐
│                   Browser / Client Layer                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Next.js App Router Pages + React Components        │   │
│  │ - Rankings Display (Players & Teams)               │   │
│  │ - Match History with Filters                       │   │
│  │ - Player/Team Detail Pages                         │   │
│  │ - Match Recording Interface                        │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS / JSON
                       │ (axios + SWR for caching)
┌──────────────────────▼──────────────────────────────────────┐
│              API Layer (Next.js Route Handlers)             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ /api/v1/matches    - Match CRUD + Export           │   │
│  │ /api/v1/players    - Player CRUD + Stats           │   │
│  │ /api/v1/teams      - Team CRUD + Stats             │   │
│  │ /api/v1/health     - Health Check                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Error Handling: handleApiRequest() wrapper                │
│  Validation: Zod schemas                                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│           Business Logic Layer (Services)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ elo.ts         - ELO calculation with pool          │   │
│  │                  correction algorithm               │   │
│  │ matches.ts     - Match orchestration (9-step flow)  │   │
│  │ players.ts     - Player lifecycle management        │   │
│  │ teams.ts       - Team lifecycle management          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Pure business logic - no direct database access            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│       Data Access Layer (Repositories)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ matches.ts     - Match queries with RPC calls       │   │
│  │ players.ts     - Player CRUD with retry logic       │   │
│  │ teams.ts       - Team CRUD with retry logic         │   │
│  │ stats.ts       - Aggregated statistics via RPC      │   │
│  │ *-elo-history  - ELO change tracking                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  All calls wrapped with withRetry() for resilience          │
└──────────────────────┬──────────────────────────────────────┘
                       │ Supabase Client
┌──────────────────────▼──────────────────────────────────────┐
│         PostgreSQL Database (Supabase)                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Tables:                                             │   │
│  │ - players (player_id, name, global_elo)            │   │
│  │ - teams (team_id, player1_id, player2_id, elo)     │   │
│  │ - matches (winner_team_id, loser_team_id, etc.)    │   │
│  │ - player_history (ELO change tracking)             │   │
│  │ - team_history (ELO change tracking)               │   │
│  │                                                     │   │
│  │ RPC Functions (SQL):                               │   │
│  │ - get_all_players_with_stats_optimized             │   │
│  │ - get_all_teams_with_stats                         │   │
│  │ - get_player_matches_json                          │   │
│  │ - get_team_match_history                           │   │
│  │ - get_all_matches_with_details                     │   │
│  │ - get_player_full_stats                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Architectural Layers

### 1. Presentation Layer (Frontend)

**Location**: `app/`, `components/`

**Responsibilities**:
- Render UI components and pages
- Handle user interactions
- Manage client-side state
- Data fetching and caching (SWR)
- Form validation and submission

**Technology Stack**:
- Next.js 16 (App Router)
- React 19
- TanStack Table (data tables)
- SWR (data fetching/caching)
- ShadCN UI (component library)
- Tailwind CSS (styling)

**Key Components**:
- `app/page.tsx` - Rankings homepage
- `app/matches/page.tsx` - Match history with filters
- `app/players/[id]/page.tsx` - Player detail view
- `components/matches/NewMatchPage.tsx` - Match creation form

### 2. API Layer (Route Handlers)

**Location**: `app/api/v1/`

**Responsibilities**:
- Receive and validate HTTP requests
- Route to appropriate service functions
- Error handling and HTTP status code mapping
- Response formatting

**Technology Stack**:
- Next.js Route Handlers (Server Components)
- Zod (runtime validation)

**Key Patterns**:
- `handleApiRequest()` wrapper for error handling
- Zod schema validation on all inputs
- Consistent response format
- HTTP status code mapping from domain errors

**Example Request Flow**:
```text
POST /api/v1/matches
  ↓
Route handler validates with MatchCreateSchema
  ↓
Calls createNewMatch() service
  ↓
Returns 201 with MatchWithEloResponse
```

### 3. Business Logic Layer (Services)

**Location**: `lib/services/`

**Responsibilities**:
- Implement core business rules
- Orchestrate complex operations
- Calculate ELO ratings
- Coordinate repository calls
- Enforce invariants

**Technology Stack**:
- TypeScript
- Pure functions (mostly)
- Domain error types

**Key Services**:

#### `elo.ts` - ELO Calculation Engine
- `processMatchResult()` - Main entry point for ELO calculation
- `calculateTeamElo()` - Average of two player ELOs
- `calculateWinProbability()` - Standard ELO formula
- `determineKFactor()` - K-factor tiers (200/100/50)
- `calculateEloChangesWithPoolCorrection()` - Zero-sum enforcement

#### `matches.ts` - Match Orchestration
- `createNewMatch()` - Atomic 9-step match creation
- `getMatches()` - Filter and paginate matches
- `getMatchesByPlayer()` - Player's match history
- `deleteMatch()` - Soft deletion

#### `players.ts` - Player Lifecycle
- `createNewPlayer()` - Create player + auto-generate teams
- `getPlayer()` - Fetch with stats
- `getAllPlayersWithStats()` - Rankings
- `updateExistingPlayer()` - Update with validation

#### `teams.ts` - Team Lifecycle
- `createNewTeam()` - Validate and create team
- `getTeam()` - Fetch with full stats
- `getAllTeamsWithStats()` - Rankings

### 4. Data Access Layer (Repositories)

**Location**: `lib/db/repositories/`

**Responsibilities**:
- All database interactions
- Call Supabase RPC functions
- Retry logic for resilience
- Type-safe query building
- Throw domain errors (not null returns)

**Technology Stack**:
- Supabase Client
- TypeScript

**Key Patterns**:
- `withRetry()` wrapper (3 attempts, 500ms delay)
- RPC functions for complex queries with CTEs
- Type-safe row interfaces (`PlayerDbRow`, etc.)
- Batch operations for performance

**Repository Files**:
- `matches.ts` - Match queries (uses RPC heavily)
- `players.ts` - Player CRUD
- `teams.ts` - Team CRUD
- `stats.ts` - Aggregated statistics via RPC
- `player-elo-history.ts` - Player ELO tracking
- `team-elo-history.ts` - Team ELO tracking

### 5. Data Layer (PostgreSQL)

**Location**: Supabase PostgreSQL + SQL functions in `supabase/`

**Responsibilities**:
- Persistent data storage
- Complex aggregations via RPC
- Data integrity (foreign keys, constraints)
- Performance optimization (indexes)

**Technology Stack**:
- PostgreSQL 15+
- Supabase platform

**Key Tables** (see `02-database-schema.md` for details):
- `players` - Individual player records
- `teams` - Team pairs
- `matches` - Match records
- `player_history` - Player ELO tracking
- `team_history` - Team ELO tracking

**RPC Functions** (see `supabase/` directory):
- Optimized SQL with CTEs for pre-aggregation
- Return nested JSON structures
- 41x faster than previous ORM approach

## Design Patterns

### Service Layer Pattern

**Purpose**: Separate business logic from HTTP and data access concerns

**Structure**:
```text
API Route → Service → Repository → Database
```

**Benefits**:
- Testable business logic
- Reusable across endpoints
- Single source of truth for rules
- No database logic in HTTP handlers

### Repository Pattern

**Purpose**: Abstract data access from business logic

**Structure**:
```text
Service calls Repository → Repository calls Supabase → Returns typed data
```

**Benefits**:
- Consistent data access interface
- Easy to mock for testing
- Retry logic in one place
- Type-safe queries

### Mapper Pattern

**Purpose**: Convert between layer representations

**Location**: `lib/mappers/entity-mappers.ts`

**Functions**:
- `mapToPlayerResponse()` - DB row → API response
- `mapToTeamResponse()` - DB row → API response
- `mapToMatchResponse()` - DB row → API response

**Benefits**:
- Loose coupling between layers
- Centralized transformation logic
- Type safety at boundaries

### Error Hierarchy Pattern

**Purpose**: Domain-specific errors with HTTP mapping

**Location**: `lib/errors/api-errors.ts`

**Structure**:
```text
ApiError (base)
├─ NotFoundError (404)
├─ ConflictError (409)
├─ ValidationError (422)
└─ OperationError (500)
```

**Benefits**:
- Consistent error handling
- Type-safe error checks
- Automatic HTTP status mapping
- Meaningful error messages

## Cross-Cutting Concerns

### Error Handling

**Strategy**: Throw domain-specific errors, catch at API boundary

**Implementation**:
```typescript
// Service throws domain error
if (!player) throw new PlayerNotFoundError(id);

// API wrapper catches and maps
export function handleApiRequest(handler) {
  return async (request, context) => {
    try {
      return await handler(request, context);
    } catch (error) {
      if (error instanceof ApiError) {
        return NextResponse.json(
          { message: error.message },
          { status: error.statusCode }
        );
      }
      return NextResponse.json(
        { message: 'Internal server error' },
        { status: 500 }
      );
    }
  };
}
```

### Retry Logic

**Strategy**: Wrap all database calls with exponential backoff

**Implementation**: `lib/db/retry.ts`

```typescript
export function withRetry<T>(fn: (...args: any[]) => Promise<T>) {
  return async (...args: any[]): Promise<T> => {
    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
      try {
        return await fn(...args);
      } catch (error) {
        if (attempt === MAX_RETRIES) throw error;
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
      }
    }
    throw new Error('Max retries exceeded');
  };
}
```

**Configuration**:
- `MAX_RETRIES = 3`
- `RETRY_DELAY_MS = 500`

### Type Safety

**Strategy**: Full TypeScript coverage with runtime validation

**Implementation**:
- TypeScript strict mode enabled
- Zod schemas for API input validation
- Interface definitions for all data structures
- Type guards where needed

**Type Organization**:
- `types/` - Domain types (Player, Team, Match)
- `lib/types/schemas/` - Zod schemas for validation
- `lib/db/types/` - Database row types

### Caching (Frontend)

**Strategy**: SWR for data fetching with automatic revalidation

**Implementation**:
```typescript
const { data, error, isLoading } = useSWR(
  '/api/v1/players/rankings',
  getPlayers,
  {
    revalidateOnFocus: false,
    refreshInterval: 30000, // 30 seconds
  }
);
```

**Cache Keys**: URL-based with query params
**TTL**: 30 seconds for rankings, on-demand for details

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 19
- **Styling**: Tailwind CSS
- **Components**: ShadCN UI
- **Data Fetching**: SWR
- **Tables**: TanStack Table
- **HTTP Client**: axios
- **Validation**: Zod

### Backend
- **Runtime**: Node.js (via Next.js)
- **Language**: TypeScript
- **API**: Next.js Route Handlers
- **Database**: PostgreSQL (Supabase)
- **ORM**: None (direct Supabase client + RPC)

### Development Tools
- **Package Manager**: bun
- **Linting**: ESLint
- **Formatting**: Prettier
- **Type Checking**: TypeScript compiler
- **Testing**: Vitest

## Performance Considerations

### Database Optimizations

1. **RPC Functions with CTEs**: Pre-aggregate stats in database (41x faster than previous approach)
2. **Indexes**: All foreign keys and commonly queried fields indexed
3. **Batch Operations**: `batchUpdatePlayersElo()` uses single query for multiple updates
4. **Pagination**: Match history supports limit/offset

### Frontend Optimizations

1. **SWR Caching**: 30-second cache for rankings, reduces API calls
2. **Skeleton Loaders**: Perceived performance during data load
3. **Lazy Loading**: Player/team details fetched on-demand
4. **Memoization**: React components use `useMemo` for expensive computations

### API Optimizations

1. **Retry Logic**: Automatic retry for transient failures
2. **Error Short-Circuiting**: Fail fast on validation errors
3. **Parallel Fetches**: `getTeam()` calls run in parallel during match creation
4. **Minimal Response Payloads**: Only return necessary fields

## Security Considerations

### Input Validation
- All API inputs validated with Zod schemas
- SQL injection prevented by Supabase client parameterization
- Type checking on all data

### Error Messages
- No stack traces exposed in production
- Generic error messages for internal failures
- Specific errors only for user-actionable issues

### Environment Variables
- Supabase credentials in environment variables
- No secrets in codebase
- `.env.local` for local development

## Deployment Architecture

### Hosting
- **Frontend + API**: Vercel (Next.js deployment)
- **Database**: Supabase Cloud

### Environment
- **Production**: Vercel production deployment
- **Development**: Local Next.js dev server + Supabase Cloud

### Configuration
- `NEXT_PUBLIC_SUPABASE_URL` - Supabase project URL
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` - Supabase publishable key (preferred)
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anon key (fallback for local)

## Scalability Considerations

### Current Limits
- Supabase free tier: 500MB database, 2GB egress/month
- No authentication (public access)
- Single database instance

### Future Scaling Options
1. **Database**: Upgrade Supabase tier or migrate to dedicated PostgreSQL
2. **Caching**: Add Redis for rankings cache
3. **CDN**: Cloudflare for static assets
4. **Authentication**: Add Supabase Auth for user accounts
5. **Rate Limiting**: Add API rate limiting

## Maintenance Notes

### When to Update This Document
- Major architectural changes (e.g., adding authentication layer)
- New service layer components
- Database schema changes affecting architecture
- Technology stack upgrades (Next.js major versions)

### Related Documentation
- `02-database-schema.md` - Complete database structure
- `03-elo-calculation-system.md` - ELO algorithm details
- `04-api-reference.md` - API endpoint documentation
- `05-sequence-diagrams.md` - Key flow diagrams
