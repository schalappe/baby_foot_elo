# ELO Calculation System

## Document Information

- **Document Type**: Algorithm Documentation
- **Target Audience**: Developers, Data Scientists, Algorithm Reviewers
- **Last Updated**: 2025-12-26
- **Maintainer**: Development Team

## Overview

The Baby Foot ELO application implements a **hybrid ELO rating system** with **pool correction** to ensure zero-sum ELO changes across all players in a match. This system is a direct port from the Python backend (`backend/app/services/elo.py`) and maintains mathematical equivalence.

### Key Characteristics

- **Hybrid System**: Both individual players and teams have independent ELO ratings
- **Zero-Sum Enforcement**: Pool correction ensures no ELO inflation/deflation
- **Tiered K-Factors**: Higher K-factors for lower ELO (faster progression)
- **Standard ELO Formula**: Win probability based on classic ELO calculation
- **Integer Arithmetic**: Uses `Math.trunc()` to match Python `int()` behavior

## Implementation File

**Location**: `lib/services/elo.ts`

## Core Concepts

### 1. Team ELO Calculation

Team ELO is the **truncated average** of the two players' individual ELO ratings.

**Function**: `calculateTeamElo(member1Elo, member2Elo)`

**Formula**:
```text
TeamELO = trunc((Player1_ELO + Player2_ELO) / 2)
```

**Example**:
```typescript
const player1Elo = 1600;
const player2Elo = 1400;
const teamElo = calculateTeamElo(1600, 1400);
// teamElo = trunc((1600 + 1400) / 2) = trunc(1500) = 1500
```

**Why Truncate?**
- Matches Python `int()` behavior for consistency with original implementation
- Ensures integer ELO values (no decimal ratings)

---

### 2. Win Probability Calculation

Win probability uses the **standard ELO formula**:

**Function**: `calculateWinProbability(competitorAElo, competitorBElo)`

**Formula**:
```text
WinProbability_A = 1 / (1 + 10^((ELO_B - ELO_A) / 400))
```

**Example 1** (Evenly Matched):
```typescript
const winProb = calculateWinProbability(1500, 1500);
// winProb = 1 / (1 + 10^((1500 - 1500) / 400))
//         = 1 / (1 + 10^0)
//         = 1 / (1 + 1)
//         = 0.5 (50% chance)
```

**Example 2** (Higher ELO vs Lower ELO):
```typescript
const winProb = calculateWinProbability(1600, 1400);
// winProb = 1 / (1 + 10^((1400 - 1600) / 400))
//         = 1 / (1 + 10^(-0.5))
//         = 1 / (1 + 0.316)
//         = 0.760 (76% chance)
```

**Example 3** (Large ELO Difference):
```typescript
const winProb = calculateWinProbability(1800, 1200);
// winProb = 1 / (1 + 10^((1200 - 1800) / 400))
//         = 1 / (1 + 10^(-1.5))
//         = 1 / (1 + 0.0316)
//         = 0.969 (97% chance)
```

**Interpretation**:
- 0.5 = Even match
- > 0.5 = Competitor A favored
- < 0.5 = Competitor B favored
- ~1.0 = Competitor A heavily favored

---

### 3. K-Factor Tiers

The K-factor determines **how quickly ELO changes**. Higher K = faster progression.

**Function**: `determineKFactor(competitorElo)`

**K-Factor Tiers**:

| ELO Range | K-Factor | Purpose |
|-----------|----------|---------|
| < 1200 | **200** | Fast progression for beginners |
| 1200 - 1799 | **100** | Moderate progression for intermediate |
| ≥ 1800 | **50** | Slow, stable progression for advanced |

**Constants**:
```typescript
export const K_TIER1 = 200; // ELO < 1200
export const K_TIER2 = 100; // 1200 <= ELO < 1800
export const K_TIER3 = 50;  // ELO >= 1800
```

**Example**:
```typescript
determineKFactor(1000);  // Returns 200 (Tier 1)
determineKFactor(1500);  // Returns 100 (Tier 2)
determineKFactor(2000);  // Returns 50  (Tier 3)
```

