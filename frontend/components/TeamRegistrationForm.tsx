'use client';

import React, { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Player, getPlayers } from '@/services/playerService';
import { createTeam, TeamCreatePayload } from '@/services/teamService';
import { toast } from 'sonner';

const formSchema = z.object({
  player1_id: z.number({ required_error: "Veuillez sélectionner le joueur 1." }).min(1, "Veuillez sélectionner le joueur 1."),
  player2_id: z.number({ required_error: "Veuillez sélectionner le joueur 2." }).min(1, "Veuillez sélectionner le joueur 2."),
}).refine(data => data.player1_id !== data.player2_id, {
  message: "Les deux joueurs doivent être différents.",
  path: ['player2_id'], // Attach error to the second player field
});

type TeamRegistrationFormValues = z.infer<typeof formSchema>;

interface TeamRegistrationFormProps {
  onTeamRegistered: () => void;
}

export function TeamRegistrationForm({ onTeamRegistered }: TeamRegistrationFormProps) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [isLoadingPlayers, setIsLoadingPlayers] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<TeamRegistrationFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      player1_id: undefined,
      player2_id: undefined,
    },
  });

  useEffect(() => {
    async function fetchPlayers() {
      try {
        setIsLoadingPlayers(true);
        const fetchedPlayers = await getPlayers({ limit: 100 }); // Fetch up to 100 players
        setPlayers(fetchedPlayers);
      } catch (error) {
        toast.error('Erreur lors de la récupération des joueurs.');
        console.error('Failed to fetch players:', error);
      }
      setIsLoadingPlayers(false);
    }
    fetchPlayers();
  }, []);

  async function onSubmit(values: TeamRegistrationFormValues) {
    setIsSubmitting(true);
    try {
      const payload: TeamCreatePayload = {
        player1_id: values.player1_id,
        player2_id: values.player2_id,
      };
      await createTeam(payload);
      toast.success('Équipe enregistrée avec succès !');
      onTeamRegistered();
      form.reset();
    } catch (error: any) {
      toast.error(`Erreur lors de l'enregistrement: ${error.message}`);
      console.error('Failed to create team:', error);
    }
    setIsSubmitting(false);
  }

  // Convert players to options for Select component
  const playerOptions = players.map((player) => ({
    value: player.player_id.toString(), // SelectItem value is usually a string
    label: player.name,
  }));

  if (isLoadingPlayers) {
    return <div className="flex justify-center items-center p-8"><Loader2 className="h-8 w-8 animate-spin" /> Chargement des joueurs...</div>;
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="player1_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Joueur 1</FormLabel>
              <Select
                onValueChange={(value) => field.onChange(parseInt(value, 10))} // Parse to number before RHF update
                defaultValue={field.value?.toString()} // field.value could be number, convert to string for Select defaultValue
                disabled={isLoadingPlayers}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner Joueur 1" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {isLoadingPlayers ? (
                    <SelectItem value="loading" disabled>Chargement...</SelectItem>
                  ) : (
                    playerOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="player2_id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Joueur 2</FormLabel>
              <Select
                onValueChange={(value) => field.onChange(parseInt(value, 10))}
                defaultValue={field.value?.toString()}
                disabled={isLoadingPlayers}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Sélectionner Joueur 2" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {isLoadingPlayers ? (
                    <SelectItem value="loading" disabled>Chargement...</SelectItem>
                  ) : (
                    playerOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        {option.label}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isSubmitting || isLoadingPlayers} className="w-full">
          {isSubmitting ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
          Enregistrer l'équipe
        </Button>
      </form>
    </Form>
  );
}
