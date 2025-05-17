"use client";

import React, { useEffect, useState } from 'react';
import { getPlayerStats, PlayerStats } from '@/services/playerService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'; // Assuming table is available
import { Skeleton } from "@/components/ui/skeleton";

interface PlayerDetailProps {
  playerId: number;
}

const PlayerDetail: React.FC<PlayerDetailProps> = ({ playerId }) => {
  const [player, setPlayer] = useState<PlayerStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

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

  if (loading) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader>
          <Skeleton className="h-8 w-3/4" />
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-6 w-1/2" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-6 w-1/2" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-1/4" />
            <Skeleton className="h-6 w-1/2" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!player) {
    return (
      <Alert variant="default">
        <AlertTitle>Non Trouvé</AlertTitle>
        <AlertDescription>Le joueur n'a pas été trouvé.</AlertDescription>
      </Alert>
    );
  }

  const formatPercentage = (value: number) => {
    return Math.floor(value) + '%';
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="text-3xl font-bold text-center">{player.name}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <section>
          <h3 className="text-xl font-semibold mb-2 border-b pb-1">Statistiques</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div><strong>ELO:</strong> {player.global_elo}</div>
            <div><strong>Matchs:</strong> {player.matches_played}</div>
            <div><strong>Victoires:</strong> {player.wins}</div>
            <div><strong>Défaites:</strong> {player.losses}</div>
            <div><strong>Taux de Victoire:</strong> {formatPercentage(player.win_rate)}</div>
          </div>
        </section>

        <section>
          <h3 className="text-xl font-semibold mb-2 border-b pb-1">Historique des Matchs</h3>
          <div className="italic text-gray-500">
            L'historique des matchs sera affiché ici une fois disponible.
          </div>
          {/* Placeholder for a match history table or list */}
          {/* <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Opponent</TableHead>
                <TableHead>Result</TableHead>
                <TableHead>Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell colSpan={3} className="text-center">Aucun match joué pour le moment.</TableCell>
              </TableRow>
            </TableBody>
          </Table> */}
        </section>

      </CardContent>
    </Card>
  );
};

export default PlayerDetail;
