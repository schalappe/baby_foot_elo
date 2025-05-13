// frontend/lib/eloCalculator.ts

/**
 * K-factors for ELO calculation.
 */
const K_TIER1 = 100; // ELO < 1200
const K_TIER2 = 50;  // 1200 <= ELO < 1800
const K_TIER3 = 24;  // ELO >= 1800

/**
 * Calculates team ELO.
 * For 1v1 matches, player1_elo is the player's ELO, and player2_elo can be the same or handled by caller.
 * For 2v2 matches, it's the average of two player ELO ratings.
 *
 * @param player1_elo - ELO rating of player 1.
 * @param player2_elo - ELO rating of player 2 (can be same as player1_elo for 1v1 if team has one player).
 * @returns Team ELO rating.
 * @throws ValueError if ELO ratings are negative.
 */
export const calculateTeamElo = (player1_elo: number, player2_elo?: number): number => {
  if (player1_elo < 0 || (player2_elo && player2_elo < 0)) {
    throw new Error("ELO ratings must be non-negative");
  }
  if (typeof player2_elo === 'number') {
    return Math.round((player1_elo + player2_elo) / 2);
  }
  return player1_elo; // For 1v1, team ELO is player's ELO
};

/**
 * Calculates win probability for Team A against Team B.
 * Formula: 1 / (1 + 10 ** ((ELO_B - ELO_A) / 400))
 *
 * @param team_a_elo - ELO rating of team A.
 * @param team_b_elo - ELO rating of team B.
 * @returns Win probability of team A (float between 0 and 1).
 * @throws ValueError if ELO ratings are negative.
 */
export const calculateWinProbability = (team_a_elo: number, team_b_elo: number): number => {
  if (team_a_elo < 0 || team_b_elo < 0) {
    throw new Error("ELO ratings must be non-negative");
  }
  const exponent = (team_b_elo - team_a_elo) / 400;
  return 1 / (1 + Math.pow(10, exponent));
};

/**
 * Determines the K factor based on player's ELO rating.
 *
 * @param player_elo - ELO rating of the player.
 * @returns K factor.
 * @throws ValueError if ELO rating is negative.
 */
export const determineKFactor = (player_elo: number): number => {
  if (player_elo < 0) {
    throw new Error("ELO rating must be non-negative");
  }
  if (player_elo < 1200) return K_TIER1;
  if (player_elo < 1800) return K_TIER2;
  return K_TIER3;
};

/**
 * Calculates individual ELO change.
 * ELO Change = K * (Result - Expected)
 * Where Result is 1 for win, 0.5 for draw (not used here), 0 for loss.
 *
 * @param player_elo - ELO rating of the player.
 * @param win_probability - Win probability of the player/team.
 * @param match_result - Match result (1 for win, 0 for loss).
 * @returns ELO change (integer).
 * @throws ValueError if inputs are invalid or out of range.
 */
export const calculateEloChange = (player_elo: number, win_probability: number, match_result: 0 | 1): number => {
  if (player_elo < 0) {
    throw new Error("ELO rating must be non-negative");
  }
  if (win_probability < 0 || win_probability > 1) {
    throw new Error("Win probability must be between 0 and 1");
  }
  if (match_result !== 0 && match_result !== 1) {
    throw new Error("Match result must be 0 (loss) or 1 (win)");
  }

  const k = determineKFactor(player_elo);
  return Math.round(k * (match_result - win_probability));
};
