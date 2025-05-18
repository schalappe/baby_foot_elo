'use client';

import { useState, useEffect } from 'react';
import useSWR, { mutate } from 'swr';
import { Team } from '@/types/team.types';
import { getTeamRankings } from '@/services/teamService'; 
import { TeamRankingsDisplay } from '@/components/rankings/TeamRankingsDisplay';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';
import Link from 'next/link'; 

const TEAMS_API_ENDPOINT = '/api/v1/teams/rankings?limit=100';

export default function TeamRankingsPage() {
  const { data: teams, error: teamsError, isLoading: teamsLoading } = 
    useSWR<Team[]>(TEAMS_API_ENDPOINT, getTeamRankings);

  useEffect(() => {
    if (teamsError) {
      toast.error("Erreur lors de la récupération des équipes.");
    }
  }, [teamsError]);

  return (
    <main className="container mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 md:mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white mb-4 md:mb-0">
          Classement des Équipes
        </h1>
        <div className="flex space-x-2">
          <Link href="/matches/new" passHref>
            <Button variant="outline" size="lg">Ajouter une Partie</Button>
          </Link> 
        </div>
      </div>
      <TeamRankingsDisplay 
        teams={teams ?? []} 
        isLoading={teamsLoading} 
        error={teamsError ? (teamsError instanceof Error ? teamsError : new Error(String(teamsError))) : null} 
      />
    </main>
  );
}
