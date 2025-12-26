import { describe, expect, it } from "vitest";
import {
  calculateTeamElo,
  calculateWinProbability,
  determineKFactor,
  calculateEloChange,
  calculateEloChangesWithPoolCorrection,
  calculatePlayersEloChange,
  processMatchResult,
  K_TIER1,
  K_TIER2,
  K_TIER3,
  type TeamWithPlayers,
} from "@/lib/services/elo";
import { ValidationError } from "@/lib/errors/api-errors";

// [>]: Helper to create team objects for testing.
function createTeam(
  teamId: number,
  teamElo: number,
  player1Id: number,
  player1Elo: number,
  player2Id: number,
  player2Elo: number,
): TeamWithPlayers {
  return {
    team_id: teamId,
    global_elo: teamElo,
    player1: { player_id: player1Id, global_elo: player1Elo },
    player2: { player_id: player2Id, global_elo: player2Elo },
  };
}

describe("calculateTeamElo", () => {
  it("should calculate average of two ELO ratings", () => {
    expect(calculateTeamElo(1400, 1500)).toBe(1450);
  });

  it("should truncate odd averages (not round)", () => {
    // (1001 + 1000) / 2 = 1000.5, should truncate to 1000
    expect(calculateTeamElo(1001, 1000)).toBe(1000);
  });

  it("should throw ValidationError for negative ELO", () => {
    expect(() => calculateTeamElo(-100, 1500)).toThrow(ValidationError);
  });
});

describe("calculateWinProbability", () => {
  it("should return 0.5 for equal ELO", () => {
    const prob = calculateWinProbability(1500, 1500);
    expect(prob).toBeCloseTo(0.5, 3);
  });

  it("should return high probability for higher ELO competitor", () => {
    // 2000 vs 1000: very high probability for 2000
    const prob = calculateWinProbability(2000, 1000);
    expect(prob).toBeCloseTo(0.9968, 3);
  });

  it("should return low probability for lower ELO competitor", () => {
    // 1000 vs 2000: very low probability for 1000
    const prob = calculateWinProbability(1000, 2000);
    expect(prob).toBeCloseTo(0.0032, 3);
  });

  it("should satisfy symmetry: P(A) + P(B) = 1", () => {
    const probA = calculateWinProbability(1300, 1500);
    const probB = calculateWinProbability(1500, 1300);
    expect(probA + probB).toBeCloseTo(1, 10);
  });

  it("should throw ValidationError for negative ELO", () => {
    expect(() => calculateWinProbability(-1500, 1500)).toThrow(ValidationError);
  });
});

describe("determineKFactor", () => {
  it("should return K_TIER1 (200) for ELO < 1200", () => {
    expect(determineKFactor(0)).toBe(K_TIER1);
    expect(determineKFactor(1000)).toBe(K_TIER1);
    expect(determineKFactor(1199)).toBe(K_TIER1);
  });

  it("should return K_TIER2 (100) for 1200 <= ELO < 1800", () => {
    expect(determineKFactor(1200)).toBe(K_TIER2);
    expect(determineKFactor(1500)).toBe(K_TIER2);
    expect(determineKFactor(1799)).toBe(K_TIER2);
  });

  it("should return K_TIER3 (50) for ELO >= 1800", () => {
    expect(determineKFactor(1800)).toBe(K_TIER3);
    expect(determineKFactor(2000)).toBe(K_TIER3);
    expect(determineKFactor(2500)).toBe(K_TIER3);
  });

  it("should throw ValidationError for negative ELO", () => {
    expect(() => determineKFactor(-10)).toThrow(ValidationError);
  });
});

describe("calculateEloChange", () => {
  it("should return positive change for win with 0.5 probability", () => {
    // K=100 (ELO 1500), win with 0.5 prob: 100 * (1 - 0.5) = 50
    const change = calculateEloChange(1500, 0.5, 1);
    expect(change).toBe(50);
  });

  it("should return negative change for loss with 0.5 probability", () => {
    // K=100 (ELO 1500), loss with 0.5 prob: 100 * (0 - 0.5) = -50
    const change = calculateEloChange(1500, 0.5, 0);
    expect(change).toBe(-50);
  });

  it("should use correct K-factor based on ELO tier", () => {
    // Low ELO player (K=200), win with 0.5 prob: 200 * (1 - 0.5) = 100
    const change = calculateEloChange(1000, 0.5, 1);
    expect(change).toBe(100);
  });

  it("should throw ValidationError for invalid probability", () => {
    expect(() => calculateEloChange(1500, 1.5, 1)).toThrow(ValidationError);
    expect(() => calculateEloChange(1500, -0.5, 1)).toThrow(ValidationError);
  });
});

