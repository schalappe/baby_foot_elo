/**
 * matchService.ts
 *
 * Provides API functions for fetching, creating, and retrieving matches from the backend.
 * Uses axios for HTTP requests. Used throughout the app for match-related data.
 *
 * Exports:
 *   - getMatches: Fetch all matches
 *   - createMatch: Create a new match
 */
// frontend/services/matchService.ts
import axios from "axios";
import {
  Match,
  BackendMatchCreatePayload,
  BackendMatchWithEloResponse,
} from "../types/index";

// [>]: Use relative URL to call Next.js API routes (same-origin).
const API_URL = "/api/v1";

/**
 * Fetches all matches from the backend.
 *
 * @returns A promise that resolves to an array of Match objects.
 * @throws {Error} If the API request fails.
 */
export const getMatches = async (): Promise<Match[]> => {
  try {
    const response = await axios.get(`${API_URL}/matches`);
    return response.data as Match[];
  } catch (error) {
    console.error("Error fetching matches:", error);
    return [];
  }
};

/**
 * Creates a new match with the provided data.
 *
 * @param matchData - The data for the match to be created.
 * @returns A promise that resolves to the newly created BackendMatchWithEloResponse object.
 * @throws {Error} If the match creation fails.
 */
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
