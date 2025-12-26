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
import axios from "axios";
import { Team, TeamStatistics, TeamMatchWithElo } from "@/types/team.types";

// [>]: Use relative URL to call Next.js API routes (same-origin).
const API_URL = "/api/v1";

/**
 * Fetches team rankings, sorted by Elo in descending order.
 *
 * @returns A promise that resolves to an array of Team objects, sorted by rank.
 * @throws {Error} If the API request fails.
 */
export const getTeamRankings = async (): Promise<Team[]> => {
  try {
    const response = await axios.get<Team[]>(`${API_URL}/teams/rankings`, {
      params: {
        limit: 100,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Échec de la récupération des équipes:", error);
    throw error;
  }
};

/**
 * Finds an existing team based on player IDs or creates a new one if it doesn't exist.
 *
 * @param player1_id - The ID of the first player in the team.
 * @param player2_id - The ID of the second player in the team.
 * @returns A promise that resolves to the found or newly created Team object.
 * @throws {Error} If the team cannot be found or created.
 */
export const findOrCreateTeam = async (
  player1_id: number,
  player2_id: number,
): Promise<Team> => {
  try {
    const response = await axios.post<Team>(`${API_URL}/teams/`, {
      player1_id,
      player2_id,
    });
    return response.data;
  } catch (error) {
    console.error(
      `Échec de la recherche ou de la création de l'équipe pour les joueurs ${player1_id} et ${player2_id}:`,
      error,
    );
    throw error;
  }
};

/**
 * Fetches detailed information about a specific team by ID, including player details.
 *
 * Calls the backend endpoint `/teams/{team_id}` and returns a Team object with nested player1 and player2.
 *
 * @param teamId - The ID of the team to fetch.
 * @returns A promise that resolves to the Team object with player details.
 * @throws {Error} If the team is not found or the request fails.
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
 * Fetches detailed statistics for a specific team by ID.
 *
 * Calls the backend endpoint `/teams/{team_id}/statistics` and returns a TeamStatistics object.
 *
 * @param team_id - The ID of the team to fetch statistics for.
 * @returns A promise that resolves to the TeamStatistics object.
 * @throws {Error} If the team statistics cannot be fetched or the request fails.
 */
export const getTeamStatistics = async (
  team_id: number,
): Promise<TeamStatistics> => {
  try {
    const response = await axios.get<TeamStatistics>(
      `${API_URL}/teams/${team_id}/statistics`,
    );
    return response.data;
  } catch (error) {
    console.error(
      `Échec de la récupération des statistiques pour l'équipe ${team_id}:`,
      error,
    );
    throw error;
  }
};

/**
 * Fetches matches for a specific team by team ID, with pagination.
 *
 * Calls the backend endpoint `/teams/{team_id}/matches?skip=&limit=` and returns a TeamMatchWithElo[] array.
 *
 * @param teamId - The ID of the team to fetch matches for.
 * @param params - Optional pagination parameters: skip (number), limit (number).
 * @returns A promise that resolves to an array of TeamMatchWithElo objects.
 * @throws {Error} If the matches cannot be fetched or the request fails.
 */
export const getTeamMatches = async (
  teamId: number,
  params?: { skip?: number; limit?: number },
): Promise<TeamMatchWithElo[]> => {
  try {
    const response = await axios.get<TeamMatchWithElo[]>(
      `${API_URL}/teams/${teamId}/matches`,
      {
        params: {
          skip: params?.skip,
          limit: params?.limit,
        },
      },
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch matches for team with ID ${teamId}:`, error);
    throw error;
  }
};
