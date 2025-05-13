'use client';

import React from 'react';
import Link from 'next/link';
import { Player } from '@/services/playerService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';

interface PlayerRankingsDisplayProps {
  players: Player[];
  isLoading: boolean;
  error: Error | null;
}

const calculateWinrate = (wins: number, matchesPlayed: number): number => {
  if (matchesPlayed === 0) {
    return 0;
  }
  return Math.round((wins / matchesPlayed) * 100);
};

export function PlayerRankingsDisplay({ players = [], isLoading, error }: PlayerRankingsDisplayProps) {
  if (isLoading) {
    return (
      <div className="w-full space-y-8">
        {/* Podium Skeletons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="flex flex-col items-center p-6">
              <Skeleton className="h-12 w-12 rounded-full mb-4" />
              <Skeleton className="h-6 w-3/4 mb-2" /> {/* Name */}
              <Skeleton className="h-4 w-1/2 mb-1" /> {/* Elo */}
              <Skeleton className="h-4 w-1/2 mb-1" /> {/* Matches */}
              <Skeleton className="h-4 w-3/4" />      {/* W-L (Winrate) */}
            </Card>
          ))}
        </div>
        {/* List Skeletons */}
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-1/4" />
          </CardHeader>
          <CardContent>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex justify-between items-center py-3 border-b last:border-b-0">
                <div className="flex items-center gap-4">
                  <Skeleton className="h-8 w-8" />   {/* Rank */}
                  <Skeleton className="h-5 w-24" />  {/* Name */}
                </div>
                <Skeleton className="h-5 w-12" /> {/* Elo */}
                <Skeleton className="h-5 w-12" /> {/* Matches */}
                <Skeleton className="h-5 w-20" /> {/* W-L (Winrate) */}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>
          Impossible de charger le classement des joueurs: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (!players || players.length === 0) {
    return <p>Aucun joueur trouvé.</p>;
  }

  const topPlayers = players.slice(0, 3);
  const otherPlayers = players.slice(3);

  return (
    <div className="w-full space-y-8">
      {/* Top 3 Players - Podium */}
      {topPlayers.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {topPlayers.map((player, index) => {
            const winrate = calculateWinrate(player.wins, player.matches_played);
            let cardClasses = "flex flex-col items-center p-6 shadow-lg border-2"; // Common classes
            if (index === 0) {
              cardClasses += " border-yellow-500 scale-105"; // Gold
            } else if (index === 1) {
              cardClasses += " border-slate-400"; // Silver
            } else if (index === 2) {
              cardClasses += " border-orange-500"; // Bronze (using orange for a bronze hue)
            }
            console.log(player.player_id);

            return (
              <Card key={player.player_id} className={cardClasses}>
                <div className="text-3xl font-bold text-primary mb-3">#{index + 1}</div>
                <Link href={`/players/${player.player_id}`} className='text-center hover:underline focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-sm'>
                  <CardTitle className="text-xl font-semibold mb-1">
                    {player.name}
                  </CardTitle>
                </Link>
                <p className="text-lg text-muted-foreground">{player.global_elo}</p> {/* Reverted to player.global_elo */}
                <p className="text-sm text-muted-foreground">Matchs: {player.matches_played}</p>
                <p className="text-sm font-medium text-muted-foreground">
                  {player.wins}W - {player.losses}L ({winrate}%)
                </p>
              </Card>
            );
          })}
        </div>
      )}

      {/* Other Players - List */}
      {otherPlayers.length > 0 && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl">Autres Joueurs</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Rang</TableHead>
                  <TableHead>Nom</TableHead>
                  <TableHead className="text-right">ELO</TableHead>
                  <TableHead className="text-right">Matchs Joués</TableHead>
                  <TableHead className="text-right">Performance</TableHead> 
                </TableRow>
              </TableHeader>
              <TableBody>
                {otherPlayers.map((player, index) => {
                  const winrate = calculateWinrate(player.wins, player.matches_played);
                  return (
                    <TableRow key={player.player_id}>
                      <TableCell className="font-medium">#{index + 4}</TableCell>
                      <TableCell>
                        <Link href={`/players/${player.player_id}`} className='hover:underline focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-sm'>
                          {player.name}
                        </Link>
                      </TableCell>
                      <TableCell className="text-right">{player.global_elo}</TableCell> {/* Reverted to player.global_elo */}
                      <TableCell className="text-right">{player.matches_played}</TableCell>
                      <TableCell className="text-right">
                        {player.wins}W - {player.losses}L ({winrate}%)
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
