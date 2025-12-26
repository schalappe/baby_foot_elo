/**
 * page.tsx
 *
 * Main landing page for player rankings in the Baby Foot ELO Championship app.
 * Features championship-styled header with trophy icon.
 *
 * Usage: This file is routed to '/' by Next.js.
 */
"use client";

import { useState, useEffect } from "react";
import useSWR, { mutate } from "swr";
import { Player } from "@/types/player.types";
import { getPlayerRankings } from "@/lib/api/client/playerService";
import { PlayerRankingsDisplay } from "../components/rankings/PlayerRankingsDisplay";
import { Button } from "../components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../components/ui/dialog";
import { PlayerRegistrationForm } from "../components/players/PlayerRegistrationForm";
import { toast } from "sonner";
import { NewMatchDialog } from "../components/matches/NewMatchDialog";
import { UserPlus, Swords, Trophy } from "lucide-react";

const PLAYERS_API_ENDPOINT = "/api/v1/players/rankings?limit=100";

export default function Home() {
  const {
    data: players,
    error: playersError,
    isLoading: playersLoading,
  } = useSWR<Player[]>(PLAYERS_API_ENDPOINT, () => getPlayerRankings(), {
    revalidateOnFocus: false,
    revalidateOnMount: true,
    refreshInterval: 30000, // [>]: Reduced from 5s to 30s - rankings don't change frequently.
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
      {/* Championship Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 md:mb-12 gap-4">
        <div className="flex items-center gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-500 shadow-lg">
            <Trophy className="h-8 w-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-black tracking-tight text-foreground">
              Classement des Joueurs
            </h1>
            <p className="text-muted-foreground text-sm md:text-base mt-1">
              Championnat Baby Foot BMIF
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3 w-full md:w-auto">
          <Dialog
            open={isAddPlayerDialogOpen}
            onOpenChange={setIsAddPlayerDialogOpen}
          >
            <DialogTrigger asChild>
              <Button
                variant="outline"
                size="lg"
                className="flex-1 md:flex-none gap-2 border-2 hover:border-primary hover:bg-primary/5 transition-all"
              >
                <UserPlus className="h-5 w-5" />
                <span className="hidden sm:inline">Ajouter un Joueur</span>
                <span className="sm:hidden">Joueur</span>
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <UserPlus className="h-5 w-5 text-primary" />
                  Enregistrer un nouveau joueur
                </DialogTitle>
              </DialogHeader>
              <PlayerRegistrationForm
                onPlayerRegistered={handlePlayerRegistered}
              />
            </DialogContent>
          </Dialog>

          <NewMatchDialog
            trigger={
              <Button
                size="lg"
                className="flex-1 md:flex-none gap-2 bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 shadow-lg hover:shadow-xl transition-all"
              >
                <Swords className="h-5 w-5" />
                <span className="hidden sm:inline">Ajouter une Partie</span>
                <span className="sm:hidden">Partie</span>
              </Button>
            }
          />
        </div>
      </div>

      {/* Rankings Display */}
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
