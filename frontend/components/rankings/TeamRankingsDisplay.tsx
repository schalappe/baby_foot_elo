'use client';

import React from 'react';
import Link from 'next/link'; // Added Link import
import { Team } from '@/types/team.types'; // Assuming Team interface is in teamService
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TeamRankingTable } from './TeamRankingTable';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from "@/components/ui/badge"
import { AlertCircle, Users } from 'lucide-react'; // Added Users icon for teams

interface TeamRankingsDisplayProps {
  teams: Team[];
  isLoading: boolean;
  error: Error | null;
}

const getTeamName = (team: Team): string => {
  const p1Name = team.player1?.name || `Joueur ID ${team.player1_id}`;
  const p2Name = team.player2?.name || `Joueur ID ${team.player2_id}`;
  return [p1Name, p2Name].sort().join(' & ');
};

export function TeamRankingsDisplay({ teams = [], isLoading, error }: TeamRankingsDisplayProps) {
  if (isLoading) {
    return (
      <div className="w-full space-y-8">
        {/* Podium Skeletons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="flex flex-col items-center p-6">
              <Skeleton className="h-12 w-12 rounded-full mb-4" />
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2" />
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
                  <Skeleton className="h-5 w-32" />
                </div>
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
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>
          Impossible de charger le classement des équipes: {error.message}
        </AlertDescription>
      </Alert>
    );
  }

  if (!teams || teams.length === 0) {
    return <p>Aucune équipe trouvée.</p>;
  }

  const topTeams = teams.slice(0, 3);
  const otherTeams = teams.slice(3);

  return (
    <div className="w-full space-y-8">
      {/* Top 3 Teams - Podium */}
      {topTeams.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {topTeams.map((team, index) => {
            // Card color styling
            let borderColor = "border-yellow-500";
            let rankColor = "text-yellow-400";
            if (index === 1) { borderColor = "border-blue-400"; rankColor = "text-blue-400"; }
            if (index === 2) { borderColor = "border-rose-500"; rankColor = "text-rose-500"; }
            let scale = index === 0 ? "scale-105 z-10" : "";
            // Winrate calculation
            const matchesPlayed = team.matches_played ?? (team.wins + team.losses);
            const winrate = matchesPlayed > 0 ? Math.round((team.wins / matchesPlayed) * 100) : 0;
            return (
              <Card
                key={team.team_id}
                className={`relative flex flex-col justify-between p-6 shadow-xl border-2 ${borderColor} ${scale} min-h-[300px]`}
                style={{ background: 'var(--color-podium-card)' }}
              >
                {/* Rank and Winrate Row */}
                <div className="flex justify-between items-start w-full mb-2">
                  <span className={`text-4xl font-extrabold ${rankColor} drop-shadow-sm`}>{index + 1}</span>
                  <Badge className="text-xs font-semibold px-2 py-1 rounded-lg ml-auto">{winrate}%</Badge>
                </div>
                {/* Team Name */}
                <Link href={`/teams/${team.team_id}`} className="block text-center">
                  <CardTitle className={`text-lg md:text-xl font-bold ${rankColor} mb-1 truncate`}>
                    {getTeamName(team)}
                  </CardTitle>
                </Link>
                {/* ELO */}
                <div className="flex flex-col items-center my-2">
                  <span className={`text-3xl md:text-4xl font-extrabold ${rankColor} tracking-wide`}>{Math.round(team.global_elo)} <span className={`text-lg font-medium ${rankColor}`}>ELO</span></span>
                </div>
                {/* W-L and % */}
                <div className="flex justify-center font-semibold mb-2">
                  <span style={{color: "var(--win-text)"}}>{team.wins}W</span> &nbsp; - &nbsp; <span style={{color: "var(--lose-text)"}}>{team.losses}L</span>
                </div>
                {/* Bottom Row: Matches */}
                <div className="flex justify-between items-end w-full mt-auto pt-2">
                  <div className={`text-xs ${rankColor}`}>
                    <span className={`font-bold ${rankColor}`}>{matchesPlayed}</span> parties
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Other Teams - List */}
      {otherTeams.length > 0 && (
        <Card className="shadow-lg border-2">
          <CardHeader className="border-b-2 rounded-t-md">
            <CardTitle className="text-xl font-bold tracking-tight text-primary">Autres Équipes</CardTitle>
          </CardHeader>
          <CardContent>
            <TeamRankingTable data={otherTeams} isLoading={false} error={null} />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
