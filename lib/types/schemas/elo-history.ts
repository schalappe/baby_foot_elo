import { z } from "zod";

export const EloHistoryBaseSchema = z.object({
  player_id: z.number().int().positive(),
  match_id: z.number().int().positive(),
  old_elo: z.number().int().nonnegative(),
  new_elo: z.number().int().nonnegative(),
  difference: z.number().int(),
  date: z.string().datetime(),
});

export const EloHistoryCreateSchema = EloHistoryBaseSchema;

// [>]: ELO history is immutable - no meaningful update fields.

export const EloHistoryUpdateSchema = z.object({});

export const EloHistoryResponseSchema = EloHistoryBaseSchema.extend({
  history_id: z.number().int().positive(),
});

export type EloHistoryBase = z.infer<typeof EloHistoryBaseSchema>;
export type EloHistoryCreate = z.infer<typeof EloHistoryCreateSchema>;
export type EloHistoryUpdate = z.infer<typeof EloHistoryUpdateSchema>;
export type EloHistoryResponse = z.infer<typeof EloHistoryResponseSchema>;
