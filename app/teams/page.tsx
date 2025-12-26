/**
 * teams/page.tsx
 *
 * Displays team rankings in the Baby Foot ELO app.
 *
 * - Fetches and displays a list of ranked teams.
 * - Handles loading and error states.
 *
 * Usage: Routed to '/teams' by Next.js.
 */
"use client";

import { useEffect } from "react";
import useSWR from "swr";
import { Team } from "@/types/team.types";
import { getTeamRankings } from "@/lib/api/client/teamService";
import { TeamRankingsDisplay } from "../../components/rankings/TeamRankingsDisplay";
import { toast } from "sonner";
import { NewMatchDialog } from "../../components/matches/NewMatchDialog";
import { Trophy } from "lucide-react";

const TEAMS_API_ENDPOINT = "/api/v1/teams/rankings?limit=100";

export default function TeamRankingsPage() {
  const {
    data: teams,
    error: teamsError,
    isLoading: teamsLoading,
  } = useSWR<Team[]>(TEAMS_API_ENDPOINT, getTeamRankings, {
    revalidateOnFocus: false,
    revalidateOnMount: true,
    refreshInterval: 30000, // [>]: Reduced from 5s to 30s - rankings don't change frequently.
  });

  useEffect(() => {
    if (teamsError) {
      toast.error("Erreur lors de la récupération des équipes.");
    }
  }, [teamsError]);

  return (
    <main className="container mx-auto p-4 md:p-8">
      {/* Championship Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 md:mb-12 gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-500 shadow-lg">
            <Trophy className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-black tracking-tight text-foreground">
              Classement des Équipes
            </h1>
            <p className="text-muted-foreground text-sm md:text-base mt-1">
              Championnat Baby Foot BMIF
            </p>
          </div>
        </div>

        {/* Action button */}
        <div className="flex gap-3 w-full md:w-auto">
          <NewMatchDialog />
        </div>
      </div>
      <TeamRankingsDisplay
        teams={teams ?? []}
        isLoading={teamsLoading}
        error={
          teamsError
            ? teamsError instanceof Error
              ? teamsError
              : new Error(String(teamsError))
            : null
        }
      />
    </main>
  );
}
