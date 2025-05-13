// frontend/services/matchService.ts
import axios from 'axios';
import { Player } from './playerService'; // Assuming Player interface is exported from playerService

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export interface MatchPlayerInfo {
  id: number;
  name: string;
  elo_before_match: number;
  elo_after_match: number;
  elo_change: number;
}

export interface MatchTeamInfo {
  player1: MatchPlayerInfo;
  player2?: MatchPlayerInfo;
  // score: number; // Score might be part of match details if available, not part of team info directly in this context
}

export interface Match {
  id: number;
  match_date: string; // ISO string
  team_a: MatchTeamInfo;
  team_b: MatchTeamInfo;
  team_a_score: number; // Added team A score
  team_b_score: number; // Added team B score
  winning_team_id: 'A' | 'B' | null; // Or actual team ID if backend provides it like that. For now, A or B for simplicity of frontend logic.
  is_fanny: boolean;
  notes?: string;
  // Individual ELO changes are now part of MatchPlayerInfo
}

const MOCK_MATCHES: Match[] = [
  {
    id: 1,
    match_date: new Date(Date.now() - 86400000).toISOString(), // Yesterday
    team_a: {
      player1: { id: 1, name: 'Player Alice', elo_before_match: 1500, elo_after_match: 1520, elo_change: 20 },
      player2: { id: 2, name: 'Player Bob', elo_before_match: 1400, elo_after_match: 1415, elo_change: 15 },
    },
    team_b: {
      player1: { id: 3, name: 'Player Charlie', elo_before_match: 1600, elo_after_match: 1580, elo_change: -20 },
    },
    team_a_score: 10, // Mock score
    team_b_score: 5,  // Mock score
    winning_team_id: 'A',
    is_fanny: false,
    notes: 'Close game!',
  },
  {
    id: 2,
    match_date: new Date(Date.now() - 172800000).toISOString(), // Two days ago
    team_a: {
      player1: { id: 4, name: 'Player Dave', elo_before_match: 1300, elo_after_match: 1280, elo_change: -20 },
    },
    team_b: {
      player1: { id: 1, name: 'Player Alice', elo_before_match: 1520, elo_after_match: 1545, elo_change: 25 },
      player2: { id: 5, name: 'Player Eve', elo_before_match: 1450, elo_after_match: 1475, elo_change: 25 },
    },
    team_a_score: 3,  // Mock score
    team_b_score: 10, // Mock score
    winning_team_id: 'B',
    is_fanny: false,
  },
  {
    id: 3,
    match_date: new Date(Date.now() - 259200000).toISOString(), // Three days ago
    team_a: {
      player1: { id: 2, name: 'Player Bob', elo_before_match: 1415, elo_after_match: 1415, elo_change: 0 },
    },
    team_b: {
      player1: { id: 3, name: 'Player Charlie', elo_before_match: 1580, elo_after_match: 1580, elo_change: 0 },
    },
    team_a_score: 7, // Mock score
    team_b_score: 7, // Mock score
    winning_team_id: null, // Draw
    is_fanny: false,
    notes: 'A very tight draw.',
  }
];

export const getMatches = async (): Promise<Match[]> => {
  try {
    // TODO: Update this endpoint when the backend provides it
    // For now, this will likely fail or return an empty array if the endpoint doesn't exist.
    const response = await axios.get(`${API_URL}/matches`); 
    return response.data as Match[]; // Add proper validation/transformation if backend structure differs
  } catch (error) {
    console.error('Error fetching matches:', error);
    // For development, return mock data if API is not ready
    // throw error; 
    console.warn('API for getMatches not ready, returning mock data.');
    return MOCK_MATCHES; // Use mock data array
  }
};

// New function to get a single match by ID
export const getMatchById = async (id: string): Promise<Match | undefined> => {
  try {
    // TODO: Update this endpoint when the backend provides it
    const response = await axios.get(`${API_URL}/matches/${id}`);
    return response.data as Match;
  } catch (error) {
    console.error(`Error fetching match with ID ${id}:`, error);
    // For development, find in mock data
    console.warn(`API for getMatchById not ready, finding match with ID ${id} in mock data.`);
    return MOCK_MATCHES.find(match => match.id.toString() === id);
  }
};
