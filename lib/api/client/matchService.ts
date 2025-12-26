/**
 * matchService.ts
 *
 * Frontend API client for match-related operations.
 * Uses axios for HTTP requests to Next.js API routes.
 *
 * Exports:
 *   - getMatches: Fetch all matches with optional filters
 *   - createMatch: Create a new match
 */
import axios from "axios";
import {
  Match,
  BackendMatchCreatePayload,
  BackendMatchWithEloResponse,
} from "@/types/index";

// [>]: Use relative URL to call Next.js API routes (same-origin).
const API_URL = "/api/v1";

// [>]: Filter options for fetching matches.
export interface MatchFilterOptions {
  startDate?: string;
  endDate?: string;
  isFanny?: boolean;
}

/**
 * Fetches matches from the backend with optional date filtering.
 *
 * @param options - Optional filter parameters (startDate, endDate, isFanny).
 * @returns A promise that resolves to an array of Match objects.
 * @throws {Error} If the API request fails.
 */
export const getMatches = async (
  options: MatchFilterOptions = {},
): Promise<Match[]> => {
  try {
    const params = new URLSearchParams();
    if (options.startDate) params.append("start_date", options.startDate);
    if (options.endDate) params.append("end_date", options.endDate);
    if (options.isFanny !== undefined)
      params.append("is_fanny", String(options.isFanny));

    const queryString = params.toString();
    const url = queryString
      ? `${API_URL}/matches?${queryString}`
      : `${API_URL}/matches`;

    const response = await axios.get(url);
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
