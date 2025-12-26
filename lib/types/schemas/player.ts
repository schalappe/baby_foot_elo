import { z } from "zod";

// [>]: Base schema defines shared validation rules matching Python Pydantic model.

export const PlayerBaseSchema = z.object({
  name: z.string().min(1).max(100),
  global_elo: z.number().int().nonnegative().default(1000),
});

export const PlayerCreateSchema = PlayerBaseSchema;

export const PlayerUpdateSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  global_elo: z.number().int().nonnegative().optional(),
});

export const PlayerResponseSchema = PlayerBaseSchema.extend({
  player_id: z.number().int().positive(),
  created_at: z.string().datetime(),
  last_match_at: z.string().datetime().nullable().optional(),
  matches_played: z.number().int().nonnegative().default(0),
  wins: z.number().int().nonnegative().default(0),
  losses: z.number().int().nonnegative().default(0),
  win_rate: z.number().nonnegative().default(0),
});

// [>]: Inferred types for use throughout the application.

export type PlayerBase = z.infer<typeof PlayerBaseSchema>;
export type PlayerCreate = z.infer<typeof PlayerCreateSchema>;
export type PlayerUpdate = z.infer<typeof PlayerUpdateSchema>;
export type PlayerResponse = z.infer<typeof PlayerResponseSchema>;
