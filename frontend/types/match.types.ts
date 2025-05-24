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
import { Player } from './player.types';

export interface GetPlayerMatchesParams {
  limit?: number;
  offset?: number;
  startDate?: string;
  endDate?: string;
}

export interface MatchPlayerInfo {
  player_id: number;
  name: string;
  global_elo: number;
}

export interface MatchTeamInfo {
  team_id: number;
  global_elo: number;
  player1: MatchPlayerInfo;
  player2: MatchPlayerInfo;
}

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

export interface BackendMatchCreatePayload {
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  played_at: string;
  notes?: string | null;
}

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

export interface EloChange {
  old_elo: number;
  new_elo: number;
  difference: number;
}

export interface BackendMatchWithEloResponse {
  match_id: number;
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  played_at: string;
  year: number;
  month: number;
  day: number;
  elo_changes: { [player_id: number]: EloChange } | {[team_id: number]: EloChange};
  winner_team: BackendTeamResponse;
  loser_team: BackendTeamResponse;
}
