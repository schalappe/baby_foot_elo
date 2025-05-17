// frontend/services/playerService.ts
import axios, { AxiosRequestConfig } from 'axios';

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

export interface PlayerStats {
  player_id: number;
  name: string;
  global_elo: number;
  matches_played: number;
  wins: number;
  losses: number;
  creation_date: string;
  win_rate: number;
  elo_difference: number[];
  elo_values: number[];
  average_elo_change: number;
  highest_elo: number;
  lowest_elo: number;
  recent: {
    matches_played: number;
    wins: number;
    losses: number;
    win_rate: number;
    average_elo_change: number;
    elo_changes: number[];
  };
}

export interface GetPlayersParams {
  limit?: number;
  skip?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export const getPlayers = async (params?: GetPlayersParams): Promise<Player[]> => {
  try {

    let url = `${API_URL}/players`;

    if (params && Object.keys(params).length > 0) {
      const queryParams = new URLSearchParams(params as Record<string, string>).toString();
      url += `?${queryParams}`;
    }

    const response = await axios.get(url);
    return response.data;

  } catch (error) {
    throw error;
  }
};

export const getPlayerById = async (playerId: number): Promise<Player> => {
  try {
    const response = await axios.get(`${API_URL}/players/${playerId}`);
    return response.data;
  } catch (error) {
    console.error(`Échec de la récupération du joueur avec l'ID ${playerId}:`, error);
    throw error;
  }
};

export const createPlayer = async (name: string): Promise<Player> => {
  try {
    const response = await axios.post(`${API_URL}/players`, { name });
    return response.data;
  } catch (error) {
    console.error('Échec de la création du joueur:', error);
    throw error;
  }
};


export const getPlayerRankings = async (): Promise<Player[]> => {
  try {
    const response = await axios.get<Player[]>(`${API_URL}/players/rankings`, {
      params: {
        limit: 100,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Échec de la récupération des joueurs:', error);
    throw error;
  }
};

export const getPlayerStats = async (playerId: number): Promise<PlayerStats> => {
  try {
    const response = await axios.get<PlayerStats>(`${API_URL}/players/${playerId}/statistics`);
    return response.data;
  } catch (error) {
    console.error(`Échec de la récupération des statistiques du joueur avec l'ID ${playerId}:`, error);
    throw error;
  }
};

// Add other service functions as needed (e.g., updatePlayer, deletePlayer)
