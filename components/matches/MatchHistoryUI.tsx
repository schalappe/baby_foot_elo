"use client";

import React, { useMemo, useEffect } from "react";
import Link from "next/link";
import { Match, MatchPlayerInfo } from "@/types/match.types";
import { Player } from "@/types/player.types";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import {
  AlertCircle,
  UserSearch,
  Trophy,
  Skull,
  MessageSquareText,
  Swords,
  Calendar,
  Crown,
} from "lucide-react";
import { format } from "date-fns";
import { NewMatchDialog } from "./NewMatchDialog";

import { DateRange } from "react-day-picker";
import { DateRangePicker } from "../ui/date-range-picker";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
} from "../ui/pagination";

/**
 * Props for the MatchHistoryUI component.
 */
interface MatchHistoryUIProps {
  /**
   * Array of match data.
   */
  matches: Match[];
  /**
   * Array of all players for filtering.
   */
  allPlayers: Player[];
  /**
   * Loading state for matches.
   */
  matchesLoading: boolean;
  /**
   * Loading state for players.
   */
  playersLoading: boolean;
  /**
   * Error object for matches.
   */
  matchesError: Error | undefined;
  /**
   * Error object for players.
   */
  playersError: Error | undefined;
  /**
   * Current page number for pagination.
   */
  currentPage: number;
  /**
   * Function to set the current page.
   */
  setCurrentPage: React.Dispatch<React.SetStateAction<number>>;
  /**
   * Currently selected date range filter.
   */
  dateRangeFilter: DateRange | undefined;
  /**
   * Function to set the date range filter.
   */
  setDateRangeFilter: (range: DateRange | undefined) => void;
  /**
   * Currently selected player ID filter.
   */
  selectedPlayerIdFilter: string | undefined;
  /**
   * Function to set the player ID filter.
   */
  setSelectedPlayerIdFilter: (playerId: string | undefined) => void;
  /**
   * Currently selected match outcome filter.
   */
  matchOutcomeFilter: "win" | "loss" | undefined;
  /**
   * Function to set the match outcome filter.
   */
  setMatchOutcomeFilter: (outcome: "win" | "loss" | undefined) => void;
}

/**
 * MatchHistoryUI component displays a comprehensive match history with filtering and pagination.
 *
 * @param props - Props for the MatchHistoryUI component.
 * @param props.matches - Array of match data.
 * @param props.allPlayers - Array of all players for filtering.
 * @param props.matchesLoading - Loading state for matches.
 * @param props.playersLoading - Loading state for players.
 * @param props.matchesError - Error object for matches.
 * @param props.playersError - Error object for players.
 * @param props.currentPage - Current page number for pagination.
 * @param props.setCurrentPage - Function to set the current page.
 * @param props.dateRangeFilter - Currently selected date range filter.
 * @param props.setDateRangeFilter - Function to set the date range filter.
 * @param props.selectedPlayerIdFilter - Currently selected player ID filter.
 * @param props.setSelectedPlayerIdFilter - Function to set the player ID filter.
 * @param props.matchOutcomeFilter - Currently selected match outcome filter.
 * @param props.setMatchOutcomeFilter - Function to set the match outcome filter.
 * @returns The rendered MatchHistoryUI component.
 */
