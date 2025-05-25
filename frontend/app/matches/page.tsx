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

import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link'; 
import { Match, MatchPlayerInfo, MatchTeamInfo } from '@/types/match.types';
import { Player } from '@/types/player.types';
import { getMatches } from '@/services/matchService';
import { getPlayers as getPlayerList } from '@/services/playerService'; 
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button'; 
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertCircle, CalendarDays, UserSearch, Trophy, Skull, MessageSquareText } from 'lucide-react'; 
import { format, startOfDay, endOfDay } from 'date-fns';
import { NewMatchDialog } from '@/components/matches/NewMatchDialog';

import { DateRange } from 'react-day-picker'; 
import { DateRangePicker } from '@/components/ui/date-range-picker';
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationPrevious, PaginationNext } from '@/components/ui/pagination';


const MatchHistoryPage = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [allPlayers, setAllPlayers] = useState<Player[]>([]); 
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRangeFilter, setDateRangeFilter] = useState<DateRange | undefined>(undefined);
  const [selectedPlayerIdFilter, setSelectedPlayerIdFilter] = useState<string | undefined>(undefined); 
  const [matchOutcomeFilter, setMatchOutcomeFilter] = useState<"win" | "loss" | undefined>(undefined);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [fetchedMatches, fetchedPlayers] = await Promise.all([
          getMatches(),
          getPlayerList()
        ]);
        setMatches(fetchedMatches);
        setAllPlayers(fetchedPlayers);
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch match history or players. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRangeFilter(range);
  };

  const handlePlayerFilterChange = (playerId: string) => {
    setSelectedPlayerIdFilter(playerId === "all" ? undefined : playerId);
  };

  const handleMatchOutcomeChange = (outcome: string) => {
    setMatchOutcomeFilter(outcome === "any" ? undefined : outcome as "win" | "loss");
  };

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const PAGE_SIZE = 30; // Number of matches per page

  const filteredMatches = useMemo(() => {
    let tempMatches = matches;

    if (dateRangeFilter && dateRangeFilter.from) {
      const fromDate = startOfDay(dateRangeFilter.from);
      const toDate = dateRangeFilter.to ? endOfDay(dateRangeFilter.to) : endOfDay(dateRangeFilter.from);
      tempMatches = tempMatches.filter(match => {
        const matchDate = new Date(match.played_at);
        return matchDate >= fromDate && matchDate <= toDate;
      });
    }

    if (selectedPlayerIdFilter) {
      const playerIdNum = parseInt(selectedPlayerIdFilter, 20);
      tempMatches = tempMatches.filter(match => {
        const teamAPlayerIds = [match.winner_team.player1.player_id, match.winner_team.player2?.player_id].filter(Boolean);
        const teamBPlayerIds = [match.loser_team.player1.player_id, match.loser_team.player2?.player_id].filter(Boolean);
        return teamAPlayerIds.includes(playerIdNum) || teamBPlayerIds.includes(playerIdNum);
      });
    }

    // Apply match outcome filter (enabled when allPlayers is fulfilled)
    if (allPlayers.length > 0 && matchOutcomeFilter) {
      const playerIdNum = selectedPlayerIdFilter ? parseInt(selectedPlayerIdFilter, 20) : null;
      tempMatches = tempMatches.filter(match => {
        if (matchOutcomeFilter === 'win') {
          return match.winner_team.player1.player_id === playerIdNum || match.winner_team.player2.player_id === playerIdNum;
        }
        if (matchOutcomeFilter === 'loss') {
          return match.loser_team.player1.player_id === playerIdNum || match.loser_team.player2.player_id === playerIdNum;
        }
        return true; // Should not reach here if outcome is win/loss
      });
    }

    return tempMatches;
  }, [matches, dateRangeFilter, selectedPlayerIdFilter, matchOutcomeFilter, allPlayers]);

  // Pagination logic
  const totalPages = Math.ceil(filteredMatches.length / PAGE_SIZE);
  const paginatedMatches = useMemo(() => {
    const startIdx = (currentPage - 1) * PAGE_SIZE;
    return filteredMatches.slice(startIdx, startIdx + PAGE_SIZE);
  }, [filteredMatches, currentPage]);

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [dateRangeFilter, selectedPlayerIdFilter, matchOutcomeFilter]);

  const renderPlayerName = (player?: MatchPlayerInfo) => {
    if (!player || typeof player.name !== 'string') {
      return <span className="text-red-500">Joueur Inconnu</span>;
    }
    return <span>{player.name}</span>;
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <CardHeader className="px-0">
          <CardTitle>Historique des matches</CardTitle>
          <CardDescription>Consultez les résultats des matches passés.</CardDescription>
        </CardHeader>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-10">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (filteredMatches.length === 0 && !loading && !error) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <CardHeader className="px-0">
          <CardTitle>Historique des matches</CardTitle>
          <CardDescription>Consultez les résultats des matches passés.</CardDescription>
        </CardHeader>
        <div className="mb-6 flex flex-col md:flex-row gap-4 justify-center items-center">
          <DateRangePicker 
            onUpdateFilter={handleDateRangeChange} 
            className="w-full md:w-auto"
          />
          <Select onValueChange={handlePlayerFilterChange} defaultValue="all">
            <SelectTrigger className="w-full md:w-[280px]">
              <UserSearch className="mr-2 h-4 w-4 text-muted-foreground" />
              <SelectValue placeholder="Filtrer par joueur..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Joueurs</SelectLabel>
                <SelectItem value="all">Tous les joueurs</SelectItem>
                {allPlayers
                  .filter(player => player && typeof player.player_id !== 'undefined' && player.name)
                  .map((player) => (
                    <SelectItem key={player.player_id} value={player.player_id.toString()}>
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
            disabled={allPlayers.length === 0}
          >
            <SelectTrigger className="w-full md:w-[280px]">
              <Trophy className="mr-2 h-4 w-4 text-muted-foreground" />
              <SelectValue placeholder="Résultat du match..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Résultat du match</SelectLabel>
                <SelectItem value="any">N'importe quel résultat</SelectItem>
                <SelectItem value="win">Victoire</SelectItem>
                <SelectItem value="loss">Défaite</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <NewMatchDialog>
            <Button variant="default" className="w-full md:w-auto">Ajouter une Partie</Button>
          </NewMatchDialog>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-10">
              <CalendarDays className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun match trouvé</h3>
              <p className="mt-1 text-sm text-gray-500">Commencez par enregistrer un nouveau match.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
      <CardHeader className="px-0 space-y-2 text-center">
        <CardTitle className="text-center">Historique des matches</CardTitle>
        <CardDescription className="text-center">Consultez les résultats des matches passés.</CardDescription>
      </CardHeader>
      <div className="mb-6 flex flex-col md:flex-row gap-4 justify-center items-center">
        <DateRangePicker 
          onUpdateFilter={handleDateRangeChange} 
          className="w-full md:w-auto"
        />
        <Select onValueChange={handlePlayerFilterChange} defaultValue="all">
          <SelectTrigger className="w-full md:w-[280px]">
            <UserSearch className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Filtrer par joueur..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Joueurs</SelectLabel>
              <SelectItem value="all">Tous les joueurs</SelectItem>
              {allPlayers
                .filter(player => player && typeof player.player_id !== 'undefined' && player.name)
                .map((player) => (
                  <SelectItem key={player.player_id} value={player.player_id.toString()}>
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
          disabled={allPlayers.length === 0}
        >
          <SelectTrigger className="w-full md:w-[280px]">
            <Trophy className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Résultat du match..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Résultat du match</SelectLabel>
              <SelectItem value="any">N'importe quel résultat</SelectItem>
              <SelectItem value="win">Victoire</SelectItem>
              <SelectItem value="loss">Défaite</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <NewMatchDialog>
          <Button variant="default" className="w-full md:w-auto">Ajouter une Partie</Button>
        </NewMatchDialog>
      </div>
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
            {paginatedMatches.map((match) => {
              if (
                !match ||
                typeof match.match_id === 'undefined' ||
                match.match_id === null ||
                !match.winner_team ||
                !match.winner_team.player1 ||
                !match.loser_team ||
                !match.loser_team.player1
              ) {
                console.error('Match object or essential winner/loser team data is invalid:', match);
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
              const renderFormattedDate = (dateString: string | null | undefined): string => {
                if (!dateString) {
                  return 'Date N/A';
                }
                const dateObj = new Date(dateString);
                if (isNaN(dateObj.getTime())) {
                  return 'Invalid Date';
                }
                return format(dateObj, 'dd/MM/yy');
              };

              // Render a team cell with clickable team name
              const renderTeamCell = (team: MatchTeamInfo, isWinner: boolean, isFannyLoser: boolean) => {
                let cellClasses = "flex items-center p-2 rounded-md";
                let icon = null;

                if (isWinner) {
                  cellClasses += " bg-green-100 text-green-800";
                  icon = <Trophy className="h-4 w-4 mr-2 text-green-700" />;
                } else if (isFannyLoser) {
                  cellClasses += " bg-red-100 text-red-800";
                  icon = <Skull className="h-4 w-4 mr-2 text-red-700" />;
                }

                const teamLink = team.team_id ? `/teams/${team.team_id}` : undefined;

                return (
                  <div className={cellClasses + " w-full"}>
                    {icon}
                    {teamLink ? (
                      <Link
                        href={teamLink}
                        className="truncate overflow-hidden whitespace-nowrap w-full block hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded"
                        aria-label={`Voir la page de l'équipe ${team.player1?.name}${team.player2 ? ' et ' + team.player2.name : ''}`}
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
                    {isFannyLoser && <Badge variant="destructive" className="ml-2">Fanny!</Badge>}
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

              const isTeamAWinner = team_A_data.team_id === match.winner_team.team_id;
              const isTeamAFannyLoser = !isTeamAWinner && match.is_fanny && team_A_data.team_id === match.loser_team.team_id;
              const isTeamBWinner = team_B_data.team_id === match.winner_team.team_id;
              const isTeamBFannyLoser = !isTeamBWinner && match.is_fanny && team_B_data.team_id === match.loser_team.team_id;

              return (
                <React.Fragment key={match.match_id}>
                  <TableRow>
                    <TableCell className="w-1/10 text-center">{renderFormattedDate(match.played_at)}</TableCell>
                    <TableCell className="w-1/4">
                      {renderTeamCell(team_A_data, isTeamAWinner, isTeamAFannyLoser)}
                    </TableCell>
                    <TableCell className="text-center font-semibold">VS</TableCell>
                    <TableCell className="w-1/4">
                      {renderTeamCell(team_B_data, isTeamBWinner, isTeamBFannyLoser)}
                    </TableCell>
                    <TableCell className="max-w-xs w-full overflow-hidden text-ellipsis text-center">
                      {match.notes?.trim() && (
                        <div className="flex items-center justify-center text-sm text-slate-600 dark:text-slate-300">
                          <MessageSquareText className="h-4 w-2 mr-2 flex-shrink-0" />
                          <span className="truncate italic" title={match.notes}>
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
    {/* Pagination Controls */}
    {totalPages > 1 && (
      <div className="flex justify-center mt-4">
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                aria-disabled={currentPage === 1}
                className={currentPage === 1 ? 'pointer-events-none opacity-50' : ''}
              />
            </PaginationItem>
            {Array.from({ length: totalPages }, (_, idx) => (
              <PaginationItem key={idx + 1}>
                <PaginationLink
                  isActive={currentPage === idx + 1}
                  onClick={() => setCurrentPage(idx + 1)}
                  href="#"
                >
                  {idx + 1}
                </PaginationLink>
              </PaginationItem>
            ))}
            <PaginationItem>
              <PaginationNext
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                aria-disabled={currentPage === totalPages}
                className={currentPage === totalPages ? 'pointer-events-none opacity-50' : ''}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      </div>
    )}
  </div>
);
}
export default MatchHistoryPage;
