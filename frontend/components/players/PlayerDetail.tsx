"use client";

import React, { useEffect, useState } from 'react';
import { getPlayerStats, PlayerStats } from '@/services/playerService';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Skeleton } from "@/components/ui/skeleton";
import { type ChartConfig, ChartContainer } from "@/components/ui/chart";
import { PieChart, Pie, Label, ResponsiveContainer } from 'recharts';

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
    <div className="w-full max-w-4xl mx-auto p-4 text-foreground">
      <h1 className="text-4xl sm:text-5xl font-bold mb-8 text-center">{player.name}</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* ELO Card */}
        <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
          <CardContent className="flex flex-col items-center justify-center p-6 h-full text-center">
            <div className="text-5xl sm:text-6xl font-bold">{player.global_elo}</div>
            <div className="text-sm text-muted-foreground mb-2">ELO GLOBAL</div>
            {player.recent && player.recent.elo_changes && player.recent.elo_changes.length > 0 ? (
              (() => {
                const lastChange = player.recent.elo_changes[player.recent.elo_changes.length - 1];
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
                    color: currentWinRate < 50 ? 'hsl(0 72.2% 50.6%)' : 'hsl(142.1 70.6% 45.3%)', // Literal Red for win rate < 50%, Green for >= 50% 
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
    </div>
  );
};

export default PlayerDetail;
