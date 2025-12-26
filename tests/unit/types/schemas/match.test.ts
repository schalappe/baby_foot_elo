import { describe, expect, it } from "vitest";
import {
  MatchCreateSchema,
  MatchWithEloResponseSchema,
} from "@/lib/types/schemas/match";

describe("MatchCreateSchema", () => {
  it("should validate valid match data", () => {
    const result = MatchCreateSchema.safeParse({
      winner_team_id: 1,
      loser_team_id: 2,
      is_fanny: false,
      played_at: "2024-01-15T14:30:00Z",
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.winner_team_id).toBe(1);
      expect(result.data.loser_team_id).toBe(2);
      expect(result.data.is_fanny).toBe(false);
    }
  });

  it("should apply default is_fanny as false", () => {
    const result = MatchCreateSchema.safeParse({
      winner_team_id: 1,
      loser_team_id: 2,
      played_at: "2024-01-15T14:30:00Z",
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.is_fanny).toBe(false);
    }
  });

  it("should reject invalid datetime format", () => {
    const result = MatchCreateSchema.safeParse({
      winner_team_id: 1,
      loser_team_id: 2,
      played_at: "not-a-date",
    });

    expect(result.success).toBe(false);
  });
});

describe("MatchWithEloResponseSchema", () => {
  it("should validate match with elo_changes", () => {
    const result = MatchWithEloResponseSchema.safeParse({
      match_id: 1,
      winner_team_id: 1,
      loser_team_id: 2,
      is_fanny: true,
      played_at: "2024-01-15T14:30:00Z",
      winner_team: null,
      loser_team: null,
      elo_changes: {
        "1": { old_elo: 1000, new_elo: 1020, difference: 20 },
        "2": { old_elo: 1000, new_elo: 1020, difference: 20 },
        "3": { old_elo: 1000, new_elo: 980, difference: -20 },
        "4": { old_elo: 1000, new_elo: 980, difference: -20 },
      },
    });

    expect(result.success).toBe(true);
  });
});
