# Implementation: Foundation Layer (Task Groups 1-4)

**Date:** 2025-12-25
**Task Groups:** 1 (Project Setup), 2 (Database Utilities), 3 (Error Classes), 4 (Zod Schemas)

## Summary

Implemented the foundation layer for the Python→TypeScript backend migration. This includes project setup with Vitest, database utilities (Supabase client singleton and retry HOF), error hierarchy matching Python exceptions, and Zod schemas porting Pydantic models.

## Architecture Approach

Selected **Clean Architecture** with consolidated files:

- All errors in single `api-errors.ts` with domain errors as additional exports
- Schemas in `lib/types/schemas/` mirroring the existing `types/` folder structure
- Server-only Supabase client with lazy initialization

## Files Created

### Database Utilities

- `lib/db/client.ts` — Supabase singleton with lazy initialization and env validation
- `lib/db/retry.ts` — Generic `withRetry()` HOF with configurable retries (default 3) and delay (default 500ms)

### Error Classes

- `lib/errors/api-errors.ts` — Full error hierarchy:
  - Base: `ApiError` (with `statusCode`, `detail`, `toResponse()`)
  - HTTP types: `NotFoundError` (404), `ConflictError` (409), `ValidationError` (422), `OperationError` (500)
  - Player: `PlayerNotFoundError`, `PlayerAlreadyExistsError`, `InvalidPlayerDataError`, `PlayerOperationError`
  - Team: `TeamNotFoundError`, `TeamAlreadyExistsError`, `InvalidTeamDataError`, `TeamOperationError`
  - Match: `MatchNotFoundError`, `InvalidMatchTeamsError` (400), `MatchCreationError`, `MatchDeletionError`, `MatchUpdateError`

### Zod Schemas

- `lib/types/schemas/player.ts` — `PlayerBaseSchema`, `PlayerCreateSchema`, `PlayerUpdateSchema`, `PlayerResponseSchema`
- `lib/types/schemas/team.ts` — `TeamCreateSchema` with `.refine().transform()` for ID normalization, `TeamUpdateSchema`, `TeamResponseSchema`
- `lib/types/schemas/match.ts` — `MatchBaseSchema`, `MatchCreateSchema`, `MatchResponseSchema`, `EloChangeSchema`, `MatchWithEloResponseSchema`
- `lib/types/schemas/elo-history.ts` — `EloHistoryBaseSchema`, `EloHistoryCreateSchema`, `EloHistoryResponseSchema`
- `lib/types/schemas/index.ts` — Barrel export for all schemas

### Configuration

- `vitest.config.ts` — Vitest configuration with path aliases and node environment

### Tests

- `tests/unit/db/retry.test.ts` — 3 tests (success, retry success, exhaust retries)
- `tests/unit/errors/api-errors.test.ts` — 10 tests (base classes + domain errors)
- `tests/unit/types/schemas/player.test.ts` — 5 tests (create, response validation)
- `tests/unit/types/schemas/team.test.ts` — 5 tests (ID normalization, same-player rejection)
- `tests/unit/types/schemas/match.test.ts` — 4 tests (create, elo_changes validation)

## Files Modified

- `package.json` — Added `vitest` devDependency, added `test` and `test:run` scripts

## Key Details

### Team ID Normalization

The `TeamCreateSchema` enforces canonical order where `player1_id < player2_id`:

```typescript
export const TeamCreateSchema = TeamBaseSchema.refine(
  (data) => data.player1_id !== data.player2_id,
  { message: "player1_id and player2_id cannot be the same" },
).transform((data) => {
  if (data.player1_id > data.player2_id) {
    return {
      ...data,
      player1_id: data.player2_id,
      player2_id: data.player1_id,
    };
  }
  return data;
});
```

### Error Hierarchy Pattern

All errors extend `ApiError` which provides:

- `statusCode` - HTTP status code (404, 409, 422, 500)
- `detail` - Human-readable error message
- `toResponse()` - Returns `{ detail: string }` for consistent API responses

### Retry Logic

The `withRetry()` function matches Python backend behavior:

- Default 3 retries with 500ms delay
- Logs warnings on each failure
- Throws last error after exhausting retries

## Integration Points

- **Supabase Client**: Uses existing `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` environment variables
- **Zod Schemas**: Infer TypeScript types that can eventually replace existing interfaces in `frontend/types/`
- **Error Classes**: Ready for use in route handlers with consistent HTTP status codes

## Testing Notes

- All 27 tests pass
- Tests use Vitest with globals enabled
- Schema tests verify both valid and invalid inputs
- Team tests specifically verify ID normalization behavior