**Rationale**:
- **Beginners (K=200)**: Rapid adjustment to find true skill level
- **Intermediate (K=100)**: Balance between responsiveness and stability
- **Advanced (K=50)**: Stable ratings, small changes prevent volatility

---

### 4. Base ELO Change Calculation

The base ELO change uses the **standard ELO formula**:

**Function**: `calculateEloChange(competitorElo, winProbability, matchResult)`

**Formula**:
```text
ELO_Change = K * (Result - Expected)
```

Where:
- `K` = K-factor based on competitor's ELO
- `Result` = 1 (win) or 0 (loss)
- `Expected` = Win probability (0-1)

**Example 1** (Unexpected Win):
```typescript
const elo = 1400;
const winProb = 0.24; // Low chance to win
const result = 1; // Won
const kFactor = determineKFactor(1400); // 100

const change = calculateEloChange(1400, 0.24, 1);
// change = trunc(100 * (1 - 0.24))
//        = trunc(100 * 0.76)
//        = trunc(76)
//        = 76
```
**Interpretation**: Beating a stronger opponent → large gain (+76)

**Example 2** (Expected Win):
```typescript
const change = calculateEloChange(1600, 0.76, 1);
// change = trunc(100 * (1 - 0.76))
//        = trunc(100 * 0.24)
//        = 24
```
**Interpretation**: Beating a weaker opponent → small gain (+24)

**Example 3** (Expected Loss):
```typescript
const change = calculateEloChange(1400, 0.24, 0);
// change = trunc(100 * (0 - 0.24))
//        = trunc(-24)
//        = -24
```
**Interpretation**: Losing to a stronger opponent → small loss (-24)

**Example 4** (Unexpected Loss):
```typescript
const change = calculateEloChange(1600, 0.76, 0);
// change = trunc(100 * (0 - 0.76))
//        = trunc(-76)
//        = -76
```
**Interpretation**: Losing to a weaker opponent → large loss (-76)

---

### 5. Pool Correction (Zero-Sum Enforcement)

The **pool correction** system ensures that the **sum of all ELO changes in a match equals zero**. This prevents ELO inflation or deflation over time.

**Function**: `calculateEloChangesWithPoolCorrection(competitorsData)`

**Algorithm**:

1. **Calculate Initial Changes**:
   - For each competitor, calculate base ELO change using standard formula
   - Track sum of all initial changes
   - Track total K-factors

2. **Calculate Correction Factor**:
   ```text
   CorrectionFactorPerK = -SumOfInitialChanges / TotalKFactors
   ```

3. **Apply Correction**:
   ```text
   CorrectedChange = InitialChange + trunc(K_factor * CorrectionFactorPerK)
   ```

4. **Verify Zero-Sum**:
   ```text
   Sum(CorrectedChanges) = 0
   ```

**Why Pool Correction?**
- Without correction, sum of changes may not equal zero due to rounding
- Ensures fair ELO economy (total ELO in system remains constant)
- Prevents rating inflation over time

---

## Complete Match ELO Calculation (Worked Example)

### Scenario

**Match**: Team A (Alice + Bob) vs Team B (Charlie + Diana)

**Initial ELOs**:
- Alice: 1600
- Bob: 1400
- Charlie: 1200
- Diana: 1100

**Result**: Team A wins

### Step-by-Step Calculation

#### Step 1: Calculate Team ELOs

```text
Team A ELO = trunc((1600 + 1400) / 2) = trunc(1500) = 1500
Team B ELO = trunc((1200 + 1100) / 2) = trunc(1150) = 1150
```

#### Step 2: Calculate Win Probability

```text
WinProb_A = 1 / (1 + 10^((1150 - 1500) / 400))
          = 1 / (1 + 10^(-0.875))
          = 1 / (1 + 0.133)
          = 0.795 (79.5% chance Team A wins)

WinProb_B = 1 - 0.795 = 0.205 (20.5% chance Team B wins)
```

#### Step 3: Determine K-Factors