describe("calculateEloChangesWithPoolCorrection", () => {
  it("should ensure zero-sum changes", () => {
    const competitorsData = {
      1: {
        old_elo: 1500,
        win_prob: 0.5,
        match_result: 1 as const,
        k_factor: 100,
      },
      2: {
        old_elo: 1500,
        win_prob: 0.5,
        match_result: 0 as const,
        k_factor: 100,
      },
    };

    const result = calculateEloChangesWithPoolCorrection(competitorsData);
    const totalChange = result[1].difference + result[2].difference;

    expect(totalChange).toBe(0);
  });

  it("should apply pool correction with different K-factors", () => {
    // Low ELO player (K=200) beats high ELO player (K=50)
    // Without correction, sum would be non-zero
    const competitorsData = {
      1: {
        old_elo: 1000,
        win_prob: 0.1,
        match_result: 1 as const,
        k_factor: 200,
      },
      2: {
        old_elo: 2000,
        win_prob: 0.9,
        match_result: 0 as const,
        k_factor: 50,
      },
    };

    const result = calculateEloChangesWithPoolCorrection(competitorsData);
    const totalChange = result[1].difference + result[2].difference;

    // [>]: Due to integer truncation, may be off by 1-2.
    expect(Math.abs(totalChange)).toBeLessThanOrEqual(2);
  });
});

describe("calculatePlayersEloChange", () => {
  it("should calculate ELO changes for all 4 players", () => {
    const winningTeam = createTeam(1, 1000, 1, 1000, 2, 1000);
    const losingTeam = createTeam(2, 1000, 3, 1000, 4, 1000);

    const result = calculatePlayersEloChange(winningTeam, losingTeam);

    expect(Object.keys(result)).toHaveLength(4);
    expect(result[1]).toBeDefined();
    expect(result[2]).toBeDefined();
    expect(result[3]).toBeDefined();
    expect(result[4]).toBeDefined();
  });

  it("should produce zero-sum across all 4 players", () => {
    const winningTeam = createTeam(1, 1000, 1, 1000, 2, 1000);
    const losingTeam = createTeam(2, 1000, 3, 1000, 4, 1000);

    const result = calculatePlayersEloChange(winningTeam, losingTeam);
    const totalChange =
      result[1].difference +
      result[2].difference +
      result[3].difference +
      result[4].difference;

    // [>]: Due to integer truncation, may be off by 1-2.
    expect(Math.abs(totalChange)).toBeLessThanOrEqual(2);
  });

  it("should give winners positive change and losers negative change for equal ELO", () => {
    const winningTeam = createTeam(1, 1000, 1, 1000, 2, 1000);
    const losingTeam = createTeam(2, 1000, 3, 1000, 4, 1000);

    const result = calculatePlayersEloChange(winningTeam, losingTeam);

    expect(result[1].difference).toBeGreaterThan(0);
    expect(result[2].difference).toBeGreaterThan(0);
    expect(result[3].difference).toBeLessThan(0);
    expect(result[4].difference).toBeLessThan(0);
  });
});

describe("processMatchResult", () => {
  it("should return both player and team ELO changes", () => {
    const winningTeam = createTeam(1, 1500, 1, 1500, 2, 1500);
    const losingTeam = createTeam(2, 1500, 3, 1500, 4, 1500);

    const [playerChanges, teamChanges] = processMatchResult(
      winningTeam,
      losingTeam,
    );

    expect(Object.keys(playerChanges)).toHaveLength(4);
    expect(Object.keys(teamChanges)).toHaveLength(2);
  });

  it("should handle equal ELO scenario correctly", () => {
    const winningTeam = createTeam(1, 1500, 1, 1500, 2, 1500);
    const losingTeam = createTeam(2, 1500, 3, 1500, 4, 1500);

    const [playerChanges] = processMatchResult(winningTeam, losingTeam);

    // [>]: With equal ELO, win probability is 0.5.
    // K=100 (tier 2), so difference = 100 * (1 - 0.5) = 50 for winners.
    expect(playerChanges[1].difference).toBe(50);
    expect(playerChanges[2].difference).toBe(50);
    expect(playerChanges[3].difference).toBe(-50);
    expect(playerChanges[4].difference).toBe(-50);
  });

  it("should handle upset scenario (low ELO beats high ELO)", () => {
    const winningTeam = createTeam(1, 1000, 1, 1000, 2, 1000);
    const losingTeam = createTeam(2, 2000, 3, 2000, 4, 2000);

    const [playerChanges] = processMatchResult(winningTeam, losingTeam);

    // [>]: Winners gain, losers lose. Pool correction applies.
    // Low ELO winners (K=200) gain more than high ELO losers (K=50) lose.
    expect(playerChanges[1].difference).toBeGreaterThan(50);
    expect(playerChanges[2].difference).toBeGreaterThan(50);
    expect(playerChanges[3].difference).toBeLessThan(0);
    expect(playerChanges[4].difference).toBeLessThan(0);

    // [>]: Zero-sum property should hold.
    const total =
      playerChanges[1].difference +
      playerChanges[2].difference +
      playerChanges[3].difference +
      playerChanges[4].difference;
    expect(Math.abs(total)).toBeLessThanOrEqual(2);
  });

  it("should handle expected win scenario (high ELO beats low ELO)", () => {
    const winningTeam = createTeam(1, 2000, 1, 2000, 2, 2000);
    const losingTeam = createTeam(2, 1000, 3, 1000, 4, 1000);

    const [playerChanges] = processMatchResult(winningTeam, losingTeam);

    // [>]: Expected wins result in small or zero changes.
    expect(playerChanges[1].difference).toBeLessThanOrEqual(5);
    expect(playerChanges[2].difference).toBeLessThanOrEqual(5);
    expect(playerChanges[3].difference).toBeGreaterThanOrEqual(-5);
    expect(playerChanges[4].difference).toBeGreaterThanOrEqual(-5);
  });
});
