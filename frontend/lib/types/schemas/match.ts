import { z } from "zod";
import { TeamResponseSchema } from "./team";

export const MatchBaseSchema = z.object({
  winner_team_id: z.number().int().positive(),
  loser_team_id: z.number().int().positive(),
  is_fanny: z.boolean().default(false),
  played_at: z.string().datetime(),
  notes: z.string().nullable().optional(),
});

export const MatchCreateSchema = MatchBaseSchema;

export const MatchUpdateSchema = z.object({});

export const MatchResponseSchema = MatchBaseSchema.extend({
  match_id: z.number().int().positive(),
  winner_team: TeamResponseSchema.optional().nullable(),
  loser_team: TeamResponseSchema.optional().nullable(),
});

// [>]: EloChange structure for elo_changes map.

export const EloChangeSchema = z.object({
  old_elo: z.number().int().nonnegative(),
  new_elo: z.number().int().nonnegative(),
  difference: z.number().int(),
});

export const MatchWithEloResponseSchema = MatchResponseSchema.extend({
  elo_changes: z.record(z.string(), EloChangeSchema).default({}),
});

export type MatchBase = z.infer<typeof MatchBaseSchema>;
export type MatchCreate = z.infer<typeof MatchCreateSchema>;
export type MatchUpdate = z.infer<typeof MatchUpdateSchema>;
export type MatchResponse = z.infer<typeof MatchResponseSchema>;
export type EloChange = z.infer<typeof EloChangeSchema>;
export type MatchWithEloResponse = z.infer<typeof MatchWithEloResponseSchema>;