const MatchHistoryUI: React.FC<MatchHistoryUIProps> = ({
  matches,
  allPlayers,
  matchesLoading,
  playersLoading,
  matchesError,
  playersError,
  currentPage,
  setCurrentPage,
  dateRangeFilter,
  setDateRangeFilter,
  selectedPlayerIdFilter,
  setSelectedPlayerIdFilter,
  matchOutcomeFilter,
  setMatchOutcomeFilter,
}) => {
  /**
   * Handles changes to the date range filter.
   *
   * @param range - The new date range.
   */
  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRangeFilter(range);
  };

  /**
   * Handles changes to the player filter.
   *
   * @param playerId - The ID of the selected player, or "all" to clear the filter.
   */
  const handlePlayerFilterChange = (playerId: string) => {
    setSelectedPlayerIdFilter(playerId === "all" ? undefined : playerId);
    setCurrentPage(1);
  };

  /**
   * Handles changes to the match outcome filter.
   *
   * @param outcome - The selected outcome ("win", "loss", or "any").
   */
  const handleMatchOutcomeChange = (outcome: "win" | "loss" | "any") => {
    setMatchOutcomeFilter(outcome === "any" ? undefined : outcome);
    setCurrentPage(1);
  };

  // Pagination state
  const PAGE_SIZE = 30; // Number of matches per page

  /**
   * Memoized filtered matches based on player and outcome filters.
   * Date filtering is now done server-side for better scalability.
   */
  const filteredMatches = useMemo(() => {
    let tempMatches = matches || [];

    // [>]: Date filtering now happens server-side via API query params.

    if (selectedPlayerIdFilter) {
      const playerIdNum = parseInt(selectedPlayerIdFilter, 10);
      tempMatches = tempMatches.filter((match) => {
        const teamAPlayerIds = [
          match.winner_team.player1.player_id,
          match.winner_team.player2?.player_id,
        ].filter(Boolean);
        const teamBPlayerIds = [
          match.loser_team.player1.player_id,
          match.loser_team.player2?.player_id,
        ].filter(Boolean);
        return (
          teamAPlayerIds.includes(playerIdNum) ||
          teamBPlayerIds.includes(playerIdNum)
        );
      });
    }

    // [>]: Apply match outcome filter (enabled when allPlayers is fulfilled).
    if (allPlayers && allPlayers.length > 0 && matchOutcomeFilter) {
      const playerIdNum = selectedPlayerIdFilter
        ? parseInt(selectedPlayerIdFilter, 10)
        : null;
      tempMatches = tempMatches.filter((match) => {
        if (playerIdNum === null) return true;

        const isWinner =
          match.winner_team.player1.player_id === playerIdNum ||
          match.winner_team.player2?.player_id === playerIdNum;
        const isLoser =
          match.loser_team.player1.player_id === playerIdNum ||
          match.loser_team.player2?.player_id === playerIdNum;

        if (matchOutcomeFilter === "win") {
          return isWinner;
        }
        if (matchOutcomeFilter === "loss") {
          return isLoser;
        }
        return true;
      });
    }

    return tempMatches;
  }, [matches, selectedPlayerIdFilter, matchOutcomeFilter, allPlayers]);

  // Pagination logic
  const totalPages = Math.ceil((filteredMatches || []).length / PAGE_SIZE);
  /**
   * Memoized paginated matches based on filtered matches and current page.
   */
  const paginatedMatches = useMemo(() => {
    const startIdx = (currentPage - 1) * PAGE_SIZE;
    return (filteredMatches || []).slice(startIdx, startIdx + PAGE_SIZE);
  }, [filteredMatches, currentPage]);

  useEffect(() => {
    setCurrentPage(1);
  }, [
    dateRangeFilter,
    selectedPlayerIdFilter,
    matchOutcomeFilter,
    setCurrentPage,
  ]);

  /**
   * Renders the player's name, handling cases where player info might be missing.
   *
   * @param player - The player information object.
   * @returns A JSX element displaying the player's name or an "Unknown Player" message.
   */
  const renderPlayerName = (player?: MatchPlayerInfo) => {
    if (!player || typeof player.name !== "string") {
      return <span className="text-red-500">Joueur Inconnu</span>;
    }
    return <span>{player.name}</span>;
  };

  if (matchesLoading || playersLoading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <CardHeader className="px-0 text-center">
          <CardTitle>Historique des matches</CardTitle>
          <CardDescription>
            Chargement de l&apos;historique des matches...
          </CardDescription>
        </CardHeader>
        <div className="grid grid-cols-1 gap-4">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="animate-card-entrance rounded-xl border bg-card p-4"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex-1 flex items-center gap-3">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-28" />
                    <Skeleton className="h-3 w-20" />
                  </div>
                </div>
                <Skeleton className="h-8 w-12 rounded-full" />
                <div className="flex-1 flex items-center justify-end gap-3">
                  <div className="space-y-2 text-right">
                    <Skeleton className="h-4 w-28 ml-auto" />
                    <Skeleton className="h-3 w-20 ml-auto" />
                  </div>
                  <Skeleton className="h-10 w-10 rounded-full" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (matchesError || playersError) {
    return (
      <div className="container mx-auto py-10">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {matchesError?.message || playersError?.message}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  // [>]: Check if no matches found (show message but keep filter controls visible).
  const noMatchesFound =
    (filteredMatches || []).length === 0 && !matchesLoading && !playersLoading;

  return (
    <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
      <CardHeader className="px-0 space-y-2 text-center">
        <CardTitle className="text-center">Historique des matches</CardTitle>
        <CardDescription className="text-center">
          {noMatchesFound
            ? "Aucun match trouvé avec les filtres actuels."
            : "Consultez les résultats des matches passés."}
        </CardDescription>
      </CardHeader>
      <div className="mb-6 flex flex-col md:flex-row gap-4 justify-center items-center">
        <DateRangePicker
          value={dateRangeFilter}
          onUpdateFilter={handleDateRangeChange}
          className="w-full md:w-auto"
        />
        <Select
          onValueChange={handlePlayerFilterChange}
          value={selectedPlayerIdFilter || "all"}
        >
          <SelectTrigger className="w-full md:w-70">
            <UserSearch className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Filtrer par joueur..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Joueurs</SelectLabel>
              <SelectItem value="all">Tous les joueurs</SelectItem>
              {(allPlayers || [])
                .filter(
                  (player) =>
                    player &&
                    typeof player.player_id !== "undefined" &&
                    player.name,
                )
                .map((player) => (
                  <SelectItem
                    key={player.player_id}
                    value={player.player_id.toString()}
                  >
                    {player.name}
                  </SelectItem>
                ))}
            </SelectGroup>
          </SelectContent>
        </Select>

        {/* Match Outcome Filter (enabled when players are loaded) */}
        <Select
          onValueChange={handleMatchOutcomeChange}
          value={matchOutcomeFilter || "any"}
          disabled={(allPlayers || []).length === 0}
        >
          <SelectTrigger className="w-full md:w-70">
            <Trophy className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Résultat du match..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Résultat du match</SelectLabel>
              <SelectItem value="any">N&apos;importe quel résultat</SelectItem>
              <SelectItem value="win">Victoire</SelectItem>
              <SelectItem value="loss">Défaite</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <NewMatchDialog />
      </div>

      {/* [>]: Show empty state or match cards based on results. */}
      {noMatchesFound ? (
        <Card className="border-dashed">
          <CardContent className="p-12 text-center">
            <Swords className="h-12 w-12 mx-auto mb-4 text-muted-foreground/50" />
            <p className="text-muted-foreground text-lg">
              Aucun match ne correspond aux critères de recherche.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {(paginatedMatches || []).map((match, index) => {
            if (
              !match ||
              typeof match.match_id === "undefined" ||
              match.match_id === null ||
              !match.winner_team ||
              !match.winner_team.player1 ||
              !match.loser_team ||
              !match.loser_team.player1
            ) {
              console.error(
                "Match object or essential winner/loser team data is invalid:",
                match,
              );
              return (
                <Alert key={Math.random().toString()} variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertTitle>Erreur de données</AlertTitle>
                  <AlertDescription>
                    Erreur de données: match invalide.
                  </AlertDescription>
                </Alert>
              );
            }

            const renderFormattedDate = (
              dateString: string | null | undefined,
            ): string => {
              if (!dateString) return "Date N/A";
              const dateObj = new Date(dateString);
              if (isNaN(dateObj.getTime())) return "Date invalide";
              return format(dateObj, "dd MMM yyyy");
            };

            const winnerTeam = match.winner_team;
            const loserTeam = match.loser_team;
            const isFanny = match.is_fanny;

            return (
              <div
                key={match.match_id}
                className="relative bg-card border border-border rounded-xl p-4 transition-all duration-300 ease-out overflow-hidden hover:-translate-y-0.5 hover:shadow-lg hover:border-primary group animate-card-entrance"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                {/* Top gradient bar */}
                <div
                  className="absolute top-0 left-0 right-0 h-[3px] opacity-70 group-hover:opacity-100 transition-opacity"
                  style={{
                    background: `linear-gradient(90deg, var(--win) 0%, var(--win) 50%, var(--lose) 50%, var(--lose) 100%)`,
                  }}
                />

                {/* Date Badge */}
                <div className="flex items-center justify-center gap-1.5 text-xs font-medium text-muted-foreground mb-3 pb-2 border-b border-dashed border-border">
                  <Calendar className="h-3 w-3" />
                  <span>{renderFormattedDate(match.played_at)}</span>
                </div>

                {/* Battle Arena */}
                <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-3 sm:gap-4">
                  {/* Winner Side */}
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-transform duration-300 group-hover:scale-110 group-hover:-rotate-3"
                      style={{
                        background: "var(--match-win-bg)",
                        color: "var(--win)",
                        boxShadow:
                          "0 0 0 3px var(--match-win-bg), 0 0 12px var(--win)",
                      }}
                    >
                      <Crown className="h-5 w-5" />
                    </div>
                    <div className="flex flex-col gap-0.5 min-w-0 flex-1">
                      <span
                        className="text-[10px] font-semibold uppercase tracking-wide"
                        style={{ color: "var(--win)" }}
                      >
                        Vainqueur
                      </span>
                      {winnerTeam.team_id ? (
                        <Link
                          href={`/teams/${winnerTeam.team_id}`}
                          className="text-sm font-semibold text-foreground hover:underline truncate"
                          aria-label={`Voir l'équipe ${winnerTeam.player1?.name}`}
                        >
                          {renderPlayerName(winnerTeam.player1)}
                          {winnerTeam.player2 && (
                            <>
                              <span className="mx-1 opacity-50">&</span>
                              {renderPlayerName(winnerTeam.player2)}
                            </>
                          )}
                        </Link>
                      ) : (
                        <span className="text-sm font-semibold text-foreground truncate">
                          {renderPlayerName(winnerTeam.player1)}
                          {winnerTeam.player2 && (
                            <>
                              <span className="mx-1 opacity-50">&</span>
                              {renderPlayerName(winnerTeam.player2)}
                            </>
                          )}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* VS Badge */}
                  <div className="flex flex-col items-center justify-center gap-0.5 px-3 py-2 bg-muted rounded-full text-muted-foreground text-[10px] font-bold tracking-wider transition-all duration-300 group-hover:bg-primary group-hover:text-primary-foreground group-hover:scale-110">
                    <Swords className="h-4 w-4 transition-transform duration-300 group-hover:rotate-12" />
                    <span>VS</span>
                  </div>

                  {/* Loser Side */}
                  <div className="flex items-center gap-3 flex-row-reverse">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 transition-all duration-300 ${
                        isFanny ? "animate-pulse" : ""
                      }`}
                      style={{
                        background: isFanny
                          ? "var(--match-lose-bg)"
                          : "var(--muted)",
                        color: isFanny
                          ? "var(--lose)"
                          : "var(--muted-foreground)",
                        boxShadow: isFanny
                          ? "0 0 0 3px var(--match-lose-bg), 0 0 12px var(--lose)"
                          : "none",
                      }}
                    >
                      {isFanny ? (
                        <Skull className="h-5 w-5" />
                      ) : (
                        <Trophy className="h-5 w-5 opacity-40" />
                      )}
                    </div>
                    <div className="flex flex-col gap-0.5 min-w-0 flex-1 text-right">
                      <span
                        className="text-[10px] font-semibold uppercase tracking-wide"
                        style={{ color: "var(--lose)" }}
                      >
                        {isFanny ? "Fanny!" : "Défaite"}
                      </span>
                      {loserTeam.team_id ? (
                        <Link
                          href={`/teams/${loserTeam.team_id}`}
                          className="text-sm font-semibold text-foreground hover:underline truncate"
                          aria-label={`Voir l'équipe ${loserTeam.player1?.name}`}
                        >
                          {renderPlayerName(loserTeam.player1)}
                          {loserTeam.player2 && (
                            <>
                              <span className="mx-1 opacity-50">&</span>
                              {renderPlayerName(loserTeam.player2)}
                            </>
                          )}
                        </Link>
                      ) : (
                        <span className="text-sm font-semibold text-foreground truncate">
                          {renderPlayerName(loserTeam.player1)}
                          {loserTeam.player2 && (
                            <>
                              <span className="mx-1 opacity-50">&</span>
                              {renderPlayerName(loserTeam.player2)}
                            </>
                          )}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Fanny Banner */}
                {isFanny && (
                  <div
                    className="flex items-center justify-center gap-2 mt-3 py-1.5 px-3 rounded text-[11px] font-extrabold uppercase tracking-widest"
                    style={{
                      background: `linear-gradient(90deg, transparent 0%, var(--match-lose-bg) 20%, var(--match-lose-bg) 80%, transparent 100%)`,
                      color: "var(--lose)",
                    }}
                  >
                    <Skull className="h-3 w-3" />
                    <span>FANNY</span>
                    <Skull className="h-3 w-3" />
                  </div>
                )}

                {/* Notes Footer */}
                {match.notes?.trim() && (
                  <div className="flex items-center gap-2 mt-3 pt-2 border-t border-dashed border-border text-xs text-muted-foreground italic">
                    <MessageSquareText className="h-3 w-3 shrink-0" />
                    <span className="truncate" title={match.notes}>
                      {match.notes}
                    </span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination Controls */}
      {!noMatchesFound && totalPages > 1 && (
        <div className="flex justify-center mt-4">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  onClick={() =>
                    setCurrentPage((prev: number) => Math.max(1, prev - 1))
                  }
                  aria-disabled={currentPage === 1}
                  className={
                    currentPage === 1 ? "pointer-events-none opacity-50" : ""
                  }
                />
              </PaginationItem>
              {Array.from({ length: totalPages }, (_, idx) => (
                <PaginationItem key={idx + 1}>
                  <PaginationLink
                    onClick={() => setCurrentPage(idx + 1)}
                    isActive={currentPage === idx + 1}
                  >
                    {idx + 1}
                  </PaginationLink>
                </PaginationItem>
              ))}
              <PaginationItem>
                <PaginationNext
                  onClick={() =>
                    setCurrentPage((prev: number) =>
                      Math.min(totalPages, prev + 1),
                    )
                  }
                  aria-disabled={currentPage === totalPages}
                  className={
                    currentPage === totalPages
                      ? "pointer-events-none opacity-50"
                      : ""
                  }
                />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
};

export default MatchHistoryUI;