```text
K_Alice = determineKFactor(1600) = 100  (Tier 2)
K_Bob = determineKFactor(1400) = 100    (Tier 2)
K_Charlie = determineKFactor(1200) = 100 (Tier 2, edge case)
K_Diana = determineKFactor(1100) = 200  (Tier 1)
```

#### Step 4: Calculate Initial Player ELO Changes

**Team A (Winners)**:
```text
Alice_Initial = trunc(100 * (1 - 0.795)) = trunc(20.5) = 20
Bob_Initial = trunc(100 * (1 - 0.795)) = trunc(20.5) = 20
```

**Team B (Losers)**:
```text
Charlie_Initial = trunc(100 * (0 - 0.205)) = trunc(-20.5) = -20
Diana_Initial = trunc(200 * (0 - 0.205)) = trunc(-41.0) = -41
```

**Sum of Initial Changes**:
```text
Sum = 20 + 20 + (-20) + (-41) = -21 ≠ 0
```

❌ **Not zero-sum!** Need correction.

#### Step 5: Apply Pool Correction

```text
TotalKFactors = 100 + 100 + 100 + 200 = 500

CorrectionFactorPerK = -(-21) / 500 = 21 / 500 = 0.042
```

**Apply correction to each player**:
```text
Alice_Correction = trunc(100 * 0.042) = trunc(4.2) = 4
Bob_Correction = trunc(100 * 0.042) = trunc(4.2) = 4
Charlie_Correction = trunc(100 * 0.042) = trunc(4.2) = 4
Diana_Correction = trunc(200 * 0.042) = trunc(8.4) = 8
```

**Final Corrected Changes**:
```text
Alice_Final = 20 + 4 = 24
Bob_Final = 20 + 4 = 24
Charlie_Final = -20 + 4 = -16
Diana_Final = -41 + 8 = -33
```

**Verify Zero-Sum**:
```text
Sum = 24 + 24 + (-16) + (-33) = -1
```

⚠️ **Still not perfect due to truncation**, but within rounding error.

#### Step 6: Final Player ELOs

```text
Alice_New = 1600 + 24 = 1624
Bob_New = 1400 + 24 = 1424
Charlie_New = 1200 + (-16) = 1184
Diana_New = 1100 + (-33) = 1067
```

#### Step 7: Calculate Team ELO Changes

**Initial Team Changes**:
```text
K_TeamA = determineKFactor(1500) = 100
K_TeamB = determineKFactor(1150) = 200

TeamA_Initial = trunc(100 * (1 - 0.795)) = trunc(20.5) = 20
TeamB_Initial = trunc(200 * (0 - 0.205)) = trunc(-41.0) = -41
```

**Pool Correction for Teams**:
```text
TotalKFactors_Teams = 100 + 200 = 300
Sum = 20 + (-41) = -21

CorrectionFactorPerK = -(-21) / 300 = 21 / 300 = 0.07

TeamA_Correction = trunc(100 * 0.07) = 7
TeamB_Correction = trunc(200 * 0.07) = 14
```

**Final Team Changes**:
```text
TeamA_Final = 20 + 7 = 27
TeamB_Final = -41 + 14 = -27
```

**Verify Zero-Sum**:
```text
Sum = 27 + (-27) = 0 ✅
```

**Final Team ELOs**:
```text
TeamA_New = 1500 + 27 = 1527
TeamB_New = 1150 + (-27) = 1123
```

---

## Code Structure

### Type Definitions

```typescript
interface CompetitorData {
  old_elo: number;
  win_prob: number;
  match_result: 0 | 1;
  k_factor: number;
}

export interface EloChangeResult {
  old_elo: number;
  new_elo: number;
  difference: number;
}

export type EloChangesMap = Record<number, EloChangeResult>;

export interface TeamWithPlayers {
  team_id: number;
  global_elo: number;
  player1: PlayerForElo;
  player2: PlayerForElo;
}
```

### Public API

**Main Entry Point**:
```typescript
processMatchResult(
  winningTeam: TeamWithPlayers,
  losingTeam: TeamWithPlayers
): [EloChangesMap, EloChangesMap]
```

