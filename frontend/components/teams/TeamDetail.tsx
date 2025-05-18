"use client";

import React, { useState } from 'react';
import { Team, TeamStatistics } from '@/types/team.types';
import { BackendMatchWithEloResponse } from '@/types/match.types';
import TeamStatsCards from './TeamStatsCards';
import TeamMatchesSection from './TeamMatchesSection';
import TeamLoadingSkeleton from './TeamLoadingSkeleton';
import TeamErrorAlert from './TeamErrorAlert';
import { Player } from '@/types/player.types';

/**
 * TeamDetail component displays detailed information about a team.
 *
 * Uses mock data for demonstration. Replace with real data fetching logic as needed.
 *
 * Parameters
 * ----------
 * teamId : number
 *     The ID of the team to display details for.
 *
 * Returns
 * -------
 * JSX.Element
 *     The rendered team detail component.
 */
interface TeamDetailProps {
  teamId: number;
}

// Mock player data for demonstration
const mockPlayer1: Player = {
  player_id: 1,
  name: 'Alice',
  global_elo: 1450,
  matches_played: 42,
  wins: 24,
  losses: 18,
  creation_date: '2024-01-15T10:00:00Z',
};

const mockPlayer2: Player = {
  player_id: 2,
  name: 'Bob',
  global_elo: 1400,
  matches_played: 38,
  wins: 20,
  losses: 18,
  creation_date: '2024-02-02T14:30:00Z',
};

// Mock team data
const mockTeam: Team = {
  team_id: 101,
  player1_id: mockPlayer1.player_id,
  player2_id: mockPlayer2.player_id,
  global_elo: 1425,
  created_at: '2024-03-01T09:00:00Z',
  last_match_at: '2025-05-10T12:00:00Z',
  player1: mockPlayer1,
  player2: mockPlayer2,
  rank: 3,
};

// Mock team statistics
const mockTeamStats: TeamStatistics = {
  team_id: 101,
  global_elo: 1425,
  total_matches: 30,
  wins: 18,
  losses: 12,
  win_rate: 0.6,
  elo_difference: [10, -5, 15, 0, -10],
  elo_values: [1400, 1410, 1405, 1420, 1420, 1410],
  average_elo_change: 2.5,
  highest_elo: 1450,
  lowest_elo: 1380,
  created_at: '2024-03-01T09:00:00Z',
  last_match_at: '2025-05-10T12:00:00Z',
  recent: {
    matches_played: 5,
    wins: 3,
    losses: 2,
    win_rate: 0.6,
    average_elo_change: 3,
    elo_changes: [5, -2, 7, -1, 3],
  },
};

const ITEMS_PER_PAGE = 10;

/**
 * TeamDetail component displays detailed information about a team.
 *
 * Uses mock data for demonstration. Replace with real data fetching logic as needed.
 *
 * Parameters
 * ----------
 * teamId : number
 *     The ID of the team to display details for.
 *
 * Returns
 * -------
 * JSX.Element
 *     The rendered team detail component.
 */
const TeamDetail: React.FC<TeamDetailProps> = ({ teamId }) => {
  // Mock data for demonstration
  const team = mockTeam;
  const stats = mockTeamStats;
  // Mock matches data - should be replaced with real API data
  const mockMatches: BackendMatchWithEloResponse[] = [
    // Add mock matches here if needed
  ];

  // State for pagination and loading (mocked)
  const [matches, setMatches] = useState<BackendMatchWithEloResponse[]>(mockMatches);
  const [loading, setLoading] = useState<boolean>(false);
  const [matchesLoading, setMatchesLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalMatches, setTotalMatches] = useState(mockMatches.length);
  const [totalPages, setTotalPages] = useState(1);

  // Pagination handler
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  if (loading) {
    return <TeamLoadingSkeleton />;
  }

  if (error) {
    return <TeamErrorAlert error={error} />;
  }
  if (!team) {
    return <TeamErrorAlert notFound />;
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-4 text-foreground space-y-8">
      <h1 className="text-4xl sm:text-5xl font-bold text-center">
        Équipe #{team.team_id}: {team.player1?.name} & {team.player2?.name}
      </h1>
      <TeamStatsCards stats={stats} />
      <div className="mt-12 flex flex-col lg:flex-row gap-8">
        <div className="flex-1 w-full">
          <TeamMatchesSection
            matches={matches}
            teamId={teamId}
            matchesLoading={matchesLoading}
            currentPage={currentPage}
            totalPages={totalPages}
            totalMatches={totalMatches}
            handlePageChange={handlePageChange}
          />
        </div>
      </div>
    </div>
  );
};

export default TeamDetail;
