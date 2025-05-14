// frontend/app/matches/new/page.tsx
"use client";

import React, { useEffect, useState } from 'react';
import { Player } from '@/services/playerService';
import { getPlayers } from '@/services/playerService';
import { findOrCreateTeam } from '@/services/teamService';
import { createMatch, BackendMatchCreatePayload } from '@/services/matchService';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { CalendarIcon, AlertCircle } from 'lucide-react';

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
  teamAPlayer1: z.string().min(1, { message: "Player 1 for Team A is required." }),
  teamAPlayer2: z.string().optional(),
  teamBPlayer1: z.string().min(1, { message: "Player 1 for Team B is required." }),
  teamBPlayer2: z.string().optional(),
  winningTeam: z.enum(['A', 'B'], { required_error: "Please select the winning team." }),
  isFanny: z.boolean(),
  matchDate: z.date({ required_error: "Match date is required." }),
  notes: z.string().optional(),
}).refine(data => {
  const players = [data.teamAPlayer1, data.teamAPlayer2, data.teamBPlayer1, data.teamBPlayer2].filter(Boolean);
  return new Set(players).size === players.length;
}, { message: "Each player can only be selected once.", path: ["teamAPlayer1"] 
});

type MatchFormValues = z.infer<typeof matchFormSchema>;

interface EloPreviewPlayer {
  playerId: string;
  name: string;
  oldElo: number;
  newElo: number;
  change: number;
}

