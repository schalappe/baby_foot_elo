// frontend/services/playerService.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface Player {
  player_id: number;
  name: string;
  global_elo: number;
  matches_played: number;
  wins: number;
  losses: number;
  creation_date: string;
}

export const getPlayers = async (): Promise<Player[]> => {
  try {
    const response = await axios.get(`${API_URL}/players`);
    return response.data;
  } catch (error) {
    console.error('Error fetching players:', error);
    throw error;
  }
};

export const getPlayerById = async (playerId: number): Promise<Player> => {
  try {
    const response = await axios.get(`${API_URL}/players/${playerId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching player with id ${playerId}:`, error);
    throw error;
  }
};

export const createPlayer = async (name: string): Promise<Player> => {
  try {
    const response = await axios.post(`${API_URL}/players`, { name });
    return response.data;
  } catch (error) {
    console.error('Error creating player:', error);
    throw error;
  }
};

// Fetch player rankings (sorted by Elo descending)
export const getPlayerRankings = async (): Promise<Player[]> => {
  try {
    const response = await axios.get<Player[]>(`${API_URL}/players`, {
      params: {
        sort_by: 'global_elo',
        order: 'desc',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching player rankings:', error);
    // Re-throw or handle error as needed for SWR
    throw error;
  }
};

// Add other service functions as needed (e.g., updatePlayer, deletePlayer)
