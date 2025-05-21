/**
 * teamService.ts
 *
 * Provides API functions for fetching, creating, and retrieving team data from the backend.
 * Uses axios for HTTP requests. Used throughout the app for team-related data.
 *
 * Exports:
 *   - getTeamRankings: Fetch team rankings
 *   - findOrCreateTeam: Find or create a team
 *   - getTeamById: Fetch team details by ID
 *   - getTeamStatistics: Fetch team statistics
 *   - getTeamMatches: Fetch matches for a team
 */
// frontend/services/teamService.ts
import axios from 'axios';
import { Team, TeamStatistics, TeamMatchWithElo } from '@/types/team.types';

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

// Fetch team details by ID (with player details)
/**
 * Fetch detailed information about a specific team by ID, including player details.
 *
 * Calls the backend endpoint `/teams/{team_id}` and returns a Team object with nested player1 and player2.
 *
 * Parameters
 * ----------
 * teamId : number
 *     The ID of the team to fetch.
 *
 * Returns
 * -------
 * Promise<Team>
 *     The team details, including player information.
 *
 * Throws
 * ------
 * Error
 *     If the request fails or the team is not found.
 */
export const getTeamById = async (teamId: number): Promise<Team> => {
  try {
    const response = await axios.get<Team>(`${API_URL}/teams/${teamId}`);
    return response.data;
  } catch (error) {
    console.error(`Échec de la récupération de l'équipe ${teamId}:`, error);
    throw error;
  }
};

/**
 * Fetch detailed statistics for a specific team by ID.
 *
 * Calls the backend endpoint `/teams/{team_id}/statistics` and returns a TeamStatistics object.
 *
 * @param team_id - The ID of the team to fetch statistics for
 * @returns Promise<TeamStatistics> - Team statistics data
 */
export const getTeamStatistics = async (team_id: number): Promise<TeamStatistics> => {
  try {
    const response = await axios.get<TeamStatistics>(`${API_URL}/teams/${team_id}/statistics`);
    return response.data;
  } catch (error) {
    console.error(`Échec de la récupération des statistiques pour l'équipe ${team_id}:`, error);
    throw error;
  }
};

// Fetch team matches (paginated, with ELO change info)
/**
 * Fetch matches for a specific team by team ID, with pagination.
 *
 * Calls the backend endpoint `/teams/{team_id}/matches?skip=&limit=` and returns a TeamMatchWithElo[] array.
 *
 * @param teamId - The ID of the team to fetch matches for
 * @param params - Optional pagination parameters: skip (number), limit (number)
 * @returns Promise<TeamMatchWithElo[]> - Array of matches with ELO info
 */

export const getTeamMatches = async (
  teamId: number,
  params?: { skip?: number; limit?: number }
): Promise<TeamMatchWithElo[]> => {
  try {
    const response = await axios.get<TeamMatchWithElo[]>(`${API_URL}/teams/${teamId}/matches`, {
      params: {
        skip: params?.skip,
        limit: params?.limit,
      },
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch matches for team with ID ${teamId}:`, error);
    throw error;
  }
};
