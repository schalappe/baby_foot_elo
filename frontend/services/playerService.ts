// frontend/services/playerService.ts
import axios from 'axios';
import { Player, PlayerStats, GetPlayersParams } from '../types/index';
import { BackendMatchWithEloResponse, GetPlayerMatchesParams } from '../types/match.types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

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

export const getPlayerMatches = async (playerId: number, params?: GetPlayerMatchesParams): Promise<BackendMatchWithEloResponse[]> => {
  try {
    const response = await axios.get<BackendMatchWithEloResponse[]>(`${API_URL}/players/${playerId}/matches`, {
      params: {
        limit: params?.limit,
        offset: params?.offset,
        start_date: params?.startDate,
        end_date: params?.endDate,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch matches for player with ID ${playerId}:`, error);
    throw error;
  }
};
