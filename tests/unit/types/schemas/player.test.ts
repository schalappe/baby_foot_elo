import { describe, expect, it } from "vitest";
import {
  PlayerCreateSchema,
  PlayerResponseSchema,
} from "@/lib/types/schemas/player";

describe("PlayerCreateSchema", () => {
  it("should validate valid player data", () => {
    const result = PlayerCreateSchema.safeParse({
      name: "John Doe",
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.name).toBe("John Doe");
      expect(result.data.global_elo).toBe(1000);
    }
  });

  it("should reject empty name", () => {
    const result = PlayerCreateSchema.safeParse({
      name: "",
    });

    expect(result.success).toBe(false);
  });

  it("should reject name exceeding max length", () => {
    const result = PlayerCreateSchema.safeParse({
      name: "a".repeat(101),
    });

    expect(result.success).toBe(false);
  });
});

describe("PlayerResponseSchema", () => {
  it("should validate complete player response", () => {
    const result = PlayerResponseSchema.safeParse({
      player_id: 1,
      name: "Jane Doe",
      global_elo: 1200,
      created_at: "2024-01-01T00:00:00Z",
      last_match_at: null,
      matches_played: 10,
      wins: 6,
      losses: 4,
      win_rate: 0.6,
    });

    expect(result.success).toBe(true);
  });

  it("should reject negative player_id", () => {
    const result = PlayerResponseSchema.safeParse({
      player_id: -1,
      name: "Jane Doe",
      global_elo: 1200,
      created_at: "2024-01-01T00:00:00Z",
      matches_played: 0,
      wins: 0,
      losses: 0,
      win_rate: 0,
    });

    expect(result.success).toBe(false);
  });
});
