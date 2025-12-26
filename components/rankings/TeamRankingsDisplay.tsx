/**
 * TeamRankingsDisplay.tsx
 *
 * Displays the full team rankings page, including podium and table.
 * Handles loading, error, and empty states for team ranking data.
 *
 * Exports:
 *   - TeamRankingsDisplay: React.FC for team rankings display.
 */
"use client";

import React from "react";
import { Team } from "@/types/team.types";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { TeamRankingTable } from "./TeamRankingTable";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { AlertCircle } from "lucide-react";
import { PodiumGrid } from "../common/PodiumGrid";

interface TeamRankingsDisplayProps {
  teams: Team[];
  isLoading: boolean;
  error: Error | null;
}

const getTeamName = (team: Team): string => {
  const p1Name = team.player1?.name || `Joueur ID ${team.player1_id}`;
  const p2Name = team.player2?.name || `Joueur ID ${team.player2_id}`;
  return [p1Name, p2Name].sort().join(" & ");
};

export function TeamRankingsDisplay({
  teams = [],
  isLoading,
  error,
}: TeamRankingsDisplayProps) {
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
              <div
                key={i}
                className="flex justify-between items-center py-3 border-b last:border-b-0"
              >
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
        <PodiumGrid
          items={topTeams}
          getKey={(team) => team.team_id}
          getLink={(team) => `/teams/${team.team_id}`}
          getName={(team) => getTeamName(team)}
          getElo={(team) => Math.round(team.global_elo)}
          getWinrate={(team) => {
            const matchesPlayed =
              team.matches_played ?? team.wins + team.losses;
            return `${matchesPlayed > 0 ? Math.round((team.wins / matchesPlayed) * 100) : 0}%`;
          }}
          renderExtra={(team) => {
            const matchesPlayed =
              team.matches_played ?? team.wins + team.losses;
            return (
              <>
                {/* W-L and % */}
                <div className="flex justify-center font-semibold mb-2">
                  <span style={{ color: "var(--win-text)" }}>{team.wins}W</span>{" "}
                  &nbsp; - &nbsp;{" "}
                  <span style={{ color: "var(--lose-text)" }}>
                    {team.losses}L
                  </span>
                </div>
                {/* Bottom Row: Matches */}
                <div className="flex justify-between items-end w-full mt-auto pt-2">
                  <div className={`text-xs`}>
                    <span className={`font-bold`}>{matchesPlayed}</span> parties
                  </div>
                </div>
              </>
            );
          }}
        />
      )}

      {/* Other Teams - Clean List */}
      {otherTeams.length > 0 && (
        <Card className="shadow-lg border-2 overflow-hidden">
          <CardHeader className="py-5 px-6">
            <CardTitle className="text-xl font-bold tracking-tight text-primary text-center">
              Autres Équipes
            </CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <TeamRankingTable
              data={otherTeams}
              isLoading={false}
              error={null}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
