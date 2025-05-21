/**
 * PlayerDetail.tsx
 *
 * Displays the detailed view for a single player, including stats and matches.
 * Fetches player data and renders PlayerStatsCards and PlayerMatchesSection.
 * Handles loading and error states.
 *
 * Exports:
 *   - PlayerDetail: React.FC for player detail view.
 */
"use client";

import React, { useEffect, useState } from "react";
import { PlayerStats } from "@/types/player.types";
import { getPlayerStats, getPlayerMatches } from "@/services/playerService";
import { BackendMatchWithEloResponse } from "@/types/match.types";
import PlayerStatsCards from "./PlayerStatsCards";
import PlayerMatchesSection from "./PlayerMatchesSection";
import PlayerLoadingSkeleton from "./PlayerLoadingSkeleton";
import PlayerErrorAlert from "./PlayerErrorAlert";

const ITEMS_PER_PAGE = 10;

/**
 * Props for PlayerDetail component.
 * @property playerId - The ID of the player to display
 */
interface PlayerDetailProps {
  playerId: number;
}

/**
 * Displays the detailed view for a single player, including stats and matches.
 * Handles data fetching, loading, and error states.
 *
 * @param playerId - The ID of the player to display
 * @returns The rendered player detail view
 */
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
          setError("Failed to fetch player details.");
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
            offset,
          });

          setMatches(matchesData);
          setTotalMatches((prev) => {
            const calculatedTotal =
              matchesData.length === ITEMS_PER_PAGE
                ? currentPage * ITEMS_PER_PAGE + 1
                : (currentPage - 1) * ITEMS_PER_PAGE + matchesData.length;
            return Math.max(prev, calculatedTotal);
          });
          setTotalPages(Math.ceil(totalMatches / ITEMS_PER_PAGE) || 1);
        } catch (err) {
          console.error("Failed to fetch matches:", err);
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
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

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
      <h1 className="text-4xl sm:text-5xl font-bold text-center">
        {player.name}
      </h1>
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
};

export default PlayerDetail;
