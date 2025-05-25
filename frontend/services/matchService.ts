/**
 * matchService.ts
 *
 * Provides API functions for fetching, creating, and retrieving matches from the backend.
 * Uses axios for HTTP requests. Used throughout the app for match-related data.
 *
 * Exports:
 *   - getMatches: Fetch all matches
 *   - getMatchWithPlayerDetailsById: Fetch a match by ID with player details
 *   - getMatchWithTeamDetailsById: Fetch a match by ID with team details
 *   - createMatch: Create a new match
 */
// frontend/services/matchService.ts
import axios from "axios";
import {
  Match,
  BackendMatchCreatePayload,
  BackendMatchWithEloResponse,
} from "../types/index";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export const getMatches = async (): Promise<Match[]> => {
  try {
    const response = await axios.get(`${API_URL}/matches`);
    return response.data as Match[];
  } catch (error) {
    console.error("Error fetching matches:", error);
    return [];
  }
};

export const getMatchWithPlayerDetailsById = async (
  id: string,
): Promise<BackendMatchWithEloResponse | undefined> => {
  try {
    const response = await axios.get(`${API_URL}/matches/${id}/player`);
    return response.data as BackendMatchWithEloResponse;
  } catch (error) {
    console.error(`Error fetching match with ID ${id}:`, error);
    return undefined;
  }
};

export const getMatchWithTeamDetailsById = async (
  id: string,
): Promise<BackendMatchWithEloResponse | undefined> => {
  try {
    const response = await axios.get(`${API_URL}/matches/${id}/team`);
    return response.data as BackendMatchWithEloResponse;
  } catch (error) {
    console.error(`Error fetching match with ID ${id}:`, error);
    return undefined;
  }
};

export const createMatch = async (
  matchData: BackendMatchCreatePayload,
): Promise<BackendMatchWithEloResponse> => {
  try {
    const response = await axios.post<BackendMatchWithEloResponse>(
      `${API_URL}/matches/`,
      matchData,
    );
    return response.data;
  } catch (error) {
    console.error("Error creating match:", error);
    throw error;
  }
};
