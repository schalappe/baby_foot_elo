/**
 * match.types.ts
 *
 * TypeScript interfaces and types for match-related data structures.
 * Used throughout the app for type safety in API responses and UI.
 *
 * Exports:
 *   - Match, BackendMatchCreatePayload, BackendMatchWithEloResponse, etc.
 */
// frontend/types/match.types.ts

/**
 * Parameters for fetching a player's matches.
 */
export interface GetPlayerMatchesParams {
  limit?: number;
  offset?: number;
  startDate?: string;
  endDate?: string;
}

/**
 * Basic information about a player involved in a match.
 */
export interface MatchPlayerInfo {
  player_id: number;
  name: string;
  global_elo: number;
}

/**
 * Basic information about a team involved in a match, including its players.
 */
export interface MatchTeamInfo {
  team_id: number;
  global_elo: number;
  player1: MatchPlayerInfo;
  player2: MatchPlayerInfo;
}

/**
 * Detailed information about a single match, including participating teams and outcome.
 */
export interface Match {
  match_id: number;
  played_at: string;
  winner_team_id: number;
  loser_team_id: number;
  winner_team: MatchTeamInfo;
  loser_team: MatchTeamInfo;
  is_fanny: boolean;
  notes: string;
}

/**
 * Payload structure for creating a new match via the backend API.
 */
export interface BackendMatchCreatePayload {
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  played_at: string;
  notes?: string | null;
}

/**
 * Structure of a team response from the backend, often nested within match data.
 * Includes player details.
 */
export interface BackendTeamResponse {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
  player1: MatchPlayerInfo;
  player2: MatchPlayerInfo;
}

/**
 * Represents the change in Elo rating for a player or team after a match.
 */
export interface EloChange {
  old_elo: number;
  new_elo: number;
  difference: number;
}

/**
 * Structure of a match response from the backend when Elo changes are included.
 * Contains detailed information about the match, teams, and Elo adjustments.
 */
export interface BackendMatchWithEloResponse {
  match_id: number;
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  played_at: string;
  year: number;
  month: number;
  day: number;
  elo_changes:
    | { [player_id: number]: EloChange }
    | { [team_id: number]: EloChange };
  winner_team: BackendTeamResponse;
  loser_team: BackendTeamResponse;
}
