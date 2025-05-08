// frontend/services/playerService.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface Player {
  id: number;
  name: string;
  elo: number; // From PlayersList
  matches_played: number; // From PlayersList
  wins: number; // From PlayersList
  losses: number; // From PlayersList
  creation_date: string; // Added to match backend model
  // Add other player attributes here as defined by the backend
  // For example:
  // games_played: number; // This seems to be an older name for matches_played
  // created_at: string;
  // updated_at: string;
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

export const registerPlayer = async (playerName: string, initialElo?: number): Promise<Player> => {
  try {
    const payload: { name: string; initial_elo?: number } = { name: playerName };
    if (initialElo !== undefined) {
      payload.initial_elo = initialElo;
    }
    console.log(payload);
    const response = await axios.post(`${API_URL}/players`, payload);
    return response.data;
  } catch (error) {
    console.error('Error registering player:', error);
    throw error;
  }
};

// Add other service functions as needed (e.g., updatePlayer, deletePlayer)
