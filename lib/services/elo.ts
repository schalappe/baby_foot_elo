// [>]: ELO Calculation Service.
// Implements hybrid ELO system with pool correction for zero-sum ELO changes.
// Direct port from Python backend/app/services/elo.py.

import { ValidationError } from "@/lib/errors/api-errors";

// [>]: K-factor tiers matching Python backend.
export const K_TIER1 = 200; // ELO < 1200
export const K_TIER2 = 100; // 1200 <= ELO < 1800
export const K_TIER3 = 50; // ELO >= 1800

// [>]: Input data structure for pool correction calculation.
interface CompetitorData {
  old_elo: number;
  win_prob: number;
  match_result: 0 | 1;
  k_factor: number;
}

// [>]: Output structure for ELO change results.
// Matches EloChangeSchema in lib/types/schemas/match.ts.
export interface EloChangeResult {
  old_elo: number;
  new_elo: number;
  difference: number;
}

// [>]: Generic mapping for competitor/team ELO changes.
export type EloChangesMap = Record<number, EloChangeResult>;
type CompetitorsDataMap = Record<number, CompetitorData>;

// [>]: Minimal player data required for ELO calculations.
interface PlayerForElo {
  player_id: number;
  global_elo: number;
}

// [>]: Team with required players for player ELO calculations.
export interface TeamWithPlayers {
  team_id: number;
  global_elo: number;
  player1: PlayerForElo;
  player2: PlayerForElo;
}

/**
 * Calculate team ELO as the average of two player ELO ratings.
 * Uses Math.trunc() for integer conversion to match Python int() behavior.
 *
 * @param member1Elo - ELO rating of member 1.
 * @param member2Elo - ELO rating of member 2.
 * @returns Team ELO rating.
 * @throws ValidationError if ELO ratings are negative.
 */
export function calculateTeamElo(
  member1Elo: number,
  member2Elo: number,
): number {
  if (member1Elo < 0 || member2Elo < 0) {
    throw new ValidationError("ELO ratings must be non-negative");
  }
  return Math.trunc((member1Elo + member2Elo) / 2);
}

/**
 * Calculate win probability using the ELO formula.
 * Formula: 1 / (1 + 10 ** ((ELO_B - ELO_A) / 400))
 *
 * @param competitorAElo - ELO rating of competitor A.
 * @param competitorBElo - ELO rating of competitor B.
 * @returns Win probability of competitor A (between 0 and 1).
 * @throws ValidationError if ELO ratings are negative.
 */
export function calculateWinProbability(
  competitorAElo: number,
  competitorBElo: number,
): number {
  if (competitorAElo < 0 || competitorBElo < 0) {
    throw new ValidationError("ELO ratings must be non-negative");
  }

  const exponent = (competitorBElo - competitorAElo) / 400;
  return 1 / (1 + Math.pow(10, exponent));
}

/**
 * Determine the K factor based on competitor's ELO rating.
 *
 * K factor tiers:
 * - 200 for ELO < 1200
 * - 100 for 1200 <= ELO < 1800
 * - 50 for ELO >= 1800
 *
 * @param competitorElo - ELO rating of the competitor.
 * @returns K factor.
 * @throws ValidationError if ELO rating is negative.
 */
export function determineKFactor(competitorElo: number): number {
  if (competitorElo < 0) {
    throw new ValidationError("ELO rating must be non-negative");
  }

  if (competitorElo < 1200) {
    return K_TIER1;
  }

  if (competitorElo < 1800) {
    return K_TIER2;
  }

  return K_TIER3;
}

/**
 * Calculate individual ELO change using the formula:
 * ELO Change = K * (Result - Expected)
 *
 * Where Result is 1 for win, 0 for loss.
 *
 * @param competitorElo - ELO rating of the competitor.
 * @param winProbability - Win probability of the competitor (0-1).
 * @param matchResult - Match result (1 for win, 0 for loss).
 * @returns ELO change (can be negative for losses).
 * @throws ValidationError if inputs are invalid.
 */
export function calculateEloChange(
  competitorElo: number,
  winProbability: number,
  matchResult: 0 | 1,
): number {
  if (competitorElo < 0) {
    throw new ValidationError("ELO rating must be non-negative");
  }
  if (winProbability < 0 || winProbability > 1) {
    throw new ValidationError("Win probability must be between 0 and 1");
  }

  const factor = determineKFactor(competitorElo);
  return Math.trunc(factor * (matchResult - winProbability));
}

/**
 * Calculate ELO changes for a group of competitors, applying a "pool" system
 * correction to ensure the sum of ELO changes is zero.
 *
 * The pool correction distributes any surplus/deficit proportionally based on
 * each competitor's K-factor. This prevents ELO inflation/deflation.
 *
 * @param competitorsData - Map of competitor IDs to their data.
 * @returns Map of competitor IDs to ELO change results.
 */
