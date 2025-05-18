'use client';

import React from 'react';
import Link from 'next/link';
import { Player } from '@/types/player.types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PlayerRankingTable } from './PlayerRankingTable';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from "@/components/ui/badge"
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
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2 mb-1" />
              <Skeleton className="h-4 w-1/2 mb-1" />
              <Skeleton className="h-4 w-3/4" />
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
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-5 w-24" />
                </div>
                <Skeleton className="h-5 w-12" />
                <Skeleton className="h-5 w-12" />
                <Skeleton className="h-5 w-20" />
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
            // Card color styling
            let borderColor = "border-yellow-500";
            let rankColor = "text-yellow-400";
            if (index === 1) { borderColor = "border-blue-400"; rankColor = "text-blue-400"; }
            if (index === 2) { borderColor = "border-rose-500"; rankColor = "text-rose-500"; }
            // Card scaling for 1st
            let scale = index === 0 ? "scale-105 z-10" : "";
            return (
              <Card
                key={player.player_id}
                className={`relative flex flex-col justify-between p-6 shadow-xl border-2 ${borderColor} ${scale} min-h-[300px]`}
                style={{ background: 'var(--color-podium-card)' }}
              >
                {/* Rank and Winrate Row */}
                <div className="flex justify-between items-start w-full mb-2">
                  <span className={`text-4xl font-extrabold ${rankColor} drop-shadow-sm`}>{index + 1}</span>
                  <Badge className="text-xs font-semibold px-2 py-1 rounded-lg ml-auto">{winrate}%</Badge>
                </div>
                {/* Player Name */}
                <Link href={`/players/${player.player_id}`} className="block text-center">
                  <CardTitle className={`text-lg md:text-xl font-bold ${rankColor} mb-1 truncate`}>
                    {player.name}
                  </CardTitle>
                </Link>
                {/* ELO */}
                <div className="flex flex-col items-center my-2">
                  <span className={`text-3xl md:text-4xl font-extrabold ${rankColor} tracking-wide`}>{player.global_elo} <span className={`text-lg font-medium ${rankColor}`}>ELO</span></span>
                </div>
                {/* W-L and % */}
                <div className="flex justify-center font-semibold mb-2">
                  <span style={{color: "var(--win-text)"}}>{player.wins}W</span> &nbsp; - &nbsp; <span style={{color: "var(--lose-text)"}}>{player.losses}L</span>
                </div>
                {/* Bottom Row: Matches */}
                <div className="flex justify-between items-end w-full mt-auto pt-2">
                  <div className={`text-xs ${rankColor}`}>
                    <span className={`font-bold ${rankColor}`}>{player.matches_played}</span> parties
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Other Players - List */}
      {otherPlayers.length > 0 && (
        <Card className="shadow-lg border-2 border-primary">
          <CardHeader className="bg-muted/50 border-b-2 border-primary rounded-t-md">
            <CardTitle className="text-xl font-bold tracking-tight text-primary">Autres Joueurs</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Use the paginated PlayerRankingTable for 'otherPlayers' */}
            <PlayerRankingTable data={otherPlayers} isLoading={false} error={null} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
