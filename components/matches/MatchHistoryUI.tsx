"use client";

import React, { useMemo, useEffect } from "react";
import Link from "next/link";
import { Match, MatchPlayerInfo, MatchTeamInfo } from "@/types/match.types";
import { Player } from "@/types/player.types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../ui/card";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { Badge } from "../ui/badge";
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
        <CardHeader className="px-0">
          <CardTitle>Historique des matches</CardTitle>
          <CardDescription>
            Loading match history and player data...
          </CardDescription>
        </CardHeader>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
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

      {/* [>]: Show empty state or match table based on results. */}
      {noMatchesFound ? (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            Aucun match ne correspond aux critères de recherche.
          </CardContent>
        </Card>
      ) : (
        <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-center">Date</TableHead>
                <TableHead className="text-center">Équipe</TableHead>
                <TableHead className="text-center">VS</TableHead>
                <TableHead className="text-center">Équipe</TableHead>
                <TableHead className="text-center">Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(paginatedMatches || []).map((match) => {
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
                    <TableRow key={Math.random().toString()}>
                      <TableCell colSpan={5}>
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>Erreur de données</AlertTitle>
                          <AlertDescription>
                            Erreur de données: match invalide.
                          </AlertDescription>
                        </Alert>
                      </TableCell>
                    </TableRow>
                  );
                }
                const renderFormattedDate = (
                  dateString: string | null | undefined,
                ): string => {
                  if (!dateString) {
                    return "Date N/A";
                  }
                  const dateObj = new Date(dateString);
                  if (isNaN(dateObj.getTime())) {
                    return "Invalid Date";
                  }
                  return format(dateObj, "dd/MM/yy");
                };

                // Render a team cell with clickable team name
                const renderTeamCell = (
                  team: MatchTeamInfo,
                  isWinner: boolean,
                  isFannyLoser: boolean,
                ) => {
                  let cellClasses = "flex items-center p-2 rounded-md";
                  let icon = null;

                  if (isWinner) {
                    cellClasses += " bg-green-100 text-green-800";
                    icon = <Trophy className="h-4 w-4 mr-2 text-green-700" />;
                  } else if (isFannyLoser) {
                    cellClasses += " bg-red-100 text-red-800";
                    icon = <Skull className="h-4 w-4 mr-2 text-red-700" />;
                  }

                  const teamLink = team.team_id
                    ? `/teams/${team.team_id}`
                    : undefined;

                  return (
                    <div className={cellClasses + " w-full"}>
                      {icon}
                      {teamLink ? (
                        <Link
                          href={teamLink}
                          className="truncate overflow-hidden whitespace-nowrap w-full block hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded"
                          aria-label={`Voir la page de l'équipe ${team.player1?.name}${team.player2 ? " et " + team.player2.name : ""}`}
                        >
                          {renderPlayerName(team.player1)}
                          {team.player2 && <span className="mx-1">&</span>}
                          {team.player2 && renderPlayerName(team.player2)}
                        </Link>
                      ) : (
                        <div className="truncate overflow-hidden whitespace-nowrap w-full block">
                          {renderPlayerName(team.player1)}
                          {team.player2 && <span className="mx-1">&</span>}
                          {team.player2 && renderPlayerName(team.player2)}
                        </div>
                      )}
                      {isFannyLoser && (
                        <Badge variant="destructive" className="ml-2">
                          Fanny!
                        </Badge>
                      )}
                    </div>
                  );
                };

                let team_A_data: MatchTeamInfo;
                let team_B_data: MatchTeamInfo;
                if (match.winner_team.team_id < match.loser_team.team_id) {
                  team_A_data = match.winner_team;
                  team_B_data = match.loser_team;
                } else {
                  team_A_data = match.loser_team;
                  team_B_data = match.winner_team;
                }

                const isTeamAWinner =
                  team_A_data.team_id === match.winner_team.team_id;
                const isTeamAFannyLoser =
                  !isTeamAWinner &&
                  match.is_fanny &&
                  team_A_data.team_id === match.loser_team.team_id;
                const isTeamBWinner =
                  team_B_data.team_id === match.winner_team.team_id;
                const isTeamBFannyLoser =
                  !isTeamBWinner &&
                  match.is_fanny &&
                  team_B_data.team_id === match.loser_team.team_id;

                return (
                  <React.Fragment key={match.match_id}>
                    <TableRow>
                      <TableCell className="w-1/10 text-center">
                        {renderFormattedDate(match.played_at)}
                      </TableCell>
                      <TableCell className="w-1/4">
                        {renderTeamCell(
                          team_A_data,
                          isTeamAWinner,
                          isTeamAFannyLoser,
                        )}
                      </TableCell>
                      <TableCell className="text-center font-semibold">
                        VS
                      </TableCell>
                      <TableCell className="w-1/4">
                        {renderTeamCell(
                          team_B_data,
                          isTeamBWinner,
                          isTeamBFannyLoser,
                        )}
                      </TableCell>
                      <TableCell className="max-w-xs w-full overflow-hidden text-ellipsis text-center">
                        {match.notes?.trim() && (
                          <div className="flex items-center justify-center text-sm text-slate-600 dark:text-slate-300">
                            <MessageSquareText className="h-4 w-2 mr-2 shrink-0" />
                            <span
                              className="truncate italic"
                              title={match.notes}
                            >
                              {match.notes}
                            </span>
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                  </React.Fragment>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
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