**Returns**: Tuple of `[playersEloChanges, teamsEloChanges]`

**Example Usage**:
```typescript
const [playersChanges, teamsChanges] = processMatchResult(
  winningTeam,
  losingTeam
);

// playersChanges = {
//   1: { old_elo: 1600, new_elo: 1624, difference: 24 },
//   2: { old_elo: 1400, new_elo: 1424, difference: 24 },
//   3: { old_elo: 1200, new_elo: 1184, difference: -16 },
//   4: { old_elo: 1100, new_elo: 1067, difference: -33 }
// }

// teamsChanges = {
//   5: { old_elo: 1500, new_elo: 1527, difference: 27 },
//   6: { old_elo: 1150, new_elo: 1123, difference: -27 }
// }
```

---

## Mathematical Properties

### 1. Fairness Properties

**Symmetric Win Probability**:
```text
P(A beats B) + P(B beats A) = 1
```

**Zero-Sum After Correction**:
```text
Sum(All Player ELO Changes) ≈ 0 (within rounding error)
Sum(Both Team ELO Changes) = 0 (exact)
```

**K-Factor Proportionality**:
- Correction distributed proportionally to K-factor
- Players with higher K-factors receive larger corrections
- Ensures faster-progressing players contribute more to balancing

### 2. Boundary Conditions

**Minimum ELO**: No hard minimum (can go below 0 in theory, but unlikely)
**Maximum ELO**: No hard maximum
**Starting ELO**: 1000 (arbitrary baseline)

**Edge Cases**:
- **Same ELO**: Win probability = 0.5, symmetric changes
- **Very Large Difference**: Win probability approaches 1.0 or 0.0
- **All Same K-Factor**: Correction distributes equally

### 3. Convergence Properties

- **Skill Convergence**: Players' ELOs converge to true skill over time
- **K-Factor Decay**: As ELO increases, K decreases → more stable ratings
- **Team Independence**: Team ELO evolves independently from player ELOs after creation

---

## Testing Considerations

### Unit Tests Should Verify

1. **Team ELO Calculation**:
   - Average of two players
   - Truncation behavior
   - Negative ELO validation error

2. **Win Probability**:
   - Symmetric property: `P(A vs B) + P(B vs A) = 1`
   - Boundary: Equal ELOs → 0.5
   - Large difference → near 0 or 1

3. **K-Factor Tiers**:
   - Correct tier selection
   - Boundary values (1199, 1200, 1799, 1800)

4. **Pool Correction**:
   - Zero-sum property (within rounding tolerance)
   - Proportional distribution by K-factor
   - Handles edge cases (all same K)

5. **Full Match Processing**:
   - Returns correct structure
   - All players have ELO changes
   - Teams have ELO changes
   - No NaN or Infinity values

### Example Test (Vitest)

```typescript
import { describe, it, expect } from 'vitest';
import { calculateTeamElo, calculateWinProbability, processMatchResult } from './elo';

describe('ELO Calculation', () => {
  it('should calculate team ELO as truncated average', () => {
    expect(calculateTeamElo(1600, 1400)).toBe(1500);
    expect(calculateTeamElo(1601, 1400)).toBe(1500); // Truncation
  });

  it('should calculate symmetric win probabilities', () => {
    const probA = calculateWinProbability(1500, 1300);
    const probB = calculateWinProbability(1300, 1500);
    expect(probA + probB).toBeCloseTo(1.0, 5);
  });

  it('should apply pool correction for zero-sum', () => {
    const winningTeam = {
      team_id: 1,
      global_elo: 1500,
      player1: { player_id: 1, global_elo: 1600 },
      player2: { player_id: 2, global_elo: 1400 },
    };
    const losingTeam = {
      team_id: 2,
      global_elo: 1150,
      player1: { player_id: 3, global_elo: 1200 },
      player2: { player_id: 4, global_elo: 1100 },
    };

    const [playersChanges, teamsChanges] = processMatchResult(
      winningTeam,
      losingTeam
    );

    // Verify structure
    expect(playersChanges).toHaveProperty('1');
    expect(playersChanges).toHaveProperty('2');
    expect(playersChanges).toHaveProperty('3');
    expect(playersChanges).toHaveProperty('4');

    // Verify zero-sum (within rounding tolerance)
    const sumPlayers = Object.values(playersChanges)
      .reduce((sum, change) => sum + change.difference, 0);
    expect(Math.abs(sumPlayers)).toBeLessThan(5); // Allow small rounding error

    const sumTeams = Object.values(teamsChanges)
      .reduce((sum, change) => sum + change.difference, 0);
    expect(sumTeams).toBe(0); // Exact zero-sum for teams
  });
});
```