const NewMatchPage = () => {
  const [allPlayers, setAllPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [eloPreview, setEloPreview] = useState<EloPreviewPlayer[]>([]);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionStatus, setSubmissionStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const form = useForm<MatchFormValues>({
    resolver: zodResolver(matchFormSchema),
    defaultValues: {
      matchDate: new Date(),
      isFanny: false,
      notes: '',
    },
  });

  const { watch, control, getValues } = form; 

  // Watched values for ELO calculation useEffect dependencies
  const p1AId_dep = watch('teamAPlayer1');
  const p2AId_dep = watch('teamAPlayer2');
  const p1BId_dep = watch('teamBPlayer1');
  const p2BId_dep = watch('teamBPlayer2');
  const winningTeam_dep = watch('winningTeam');

  // selectedPlayerIds is used for getAvailablePlayers filter
  const selectedPlayerIds = [
    p1AId_dep,
    p2AId_dep,
    p1BId_dep,
    p2BId_dep,
  ].filter(Boolean) as string[];

  useEffect(() => {
    const fetchPlayersList = async () => {
      try {
        setLoading(true);
        const fetchedPlayers = await getPlayers();
        setAllPlayers(fetchedPlayers);
        setError(null);
      } catch (err) {
        setError('Échec de la récupération des joueurs.');
        console.error('Échec de la récupération des joueurs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPlayersList();
  }, []);

  // useEffect for ELO Preview Calculation
  useEffect(() => {
    // Use the watched dependency values directly
    const p1AId = p1AId_dep;
    const p2AId = p2AId_dep;
    const p1BId = p1BId_dep;
    const p2BId = p2BId_dep;
    const winningTeam = winningTeam_dep;

    if (!allPlayers.length || !winningTeam) {
      setEloPreview([]);
      return;
    }

    const getPlayerById = (id: string): Player | undefined => allPlayers.find(p => p.player_id.toString() === id);

    const teamAPlayers: Player[] = [];
    if (p1AId) {
      const p = getPlayerById(p1AId); if (p) teamAPlayers.push(p);
    }
    if (p2AId) {
      const p = getPlayerById(p2AId); if (p) teamAPlayers.push(p);
    }

    const teamBPlayers: Player[] = [];
    if (p1BId) {
      const p = getPlayerById(p1BId); if (p) teamBPlayers.push(p);
    }
    if (p2BId) {
      const p = getPlayerById(p2BId); if (p) teamBPlayers.push(p);
    }

    if (teamAPlayers.length === 0 || teamBPlayers.length === 0) {
      setEloPreview([]);
      return;
    }
    
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
        newElo: player.global_elo + change,
        change: change,
      });
    });

    teamBPlayers.forEach(player => {
      const result = winningTeam === 'B' ? 1 : 0;
      const change = calculateEloChange(player.global_elo, probB, result as 0 | 1);
      previewData.push({
        playerId: player.player_id.toString(),
        name: player.name,
        oldElo: player.global_elo,
        newElo: player.global_elo + change,
        change: change,
      });
    });
    setEloPreview(previewData);

  }, [p1AId_dep, p2AId_dep, p1BId_dep, p2BId_dep, winningTeam_dep, allPlayers]);

  const onSubmit = async (data: MatchFormValues) => {
    setIsSubmitting(true);
    setSubmissionStatus(null);

    // Validate that all selected players are unique and primary players for teams are selected.
    if (!data.teamAPlayer1 || !data.teamBPlayer1) {
      setSubmissionStatus({ type: 'error', message: 'Player 1 for both teams must be selected.' });
      setIsSubmitting(false);
      return;
    }
    
    // Convert player IDs from string to number. Handle optional players.
    const p1A = parseInt(data.teamAPlayer1, 10);
    const p2A_str = data.teamAPlayer2;
    const p1B = parseInt(data.teamBPlayer1, 10);
    const p2B_str = data.teamBPlayer2;

    // Backend expects two players per team for team creation via /api/v1/teams/
    // TeamCreate model requires player1_id and player2_id.
    if (!p2A_str || !p2B_str) {
        setSubmissionStatus({ type: 'error', message: 'Both Team A and Team B must have two players selected.' });
        setIsSubmitting(false);
        return;
    }

    const p2A = parseInt(p2A_str, 10);
    const p2B = parseInt(p2B_str, 10);

    try {
      // Step 1: Get or create Team A
      const teamA = await findOrCreateTeam(p1A, p2A);
      console.log('Team A:', teamA);

      // Step 2: Get or create Team B
      const teamB = await findOrCreateTeam(p1B, p2B);
      console.log('Team B:', teamB);

      if (!teamA || !teamB || !teamA.team_id || !teamB.team_id) {
        throw new Error('Failed to retrieve or create one or both teams.');
      }

      // Step 3: Determine winner and loser team IDs
      let winner_team_id: number;
      let loser_team_id: number;

      if (data.winningTeam === 'A') {
        winner_team_id = teamA.team_id;
        loser_team_id = teamB.team_id;
      } else {
        winner_team_id = teamB.team_id;
        loser_team_id = teamA.team_id;
      }

      // Step 4: Construct payload for creating the match
      const matchPayload: BackendMatchCreatePayload = {
        winner_team_id,
        loser_team_id,
        is_fanny: data.isFanny,
        played_at: data.matchDate.toISOString(),
      };

      // Step 5: Call API to create the match
      const createdMatch = await createMatch(matchPayload);
      setSubmissionStatus({ type: 'success', message: `Match created successfully! ID: ${createdMatch.match_id}` });
      form.reset(); // Reset form on success
      setEloPreview([]); // Clear ELO preview

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred.';
      setSubmissionStatus({ type: 'error', message: `Failed to create match: ${errorMessage}` });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getAvailablePlayers = (allPlayersList: Player[], currentlySelectedIds: string[], currentPlayerSlotValue?: string): Player[] => {
    return allPlayersList.filter(
      player => 
        (player.player_id.toString() === currentPlayerSlotValue) || 
        !currentlySelectedIds.includes(player.player_id.toString())
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4 max-w-2xl space-y-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-8 w-3/4" />
        {[1, 2, 3, 4].map(i => <Skeleton key={i} className="h-48 w-full" />)}
        <Skeleton className="h-10 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4 max-w-md">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
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
            <CardTitle>Equipe A</CardTitle>
            <CardDescription>Sélectionnez les joueurs pour l'équipe A.</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="teamAPlayer1">Joueur 1*</Label>
              <Select onValueChange={(value: string) => form.setValue('teamAPlayer1', value)} value={form.watch('teamAPlayer1')}>
                <SelectTrigger id="teamAPlayer1">
                  <SelectValue placeholder="Select Player 1" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Available Players</SelectLabel>
                    {getAvailablePlayers(allPlayers, selectedPlayerIds, form.watch('teamAPlayer1')).map(player => (
                      <SelectItem key={player.player_id} value={player.player_id.toString()}>
                        {player.name} (Elo: {player.global_elo})
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              {form.formState.errors.teamAPlayer1 && <p className="text-sm text-red-500">{form.formState.errors.teamAPlayer1.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="teamAPlayer2">Joueur 2 (Optionnel)</Label>
              <Select onValueChange={(value: string) => form.setValue('teamAPlayer2', value)} value={form.watch('teamAPlayer2')}>
                <SelectTrigger id="teamAPlayer2">
                  <SelectValue placeholder="Select Player 2" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Available Players</SelectLabel>
                    {getAvailablePlayers(allPlayers, selectedPlayerIds, form.watch('teamAPlayer2')).map(player => (
                      <SelectItem key={player.player_id} value={player.player_id.toString()}>
                        {player.name} (Elo: {player.global_elo})
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              {form.formState.errors.teamAPlayer2 && <p className="text-sm text-red-500">{form.formState.errors.teamAPlayer2.message}</p>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Equipe B</CardTitle>
            <CardDescription>Sélectionnez les joueurs pour l'équipe B.</CardDescription>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="teamBPlayer1">Joueur 1*</Label>
              <Select onValueChange={(value: string) => form.setValue('teamBPlayer1', value)} value={form.watch('teamBPlayer1')}>
                <SelectTrigger id="teamBPlayer1">
                  <SelectValue placeholder="Select Player 1" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Available Players</SelectLabel>
                    {getAvailablePlayers(allPlayers, selectedPlayerIds, form.watch('teamBPlayer1')).map(player => (
                      <SelectItem key={player.player_id} value={player.player_id.toString()}>
                        {player.name} (Elo: {player.global_elo})
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              {form.formState.errors.teamBPlayer1 && <p className="text-sm text-red-500">{form.formState.errors.teamBPlayer1.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="teamBPlayer2">Joueur 2 (Optionnel)</Label>
              <Select onValueChange={(value: string) => form.setValue('teamBPlayer2', value)} value={form.watch('teamBPlayer2')}>
                <SelectTrigger id="teamBPlayer2">
                  <SelectValue placeholder="Select Player 2" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Available Players</SelectLabel>
                    {getAvailablePlayers(allPlayers, selectedPlayerIds, form.watch('teamBPlayer2')).map(player => (
                      <SelectItem key={player.player_id} value={player.player_id.toString()}>
                        {player.name} (Elo: {player.global_elo})
                      </SelectItem>
                    ))}
                  </SelectGroup>
                </SelectContent>
              </Select>
              {form.formState.errors.teamBPlayer2 && <p className="text-sm text-red-500">{form.formState.errors.teamBPlayer2.message}</p>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Résultat du match</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Equipe gagnante*</Label>
              <Controller
                control={control}
                name="winningTeam"
                render={({ field }) => (
                  <RadioGroup
                    onValueChange={field.onChange}
                    defaultValue={field.value}
                    className="flex space-x-4"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="A" id="teamAwin" />
                      <Label htmlFor="teamAwin">Equipe A</Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="B" id="teamBwin" />
                      <Label htmlFor="teamBwin">Equipe B</Label>
                    </div>
                  </RadioGroup>
                )}
              />
              {form.formState.errors.winningTeam && <p className="text-sm text-red-500">{form.formState.errors.winningTeam.message}</p>}
            </div>
            <div className="flex items-center space-x-2">
              <Controller
                control={control}
                name="isFanny"
                render={({ field }) => (
                  <Checkbox
                    id="isFanny"
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                )}
              />
              <Label htmlFor="isFanny" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                C'était une Fanny? (Le perdant a marqué 0)
              </Label>
              {form.formState.errors.isFanny && <p className="text-sm text-red-500">{form.formState.errors.isFanny.message}</p>}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Détails du match</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="matchDate">Date du match*</Label>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    id="matchDate"
                    variant={"outline"}
                    className={cn(
                      "w-full justify-start text-left font-normal",
                      !form.watch('matchDate') && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {form.watch('matchDate') ? format(form.watch('matchDate')!, "PPP") : <span>Pick a date</span>}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                  <Calendar
                    mode="single"
                    selected={form.watch('matchDate')}
                    onSelect={(date) => form.setValue('matchDate', date || new Date())}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
              {form.formState.errors.matchDate && <p className="text-sm text-red-500">{form.formState.errors.matchDate.message}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea id="notes" placeholder="Any notable events, disputes, etc." {...form.register('notes')} />
              {form.formState.errors.notes && <p className="text-sm text-red-500">{form.formState.errors.notes.message}</p>}
            </div>
          </CardContent>
        </Card>
        
        {(form.formState.errors.root || form.formState.errors.teamAPlayer1?.type === 'custom') && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Erreur de validation</AlertTitle>
            <AlertDescription>
              {form.formState.errors.root?.message || 
               (form.formState.errors.teamAPlayer1?.type === 'custom' && form.formState.errors.teamAPlayer1.message)}
            </AlertDescription>
          </Alert>
        )}

        {eloPreview.length > 0 && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle>Prévisualisation des changements d'ELO</CardTitle>
              <CardDescription>Prévisualisation des changements d'ELO basés sur les selections actuelles.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {eloPreview.map(player => (
                <div key={player.playerId} className="flex justify-between items-center p-2 border rounded-md">
                  <div>
                    <p className="font-semibold">{player.name}</p>
                    <p className="text-sm text-muted-foreground">Ancien ELO: {player.oldElo}</p>
                  </div>
                  <div className="text-right">
                    <Badge variant={player.change >= 0 ? 'default' : 'destructive'} className="mb-1">
                      {player.change >= 0 ? '+' : ''}{player.change}
                    </Badge>
                    <p className="text-sm font-semibold">Nouveau ELO: {player.newElo}</p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? 'Enregistrement...' : 'Enregistrer le match'}
        </Button>
        {submissionStatus && (
          <Alert variant={submissionStatus.type === 'error' ? 'destructive' : 'default'} className="mt-4">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>{submissionStatus.type === 'error' ? 'Error' : 'Success'}</AlertTitle>
            <AlertDescription>
              {submissionStatus.message}
            </AlertDescription>
          </Alert>
        )}
      </form>
    </div>
  );
};

export default NewMatchPage;
