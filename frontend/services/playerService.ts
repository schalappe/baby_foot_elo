// frontend/services/playerService.ts
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Player {
  id: number;
  name: string;
  elo: number;
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

// Add other service functions as needed (e.g., updatePlayer, deletePlayer)
