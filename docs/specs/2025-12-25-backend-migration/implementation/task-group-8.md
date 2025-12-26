# Implementation: Task Group 8 - Route Handlers

**Date:** 2025-12-25
**Task Group:** 8 - API Route Handlers

## Summary

Implemented all 18 Next.js API route handlers for the Baby Foot ELO backend migration. The routes follow a Clean Architecture pattern with a shared error handling wrapper for consistent error transformation.

## Architecture Approach

Selected **Clean Architecture** approach with a shared `handleApiRequest` wrapper that:

- Catches `ZodError` and returns 422 with formatted validation message
- Catches `ApiError` and returns its status code with `toResponse()`
- Catches unknown errors and returns 500 with generic message

This reduced ~180 lines of duplicated error handling to a single 30-line utility.

## Files Created

### Error Handling Utility

- `frontend/lib/api/handle-request.ts` — Shared error handler wrapper

### Health Route

- `frontend/app/api/v1/health/route.ts` — GET returns `{ status: "ok" }`

### Player Routes

- `frontend/app/api/v1/players/route.ts` — GET (list), POST (create)
- `frontend/app/api/v1/players/rankings/route.ts` — GET (ranked by ELO with activity filter)
- `frontend/app/api/v1/players/[playerId]/route.ts` — GET, PUT, DELETE
- `frontend/app/api/v1/players/[playerId]/matches/route.ts` — GET (match history)
- `frontend/app/api/v1/players/[playerId]/elo-history/route.ts` — GET (ELO history)
- `frontend/app/api/v1/players/[playerId]/statistics/route.ts` — GET (detailed stats)

### Team Routes

- `frontend/app/api/v1/teams/route.ts` — GET (list), POST (create)
- `frontend/app/api/v1/teams/rankings/route.ts` — GET (ranked by ELO with activity filter)
- `frontend/app/api/v1/teams/[teamId]/route.ts` — GET, DELETE
- `frontend/app/api/v1/teams/[teamId]/matches/route.ts` — GET (match history)

### Match Routes

- `frontend/app/api/v1/matches/route.ts` — GET (list with filters), POST (create with ELO)
- `frontend/app/api/v1/matches/export/route.ts` — GET (export all as JSON)
- `frontend/app/api/v1/matches/[matchId]/route.ts` — GET, DELETE

### Tests

- `frontend/tests/integration/api/routes.test.ts` — 12 integration tests covering all endpoint types

## Key Details

### Error Handling Pattern

All routes use the `handleApiRequest` wrapper:

```typescript
export const GET = handleApiRequest(async (request: NextRequest) => {
  const data = await someService();
  return NextResponse.json(data);
});
```

### Rankings Filter

Both player and team rankings implement the Python backend's `days_since_last_match` filter:

- Default: 180 days
- Filters out players/teams with no matches
- Filters out inactive players/teams

### Status Codes

- `200` — Successful GET/PUT
- `201` — Successful POST (resource created)
- `204` — Successful DELETE (no content)
- `404` — Resource not found
- `409` — Conflict (duplicate resource)
- `422` — Validation error (Zod)
- `500` — Internal server error

### Next.js 15 Params

Routes use the new async params pattern:

```typescript
type RouteContext = { params: Promise<{ playerId: string }> };

export const GET = handleApiRequest(
  async (_request: NextRequest, context?: RouteContext) => {
    const { playerId } = await context!.params;
    // ...
  },
);
```

## Integration Points

### Existing Services

All routes delegate to existing TypeScript services:

- `lib/services/players.ts`
- `lib/services/teams.ts`
- `lib/services/matches.ts`

### Existing Error Classes

Routes catch and transform errors from:

- `lib/errors/api-errors.ts`

### Existing Schemas

Request bodies validated with:

- `lib/types/schemas/player.ts`
- `lib/types/schemas/team.ts`
- `lib/types/schemas/match.ts`

## Testing Notes

Integration tests created at `frontend/tests/integration/api/routes.test.ts`:

- Tests require Supabase environment variables
- Tests create and clean up their own test data
- Tests invoke route handlers directly with mocked NextRequest
- Tests verify HTTP status codes and response shapes

**Test coverage:**

- Health endpoint: 1 test
- Player endpoints: 6 tests (create, list, get, update, 404, validation)
- Team endpoints: 4 tests (create, list, get, validation)
- Match endpoints: 3 tests (create, list, get)
