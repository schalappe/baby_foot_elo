// frontend/app/matches/new/page.tsx
"use client";

import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Player } from '@/services/playerService';
import { getPlayers } from '@/services/playerService';
import { findOrCreateTeam } from '@/services/teamService';
import { createMatch, BackendMatchCreatePayload } from '@/services/matchService';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { fr } from 'date-fns/locale';
import { CalendarIcon, AlertCircle, Trophy, Loader2 } from 'lucide-react'; // Added Loader2

import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import {
  calculateTeamElo,
  calculateWinProbability,
  calculateEloChange,
} from '@/lib/eloCalculator';

const matchFormSchema = z.object({
  teamAPlayer1: z.string().min(1, { message: "Joueur 1 de l'équipe A est requis." }),
  teamAPlayer2: z.string().min(1, { message: "Joueur 2 de l'équipe A est requis." }),
  teamBPlayer1: z.string().min(1, { message: "Joueur 1 de l'équipe B est requis." }),
  teamBPlayer2: z.string().min(1, { message: "Joueur 2 de l'équipe B est requis." }),
  winningTeam: z.enum(['A', 'B'], { required_error: "Veuillez sélectionner l'équipe gagnante." }),
  isFanny: z.boolean(),
  matchDate: z.date({ required_error: "La date du match est requise." }),
  notes: z.string().optional(),
}).refine(data => {
  const players = [data.teamAPlayer1, data.teamAPlayer2, data.teamBPlayer1, data.teamBPlayer2].filter(Boolean);
  return new Set(players).size === players.length;
}, { message: "Chaque joueur ne peut être sélectionné qu'une seule fois.", path: ["teamAPlayer1"] });

type MatchFormValues = z.infer<typeof matchFormSchema>;

interface EloPreviewPlayer {
  playerId: string;
  name: string;
  oldElo: number;
  newElo: number;
  change: number;
}

