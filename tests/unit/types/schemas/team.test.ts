import { describe, expect, it } from "vitest";
import { TeamCreateSchema } from "@/lib/types/schemas/team";

describe("TeamCreateSchema", () => {
  it("should normalize player IDs to canonical order (lower first)", () => {
    const result = TeamCreateSchema.safeParse({
      player1_id: 5,
      player2_id: 1,
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.player1_id).toBe(1);
      expect(result.data.player2_id).toBe(5);
    }
  });

  it("should keep order when already canonical", () => {
    const result = TeamCreateSchema.safeParse({
      player1_id: 2,
      player2_id: 8,
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.player1_id).toBe(2);
      expect(result.data.player2_id).toBe(8);
    }
  });

  it("should reject same player for both positions", () => {
    const result = TeamCreateSchema.safeParse({
      player1_id: 3,
      player2_id: 3,
    });

    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.issues[0].message).toBe(
        "player1_id and player2_id cannot be the same",
      );
    }
  });

  it("should apply default ELO of 1000", () => {
    const result = TeamCreateSchema.safeParse({
      player1_id: 1,
      player2_id: 2,
    });

    expect(result.success).toBe(true);
    if (result.success) {
      expect(result.data.global_elo).toBe(1000);
    }
  });

  it("should reject non-positive player IDs", () => {
    const result = TeamCreateSchema.safeParse({
      player1_id: 0,
      player2_id: 2,
    });

    expect(result.success).toBe(false);
  });
});
