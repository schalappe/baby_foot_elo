'use client';

import Image from "next/image";
import useSWR from 'swr';
import { getPlayerRankings } from '@/services/playerService';
import { getTeamRankings } from '@/services/teamService';
import { PlayerRankingTable } from '@/components/rankings/PlayerRankingTable';
import { TeamRankingTable } from '@/components/rankings/TeamRankingTable';

// Define a generic fetcher for SWR
const fetcher = (url: string) => url;

export default function Home() {
  // Fetch Player Rankings
  const { data: players, error: playersError, isLoading: playersLoading } =
    useSWR('/api/v1/players?sort_by=global_elo&order=desc&limit=100', getPlayerRankings);

  // Fetch Team Rankings
  const { data: teams, error: teamsError, isLoading: teamsLoading } =
    useSWR('/api/v1/teams/rankings?limit=100', getTeamRankings);

  return (
    <>
      <section className="w-full flex flex-col items-center gap-12 py-12">
        <div className="text-center">
          <h1 className="text-4xl sm:text-5xl font-extrabold mb-4 text-primary dark:text-primary drop-shadow-lg">Classement Baby Foot Elo</h1>
        </div>

        {/* Player Ranking Section */}
        <div className="w-full max-w-4xl bg-card dark:bg-card rounded-xl shadow-lg p-6 md:p-8 flex flex-col gap-6">
          <h2 className="text-2xl font-bold text-primary mb-4 drop-shadow">Top Joueurs</h2>
          <PlayerRankingTable
            data={players ?? []}
            isLoading={playersLoading}
            error={playersError}
          />
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

        <div className="mt-8">
        <a href="#" className="inline-block px-8 py-3 rounded-full bg-primary text-primary-foreground text-lg font-bold shadow-lg border border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary transition">Ajouter une partie</a>
        </div>
      </section>
    </>
  );
}