export function calculateEloChangesWithPoolCorrection(
  competitorsData: CompetitorsDataMap,
): EloChangesMap {
  const initialEloChanges: Record<number, number> = {};
  let totalKFactor = 0;
  let sumOfInitialChanges = 0;

  // [>]: Calculate initial changes for each competitor.
  for (const [compIdStr, data] of Object.entries(competitorsData)) {
    const compId = Number(compIdStr);
    const initialChange = calculateEloChange(
      data.old_elo,
      data.win_prob,
      data.match_result,
    );
    initialEloChanges[compId] = initialChange;
    totalKFactor += data.k_factor;
    sumOfInitialChanges += initialChange;
  }

  // [>]: Apply pool system correction.
  const correctedEloChanges: EloChangesMap = {};
  const correctionFactorPerK =
    totalKFactor !== 0 ? -sumOfInitialChanges / totalKFactor : 0;

  for (const [compIdStr, data] of Object.entries(competitorsData)) {
    const compId = Number(compIdStr);
    const initialChange = initialEloChanges[compId];
    const correctedChange =
      initialChange + Math.trunc(data.k_factor * correctionFactorPerK);

    correctedEloChanges[compId] = {
      old_elo: data.old_elo,
      new_elo: data.old_elo + correctedChange,
      difference: correctedChange,
    };
  }

  return correctedEloChanges;
}

/**
 * Calculate ELO changes for each player in a match.
 *
 * This function applies a "pool" system correction to ensure that the sum of
 * ELO changes for all players in a match is zero, preventing ELO inflation/deflation.
 *
 * @param winningTeam - The winning team with players.
 * @param losingTeam - The losing team with players.
 * @returns Map of player IDs to ELO change results.
 */
export function calculatePlayersEloChange(
  winningTeam: TeamWithPlayers,
  losingTeam: TeamWithPlayers,
): EloChangesMap {
  const eloWinner = calculateTeamElo(
    winningTeam.player1.global_elo,
    winningTeam.player2.global_elo,
  );
  const eloLoser = calculateTeamElo(
    losingTeam.player1.global_elo,
    losingTeam.player2.global_elo,
  );
  const winProb = calculateWinProbability(eloWinner, eloLoser);

  const allPlayersData: CompetitorsDataMap = {
    // [>]: Winning team players.
    [winningTeam.player1.player_id]: {
      old_elo: winningTeam.player1.global_elo,
      win_prob: winProb,
      match_result: 1,
      k_factor: determineKFactor(winningTeam.player1.global_elo),
    },
    [winningTeam.player2.player_id]: {
      old_elo: winningTeam.player2.global_elo,
      win_prob: winProb,
      match_result: 1,
      k_factor: determineKFactor(winningTeam.player2.global_elo),
    },
    // [>]: Losing team players.
    [losingTeam.player1.player_id]: {
      old_elo: losingTeam.player1.global_elo,
      win_prob: 1 - winProb,
      match_result: 0,
      k_factor: determineKFactor(losingTeam.player1.global_elo),
    },
    [losingTeam.player2.player_id]: {
      old_elo: losingTeam.player2.global_elo,
      win_prob: 1 - winProb,
      match_result: 0,
      k_factor: determineKFactor(losingTeam.player2.global_elo),
    },
  };

  return calculateEloChangesWithPoolCorrection(allPlayersData);
}

/**
 * Calculate ELO changes for teams in a match.
 *
 * This function applies a "pool" system correction to ensure that the sum of
 * ELO changes for both teams is zero.
 *
 * @param winningTeam - The winning team.
 * @param losingTeam - The losing team.
 * @returns Map of team IDs to ELO change results.
 */
export function calculateTeamEloChange(
  winningTeam: TeamWithPlayers,
  losingTeam: TeamWithPlayers,
): EloChangesMap {
  const winProbability = calculateWinProbability(
    winningTeam.global_elo,
    losingTeam.global_elo,
  );

  const teamsData: CompetitorsDataMap = {
    [winningTeam.team_id]: {
      old_elo: winningTeam.global_elo,
      win_prob: winProbability,
      match_result: 1,
      k_factor: determineKFactor(winningTeam.global_elo),
    },
    [losingTeam.team_id]: {
      old_elo: losingTeam.global_elo,
      win_prob: 1 - winProbability,
      match_result: 0,
      k_factor: determineKFactor(losingTeam.global_elo),
    },
  };

  return calculateEloChangesWithPoolCorrection(teamsData);
}

/**
 * Process match results and calculate updated ELO values for each player and team.
 *
 * @param winningTeam - The winning team with players.
 * @param losingTeam - The losing team with players.
 * @returns Tuple of [playersEloChanges, teamsEloChanges].
 * @throws ValidationError if any player is missing.
 */
export function processMatchResult(
  winningTeam: TeamWithPlayers,
  losingTeam: TeamWithPlayers,
): [EloChangesMap, EloChangesMap] {
  if (
    !winningTeam.player1 ||
    !winningTeam.player2 ||
    !losingTeam.player1 ||
    !losingTeam.player2
  ) {
    throw new ValidationError("All players must be provided");
  }

  const playersEloChange = calculatePlayersEloChange(winningTeam, losingTeam);
  const teamEloChange = calculateTeamEloChange(winningTeam, losingTeam);

  return [playersEloChange, teamEloChange];
}
