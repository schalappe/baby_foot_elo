'use client';

import React from 'react';
import Link from 'next/link'; // Added Link import
import { Team } from '@/services/teamService'; // Assuming Team interface is in teamService
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
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

  // Assuming teams are pre-sorted by rank or ELO. If not, sort here.
  // For now, we'll use the order from the API and assign rank based on index.
  const topTeams = teams.slice(0, 3);
  const otherTeams = teams.slice(3);

  return (
    <div className="w-full space-y-8">
      {/* Top 3 Teams - Podium */}
      {topTeams.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {topTeams.map((team, index) => {
            let cardClasses = "flex flex-col items-center p-6 shadow-lg border-2"; // Common classes
            if (index === 0) {
              cardClasses += " border-yellow-500 scale-105"; // Gold
            } else if (index === 1) {
              cardClasses += " border-slate-400"; // Silver
            } else if (index === 2) {
              cardClasses += " border-orange-500"; // Bronze
            }
            return (
            <Card key={team.team_id} className={cardClasses}>
              <div className="text-3xl font-bold text-primary mb-3">#{team.rank !== undefined ? team.rank : index + 1}</div>
              <Users className="h-10 w-10 text-muted-foreground mb-3" />
              <Link href={`/teams/${team.team_id}`} passHref legacyBehavior>
                <a className='text-center hover:underline focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-sm'>
                  <CardTitle className="text-lg font-semibold mb-1">
                    {getTeamName(team)}
                  </CardTitle>
                </a>
              </Link>
              <p className="text-md text-muted-foreground">{Math.round(team.global_elo)}</p>
              {/* <p className="text-sm text-muted-foreground">Matches: {team.matches_played}</p> TODO: Add matches_played to Team interface if available */}
            </Card>
          )})}
        </div>
      )}

      {/* Other Teams - List */}
      {otherTeams.length > 0 && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="text-xl">Autres Équipes</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[80px]">Rang</TableHead>
                  <TableHead>Équipe</TableHead>
                  <TableHead className="text-right">ELO</TableHead>
                  {/* <TableHead className="text-right">Matchs Joués</TableHead> TODO: Add matches_played if available */}
                </TableRow>
              </TableHeader>
              <TableBody>
                {otherTeams.map((team, index) => (
                  <TableRow key={team.team_id}>
                    <TableCell className="font-medium">#{team.rank !== undefined ? team.rank : index + 4}</TableCell>
                    <TableCell>
                      <Link href={`/teams/${team.team_id}`} passHref legacyBehavior>
                        <a className='hover:underline focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 rounded-sm'>
                          {getTeamName(team)}
                        </a>
                      </Link>
                    </TableCell>
                    <TableCell className="text-right">{Math.round(team.global_elo)}</TableCell>
                    {/* <TableCell className="text-right">{team.matches_played}</TableCell> TODO: Add matches_played if available */}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