---

## Design Decisions and Trade-offs

### 1. Integer Arithmetic

**Decision**: Use `Math.trunc()` for all ELO calculations

**Rationale**:
- Matches Python `int()` behavior (direct port requirement)
- Avoids floating-point precision issues
- Simpler database storage (INTEGER type)

**Trade-off**:
- Loses precision in intermediate calculations
- Zero-sum not always exact (within ±5 due to rounding)

### 2. Pool Correction

**Decision**: Distribute surplus/deficit proportionally by K-factor

**Rationale**:
- Fairer than equal distribution (accounts for progression speed)
- Prevents ELO inflation in system with varying K-factors
- Mathematically sound approach

**Trade-off**:
- More complex algorithm
- Requires tracking all competitors' K-factors
- Small rounding errors still possible

### 3. K-Factor Tiers

**Decision**: Three tiers (200/100/50) with thresholds at 1200 and 1800

**Rationale**:
- Standard chess ELO system approach
- Balances fast progression for beginners vs stability for advanced
- Clear, simple thresholds

**Trade-off**:
- Discontinuous jump in progression speed at thresholds
- Could use smooth curve instead (more complex)

### 4. Team ELO Independence

**Decision**: Team ELO evolves independently after creation

**Rationale**:
- Allows team synergy to be captured
- Two players may perform differently with different partners
- More interesting statistics (player vs team rankings)

**Trade-off**:
- Initial team ELO may not reflect current player ELOs
- More complex to explain to users

---

## Future Enhancements

### Potential Improvements

1. **Fanny Bonus**: Apply multiplier for "fanny" matches (loser scored 0)
   ```typescript
   if (isFanny) {
     eloChange *= 1.5; // 50% bonus
   }
   ```

2. **ELO Decay**: Reduce ELO for inactive players
   ```typescript
   if (daysSinceLastMatch > 90) {
     elo -= Math.trunc((daysSinceLastMatch - 90) * 0.5);
   }
   ```

3. **Provisional Rating Period**: Higher K-factor for first N matches
   ```typescript
   if (matchesPlayed < 10) {
     kFactor = 400; // Provisional K
   }
   ```

4. **Smooth K-Factor Curve**: Replace tiers with continuous function
   ```typescript
   kFactor = 200 / (1 + Math.exp((elo - 1400) / 200));
   ```

---

## Maintenance Notes

### When to Update This Document

- Changes to K-factor thresholds or values
- Modifications to pool correction algorithm
- Addition of fanny bonuses or other modifiers
- Changes to base ELO formula
- Updates to team ELO calculation

### Validation Checklist

When modifying ELO calculations:
- [ ] Verify zero-sum property still holds
- [ ] Test boundary conditions (very high/low ELOs)
- [ ] Ensure Python backend and TypeScript frontend stay in sync
- [ ] Update worked examples in this document
- [ ] Run full test suite
- [ ] Verify database integer storage compatibility

### Related Documentation

- `01-architecture-overview.md` - Service layer context
- `03-sequence-diagrams.md` - Match creation flow with ELO calculation
- `05-service-layer.md` - Service integration details
- Python Backend: `backend/app/services/elo.py` - Original implementation

---

**Last Updated**: 2025-12-26
**Maintained By**: Development Team
**Algorithm Author**: Original Python implementation
**TypeScript Port**: Development Team
