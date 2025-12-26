/**
 * PlayerRankingsDisplay.tsx
 *
 * Displays the full player rankings page with championship-style podium and enhanced table.
 * Handles loading, error, and empty states for player ranking data.
 *
 * Exports:
 *   - PlayerRankingsDisplay: React.FC for player rankings display.
 */
"use client";

import React from "react";
import { Player } from "@/types/player.types";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { PlayerRankingTable } from "./PlayerRankingTable";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { AlertCircle, Users } from "lucide-react";
import { PodiumGrid } from "../common/PodiumGrid";

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

export function PlayerRankingsDisplay({
  players = [],
  isLoading,
  error,
}: PlayerRankingsDisplayProps) {
  if (isLoading) {
    return (
      <div className="w-full space-y-8">
        {/* Podium Skeletons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 md:items-end">
          {[...Array(3)].map((_, i) => (
            <Card
              key={i}
              className={`flex flex-col items-center p-6 min-h-[280px] md:min-h-[320px] ${i === 0 ? "md:scale-105" : ""}`}
            >
              <div className="flex justify-between w-full mb-4">
                <Skeleton className="h-14 w-14 rounded-lg" />
                <Skeleton className="h-8 w-16 rounded-full" />
              </div>
              <Skeleton className="h-8 w-3/4 mb-4" />
              <Skeleton className="h-12 w-32 mb-2" />
              <Skeleton className="h-4 w-16 mb-4" />
              <div className="w-full pt-4 border-t border-border/50">
                <Skeleton className="h-6 w-full" />
              </div>
            </Card>
          ))}
        </div>
        {/* List Skeletons */}
        <Card className="shadow-lg border-2">
          <CardHeader className="border-b">
            <Skeleton className="h-6 w-40" />
          </CardHeader>
          <CardContent className="pt-4">
            {[...Array(5)].map((_, i) => (
              <div
                key={i}
                className="flex justify-between items-center py-4 border-b last:border-b-0"
              >
                <div className="flex items-center gap-4">
                  <Skeleton className="h-8 w-8 rounded" />
                  <Skeleton className="h-5 w-28" />
                </div>
                <Skeleton className="h-5 w-16" />
                <Skeleton className="h-5 w-12" />
                <Skeleton className="h-5 w-12" />
                <Skeleton className="h-5 w-16" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="border-2">
        <AlertCircle className="h-5 w-5" />
        <AlertTitle className="font-bold">Erreur</AlertTitle>
        <AlertDescription>
          Impossible de charger le classement des joueurs: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (!players || players.length === 0) {
    return (
      <Card className="p-8 text-center border-2 border-dashed">
        <Users className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <p className="text-lg font-medium text-muted-foreground">
          Aucun joueur trouvé.
        </p>
        <p className="text-sm text-muted-foreground mt-1">
          Commencez par ajouter des joueurs pour voir le classement.
        </p>
      </Card>
    );
  }

  const topPlayers = players.slice(0, 3);
  const otherPlayers = players.slice(3);

  return (
    <div className="w-full space-y-8">
      {/* Top 3 Players - Championship Podium */}
      {topPlayers.length > 0 && (
        <PodiumGrid
          items={topPlayers}
          getKey={(player) => player.player_id}
          getLink={(player) => `/players/${player.player_id}`}
          getName={(player) => player.name}
          getElo={(player) => player.global_elo}
          getWinrate={(player) =>
            `${calculateWinrate(player.wins, player.matches_played)}%`
          }
          renderExtra={(player) => (
            <div className="flex justify-between items-center text-sm">
              <div className="flex gap-3 font-semibold">
                <span style={{ color: "var(--win-text)" }}>{player.wins}W</span>
                <span className="text-muted-foreground">-</span>
                <span style={{ color: "var(--lose-text)" }}>
                  {player.losses}L
                </span>
              </div>
              <div className="text-muted-foreground">
                <span className="font-bold text-foreground">
                  {player.matches_played}
                </span>{" "}
                parties
              </div>
            </div>
          )}
        />
      )}

      {/* Other Players - Clean List */}
      {otherPlayers.length > 0 && (
        <Card className="shadow-lg border-2 overflow-hidden">
          <CardHeader className="py-5 px-6">
            <CardTitle className="text-xl font-bold tracking-tight text-primary text-center">
              Autres Joueurs
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <PlayerRankingTable
              data={otherPlayers}
              isLoading={false}
              error={null}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
