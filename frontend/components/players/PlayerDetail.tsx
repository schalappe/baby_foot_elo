"use client";

import React, { useEffect, useState } from 'react';
import { getPlayerStats, PlayerStats } from '@/services/playerService';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
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
            <div className="relative w-28 h-28 sm:w-32 sm:h-32">
              {(() => {
                const winRate = player.recent?.win_rate ?? 0;
                const radius = 15.9155;
                const circumference = 2 * Math.PI * radius;

                const trackArcDegrees = 270;
                const trackArcLength = (trackArcDegrees / 360) * circumference;
                const trackGapLength = circumference - trackArcLength;

                const progressFillLength = (winRate / 100) * trackArcLength;

                const rotationAngle = 225;
                const strokeW = 4;

                return (
                  <>
                    <svg viewBox="0 0 36 36" className="absolute top-0 left-0 w-full h-full">
                      <path
                        stroke="grey"
                        d={`M18 ${18 - radius} a ${radius} ${radius} 0 0 1 0 ${2 * radius} a ${radius} ${radius} 0 0 1 0 ${-2 * radius}`}
                        fill="none"
                        strokeWidth={strokeW}
                        strokeDasharray={`${trackArcLength} ${trackGapLength}`}
                        transform={`rotate(${rotationAngle} 18 18)`}
                        strokeLinecap="round"
                      />
                      {winRate > 0 && (
                        <path
                          stroke="blue"
                          d={`M18 ${18 - radius} a ${radius} ${radius} 0 0 1 0 ${2 * radius} a ${radius} ${radius} 0 0 1 0 ${-2 * radius}`}
                          fill="none"
                          strokeWidth={strokeW}
                          strokeDasharray={`${progressFillLength} ${circumference - progressFillLength}`}
                          transform={`rotate(${rotationAngle} 18 18)`}
                          strokeLinecap="round"
                        />
                      )}
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center text-2xl sm:text-3xl font-semibold">
                      {Math.round(winRate)}%
                    </div>
                  </>
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
