// frontend/services/matchService.ts
import axios from 'axios';
import { Player } from './playerService';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface MatchPlayerInfo {
  player_id: number;
  name: string;
  elo_before_match: number;
  elo_after_match: number;
  elo_change: number;
}

export interface MatchTeamInfo {
  player1: MatchPlayerInfo;
  player2?: MatchPlayerInfo;
}

export interface Match {
  match_id: number;
  played_at: string;
  winner_team: MatchTeamInfo;
  loser_team: MatchTeamInfo;
  is_fanny: boolean;
  notes?: string;
}

export const getMatches = async (): Promise<Match[]> => {
  try {
    const response = await axios.get(`${API_URL}/matches`); 
    return response.data as Match[];
  } catch (error) {
    console.error('Error fetching matches:', error);
    return [];
  }
};

export const getMatchById = async (id: string): Promise<Match | undefined> => {
  try {
    const response = await axios.get(`${API_URL}/matches/${id}`);
    return response.data as Match;
  } catch (error) {
    console.error(`Error fetching match with ID ${id}:`, error);
    return undefined;
  }
};

export interface BackendMatchCreatePayload {
  winner_team_id: number;
  loser_team_id: number;
  is_fanny: boolean;
  played_at: string;
  notes?: string | null;
}

interface BackendTeamResponse {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
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
  elo_changes: Record<string, { old_elo: number; new_elo: number; change: number }>;
  winner_team?: BackendTeamResponse;
  loser_team?: BackendTeamResponse;
}

export const createMatch = async (matchData: BackendMatchCreatePayload): Promise<BackendMatchWithEloResponse> => {
  try {
    const response = await axios.post<BackendMatchWithEloResponse>(`${API_URL}/matches/`, matchData);
    return response.data;
  } catch (error) {
    console.error('Error creating match:', error);
    throw error;
  }
};