const NewMatchPage = () => {
  const router = useRouter();
  const [allPlayers, setAllPlayers] = useState<Player[]>([]);
  const [loadingPlayers, setLoadingPlayers] = useState<boolean>(true); // Renamed for clarity
  const [pageError, setPageError] = useState<string | null>(null); // Renamed for clarity
  const [eloPreview, setEloPreview] = useState<EloPreviewPlayer[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionStatus, setSubmissionStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const form = useForm<MatchFormValues>({
    resolver: zodResolver(matchFormSchema),
    defaultValues: {
      matchDate: new Date(),
      isFanny: false,
      notes: '',
      teamAPlayer1: '',
      teamAPlayer2: '',
      teamBPlayer1: '',
      teamBPlayer2: '',
    },
  });

  const { watch, control, getValues, setValue, reset, formState: { errors } } = form;

  const watchedValues = watch(); // Watch all fields for ELO calculation & available players

  const selectedPlayerIds = useCallback(() : string[] => {
    return [
      watchedValues.teamAPlayer1,
      watchedValues.teamAPlayer2,
      watchedValues.teamBPlayer1,
      watchedValues.teamBPlayer2,
    ].filter(Boolean) as string[];
  }, [watchedValues.teamAPlayer1, watchedValues.teamAPlayer2, watchedValues.teamBPlayer1, watchedValues.teamBPlayer2]);


  useEffect(() => {
    const fetchPlayersList = async () => {
      try {
        setLoadingPlayers(true);
        const fetchedPlayers = await getPlayers();
        setAllPlayers(fetchedPlayers);
        setPageError(null);
      } catch (err) {
        setPageError('Échec de la récupération des joueurs.');
        console.error('Échec de la récupération des joueurs:', err);
      } finally {
        setLoadingPlayers(false);
      }
    };
    fetchPlayersList();
  }, []);

  useEffect(() => {
    const { teamAPlayer1, teamAPlayer2, teamBPlayer1, teamBPlayer2, winningTeam } = watchedValues;

    if (!allPlayers.length || !winningTeam || !teamAPlayer1 || !teamAPlayer2 || !teamBPlayer1 || !teamBPlayer2) {
      setEloPreview([]);
      return;
    }

    const getPlayerById = (id: string): Player | undefined => allPlayers.find(p => p.player_id.toString() === id);

    const pA1 = getPlayerById(teamAPlayer1);
    const pA2 = getPlayerById(teamAPlayer2);
    const pB1 = getPlayerById(teamBPlayer1);
    const pB2 = getPlayerById(teamBPlayer2);

    if (!pA1 || !pA2 || !pB1 || !pB2) {
        setEloPreview([]);
        return;
    }
    
    const teamAPlayers = [pA1, pA2];
    const teamBPlayers = [pB1, pB2];
    
    const teamAElo = calculateTeamElo(teamAPlayers[0].global_elo, teamAPlayers[1]?.global_elo);
    const teamBElo = calculateTeamElo(teamBPlayers[0].global_elo, teamBPlayers[1]?.global_elo);

    const probA = calculateWinProbability(teamAElo, teamBElo);
    const probB = 1 - probA;

    const previewData: EloPreviewPlayer[] = [];

    teamAPlayers.forEach(player => {
      const result = winningTeam === 'A' ? 1 : 0;
      const change = calculateEloChange(player.global_elo, probA, result as 0 | 1);
      previewData.push({
        playerId: player.player_id.toString(),
        name: player.name,
        oldElo: player.global_elo,
        newElo: Math.round(player.global_elo + change),
        change: Math.round(change),
      });
    });

    teamBPlayers.forEach(player => {
      const result = winningTeam === 'B' ? 1 : 0;
      const change = calculateEloChange(player.global_elo, probB, result as 0 | 1);
      previewData.push({
        playerId: player.player_id.toString(),
        name: player.name,
        oldElo: player.global_elo,
        newElo: Math.round(player.global_elo + change),
        change: Math.round(change),
      });
    });
    setEloPreview(previewData);

  }, [watchedValues.teamAPlayer1, watchedValues.teamAPlayer2, watchedValues.teamBPlayer1, watchedValues.teamBPlayer2, watchedValues.winningTeam, allPlayers]);

  const onSubmit = async (data: MatchFormValues) => {
    setIsSubmitting(true);
    setSubmissionStatus(null);

    if (!data.teamAPlayer1 || !data.teamAPlayer2 || !data.teamBPlayer1 || !data.teamBPlayer2) {
        setSubmissionStatus({ type: 'error', message: 'Tous les joueurs doivent être sélectionnés.' });
        setIsSubmitting(false);
        return;
    }

    const p1A = parseInt(data.teamAPlayer1, 10);
    const p2A = parseInt(data.teamAPlayer2, 10);
    const p1B = parseInt(data.teamBPlayer1, 10);
    const p2B = parseInt(data.teamBPlayer2, 10);

    try {
      const teamA = await findOrCreateTeam(p1A, p2A);
      const teamB = await findOrCreateTeam(p1B, p2B);

      if (!teamA || !teamB || !teamA.team_id || !teamB.team_id) {
        throw new Error('Échec de la récupération ou de la création d\'une ou des deux équipes.');
      }

      let winner_team_id: number;
      let loser_team_id: number;

      if (data.winningTeam === 'A') {
        winner_team_id = teamA.team_id;
        loser_team_id = teamB.team_id;
      } else {
        winner_team_id = teamB.team_id;
        loser_team_id = teamA.team_id;
      }

      const matchPayload: BackendMatchCreatePayload = {
        winner_team_id,
        loser_team_id,
        is_fanny: data.isFanny,
        played_at: data.matchDate.toISOString(),
        notes: data.notes || null,
      };

      await createMatch(matchPayload);
      setSubmissionStatus({ type: 'success', message: 'Match créé avec succès! Redirection...' });
      reset();
      setEloPreview([]);
      setTimeout(() => router.push('/'), 1500);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Une erreur inconnue est survenue.';
      setSubmissionStatus({ type: 'error', message: `Échec de la création du match: ${errorMessage}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getAvailablePlayers = (allPlayersList: Player[], currentSelectedIds: string[], currentPlayerSlotValue?: string): Player[] => {
    return allPlayersList.filter(
      player =>
        (player.player_id.toString() === currentPlayerSlotValue) ||
        !currentSelectedIds.includes(player.player_id.toString())
    );
  };

  if (loadingPlayers) {
    return (
      <div className="container mx-auto p-4 max-w-2xl space-y-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-8 w-3/4 mb-6" />
        <Card>
            <CardHeader><Skeleton className="h-8 w-1/3" /></CardHeader>
            <CardContent className="space-y-6">
                <div className="flex space-x-4">
                    <Skeleton className="h-10 w-1/2" /> <Skeleton className="h-10 w-1/4" />
                </div>
                {[1,2,3,4].map(i => <Skeleton key={i} className="h-10 w-full" />)}
                 <Skeleton className="h-20 w-full" />
                 <Skeleton className="h-10 w-full mt-4" />
            </CardContent>
        </Card>
      </div>
    );
  }

  if (pageError) {
    return (
      <div className="container mx-auto p-4 max-w-md">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{pageError}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <header className="mb-6">
        <h1 className="text-3xl font-bold tracking-tight">Nouveau match</h1>
        <p className="text-muted-foreground">Entrez les détails du match ci-dessous.</p>
      </header>

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <Card>
          <CardHeader>
            <CardTitle>Ajouter un résultat</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Row 1: Date and Fanny */}
            <div className="flex flex-col sm:flex-row sm:items-start sm:space-x-4 space-y-4 sm:space-y-0">
              <div className="flex-grow space-y-1">
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      id="matchDate"
                      variant={"outline"}
                      className={cn(
                        "w-full sm:w-[240px] justify-start text-left font-normal",
                        !watchedValues.matchDate && "text-muted-foreground"
                      )}
                      disabled={loadingPlayers || isSubmitting}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {watchedValues.matchDate ? format(watchedValues.matchDate, "dd/MM/yyyy", { locale: fr }) : <span>Date du match</span>}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0">
                    <Calendar
                      mode="single"
                      selected={watchedValues.matchDate}
                      onSelect={(date) => setValue('matchDate', date || new Date())}
                      initialFocus
                      locale={fr}
                      disabled={isSubmitting}
                    />
                  </PopoverContent>
                </Popover>
                {errors.matchDate && <p className="text-xs text-red-500 pt-1">{errors.matchDate.message}</p>}
              </div>
              <div className="flex items-center space-x-2 pt-2 sm:pt-2.5">
                <Controller
                  control={control}
                  name="isFanny"
                  render={({ field }) => (
                    <Checkbox
                      id="isFanny"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                      aria-label="C'était une Fanny?"
                      disabled={loadingPlayers || isSubmitting}
                    />
                  )}
                />
                <Label htmlFor="isFanny" className="text-sm font-normal">Fanny</Label>
                {errors.isFanny && <p className="text-xs text-red-500 ">{errors.isFanny.message}</p>}
              </div>
            </div>

            {/* Team A Selection */}
            <div className="flex items-start space-x-3">
              <Trophy className="h-6 w-6 text-blue-500 mt-1.5" />
              <div className="flex-grow space-y-3">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3">
                  {(['teamAPlayer1', 'teamAPlayer2'] as const).map((fieldName, idx) => (
                    <div className="space-y-1" key={fieldName}>
                      <Select onValueChange={(value) => setValue(fieldName, value)} value={watchedValues[fieldName]} disabled={loadingPlayers || isSubmitting}>
                        <SelectTrigger id={fieldName}>
                          <SelectValue placeholder={`Joueur ${idx + 1} (Équipe A)`} />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectGroup>
                            <SelectLabel>Joueurs disponibles</SelectLabel>
                            {getAvailablePlayers(allPlayers, selectedPlayerIds(), watchedValues[fieldName]).map(player => (
                              <SelectItem key={player.player_id} value={player.player_id.toString()}>
                                {player.name} (Elo: {player.global_elo})
                              </SelectItem>
                            ))}
                          </SelectGroup>
                        </SelectContent>
                      </Select>
                      {errors[fieldName] && <p className="text-xs text-red-500 pt-1">{errors[fieldName]?.message}</p>}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* VS Separator */}
            <div className="flex justify-center items-center py-1">
              <span className="text-base font-semibold text-muted-foreground">VS</span>
            </div>

            {/* Team B Selection */}
            <div className="flex items-start space-x-3">
              <Trophy className="h-6 w-6 text-red-500 mt-1.5" />
              <div className="flex-grow space-y-3">
                 <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3">
                    {(['teamBPlayer1', 'teamBPlayer2'] as const).map((fieldName, idx) => (
                        <div className="space-y-1" key={fieldName}>
                        <Select onValueChange={(value) => setValue(fieldName, value)} value={watchedValues[fieldName]} disabled={loadingPlayers || isSubmitting}>
                            <SelectTrigger id={fieldName}>
                            <SelectValue placeholder={`Joueur ${idx + 1} (Équipe B)`} />
                            </SelectTrigger>
                            <SelectContent>
                            <SelectGroup>
                                <SelectLabel>Joueurs disponibles</SelectLabel>
                                {getAvailablePlayers(allPlayers, selectedPlayerIds(), watchedValues[fieldName]).map(player => (
                                <SelectItem key={player.player_id} value={player.player_id.toString()}>
                                    {player.name} (Elo: {player.global_elo})
                                </SelectItem>
                                ))}
                            </SelectGroup>
                            </SelectContent>
                        </Select>
                        {errors[fieldName] && <p className="text-xs text-red-500 pt-1">{errors[fieldName]?.message}</p>}
                        </div>
                    ))}
                </div>
              </div>
            </div>
            
            {/* Winning Team */}
            <div className="space-y-2 pt-3">
              <Label className="text-sm font-medium">Équipe gagnante*</Label>
              <Controller
                control={control}
                name="winningTeam"
                render={({ field }) => (
                  <RadioGroup
                    onValueChange={field.onChange}
                    value={field.value}
                    className="flex items-center space-x-4 pt-1"
                    disabled={loadingPlayers || isSubmitting}
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="A" id="teamAwin" disabled={loadingPlayers || isSubmitting} />
                      <Label htmlFor="teamAwin" className="font-normal">Équipe A</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="B" id="teamBwin" disabled={loadingPlayers || isSubmitting} />
                      <Label htmlFor="teamBwin" className="font-normal">Équipe B</Label>
                    </div>
                  </RadioGroup>
                )}
              />
              {errors.winningTeam && <p className="text-xs text-red-500 pt-1">{errors.winningTeam.message}</p>}
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Notes (optionnel)</Label>
              <Textarea
                id="notes"
                placeholder="Événements notables, chambrage, etc."
                {...form.register('notes')}
                disabled={loadingPlayers || isSubmitting}
              />
              {errors.notes && <p className="text-xs text-red-500 pt-1">{errors.notes.message}</p>}
            </div>
          </CardContent>
        </Card>

        {/* Form-level error (e.g. duplicate player) */}
        {errors.root?.message && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erreur de validation</AlertTitle>
            <AlertDescription>{errors.root.message}</AlertDescription>
          </Alert>
        )}
         {errors.teamAPlayer1?.type === 'custom' && !errors.root?.message && (
            <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Erreur de validation</AlertTitle>
                <AlertDescription>{errors.teamAPlayer1.message}</AlertDescription>
            </Alert>
        )}


        {/* ELO Preview */}
        {eloPreview.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Prévisualisation des ELOs</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {eloPreview.map(player => (
                <div key={player.playerId} className="flex justify-between items-center p-2 border rounded-md">
                  <div>
                    <p className="font-semibold">{player.name}</p>
                    <p className="text-sm text-muted-foreground">Ancien: {player.oldElo}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant={player.change >= 0 ? 'default' : 'destructive'} className={cn("mb-1 text-sm", player.change >=0 ? "bg-green-500 hover:bg-green-600" : "bg-red-500 hover:bg-red-600")}>
                      {player.change >= 0 ? '+' : ''}{player.change}
                    </Badge>
                    <p className="text-sm font-semibold">Nouveau: {player.newElo}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Submission Status Alert */}
        {submissionStatus && (
          <Alert variant={submissionStatus.type === 'success' ? 'default' : 'destructive'} className={submissionStatus.type === 'success' ? 'bg-green-100 border-green-400 text-green-700' : ''}>
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>{submissionStatus.type === 'success' ? 'Succès' : 'Erreur'}</AlertTitle>
            <AlertDescription>{submissionStatus.message}</AlertDescription>
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={() => router.push('/')} disabled={isSubmitting}>
            Annuler
          </Button>
          <Button type="submit" disabled={loadingPlayers || isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Soumission...
              </>
            ) : (
              'Créer le match'
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default NewMatchPage;
