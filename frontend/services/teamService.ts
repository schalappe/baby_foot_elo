// frontend/services/teamService.ts
import axios from 'axios';
import { Team } from '../types/index';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Fetch team rankings (sorted by Elo descending).
export const getTeamRankings = async (): Promise<Team[]> => {
  try {
    const response = await axios.get<Team[]>(`${API_URL}/teams/rankings`, {
      params: {
        limit: 100,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Échec de la récupération des équipes:', error);
    throw error;
  }
};

// Function to find an existing team or create a new one.
export const findOrCreateTeam = async (player1_id: number, player2_id: number): Promise<Team> => {
  try {
    const response = await axios.post<Team>(`${API_URL}/teams/`, {
      player1_id,
      player2_id,
    });
    return response.data;
  } catch (error) {
    console.error(`Échec de la recherche ou de la création de l'équipe pour les joueurs ${player1_id} et ${player2_id}:`, error);
    throw error;
  }
};
