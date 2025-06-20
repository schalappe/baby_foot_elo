/**
 * components/matches/NewMatchPage.tsx
 *
 * Enhanced component for creating a new match in the Baby Foot ELO app.
 *
 * - Provides a form to create and submit a new match.
 * - Fetches players and teams for match assignment.
 * - Uses react-hook-form and ShadCN UI components.
 * - Enhanced with better error handling and UX improvements.
 *
 * Usage: Used as a component, not a Next.js page.
 */
"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";
import type { Player } from "@/types/player.types";
import type { BackendMatchCreatePayload } from "@/types/match.types";
import { getPlayers } from "../../services/playerService";
import { findOrCreateTeam } from "../../services/teamService";
import { createMatch } from "../../services/matchService";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { cn } from "../../lib/utils";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { CalendarIcon, AlertCircle, Loader2 } from "lucide-react";

import { Button } from "../ui/button";
import { Calendar } from "../ui/calendar";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Label } from "../ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popoverDialog";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Textarea } from "../ui/textarea";
import { Skeleton } from "../ui/skeleton";
import { Alert, AlertDescription, AlertTitle } from "../ui/alert";
import { RadioGroup, RadioGroupItem } from "../ui/radio-group";
import { Checkbox } from "../ui/checkbox";
import { Badge } from "../ui/badge";

interface NewMatchPageProps {
  onMatchCreated?: () => void;
  isDialog?: boolean;
}

const matchFormSchema = z
  .object({
    teamAPlayer1: z
      .string()
      .min(1, { message: "Joueur 1 de l'équipe A est requis." }),
    teamAPlayer2: z
      .string()
      .min(1, { message: "Joueur 2 de l'équipe A est requis." }),
    teamBPlayer1: z
      .string()
      .min(1, { message: "Joueur 1 de l'équipe B est requis." }),
    teamBPlayer2: z
      .string()
      .min(1, { message: "Joueur 2 de l'équipe B est requis." }),
    winningTeam: z.enum(["A", "B"], {
      required_error: "Veuillez sélectionner l'équipe gagnante.",
    }),
    isFanny: z.boolean(),
    matchDate: z.date({ required_error: "La date du match est requise." }),
    notes: z.string().optional(),
  })
  .refine(
    (data) =>
      data.teamAPlayer1 !== data.teamAPlayer2 &&
      data.teamBPlayer1 !== data.teamBPlayer2 &&
      ![data.teamAPlayer1, data.teamAPlayer2].includes(data.teamBPlayer1) &&
      ![data.teamAPlayer1, data.teamAPlayer2].includes(data.teamBPlayer2),
    {
      message: "Un joueur ne peut être sélectionné qu'une seule fois.",
      path: ["teamAPlayer1", "teamAPlayer2", "teamBPlayer1", "teamBPlayer2"],
    },
  );

type MatchFormValues = z.infer<typeof matchFormSchema>;

