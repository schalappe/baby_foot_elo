import { Player } from './playerService';
import axios from 'axios';

// Assuming axios is configured with a base URL or proxy handles '/api/v1'
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface Team {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
  player1?: Player | null;
  player2?: Player | null;
  rank?: number | null;
}

// Fetch team rankings (sorted by Elo descending)
export const getTeamRankings = async (): Promise<Team[]> => {
  try {
    const response = await axios.get<Team[]>(`${API_URL}/teams/rankings`, {
      params: {
        limit: 100,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching team rankings:', error);
    // Re-throw or handle error as needed for SWR
    throw error;
  }
};

// Placeholder for future API functions like getTeams
