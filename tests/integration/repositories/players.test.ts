// [>]: Integration tests for player repository.
// Tests run against real Supabase instance.
// Skipped when NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY are not set.

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import {
  createPlayerByName,
  getPlayerById,
  getPlayerByName,
  getAllPlayers,
  updatePlayer,
  deletePlayerById,
} from "@/lib/db/repositories/players";
import { PlayerNotFoundError } from "@/lib/errors/api-errors";

// [>]: Check if Supabase env vars are configured.
const hasSupabaseConfig =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL &&
  !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

describe.skipIf(!hasSupabaseConfig)("Player Repository", () => {
  let testPlayerId: number;
  const testPlayerName = `Test Player ${Date.now()}`;

  beforeAll(async () => {
    // [>]: Create a test player for use in tests.
    testPlayerId = await createPlayerByName(testPlayerName, 1200);
  });

  afterAll(async () => {
    // [>]: Clean up test player.
    try {
      await deletePlayerById(testPlayerId);
    } catch {
      // [>]: Ignore if already deleted.
    }
  });

  describe("createPlayerByName", () => {
    it("creates a player and returns the ID", async () => {
      const uniqueName = `Create Test ${Date.now()}`;
      const playerId = await createPlayerByName(uniqueName, 1000);

      expect(playerId).toBeTypeOf("number");
      expect(playerId).toBeGreaterThan(0);

      // [>]: Clean up.
      await deletePlayerById(playerId);
    });
  });

  describe("getPlayerById", () => {
    it("returns player when found", async () => {
      const player = await getPlayerById(testPlayerId);

      expect(player.player_id).toBe(testPlayerId);
      expect(player.name).toBe(testPlayerName);
      expect(player.global_elo).toBe(1200);
    });

    it("throws PlayerNotFoundError when not found", async () => {
      await expect(getPlayerById(999999)).rejects.toThrow(PlayerNotFoundError);
    });
  });

  describe("getPlayerByName", () => {
    it("returns player when found", async () => {
      const player = await getPlayerByName(testPlayerName);

      expect(player).not.toBeNull();
      expect(player!.player_id).toBe(testPlayerId);
    });

    it("returns null when not found", async () => {
      const player = await getPlayerByName("NonExistent Player 999999");

      expect(player).toBeNull();
    });
  });

  describe("getAllPlayers", () => {
    it("returns an array of players", async () => {
      const players = await getAllPlayers();

      expect(Array.isArray(players)).toBe(true);
      // [>]: Should include our test player.
      const testPlayer = players.find((p) => p.player_id === testPlayerId);
      expect(testPlayer).toBeDefined();
    });
  });

  describe("updatePlayer", () => {
    it("updates player name", async () => {
      const updatedName = `${testPlayerName} Updated`;

      await updatePlayer(testPlayerId, { name: updatedName });

      const player = await getPlayerById(testPlayerId);
      expect(player.name).toBe(updatedName);

      // [>]: Restore original name for cleanup.
    });

    it("updates player ELO", async () => {
      await updatePlayer(testPlayerId, { global_elo: 1300 });

      const player = await getPlayerById(testPlayerId);
      expect(player.global_elo).toBe(1300);
    });

    it("throws PlayerNotFoundError when player does not exist", async () => {
      await expect(updatePlayer(999999, { name: "New Name" })).rejects.toThrow(
        PlayerNotFoundError,
      );
    });
  });

  describe("deletePlayerById", () => {
    it("deletes an existing player", async () => {
      // [>]: Create a player specifically for deletion.
      const deleteTestName = `Delete Test ${Date.now()}`;
      const deletePlayerId = await createPlayerByName(deleteTestName);

      await deletePlayerById(deletePlayerId);

      await expect(getPlayerById(deletePlayerId)).rejects.toThrow(
        PlayerNotFoundError,
      );
    });

    it("throws PlayerNotFoundError when player does not exist", async () => {
      await expect(deletePlayerById(999999)).rejects.toThrow(
        PlayerNotFoundError,
      );
    });
  });
});
