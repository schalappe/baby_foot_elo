/**
 * page.tsx
 *
 * Main landing page for player rankings in the Baby Foot ELO app.
 *
 * - Displays player rankings and registration dialog.
 * - Fetches player ranking data from the backend.
 * - Allows users to register new players.
 *
 * Usage: This file is routed to '/' by Next.js.
 */
"use client";

import { useState, useEffect } from "react";
import useSWR, { mutate } from "swr";
import { Player } from "@/types/player.types";
import { getPlayerRankings } from "@/services/playerService";
import { PlayerRankingsDisplay } from "@/components/rankings/PlayerRankingsDisplay";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { PlayerRegistrationForm } from "@/components/players/PlayerRegistrationForm";
import { toast } from "sonner";
import { NewMatchDialog } from "@/components/matches/NewMatchDialog";

const PLAYERS_API_ENDPOINT = "/api/v1/players/rankings?limit=100";

export default function Home() {
  const {
    data: players,
    error: playersError,
    isLoading: playersLoading,
  } = useSWR<Player[]>(PLAYERS_API_ENDPOINT, getPlayerRankings, {
    revalidateOnFocus: true,
    revalidateOnMount: true,
    refreshInterval: 5000, // Refresh every 5 seconds
  });

  const [isAddPlayerDialogOpen, setIsAddPlayerDialogOpen] = useState(false);

  const handlePlayerRegistered = async () => {
    setIsAddPlayerDialogOpen(false);
    await mutate(PLAYERS_API_ENDPOINT);
    toast.success("Nouveau joueur ajouté avec succès !");
  };

  useEffect(() => {
    if (playersError) {
      toast.error("Erreur lors de la récupération des joueurs.");
    }
  }, [playersError]);

  return (
    <main className="container mx-auto p-4 md:p-8">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 md:mb-10">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-800 dark:text-white mb-4 md:mb-0">
          Classement des Joueurs
        </h1>
        <div className="flex space-x-2">
          <Dialog
            open={isAddPlayerDialogOpen}
            onOpenChange={setIsAddPlayerDialogOpen}
          >
            <DialogTrigger asChild>
              <Button variant="default" size="lg">
                Ajouter un Joueur
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Enregistrer un nouveau joueur</DialogTitle>
              </DialogHeader>
              <PlayerRegistrationForm
                onPlayerRegistered={handlePlayerRegistered}
              />
            </DialogContent>
          </Dialog>

          <NewMatchDialog>
            <Button variant="outline" size="lg">
              Ajouter une Partie
            </Button>
          </NewMatchDialog>
        </div>
      </div>
      <PlayerRankingsDisplay
        players={players || []}
        isLoading={playersLoading}
        error={
          playersError
            ? playersError instanceof Error
              ? playersError
              : new Error(String(playersError))
            : null
        }
      />
    </main>
  );
}