const NewMatchPage: React.FC<NewMatchPageProps> = ({
  onMatchCreated,
  isDialog,
}) => {
  const router = useRouter();
  const [allPlayers, setAllPlayers] = useState<Player[]>([]);
  const [loadingPlayers, setLoadingPlayers] = useState<boolean>(true);
  const [pageError, setPageError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionStatus, setSubmissionStatus] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);

  const form = useForm<MatchFormValues>({
    resolver: zodResolver(matchFormSchema),
    defaultValues: {
      matchDate: new Date(),
      isFanny: false,
      notes: "",
      teamAPlayer1: "",
      teamAPlayer2: "",
      teamBPlayer1: "",
      teamBPlayer2: "",
    },
  });

  const {
    watch,
    control,
    formState: { errors, isValid },
    reset,
    trigger,
  } = form;

  const watchedValues = watch();

  const selectedPlayerIds = useCallback(() => {
    return [
      watchedValues.teamAPlayer1,
      watchedValues.teamAPlayer2,
      watchedValues.teamBPlayer1,
      watchedValues.teamBPlayer2,
    ].filter(Boolean) as string[];
  }, [
    watchedValues.teamAPlayer1,
    watchedValues.teamAPlayer2,
    watchedValues.teamBPlayer1,
    watchedValues.teamBPlayer2,
  ]);

  // Memoized team compositions for better UX
  const teamCompositions = useMemo(() => {
    const getPlayerName = (playerId: string) =>
      allPlayers.find((p) => p.player_id.toString() === playerId)?.name || "";

    return {
      teamA: {
        player1: getPlayerName(watchedValues.teamAPlayer1),
        player2: getPlayerName(watchedValues.teamAPlayer2),
        complete: watchedValues.teamAPlayer1 && watchedValues.teamAPlayer2,
      },
      teamB: {
        player1: getPlayerName(watchedValues.teamBPlayer1),
        player2: getPlayerName(watchedValues.teamBPlayer2),
        complete: watchedValues.teamBPlayer1 && watchedValues.teamBPlayer2,
      },
    };
  }, [allPlayers, watchedValues]);

  useEffect(() => {
    const fetchPlayersList = async () => {
      try {
        setLoadingPlayers(true);
        const fetchedPlayers = await getPlayers();
        if (fetchedPlayers.length === 0) {
          setPageError(
            "Aucun joueur trouvé. Veuillez d'abord créer des joueurs.",
          );
        } else {
          setAllPlayers(fetchedPlayers);
          setPageError(null);
        }
      } catch (err) {
        setPageError(
          "Échec de la récupération des joueurs. Veuillez réessayer.",
        );
        console.error("Échec de la récupération des joueurs:", err);
      } finally {
        setLoadingPlayers(false);
      }
    };
    fetchPlayersList();
  }, []);

  // Auto-validate form when players change
  useEffect(() => {
    if (selectedPlayerIds().length > 0) {
      trigger();
    }
  }, [selectedPlayerIds, trigger]);

  // Auto-validate winningTeam field when it changes
  useEffect(() => {
    if (watchedValues.winningTeam) {
      trigger("winningTeam");
    }
  }, [watchedValues.winningTeam, trigger]);

  const onSubmit = async (data: MatchFormValues) => {
    setIsSubmitting(true);
    setSubmissionStatus(null);

    try {
      // Validate all players are selected
      if (
        !data.teamAPlayer1 ||
        !data.teamAPlayer2 ||
        !data.teamBPlayer1 ||
        !data.teamBPlayer2
      ) {
        throw new Error("Tous les joueurs doivent être sélectionnés.");
      }

      const p1A = Number.parseInt(data.teamAPlayer1, 10);
      const p2A = Number.parseInt(data.teamAPlayer2, 10);
      const p1B = Number.parseInt(data.teamBPlayer1, 10);
      const p2B = Number.parseInt(data.teamBPlayer2, 10);

      // Validate player IDs
      if (isNaN(p1A) || isNaN(p2A) || isNaN(p1B) || isNaN(p2B)) {
        throw new Error("IDs de joueurs invalides.");
      }

      // Find or create teams
      const [teamA, teamB] = await Promise.all([
        findOrCreateTeam(p1A, p2A),
        findOrCreateTeam(p1B, p2B),
      ]);

      if (!teamA || !teamB || !teamA.team_id || !teamB.team_id) {
        throw new Error(
          "Échec de la récupération ou de la création d'une ou des deux équipes.",
        );
      }

      let winner_team_id: number;
      let loser_team_id: number;

      if (data.winningTeam === "A") {
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
      setSubmissionStatus({
        type: "success",
        message: "Match créé avec succès!",
      });
      reset();

      if (isDialog && onMatchCreated) {
        setTimeout(() => onMatchCreated(), 1000); // Small delay to show success message
      } else {
        setTimeout(() => router.push("/"), 1500);
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Une erreur inconnue est survenue.";
      setSubmissionStatus({
        type: "error",
        message: `Échec de la création du match: ${errorMessage}`,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getAvailablePlayers = (
    allPlayersList: Player[],
    currentSelectedIds: string[],
    currentPlayerSlotValue?: string,
  ): Player[] => {
    return allPlayersList.filter(
      (player) =>
        player.player_id.toString() === currentPlayerSlotValue ||
        !currentSelectedIds.includes(player.player_id.toString()),
    );
  };

  const clearForm = () => {
    reset();
    setSubmissionStatus(null);
  };

  if (loadingPlayers) {
    return (
      <div className="container mx-auto p-4 max-w-2xl space-y-6">
        <Skeleton className="h-10 w-1/2" />
        <Skeleton className="h-8 w-3/4 mb-6" />
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-1/3" />
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex space-x-4">
              <Skeleton className="h-10 w-1/2" />
              <Skeleton className="h-10 w-1/4" />
            </div>
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
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
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Team A Players */}
        <Card>
          <CardHeader>
            <CardTitle>Équipe A</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="teamAPlayer1">Joueur 1</Label>
                <Controller
                  control={control}
                  name="teamAPlayer1"
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner le joueur 1" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Joueurs disponibles</SelectLabel>
                          {getAvailablePlayers(
                            allPlayers,
                            selectedPlayerIds(),
                            field.value,
                          ).map((player) => (
                            <SelectItem
                              key={player.player_id}
                              value={player.player_id.toString()}
                            >
                              <div className="flex items-center justify-between w-full">
                                <span>{player.name}</span>
                                <Badge variant="outline" className="ml-2">
                                  {player.global_elo} ELO
                                </Badge>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.teamAPlayer1 && (
                  <p className="text-red-500 text-sm">
                    {errors.teamAPlayer1.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="teamAPlayer2">Joueur 2</Label>
                <Controller
                  control={control}
                  name="teamAPlayer2"
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner le joueur 2" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Joueurs disponibles</SelectLabel>
                          {getAvailablePlayers(
                            allPlayers,
                            selectedPlayerIds(),
                            field.value,
                          ).map((player) => (
                            <SelectItem
                              key={player.player_id}
                              value={player.player_id.toString()}
                            >
                              <div className="flex items-center justify-between w-full">
                                <span>{player.name}</span>
                                <Badge variant="outline" className="ml-2">
                                  {player.global_elo} ELO
                                </Badge>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.teamAPlayer2 && (
                  <p className="text-red-500 text-sm">
                    {errors.teamAPlayer2.message}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Team B Players */}
        <Card>
          <CardHeader>
            <CardTitle>Équipe B</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="teamBPlayer1">Joueur 1</Label>
                <Controller
                  control={control}
                  name="teamBPlayer1"
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner le joueur 1" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Joueurs disponibles</SelectLabel>
                          {getAvailablePlayers(
                            allPlayers,
                            selectedPlayerIds(),
                            field.value,
                          ).map((player) => (
                            <SelectItem
                              key={player.player_id}
                              value={player.player_id.toString()}
                            >
                              <div className="flex items-center justify-between w-full">
                                <span>{player.name}</span>
                                <Badge variant="outline" className="ml-2">
                                  {player.global_elo} ELO
                                </Badge>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.teamBPlayer1 && (
                  <p className="text-red-500 text-sm">
                    {errors.teamBPlayer1.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="teamBPlayer2">Joueur 2</Label>
                <Controller
                  control={control}
                  name="teamBPlayer2"
                  render={({ field }) => (
                    <Select onValueChange={field.onChange} value={field.value}>
                      <SelectTrigger>
                        <SelectValue placeholder="Sélectionner le joueur 2" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectGroup>
                          <SelectLabel>Joueurs disponibles</SelectLabel>
                          {getAvailablePlayers(
                            allPlayers,
                            selectedPlayerIds(),
                            field.value,
                          ).map((player) => (
                            <SelectItem
                              key={player.player_id}
                              value={player.player_id.toString()}
                            >
                              <div className="flex items-center justify-between w-full">
                                <span>{player.name}</span>
                                <Badge variant="outline" className="ml-2">
                                  {player.global_elo} ELO
                                </Badge>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      </SelectContent>
                    </Select>
                  )}
                />
                {errors.teamBPlayer2 && (
                  <p className="text-red-500 text-sm">
                    {errors.teamBPlayer2.message}
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Match Details */}
        <Card>
          <CardHeader>
            <CardTitle>Détails du Match</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Winning Team */}
            <div className="space-y-2">
              <Label htmlFor="winningTeam">Équipe gagnante</Label>
              <Controller
                control={control}
                name="winningTeam"
                render={({ field }) => (
                  <RadioGroup
                    onValueChange={field.onChange}
                    value={field.value}
                    className="flex space-x-4"
                  >
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="A" id="winningTeamA" />
                      <Label htmlFor="winningTeamA" className="cursor-pointer">
                        Équipe A
                        {teamCompositions.teamA.complete && (
                          <span className="text-sm text-muted-foreground ml-1">
                            ({teamCompositions.teamA.player1} &{" "}
                            {teamCompositions.teamA.player2})
                          </span>
                        )}
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <RadioGroupItem value="B" id="winningTeamB" />
                      <Label htmlFor="winningTeamB" className="cursor-pointer">
                        Équipe B
                        {teamCompositions.teamB.complete && (
                          <span className="text-sm text-muted-foreground ml-1">
                            ({teamCompositions.teamB.player1} &{" "}
                            {teamCompositions.teamB.player2})
                          </span>
                        )}
                      </Label>
                    </div>
                  </RadioGroup>
                )}
              />
              {errors.winningTeam && (
                <p className="text-red-500 text-sm">
                  {errors.winningTeam.message}
                </p>
              )}
            </div>

            {/* Is Fanny */}
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
              <Label htmlFor="isFanny" className="cursor-pointer">
                Fanny
              </Label>
            </div>

            {/* Match Date */}
            <div className="space-y-2">
              <Label htmlFor="matchDate">Date du match</Label>
              <Controller
                control={control}
                name="matchDate"
                render={({ field }) => (
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        variant={"outline"}
                        className={cn(
                          "w-full justify-start text-left font-normal",
                          !field.value && "text-muted-foreground",
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {field.value ? (
                          format(field.value, "PPP", { locale: fr })
                        ) : (
                          <span>Choisir une date</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={field.value}
                        locale={fr}
                        onSelect={field.onChange}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                )}
              />
              {errors.matchDate && (
                <p className="text-red-500 text-sm">
                  {errors.matchDate.message}
                </p>
              )}
            </div>

            {/* Notes */}
            <div className="space-y-2">
              <Label htmlFor="notes">Notes (optionnel)</Label>
              <Controller
                control={control}
                name="notes"
                render={({ field }) => (
                  <Textarea
                    id="notes"
                    placeholder="Ajouter des notes sur le match..."
                    {...field}
                    value={field.value || ""}
                    rows={3}
                  />
                )}
              />
              {errors.notes && (
                <p className="text-red-500 text-sm">{errors.notes.message}</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Submission Status Alert */}
        {submissionStatus && (
          <Alert
            variant={
              submissionStatus.type === "success" ? "default" : "destructive"
            }
            className={
              submissionStatus.type === "success"
                ? "bg-green-100 border-green-400 text-green-700"
                : ""
            }
          >
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>
              {submissionStatus.type === "success" ? "Succès" : "Erreur"}
            </AlertTitle>
            <AlertDescription>{submissionStatus.message}</AlertDescription>
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            type="submit"
            className="flex-1"
            disabled={isSubmitting || !isValid}
          >
            {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Créer le match
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={clearForm}
            disabled={isSubmitting}
          >
            Réinitialiser
          </Button>
        </div>
      </form>
    </div>
  );
};

export default NewMatchPage;
