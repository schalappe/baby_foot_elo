import { z } from "zod";
import { PlayerResponseSchema } from "./player";

const TeamBaseSchema = z.object({
  player1_id: z.number().int().positive(),
  player2_id: z.number().int().positive(),
  global_elo: z.number().int().nonnegative().default(1000),
});

// [>]: Matches Python backend/app/models/team.py validator behavior.
// Validates players are different, then normalizes IDs so player1_id < player2_id.

export const TeamCreateSchema = TeamBaseSchema.refine(
  (data) => data.player1_id !== data.player2_id,
  { message: "player1_id and player2_id cannot be the same" },
).transform((data) => {
  // [>]: Canonical order ensures player1_id < player2_id.
  if (data.player1_id > data.player2_id) {
    return {
      ...data,
      player1_id: data.player2_id,
      player2_id: data.player1_id,
    };
  }
  return data;
});

export const TeamUpdateSchema = z.object({
  global_elo: z.number().int().nonnegative().optional(),
  last_match_at: z.string().datetime().optional(),
});

export const TeamResponseSchema = TeamBaseSchema.extend({
  team_id: z.number().int().positive(),
  created_at: z.string().datetime(),
  last_match_at: z.string().datetime().nullable().optional(),
  matches_played: z.number().int().nonnegative(),
  wins: z.number().int().nonnegative(),
  losses: z.number().int().nonnegative(),
  win_rate: z.number().nonnegative(),
  player1: PlayerResponseSchema.optional().nullable(),
  player2: PlayerResponseSchema.optional().nullable(),
  rank: z.number().int().positive().optional().nullable(),
});

export type TeamCreate = z.infer<typeof TeamCreateSchema>;
export type TeamUpdate = z.infer<typeof TeamUpdateSchema>;
export type TeamResponse = z.infer<typeof TeamResponseSchema>;
