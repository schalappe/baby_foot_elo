/**
 * components/matches/NewMatchPage.tsx
 *
 * Championship Arena match creation form with VS battle layout.
 * Features dramatic team confrontation design with gold accents and glow effects.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import type { Player } from "@/types/player.types";
import type { BackendMatchCreatePayload } from "@/types/match.types";
import { getPlayers } from "@/lib/api/client/playerService";
import { findOrCreateTeam } from "@/lib/api/client/teamService";
import { createMatch } from "@/lib/api/client/matchService";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { cn } from "../../lib/utils";
import { format } from "date-fns";
import { fr } from "date-fns/locale";
import {
  CalendarIcon,
  AlertCircle,
  Loader2,
  Swords,
  Trophy,
  Flame,
  Users,
  Info,
} from "lucide-react";

import { Button } from "../ui/button";
import { Calendar } from "../ui/calendar";
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
import { Checkbox } from "../ui/checkbox";
import { Badge } from "../ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "../ui/tooltip";

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

// [>]: Player select component with arena styling.
function PlayerSelect({
  value,
  onChange,
  availablePlayers,
  placeholder,
  isWinner,
}: {
  value: string;
  onChange: (value: string) => void;
  availablePlayers: Player[];
  placeholder: string;
  isWinner: boolean;
}) {
  const selectedPlayer = availablePlayers.find(
    (p) => p.player_id.toString() === value,
  );

  return (
    <Select onValueChange={onChange} value={value}>
      <SelectTrigger
        className={cn(
          "w-full h-12 border-2 transition-all duration-300",
          "border-border/50 hover:border-border focus:border-primary",
          value && "bg-card/80",
          isWinner && "border-primary/50",
        )}
      >
        <SelectValue placeholder={placeholder}>
          {selectedPlayer && (
            <div className="flex items-center gap-2">
              <span className="font-medium">{selectedPlayer.name}</span>
              <Badge
                variant="outline"
                className={cn(
                  "text-xs font-bold",
                  isWinner
                    ? "border-primary/50 text-primary"
                    : "border-muted-foreground/30 text-muted-foreground",
                )}
              >
                {selectedPlayer.global_elo}
              </Badge>
            </div>
          )}
        </SelectValue>
      </SelectTrigger>
      <SelectContent className="border-2 border-border/50">
        <SelectGroup>
          <SelectLabel className="text-muted-foreground font-semibold">
            Joueurs disponibles
          </SelectLabel>
          {availablePlayers.map((player) => (
            <SelectItem
              key={player.player_id}
              value={player.player_id.toString()}
              className="cursor-pointer"
            >
              <div className="flex items-center justify-between w-full gap-3">
                <span className="font-medium">{player.name}</span>
                <Badge variant="outline" className="text-xs font-bold">
                  {player.global_elo} ELO
                </Badge>
              </div>
            </SelectItem>
          ))}
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}

// [>]: Team panel component with winner glow effect.
function TeamPanel({
  team,
  teamName,
  isWinner,
  onSelectWinner,
  player1Value,
  player2Value,
  onPlayer1Change,
  onPlayer2Change,
  availablePlayers,
  allPlayers,
  errors,
}: {
  team: "A" | "B";
  teamName: string;
  isWinner: boolean;
  onSelectWinner: () => void;
  player1Value: string;
  player2Value: string;
  onPlayer1Change: (value: string) => void;
  onPlayer2Change: (value: string) => void;
  availablePlayers: (currentValue?: string) => Player[];
  allPlayers: Player[];
  errors: {
    player1?: { message?: string };
    player2?: { message?: string };
  };
}) {
  const getPlayerName = (playerId: string) =>
    allPlayers.find((p) => p.player_id.toString() === playerId)?.name || "";

  const hasPlayers = player1Value && player2Value;

  return (
    <div
      className={cn(
        "relative flex-1 p-4 sm:p-5 rounded-xl border-2 transition-all duration-300",
        "bg-card/50",
        // [>]: Neutral border by default, primary highlight when winner.
        isWinner
          ? "border-primary shadow-[0_0_20px_rgba(234,179,8,0.25)] scale-[1.02]"
          : "border-border/50 hover:border-border",
      )}
    >
      {/* Winner badge */}
      {isWinner && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-lg bg-primary text-primary-foreground">
          <Trophy className="w-3 h-3" />
          VAINQUEUR
        </div>
      )}

      {/* Team header - clickable to select winner */}
      <button
        type="button"
        onClick={onSelectWinner}
        className={cn(
          "w-full flex flex-col items-center justify-center gap-1 mb-4 py-3 rounded-lg transition-all",
          "border-2 border-dashed",
          isWinner
            ? "border-primary/50 bg-primary/10 text-primary"
            : "border-border/50 hover:border-primary/50 hover:bg-primary/5 text-foreground hover:text-primary",
        )}
      >
        <div className="flex items-center gap-2">
          <Users className={cn("w-5 h-5", isWinner && "animate-bounce")} />
          <span className="text-lg font-bold tracking-tight">{teamName}</span>
        </div>
        {!isWinner && (
          <span className="text-xs text-muted-foreground">
            Cliquer pour gagner
          </span>
        )}
      </button>

      {/* Player selects */}
      <div className="space-y-3">
        <div>
          <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5 block">
            Joueur 1
          </Label>
          <PlayerSelect
            value={player1Value}
            onChange={onPlayer1Change}
            availablePlayers={availablePlayers(player1Value)}
            placeholder="Sélectionner..."
            isWinner={isWinner}
          />
          {errors.player1 && (
            <p className="text-destructive text-xs mt-1">
              {errors.player1.message}
            </p>
          )}
        </div>
        <div>
          <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5 block">
            Joueur 2
          </Label>
          <PlayerSelect
            value={player2Value}
            onChange={onPlayer2Change}
            availablePlayers={availablePlayers(player2Value)}
            placeholder="Sélectionner..."
            isWinner={isWinner}
          />
          {errors.player2 && (
            <p className="text-destructive text-xs mt-1">
              {errors.player2.message}
            </p>
          )}
        </div>
      </div>

      {/* Team composition preview */}
      {hasPlayers && (
        <div
          className={cn(
            "mt-4 pt-3 border-t text-center text-sm font-medium",
            isWinner
              ? "border-primary/20 text-primary"
              : "border-border/50 text-muted-foreground",
          )}
        >
          <Users className="w-4 h-4 inline mr-1.5 opacity-70" />
          {getPlayerName(player1Value)} & {getPlayerName(player2Value)}
        </div>
      )}
    </div>
  );
}

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
    setValue,
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

  useEffect(() => {
    if (selectedPlayerIds().length > 0) {
      trigger();
    }
  }, [selectedPlayerIds, trigger]);

  useEffect(() => {
    if (watchedValues.winningTeam) {
      trigger("winningTeam");
    }
  }, [watchedValues.winningTeam, trigger]);

  const onSubmit = async (data: MatchFormValues) => {
    setIsSubmitting(true);
    setSubmissionStatus(null);

    try {
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

      if (isNaN(p1A) || isNaN(p2A) || isNaN(p1B) || isNaN(p2B)) {
        throw new Error("IDs de joueurs invalides.");
      }

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
        setTimeout(() => onMatchCreated(), 1000);
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

  const getAvailablePlayers = useCallback(
    (currentPlayerSlotValue?: string): Player[] => {
      const currentSelected = selectedPlayerIds();
      return allPlayers.filter(
        (player) =>
          player.player_id.toString() === currentPlayerSlotValue ||
          !currentSelected.includes(player.player_id.toString()),
      );
    },
    [allPlayers, selectedPlayerIds],
  );

  const clearForm = () => {
    reset();
    setSubmissionStatus(null);
  };

  if (loadingPlayers) {
    return (
      <div className="space-y-6 p-2">
        {/* VS Battle skeleton */}
        <div className="flex flex-col sm:flex-row gap-4 items-stretch">
          <div className="flex-1 p-5 rounded-xl border-2 border-border/50">
            <Skeleton className="h-10 w-1/2 mx-auto mb-4" />
            <div className="space-y-3">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          </div>
          <div className="flex items-center justify-center py-4 sm:py-0">
            <Skeleton className="h-12 w-12 rounded-full" />
          </div>
          <div className="flex-1 p-5 rounded-xl border-2 border-border/50">
            <Skeleton className="h-10 w-1/2 mx-auto mb-4" />
            <div className="space-y-3">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          </div>
        </div>
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-12 w-full rounded-lg" />
      </div>
    );
  }

  if (pageError) {
    return (
      <div className="p-4">
        <Alert variant="destructive" className="border-2">
          <AlertCircle className="h-5 w-5" />
          <AlertTitle className="font-bold">Erreur</AlertTitle>
          <AlertDescription>{pageError}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="p-2 sm:p-4">
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-5">
        {/* VS Battle Arena */}
        <div className="relative">
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch">
            {/* Team A Panel */}
            <Controller
              control={control}
              name="teamAPlayer1"
              render={({ field: field1 }) => (
                <Controller
                  control={control}
                  name="teamAPlayer2"
                  render={({ field: field2 }) => (
                    <TeamPanel
                      team="A"
                      teamName="Équipe A"
                      isWinner={watchedValues.winningTeam === "A"}
                      onSelectWinner={() => setValue("winningTeam", "A")}
                      player1Value={field1.value}
                      player2Value={field2.value}
                      onPlayer1Change={field1.onChange}
                      onPlayer2Change={field2.onChange}
                      availablePlayers={getAvailablePlayers}
                      allPlayers={allPlayers}
                      errors={{
                        player1: errors.teamAPlayer1,
                        player2: errors.teamAPlayer2,
                      }}
                    />
                  )}
                />
              )}
            />

            {/* VS Divider */}
            <div className="flex sm:flex-col items-center justify-center gap-2 py-2 sm:py-0 sm:px-2">
              <div className="flex-1 sm:flex-none h-px sm:h-full w-full sm:w-px bg-gradient-to-r sm:bg-gradient-to-b from-transparent via-border to-transparent" />
              <div
                className={cn(
                  "relative flex items-center justify-center",
                  "w-14 h-14 sm:w-16 sm:h-16 rounded-full",
                  "bg-gradient-to-br from-card via-card to-muted",
                  "border-2 border-primary/30",
                  "shadow-lg shadow-primary/20",
                )}
              >
                <Swords className="w-6 h-6 sm:w-7 sm:h-7 text-primary" />
                <div className="absolute inset-0 rounded-full bg-primary/5 animate-pulse" />
              </div>
              <div className="flex-1 sm:flex-none h-px sm:h-full w-full sm:w-px bg-gradient-to-r sm:bg-gradient-to-b from-transparent via-border to-transparent" />
            </div>

            {/* Team B Panel */}
            <Controller
              control={control}
              name="teamBPlayer1"
              render={({ field: field1 }) => (
                <Controller
                  control={control}
                  name="teamBPlayer2"
                  render={({ field: field2 }) => (
                    <TeamPanel
                      team="B"
                      teamName="Équipe B"
                      isWinner={watchedValues.winningTeam === "B"}
                      onSelectWinner={() => setValue("winningTeam", "B")}
                      player1Value={field1.value}
                      player2Value={field2.value}
                      onPlayer1Change={field1.onChange}
                      onPlayer2Change={field2.onChange}
                      availablePlayers={getAvailablePlayers}
                      allPlayers={allPlayers}
                      errors={{
                        player1: errors.teamBPlayer1,
                        player2: errors.teamBPlayer2,
                      }}
                    />
                  )}
                />
              )}
            />
          </div>

          {/* Winner selection error */}
          {errors.winningTeam && (
            <p className="text-destructive text-sm text-center mt-3">
              {errors.winningTeam.message}
            </p>
          )}

          {/* Hint to select winner */}
          {!watchedValues.winningTeam && (
            <p className="text-muted-foreground text-xs text-center mt-3 animate-pulse">
              Cliquez sur une équipe pour la désigner vainqueur
            </p>
          )}
        </div>

        {/* Match Details Card */}
        <div className="rounded-xl border-2 border-border/50 bg-card/50 p-4 space-y-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground uppercase tracking-wider">
            <Swords className="w-4 h-4" />
            Détails du Match
          </div>

          {/* Fanny Badge - Prominent */}
          <div className="flex items-center justify-between p-3 rounded-lg bg-gradient-to-r from-destructive/10 via-transparent to-transparent border border-destructive/20">
            <div className="flex items-center gap-3">
              <Controller
                control={control}
                name="isFanny"
                render={({ field }) => (
                  <Checkbox
                    id="isFanny"
                    checked={field.value}
                    onCheckedChange={field.onChange}
                    className="h-5 w-5 border-2 data-[state=checked]:bg-destructive data-[state=checked]:border-destructive"
                  />
                )}
              />
              <Label
                htmlFor="isFanny"
                className="cursor-pointer flex items-center gap-2"
              >
                <span className="font-bold text-destructive flex items-center gap-1.5">
                  <Flame className="w-4 h-4" />
                  FANNY
                </span>
              </Label>
            </div>
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  className="p-1.5 rounded-full hover:bg-muted transition-colors"
                >
                  <Info className="w-4 h-4 text-muted-foreground" />
                </button>
              </TooltipTrigger>
              <TooltipContent side="left" className="max-w-[200px]">
                <p>
                  Une Fanny est une victoire écrasante où le perdant marque 0
                  point. Multiplie les points ELO!
                </p>
              </TooltipContent>
            </Tooltip>
          </div>

          {/* Date Picker */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Date du match
            </Label>
            <Controller
              control={control}
              name="matchDate"
              render={({ field }) => (
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        "w-full justify-start text-left font-normal h-11 border-2",
                        !field.value && "text-muted-foreground",
                      )}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4 opacity-70" />
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
              <p className="text-destructive text-xs">
                {errors.matchDate.message}
              </p>
            )}
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Notes (optionnel)
            </Label>
            <Controller
              control={control}
              name="notes"
              render={({ field }) => (
                <Textarea
                  id="notes"
                  placeholder="Ajouter des notes sur le match..."
                  {...field}
                  value={field.value || ""}
                  rows={2}
                  className="resize-none border-2"
                />
              )}
            />
          </div>
        </div>

        {/* Submission Status Alert */}
        {submissionStatus && (
          <Alert
            variant={
              submissionStatus.type === "success" ? "default" : "destructive"
            }
            className={cn(
              "border-2",
              submissionStatus.type === "success" &&
                "bg-[var(--match-win-bg)] border-[var(--match-win-border)] text-[var(--win-text)]",
            )}
          >
            {submissionStatus.type === "success" ? (
              <Trophy className="h-4 w-4" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <AlertTitle className="font-bold">
              {submissionStatus.type === "success" ? "Victoire!" : "Erreur"}
            </AlertTitle>
            <AlertDescription>{submissionStatus.message}</AlertDescription>
          </Alert>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={isSubmitting || !isValid}
            className={cn(
              "flex-1 h-12 font-bold text-base transition-all duration-300",
              "bg-gradient-to-r from-yellow-500 via-amber-500 to-yellow-600",
              "hover:from-yellow-400 hover:via-amber-400 hover:to-yellow-500",
              "text-amber-950 shadow-lg shadow-amber-500/25",
              "hover:shadow-amber-500/40 hover:scale-[1.02]",
              "disabled:opacity-50 disabled:hover:scale-100 disabled:shadow-none",
            )}
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Création...
              </>
            ) : (
              <>
                <Trophy className="mr-2 h-5 w-5" />
                Créer le match
              </>
            )}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={clearForm}
            disabled={isSubmitting}
            className="h-12 px-6 border-2 font-medium hover:bg-muted"
          >
            Réinitialiser
          </Button>
        </div>
      </form>
    </div>
  );
};

export default NewMatchPage;
