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

// Interface for creating a team, based on backend's TeamCreate model
export interface TeamCreatePayload {
  player1_id: number;
  player2_id: number;
  // global_elo is optional and will be calculated by backend if not provided
}

// Create a new team
export const createTeam = async (teamData: TeamCreatePayload): Promise<Team> => {
  try {
    // Ensure player1_id is less than player2_id for canonical representation
    const orderedTeamData = {
      player1_id: Math.min(teamData.player1_id, teamData.player2_id),
      player2_id: Math.max(teamData.player1_id, teamData.player2_id),
    };

    const response = await axios.post<Team>(`${API_URL}/teams/`, orderedTeamData);
    return response.data;
  } catch (error) {
    console.error('Error creating team:', error);
    if (axios.isAxiosError(error) && error.response) {
      // Re-throw with more specific error information if available
      throw new Error(error.response.data.detail || 'Failed to create team');
    }
    throw error; // Re-throw original error if not an Axios error or no response
  }
};

// Placeholder for future API functions like getTeams
