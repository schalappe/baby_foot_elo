'use client';

import useSWR from 'swr';
import { getTeamRankings } from '@/services/teamService';
import { TeamRankingTable } from '@/components/rankings/TeamRankingTable';

// Define a generic fetcher for SWR
const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function TeamRankingsPage() {
  // Fetch Team Rankings
  const { data: teams, error: teamsError, isLoading: teamsLoading } = 
    useSWR('/api/v1/teams/rankings?limit=100', getTeamRankings);

  return (
    <>
      <section className="w-full flex flex-col items-center gap-12 py-12">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 text-primary dark:text-primary drop-shadow-lg">Classement des Équipes</h1>
        </div>

        {/* Team Ranking Section */}
        <div className="w-full max-w-4xl bg-card dark:bg-card rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6">
          <h2 className="text-2xl font-bold text-primary mb-4 drop-shadow">Top Équipes</h2>
          <TeamRankingTable 
            data={teams ?? []} 
            isLoading={teamsLoading} 
            error={teamsError} 
          />
        </div>
      </section>
    </>
  );
}
