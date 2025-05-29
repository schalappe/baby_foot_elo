/**
 * PlayerRankingsDisplay.tsx
 *
 * Displays the full player rankings page, including podium and table.
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
import { AlertCircle } from "lucide-react";
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
              <div
                key={i}
                className="flex justify-between items-center py-3 border-b last:border-b-0"
              >
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
            <>
              {/* W-L and % */}
              <div className="flex justify-center font-semibold mb-2">
                <span style={{ color: "var(--win-text)" }}>{player.wins}W</span>{" "}
                &nbsp; - &nbsp;{" "}
                <span style={{ color: "var(--lose-text)" }}>
                  {player.losses}L
                </span>
              </div>
              {/* Bottom Row: Matches */}
              <div className="flex justify-between items-end w-full mt-auto pt-2">
                <div className={`text-xs`}>
                  <span className={`font-bold`}>{player.matches_played}</span>{" "}
                  parties
                </div>
              </div>
            </>
          )}
        />
      )}

      {/* Other Players - List */}
      {otherPlayers.length > 0 && (
        <Card className="shadow-lg border-2">
          <CardHeader className="border-b-2 rounded-t-md">
            <CardTitle className="text-xl font-bold tracking-tight text-primary">
              Autres Joueurs
            </CardTitle>
          </CardHeader>
          <CardContent>
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
