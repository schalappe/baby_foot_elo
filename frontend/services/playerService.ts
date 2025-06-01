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
import { supabase} from "./supabaseClient"

const API_URL = process.env.NEXT_PUBLIC_API_URL;

/**
 * Fetches all players from the backend. Can be filtered using optional parameters.
 *
 * @param params - Optional parameters for filtering players (e.g., name, limit, offset).
 * @returns A promise that resolves to an array of Player objects.
 * @throws {Error} If the API request fails.
 */
export const getPlayers = async (params?: GetPlayersParams,): Promise<Player[]> => {
  let query = supabase.from('players').select('player_id');

  if (params?.limit) {
    query = query.limit(params.limit);
  }
  if (params?.skip) {
    query = query.range(params.skip, params.skip + (params.limit || 100) - 1);
  }

  const sortBy = params?.sort_by || 'global_elo';
  const orderBy = params?.order || 'desc';

  query = query.order(sortBy, { ascending: orderBy === 'asc' });

  const { data: playersData, error: playersError } = await query;

  if (playersError) {
    console.error("Échec de la récupération des joueurs:", playersError);
    throw playersError;
  }

  if (!playersData || playersData.length === 0) {
    return [];
  }

  // Fetch full stats for each player using the RPC function.
  const fullPlayersPromises = playersData.map(async (player: { player_id: number }) => {
    const { data: fullStats, error: statsError } = await supabase
      .rpc('get_player_full_stats', {
        p_player_id: player.player_id
      });

    if (statsError) {
      console.error(`Échec de la récupération des statistiques du joueur ${player.player_id}:`, statsError);
      throw statsError;
    }
    return fullStats;
  });

  return await Promise.all(fullPlayersPromises);
};

/**
 * Fetches a single player by their ID.
 *
 * @param playerId - The unique identifier of the player.
 * @returns A promise that resolves to a Player object.
 * @throws {Error} If the player is not found or the API request fails.
 */
export const getPlayerById = async (playerId: number): Promise<Player> => {
  let { data, error } = await supabase
    .rpc('get_player_full_stats', {
      p_player_id: playerId
    });
  if (error) {
    console.error(`Échec de la récupération du joueur avec l'ID ${playerId}:`, error);
    throw error;
  }
  return Array.isArray(data) ? data[0] : data;
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
 * @param daysSinceLastMatch - Optional parameter to filter players by days since last match.
 * @returns A promise that resolves to an array of Player objects, sorted by rank.
 * @throws {Error} If the API request fails.
 */
export const getPlayerRankings = async (daysSinceLastMatch?: number): Promise<Player[]> => {
  let query = supabase.from('players').select('player_id').limit(100).order('global_elo', { ascending: false });

  const { data: playersData, error: playersError } = await query;

  if (playersError) {
    console.error("Échec de la récupération des joueurs:", playersError);
    throw playersError;
  }

  if (!playersData || playersData.length === 0) {
    return [];
  }

  // Fetch full stats for each player using the RPC function.
  const fullPlayersPromises = playersData.map(async (player: { player_id: number }) => {
    const { data: fullStats, error: statsError } = await supabase
      .rpc('get_player_full_stats', {
        p_player_id: player.player_id
      });

    if (statsError) {
      console.error(`Échec de la récupération des statistiques du joueur ${player.player_id}:`, statsError);
      throw statsError;
    }
    return fullStats;
  });

  let rankedPlayers = await Promise.all(fullPlayersPromises);

  if (daysSinceLastMatch !== undefined && daysSinceLastMatch !== null) {
    const thresholdDate = new Date();
    thresholdDate.setDate(thresholdDate.getDate() - daysSinceLastMatch);

    rankedPlayers = rankedPlayers.filter(player => {
      if (player.last_match_at === null || player.matches_played === 0) {
        return false;
      }
      const playerLastMatchDate = new Date(player.last_match_at);
      return playerLastMatchDate > thresholdDate;
    });
  }
  return rankedPlayers;
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
