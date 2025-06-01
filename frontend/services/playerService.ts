/**
 * playerService.ts
 *
 * Provides API functions for fetching, creating, and retrieving player data from the backend.
 * Uses axios for HTTP requests. Used throughout the app for player-related data.
 *
 * Exports:
 *   - getPlayers: Fetch all players (with optional filters)
 *   - getPlayerById: Fetch a player by ID
 *   - createPlayer: Create a new player
 *   - getPlayerRankings: Fetch player rankings
 *   - getPlayerStats: Fetch player statistics
 *   - getPlayerMatches: Fetch matches for a player
 */
// frontend/services/playerService.ts
import axios from "axios";
import { Player, PlayerStats, GetPlayersParams } from "../types/index";
import {BackendMatchWithEloResponse, GetPlayerMatchesParams} from "../types/match.types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

/**
 * Fetches all players from the backend. Can be filtered using optional parameters.
 *
 * @param params - Optional parameters for filtering players (e.g., name, limit, offset).
 * @returns A promise that resolves to an array of Player objects.
 * @throws {Error} If the API request fails.
 */
export const getPlayers = async (
  params?: GetPlayersParams,
): Promise<Player[]> => {
  try {
    let url = `${API_URL}/players`;

    if (params && Object.keys(params).length > 0) {
      const queryParams = new URLSearchParams(
        params as Record<string, string>,
      ).toString();
      url += `?${queryParams}`;
    }

    const response = await axios.get(url);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Fetches a single player by their ID.
 *
 * @param playerId - The unique identifier of the player.
 * @returns A promise that resolves to a Player object.
 * @throws {Error} If the player is not found or the API request fails.
 */
export const getPlayerById = async (playerId: number): Promise<Player> => {
  try {
    const response = await axios.get(`${API_URL}/players/${playerId}`);
    return response.data;
  } catch (error) {
    console.error(
      `Échec de la récupération du joueur avec l'ID ${playerId}:`,
      error,
    );
    throw error;
  }
};

/**
 * Creates a new player with the given name.
 *
 * @param name - The name of the player to create.
 * @returns A promise that resolves to the newly created Player object.
 * @throws {Error} If the player creation fails.
 */
export const createPlayer = async (name: string): Promise<Player> => {
  try {
    const response = await axios.post(`${API_URL}/players`, { name });
    return response.data;
  } catch (error) {
    console.error("Échec de la création du joueur:", error);
    throw error;
  }
};

/**
 * Fetches a list of players ordered by their global ELO ranking.
 *
 * @returns A promise that resolves to an array of Player objects, sorted by rank.
 * @throws {Error} If the API request fails.
 */
export const getPlayerRankings = async (): Promise<Player[]> => {
  try {
    const response = await axios.get<Player[]>(`${API_URL}/players/rankings`, {
      params: {
        limit: 100,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Échec de la récupération des joueurs:", error);
    throw error;
  }
};

/**
 * Fetches detailed statistics for a specific player.
 *
 * @param playerId - The unique identifier of the player.
 * @returns A promise that resolves to a PlayerStats object.
 * @throws {Error} If the player statistics are not found or the API request fails.
 */
export const getPlayerStats = async (
  playerId: number,
): Promise<PlayerStats> => {
  try {
    const response = await axios.get<PlayerStats>(
      `${API_URL}/players/${playerId}/statistics`,
      );
    return response.data;
  } catch (error) {
    console.error(
      `Échec de la récupération des statistiques du joueur avec l'ID ${playerId}:`,
      error,
    );
    throw error;
  }
};

/**
 * Fetches a list of matches played by a specific player.
 *
 * @param playerId - The unique identifier of the player.
 * @param params - Optional parameters for filtering matches (e.g., limit, offset, date range).
 * @returns A promise that resolves to an array of BackendMatchWithEloResponse objects.
 * @throws {Error} If the API request fails.
 */
export const getPlayerMatches = async (
  playerId: number,
  params?: GetPlayerMatchesParams,
): Promise<BackendMatchWithEloResponse[]> => {
  try {
    const response = await axios.get<BackendMatchWithEloResponse[]>(
      `${API_URL}/players/${playerId}/matches`,
      {
        params: {
          limit: params?.limit,
          offset: params?.offset,
          start_date: params?.startDate,
          end_date: params?.endDate,
        },
      },
    );
    return response.data;
  } catch (error) {
    console.error(
      `Failed to fetch matches for player with ID ${playerId}:`,
      error,
    );
    throw error;
  }
};
