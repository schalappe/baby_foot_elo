/**
 * matches/page.tsx
 *
 * Displays a list of all matches with filtering and details for the Baby Foot ELO app.
 *
 * - Fetches matches and player data from the backend.
 * - Allows filtering by date range and other criteria.
 * - Uses ShadCN UI components for table and controls.
 *
 * Usage: Routed to '/matches' by Next.js.
 */
"use client";

import React, { useState } from "react";
import { Match } from "@/types/match.types";
import { Player } from "@/types/player.types";
import { getMatches } from "@/lib/api/client/matchService";
import { getPlayers } from "@/lib/api/client/playerService";
import { DateRange } from "react-day-picker";
import useSWR from "swr";
import MatchHistoryUI from "../../components/matches/MatchHistoryUI";

const MatchHistoryPage = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [dateRangeFilter, setDateRangeFilter] = useState<DateRange | undefined>(
    undefined,
  );
  const [selectedPlayerIdFilter, setSelectedPlayerIdFilter] = useState<
    string | undefined
  >(undefined);
  const [matchOutcomeFilter, setMatchOutcomeFilter] = useState<
    "win" | "loss" | undefined
  >(undefined);

  const {
    data: matches,
    error: matchesError,
    isLoading: matchesLoading,
  } = useSWR<Match[]>("/api/v1/matches", getMatches, {
    revalidateOnFocus: false,
    revalidateOnMount: true,
    refreshInterval: 30000, // [>]: Reduced from 5s to 30s - match history is rarely updated.
  });

  const {
    data: allPlayers,
    error: playersError,
    isLoading: playersLoading,
  } = useSWR<Player[]>("/api/v1/players", getPlayers, {
    revalidateOnFocus: false,
    revalidateOnMount: true,
    refreshInterval: 30000, // [>]: Reduced from 5s to 30s - player list is stable.
  });

  return (
    <MatchHistoryUI
      matches={matches || []}
      allPlayers={allPlayers || []}
      matchesLoading={matchesLoading}
      playersLoading={playersLoading}
      matchesError={matchesError}
      playersError={playersError}
      currentPage={currentPage}
      setCurrentPage={setCurrentPage}
      dateRangeFilter={dateRangeFilter}
      setDateRangeFilter={setDateRangeFilter}
      selectedPlayerIdFilter={selectedPlayerIdFilter}
      setSelectedPlayerIdFilter={setSelectedPlayerIdFilter}
      matchOutcomeFilter={matchOutcomeFilter}
      setMatchOutcomeFilter={setMatchOutcomeFilter}
    />
  );
};
export default MatchHistoryPage;
