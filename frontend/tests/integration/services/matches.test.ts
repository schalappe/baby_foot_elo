// [>]: Integration tests for match service.
// Tests the complete match creation flow with ELO updates.

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { createNewMatch, getMatch, deleteMatch } from "@/lib/services/matches";
import { createNewPlayer, deletePlayer } from "@/lib/services/players";
import { createNewTeam } from "@/lib/services/teams";
import {
  InvalidMatchTeamsError,
  MatchNotFoundError,
} from "@/lib/errors/api-errors";

describe("Match Service", () => {
  // [>]: Test fixtures - we'll create players and teams for match testing.
  let player1Id: number;
  let player2Id: number;
  let player3Id: number;
  let player4Id: number;
  let team1Id: number;
  let team2Id: number;
  let testMatchId: number | null = null;

  beforeAll(async () => {
    // [>]: Create 4 test players.
    const timestamp = Date.now();
    const [p1, p2, p3, p4] = await Promise.all([
      createNewPlayer({ name: `Match Test P1 ${timestamp}`, global_elo: 1000 }),
      createNewPlayer({ name: `Match Test P2 ${timestamp}`, global_elo: 1000 }),
      createNewPlayer({ name: `Match Test P3 ${timestamp}`, global_elo: 1000 }),
      createNewPlayer({ name: `Match Test P4 ${timestamp}`, global_elo: 1000 }),
    ]);

    player1Id = p1.player_id;
    player2Id = p2.player_id;
    player3Id = p3.player_id;
    player4Id = p4.player_id;

    // [>]: Create 2 test teams.
    // Note: Teams may already be auto-created when players are created.
    // createNewTeam handles deduplication.
    const [t1, t2] = await Promise.all([
      createNewTeam({
        player1_id: player1Id,
        player2_id: player2Id,
        global_elo: 1000,
      }),
      createNewTeam({
        player1_id: player3Id,
        player2_id: player4Id,
        global_elo: 1000,
      }),
    ]);

    team1Id = t1.team_id;
    team2Id = t2.team_id;
  });

  afterAll(async () => {
    // [>]: Clean up in reverse order: matches, then teams, then players.
    try {
      if (testMatchId) {
        await deleteMatch(testMatchId);
      }
    } catch {
      // [>]: Match may have already been deleted in tests.
    }

    // [>]: Note: We don't delete teams because player deletion doesn't cascade.
    // In a real cleanup, we'd need to delete teams first, but for now we skip.

    // [>]: Delete players.
    await Promise.all([
      deletePlayer(player1Id).catch(() => {}),
      deletePlayer(player2Id).catch(() => {}),
      deletePlayer(player3Id).catch(() => {}),
      deletePlayer(player4Id).catch(() => {}),
    ]);
  });

  describe("createNewMatch", () => {
    it("creates a match and updates ELOs", async () => {
      const playedAt = new Date().toISOString();

      const match = await createNewMatch({
        winner_team_id: team1Id,
        loser_team_id: team2Id,
        played_at: playedAt,
        is_fanny: false,
        notes: "Test match",
      });

      testMatchId = match.match_id;

      // [>]: Verify match was created.
      expect(match.match_id).toBeTypeOf("number");
      expect(match.winner_team_id).toBe(team1Id);
      expect(match.loser_team_id).toBe(team2Id);
      expect(match.is_fanny).toBe(false);
      expect(match.notes).toBe("Test match");

      // [>]: Verify ELO changes were recorded.
      expect(match.elo_changes).toBeDefined();
      expect(Object.keys(match.elo_changes).length).toBe(4); // 4 players

      // [>]: Winners should have gained ELO.
      const winnerP1Change = match.elo_changes[String(player1Id)];
      const winnerP2Change = match.elo_changes[String(player2Id)];
      expect(winnerP1Change.difference).toBeGreaterThan(0);
      expect(winnerP2Change.difference).toBeGreaterThan(0);

      // [>]: Losers should have lost ELO.
      const loserP3Change = match.elo_changes[String(player3Id)];
      const loserP4Change = match.elo_changes[String(player4Id)];
      expect(loserP3Change.difference).toBeLessThan(0);
      expect(loserP4Change.difference).toBeLessThan(0);
    });

    it("throws InvalidMatchTeamsError when teams are the same", async () => {
      await expect(
        createNewMatch({
          winner_team_id: team1Id,
          loser_team_id: team1Id,
          played_at: new Date().toISOString(),
          is_fanny: false,
        }),
      ).rejects.toThrow(InvalidMatchTeamsError);
    });
  });

  describe("getMatch", () => {
    it("returns match with team details", async () => {
      // [>]: Use the match created in the previous test.
      if (!testMatchId) {
        return; // [>]: Skip if match wasn't created.
      }

      const match = await getMatch(testMatchId);

      expect(match.match_id).toBe(testMatchId);
      expect(match.winner_team).toBeDefined();
      expect(match.loser_team).toBeDefined();
      expect(match.winner_team?.team_id).toBe(team1Id);
      expect(match.loser_team?.team_id).toBe(team2Id);
    });

    it("throws MatchNotFoundError when not found", async () => {
      await expect(getMatch(999999)).rejects.toThrow(MatchNotFoundError);
    });
  });

  describe("deleteMatch", () => {
    it("deletes an existing match", async () => {
      // [>]: Create a match specifically for deletion.
      const deleteMatch1 = await createNewMatch({
        winner_team_id: team1Id,
        loser_team_id: team2Id,
        played_at: new Date().toISOString(),
        is_fanny: false,
      });

      await deleteMatch(deleteMatch1.match_id);

      await expect(getMatch(deleteMatch1.match_id)).rejects.toThrow(
        MatchNotFoundError,
      );
    });
  });
});
