"use client";

import React, { useEffect, useState, useMemo } from 'react';
import { PlayerStats } from '@/types/player.types';
import { getPlayerStats, getPlayerMatches } from '@/services/playerService';
import { BackendMatchWithEloResponse } from '@/types/match.types';
import PlayerStatsCards from './PlayerStatsCards';
import PlayerMatchesSection from './PlayerMatchesSection';
import PlayerLoadingSkeleton from './PlayerLoadingSkeleton';
import PlayerErrorAlert from './PlayerErrorAlert';

const ITEMS_PER_PAGE = 10;

interface PlayerDetailProps {
  playerId: number;
}

const PlayerDetail: React.FC<PlayerDetailProps> = ({ playerId }) => {
  const [player, setPlayer] = useState<PlayerStats | null>(null);
  const [matches, setMatches] = useState<BackendMatchWithEloResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [matchesLoading, setMatchesLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalMatches, setTotalMatches] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  // Fetch player stats.
  useEffect(() => {
    if (playerId) {
      const fetchPlayer = async () => {
        try {
          setLoading(true);
          const data = await getPlayerStats(playerId);
          setPlayer(data);
          setError(null);
        } catch (err) {
          setError('Failed to fetch player details.');
          console.error(err);
        } finally {
          setLoading(false);
        }
      };
      fetchPlayer();
    }
  }, [playerId]);

  // Fetch player matches with pagination.
  useEffect(() => {
    if (playerId) {
      const fetchMatches = async () => {
        try {
          setMatchesLoading(true);
          const offset = (currentPage - 1) * ITEMS_PER_PAGE;
          const matchesData = await getPlayerMatches(playerId, { 
            limit: ITEMS_PER_PAGE, 
            offset 
          });
          
          setMatches(matchesData);
          setTotalMatches(prev => {
            const calculatedTotal = matchesData.length === ITEMS_PER_PAGE 
              ? currentPage * ITEMS_PER_PAGE + 1 
              : (currentPage - 1) * ITEMS_PER_PAGE + matchesData.length;
            return Math.max(prev, calculatedTotal);
          });
          setTotalPages(Math.ceil(totalMatches / ITEMS_PER_PAGE) || 1);
        } catch (err) {
          console.error('Failed to fetch matches:', err);
        } finally {
          setMatchesLoading(false);
        }
      };
      fetchMatches();
    }
  }, [playerId, currentPage, totalMatches]);

  // Handle page change.
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Format match data for the table.
  const formattedMatches = useMemo(() => {
    return matches.map(match => {
      const isWinner = match.winner_team.player1.player_id === playerId || 
                      match.winner_team.player2.player_id === playerId;
      
      const opponentTeam = isWinner ? match.loser_team : match.winner_team;
      const opponentNames = [
        opponentTeam.player1.name,
        opponentTeam.player2.name
      ].filter(Boolean).join(' & ');
      
      const playerTeam = isWinner ? match.winner_team : match.loser_team;
      const playerNames = [
        playerTeam.player1.name,
        playerTeam.player2.name
      ].filter(Boolean).join(' & ');

      return {
        id: match.match_id,
        date: match.played_at,
        result: isWinner ? 'Victoire' : 'Défaite',
        playerTeam: playerNames,
        opponentTeam: opponentNames,
        eloChange: match.elo_changes[playerId].difference,
        isFanny: match.is_fanny,
      };
    });
  }, [matches, playerId]);

  if (loading) {
    return <PlayerLoadingSkeleton />;
  }

  if (error) {
    return <PlayerErrorAlert error={error} />;
  }
  if (!player) {
    return <PlayerErrorAlert notFound />;
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-4 text-foreground space-y-8">
      <h1 className="text-4xl sm:text-5xl font-bold text-center">{player.name}</h1>
      <PlayerStatsCards player={player} />
      <div className="mt-12 flex flex-col lg:flex-row gap-8">
        <div className="flex-1 w-full">
          <PlayerMatchesSection
            matches={matches}
            playerId={playerId}
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
}

export default PlayerDetail;
