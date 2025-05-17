"use client";

import React, { useEffect, useState, useMemo } from 'react';
import { PlayerStats } from '@/types/player.types';
import { getPlayerStats, getPlayerMatches } from '@/services/playerService';
import { BackendMatchWithEloResponse } from '@/types/match.types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from "@/components/ui/skeleton";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";
import { PieChart, Pie, Label, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";

const ITEMS_PER_PAGE = 5;

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

  // Fetch player stats
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

  // Fetch player matches with pagination
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
          
          // In a real app, you would get total count from the API
          // For now, we'll just use the length of the returned array
          // and assume there are more if we got a full page
          setMatches(matchesData);
          setTotalMatches(prev => {
            // If we have a full page, there might be more
            const calculatedTotal = matchesData.length === ITEMS_PER_PAGE 
              ? currentPage * ITEMS_PER_PAGE + 1 
              : (currentPage - 1) * ITEMS_PER_PAGE + matchesData.length;
            return Math.max(prev, calculatedTotal);
          });
          setTotalPages(Math.ceil(totalMatches / ITEMS_PER_PAGE) || 1);
        } catch (err) {
          console.error('Failed to fetch matches:', err);
          // Don't show error in UI for matches to avoid hiding player data
        } finally {
          setMatchesLoading(false);
        }
      };
      fetchMatches();
    }
  }, [playerId, currentPage, totalMatches]);

  // Handle page change
  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Format match data for the table
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
    return (
      <div className="w-full max-w-4xl mx-auto p-4">
        <Skeleton className="h-10 w-1/2 mx-auto mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="bg-card shadow-lg rounded-xl overflow-hidden">
            <CardContent className="flex flex-col items-center justify-center p-6 h-[200px] space-y-3">
              <Skeleton className="h-12 w-3/4" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-6 w-1/2" />
            </CardContent>
          </Card>
          <Card className="bg-card shadow-lg rounded-xl overflow-hidden">
            <CardContent className="flex flex-col items-center justify-center p-6 h-[200px] space-y-2">
              <Skeleton className="rounded-full w-24 h-24 sm:w-28 sm:h-28" />
              <Skeleton className="h-4 w-1/3 mt-1" />
              <Skeleton className="h-6 w-1/2" />
              <Skeleton className="h-4 w-1/4" />
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="max-w-4xl mx-auto">
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!player) {
    return (
      <Alert variant="default" className="max-w-4xl mx-auto">
        <AlertTitle>Non Trouvé</AlertTitle>
        <AlertDescription>Le joueur n'a pas été trouvé.</AlertDescription>
      </Alert>
    );
  }



  return (
    <div className="w-full max-w-6xl mx-auto p-4 text-foreground space-y-8">
      <h1 className="text-4xl sm:text-5xl font-bold text-center">{player.name}</h1>
      
      {/* Player Stats Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* ELO Card */}
        <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
          <CardContent className="flex flex-col items-center justify-center p-6 h-full text-center">
            <div className="text-5xl sm:text-6xl font-bold">{player.global_elo}</div>
            <div className="text-sm text-muted-foreground mb-2">ELO GLOBAL</div>
            {player.recent && player.recent.elo_changes && player.recent.elo_changes.length > 0 ? (
              (() => {
                const lastChange = player.recent.elo_changes[0];
                return (
                  <div className={`text-lg font-medium ${lastChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {lastChange >= 0 ? '+' : ''}
                    {lastChange.toFixed(0)} ELO (dernier match)
                  </div>
                );
              })()
            ) : (
              <div className="text-lg text-muted-foreground">- ELO (dernier match)</div>
            )}
          </CardContent>
        </Card>

        {/* Win Rate Card */}
        <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
          <CardContent className="flex flex-col items-center justify-center p-6 h-full space-y-2 text-center">
            <div className="relative w-32 h-32 sm:w-36 sm:h-36"> 
              {(() => {
                const currentWinRate = player.recent?.win_rate ?? 0;

                const chartConfig = {
                  winSegment: {
                    label: 'Win Rate',
                    color: currentWinRate < 50 ? 'hsl(0 72.2% 50.6%)' : 'hsl(142.1 70.6% 45.3%)',
                  },
                  remainderSegment: {
                    label: 'Remainder',
                    color: 'hsl(var(--muted))',
                  },
                } satisfies ChartConfig;

                const chartData = [
                  { segment: 'winSegment', value: currentWinRate, fill: 'var(--color-winSegment)' },
                  { segment: 'remainderSegment', value: 100 - currentWinRate, fill: 'var(--color-remainderSegment)' },
                ];

                return (
                  <ChartContainer config={chartConfig} className="w-full h-full aspect-square">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={chartData}
                          dataKey="value"
                          nameKey="segment"
                          cx="50%"
                          cy="50%"
                          innerRadius="70%"
                          outerRadius="100%"
                          startAngle={225}
                          endAngle={-45}
                          paddingAngle={0}
                          cornerRadius={8}
                        >
                          <Label
                            value={`${Math.round(currentWinRate)}%`}
                            position="center"
                            dy={4} 
                            className="fill-foreground text-2xl sm:text-3xl font-semibold"
                          />
                        </Pie>
                      </PieChart>
                    </ResponsiveContainer>
                  </ChartContainer>
                );
              })()}
            </div>
            <div className="text-sm text-muted-foreground uppercase tracking-wider">TAUX DE VICTOIRE</div>
            <div>
              <span className="text-lg sm:text-xl font-bold text-green-500">{player.recent?.wins ?? 0}W</span>
              <span className="text-lg sm:text-xl font-bold"> - </span>
              <span className="text-lg sm:text-xl font-bold text-red-500">{player.recent?.losses ?? 0}L</span>
            </div>
            <div className="text-xs text-muted-foreground">{player.recent?.matches_played ?? 0} dernières parties</div>
          </CardContent>
        </Card>
      </div>
      
      {/* Matches Section */}
      <div className="mt-12">
        <h2 className="text-2xl font-bold mb-6">Historique des matchs</h2>
        <Card>
          <CardContent className="p-0">
            {matchesLoading ? (
              <div className="p-6 space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : matches.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">
                Aucun match trouvé pour ce joueur.
              </div>
            ) : (
              <>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Résultat</TableHead>
                      <TableHead>Équipe</TableHead>
                      <TableHead>Adversaire</TableHead>
                      <TableHead className="text-right">Δ ELO</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {formattedMatches.map((match) => (
                      <TableRow key={match.id}>
                        <TableCell className="font-medium">
                          {format(new Date(match.date), 'PPP', { locale: fr })}
                        </TableCell>
                        <TableCell>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            match.result === 'Victoire' 
                              ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' 
                              : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                          }`}>
                            {match.result}
                          </span>
                          {match.isFanny && (
                            <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300 text-xs rounded-full">
                              Fanny
                            </span>
                          )}
                        </TableCell>
                        <TableCell className="max-w-[200px] truncate">{match.playerTeam}</TableCell>
                        <TableCell className="max-w-[200px] truncate">{match.opponentTeam}</TableCell>
                        <TableCell className={`text-right font-medium ${
                          match.result === 'Victoire' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
                        }`}>
                          {match.eloChange > 0 ? '+' : ''}{match.eloChange}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
                
                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-4 py-3 border-t">
                    <div className="text-sm text-muted-foreground">
                      Affichage de <span className="font-medium">
                        {Math.min((currentPage - 1) * ITEMS_PER_PAGE + 1, totalMatches)}
                      </span> à <span className="font-medium">
                        {Math.min(currentPage * ITEMS_PER_PAGE, totalMatches)}
                      </span> sur <span className="font-medium">{totalMatches}</span> matchs
                    </div>
                    <Pagination className="m-0">
                      <PaginationContent>
                        <PaginationItem>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handlePageChange(currentPage - 1)}
                            disabled={currentPage === 1}
                          >
                            <ChevronLeft className="h-4 w-4" />
                          </Button>
                        </PaginationItem>
                        {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                          // Show first 2 pages, current page, and last 2 pages
                          let pageNum;
                          if (currentPage <= 3) {
                            pageNum = i + 1;
                          } else if (currentPage >= totalPages - 2) {
                            pageNum = totalPages - 4 + i;
                          } else {
                            pageNum = currentPage - 2 + i;
                          }
                          
                          if (pageNum < 1 || pageNum > totalPages) return null;
                          
                          return (
                            <PaginationItem key={pageNum}>
                              <PaginationLink
                                isActive={currentPage === pageNum}
                                onClick={() => handlePageChange(pageNum)}
                                className="cursor-pointer"
                              >
                                {pageNum}
                              </PaginationLink>
                            </PaginationItem>
                          );
                        })}
                        <PaginationItem>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            onClick={() => handlePageChange(currentPage + 1)}
                            disabled={currentPage === totalPages}
                          >
                            <ChevronRight className="h-4 w-4" />
                          </Button>
                        </PaginationItem>
                      </PaginationContent>
                    </Pagination>
                  </div>
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PlayerDetail;
