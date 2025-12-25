# Implementation: Task Group 5 - ELO Service

**Date:** 2025-12-25
**Task Group:** 5.0 Complete ELO calculation service

## Summary

Successfully ported the Python ELO calculation service to TypeScript. The implementation maintains exact numerical equivalence with the Python version while leveraging TypeScript's type system for improved compile-time safety.

## Architecture Approach

**Selected:** Minimal Changes approach

**Rationale:**
- Single file (`lib/services/elo.ts`) mirrors Python's single module structure
- Direct port of all 8 functions from `backend/app/services/elo.py`
- No external dependencies beyond existing error classes
- Pure functions with no I/O, making the service easy to test

## Files Modified

None - this was a new implementation.

## Files Created

- `frontend/lib/services/elo.ts` — Main ELO calculation service (311 lines)
- `frontend/tests/unit/services/elo.test.ts` — Unit tests (281 lines)

## Key Details

### K-Factor Configuration

| ELO Range | K-Factor | Purpose |
|-----------|----------|---------|
| < 1200 | 200 | Fast progression for new players |
| 1200-1799 | 100 | Moderate for intermediate players |
| >= 1800 | 50 | Stable for established players |

### Functions Implemented

1. `calculateTeamElo(member1Elo, member2Elo)` — Team ELO as average of players
2. `calculateWinProbability(competitorAElo, competitorBElo)` — Standard ELO formula
3. `determineKFactor(competitorElo)` — K-factor based on tier
4. `calculateEloChange(competitorElo, winProbability, matchResult)` — Individual change
5. `calculateEloChangesWithPoolCorrection(competitorsData)` — Zero-sum correction
6. `calculatePlayersEloChange(winningTeam, losingTeam)` — All 4 players
7. `calculateTeamEloChange(winningTeam, losingTeam)` — Both teams
8. `processMatchResult(winningTeam, losingTeam)` — Main entry point

### Critical Implementation Decisions

1. **Integer Truncation:** Used `Math.trunc()` to match Python's `int()` behavior (truncates toward zero)

2. **Field Naming:** Used `difference` instead of `change` to match existing `EloChangeSchema` in `lib/types/schemas/match.ts`

3. **Type Safety:** TypeScript union type `0 | 1` for match results provides compile-time safety (better than Python's runtime validation)

4. **Error Handling:** Uses `ValidationError` from `lib/errors/api-errors.ts` for consistency with existing error hierarchy

### Pool Correction Algorithm

The pool correction ensures zero-sum ELO changes:

```text
correction_factor = -sum(initial_changes) / sum(k_factors)
corrected_change = initial_change + trunc(k_factor * correction_factor)
```

Due to integer truncation, the total may be off by ±1-2 points, which is acceptable and matches Python behavior.

## Integration Points

- **Input Types:** Uses `TeamWithPlayers` interface for team data
- **Output Types:** Returns `EloChangesMap` (Record of `EloChangeResult`)
- **Error Types:** Throws `ValidationError` for invalid inputs
- **Schema Compatibility:** `EloChangeResult` matches `EloChangeSchema` field names

## Testing Notes

25 unit tests cover:
- Basic calculations (team ELO, win probability, K-factors)
- ELO change calculations (wins, losses, different tiers)
- Pool correction (zero-sum property, mixed K-factors)
- Full match processing (equal ELO, upsets, expected wins)
- Edge cases (negative ELO, invalid probability)
- Validation errors

All tests pass with 100% coverage of business logic.
