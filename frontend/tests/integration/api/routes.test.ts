// [>]: Integration tests for API route handlers.
// Tests the complete request/response flow using Next.js route handlers.
// Skipped when NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY are not set.

import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { NextRequest } from "next/server";

// [>]: Import route handlers.
import { GET as healthGet } from "@/app/api/v1/health/route";
import {
  GET as playersGet,
  POST as playersPost,
} from "@/app/api/v1/players/route";
import {
  GET as playerGet,
  PUT as playerPut,
  DELETE as playerDelete,
} from "@/app/api/v1/players/[playerId]/route";
import { GET as teamsGet, POST as teamsPost } from "@/app/api/v1/teams/route";
import {
  GET as teamGet,
} from "@/app/api/v1/teams/[teamId]/route";
import {
  GET as matchesGet,
  POST as matchesPost,
} from "@/app/api/v1/matches/route";
import {
  GET as matchGet,
  DELETE as matchDelete,
} from "@/app/api/v1/matches/[matchId]/route";
import type { RouteContext } from "@/lib/api/handle-request";

// [>]: Check if Supabase env vars are configured.
const hasSupabaseConfig =
  !!process.env.NEXT_PUBLIC_SUPABASE_URL &&
  !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

// [>]: Helper to create a mock NextRequest.
function createRequest(
  url: string,
  options: { method?: string; body?: object } = {},
): NextRequest {
  const { method = "GET", body } = options;
  return new NextRequest(`http://localhost${url}`, {
    method,
    body: body ? JSON.stringify(body) : undefined,
    headers: body ? { "Content-Type": "application/json" } : {},
  });
}

// [>]: Helper to create a mock route context with params.
function createContext<T extends Record<string, string>>(
  params: T,
): RouteContext {
  return { params: Promise.resolve(params) };
}

describe.skipIf(!hasSupabaseConfig)("API Route Handlers", () => {
  let testPlayerId: number | null = null;
  let testPlayer2Id: number | null = null;
  let testPlayer3Id: number | null = null;
  let testPlayer4Id: number | null = null;
  let testTeamId: number | null = null;
  let testTeam2Id: number | null = null;
  let testMatchId: number | null = null;

  afterAll(async () => {
    // [>]: Clean up test data.
    if (testMatchId) {
      try {
        await matchDelete(
          createRequest(`/api/v1/matches/${testMatchId}`, { method: "DELETE" }),
          createContext({ matchId: String(testMatchId) }),
        );
      } catch {
        // [>]: Ignore cleanup errors.
      }
    }

    // [>]: Delete players (this also cascades to teams).
    const playerIds = [
      testPlayerId,
      testPlayer2Id,
      testPlayer3Id,
      testPlayer4Id,
    ].filter(Boolean);
    for (const id of playerIds) {
      try {
        await playerDelete(
          createRequest(`/api/v1/players/${id}`, { method: "DELETE" }),
          createContext({ playerId: String(id) }),
        );
      } catch {
        // [>]: Ignore cleanup errors.
      }
    }
  }, 30000);

  describe("Health endpoint", () => {
    it("returns status ok", async () => {
      const response = await healthGet();
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.status).toBe("ok");
    });
  });

  describe("Player endpoints", () => {
    // [>]: Increased timeout because createNewPlayer creates teams with all existing players.
    it("POST /players creates a player", async () => {
      const timestamp = Date.now();
      const request = createRequest("/api/v1/players", {
        method: "POST",
        body: { name: `API Test Player ${timestamp}`, global_elo: 1000 },
      });

      const response = await playersPost(request);
      const data = await response.json();

      expect(response.status).toBe(201);
      expect(data.name).toBe(`API Test Player ${timestamp}`);
      expect(data.player_id).toBeTypeOf("number");

      testPlayerId = data.player_id;
    }, 30000);

    it("POST /players returns 422 for invalid data", async () => {
      const request = createRequest("/api/v1/players", {
        method: "POST",
        body: { name: "", global_elo: 1000 }, // [>]: Empty name is invalid.
      });

      const response = await playersPost(request);
      const data = await response.json();

      expect(response.status).toBe(422);
      expect(data.detail).toBeDefined();
    });

    it("GET /players returns player list", async () => {
      const request = createRequest("/api/v1/players");
      const response = await playersGet(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
    });

    it("GET /players/[id] returns player details", async () => {
      if (!testPlayerId) return;

      const response = await playerGet(
        createRequest(`/api/v1/players/${testPlayerId}`),
        createContext({ playerId: String(testPlayerId) }),
      );
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.player_id).toBe(testPlayerId);
    });

    it("GET /players/[id] returns 404 for non-existent player", async () => {
      const response = await playerGet(
        createRequest("/api/v1/players/999999"),
        createContext({ playerId: "999999" }),
      );
      const data = await response.json();

      expect(response.status).toBe(404);
      expect(data.detail).toContain("not found");
    });

    it("GET /players/[id] returns 422 for invalid player ID", async () => {
      const response = await playerGet(
        createRequest("/api/v1/players/abc"),
        createContext({ playerId: "abc" }),
      );
      const data = await response.json();

      expect(response.status).toBe(422);
      expect(data.detail).toContain("Invalid playerId");
    });

    it("PUT /players/[id] updates player", async () => {
      if (!testPlayerId) return;

      const request = createRequest(`/api/v1/players/${testPlayerId}`, {
        method: "PUT",
        body: { name: `Updated Player ${Date.now()}` },
      });

      const response = await playerPut(
        request,
        createContext({ playerId: String(testPlayerId) }),
      );
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.name).toContain("Updated Player");
    });
  });

  describe("Team endpoints", () => {
    // [>]: Increased timeout for creating 3 players with team generation.
    beforeAll(async () => {
      // [>]: Create additional players for team testing.
      const timestamp = Date.now();
      const p2 = await playersPost(
        createRequest("/api/v1/players", {
          method: "POST",
          body: { name: `API Test P2 ${timestamp}`, global_elo: 1000 },
        }),
      );
      const p3 = await playersPost(
        createRequest("/api/v1/players", {
          method: "POST",
          body: { name: `API Test P3 ${timestamp}`, global_elo: 1000 },
        }),
      );
      const p4 = await playersPost(
        createRequest("/api/v1/players", {
          method: "POST",
          body: { name: `API Test P4 ${timestamp}`, global_elo: 1000 },
        }),
      );

      const p2Data = await p2.json();
      const p3Data = await p3.json();
      const p4Data = await p4.json();

      testPlayer2Id = p2Data.player_id;
      testPlayer3Id = p3Data.player_id;
      testPlayer4Id = p4Data.player_id;
    }, 90000);

    it("POST /teams creates a team", async () => {
      if (!testPlayerId || !testPlayer2Id) return;

      const request = createRequest("/api/v1/teams", {
        method: "POST",
        body: {
          player1_id: testPlayerId,
          player2_id: testPlayer2Id,
          global_elo: 1000,
        },
      });

      const response = await teamsPost(request);
      const data = await response.json();

      expect(response.status).toBe(201);
      expect(data.team_id).toBeTypeOf("number");

      testTeamId = data.team_id;
    });

    it("POST /teams returns 422 for same players", async () => {
      if (!testPlayerId) return;

      const request = createRequest("/api/v1/teams", {
        method: "POST",
        body: {
          player1_id: testPlayerId,
          player2_id: testPlayerId,
          global_elo: 1000,
        },
      });

      const response = await teamsPost(request);
      const data = await response.json();

      expect(response.status).toBe(422);
      expect(data.detail).toBeDefined();
    });

    it("GET /teams returns team list", async () => {
      const request = createRequest("/api/v1/teams");
      const response = await teamsGet(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
    });

    it("GET /teams/[id] returns team details", async () => {
      if (!testTeamId) return;

      const response = await teamGet(
        createRequest(`/api/v1/teams/${testTeamId}`),
        createContext({ teamId: String(testTeamId) }),
      );
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.team_id).toBe(testTeamId);
    });
  });

  describe("Match endpoints", () => {
    beforeAll(async () => {
      // [>]: Create a second team for match testing.
      if (!testPlayer3Id || !testPlayer4Id) return;

      const request = createRequest("/api/v1/teams", {
        method: "POST",
        body: {
          player1_id: testPlayer3Id,
          player2_id: testPlayer4Id,
          global_elo: 1000,
        },
      });

      const response = await teamsPost(request);
      const data = await response.json();
      testTeam2Id = data.team_id;
    }, 30000);

    it("POST /matches creates a match with ELO updates", async () => {
      if (!testTeamId || !testTeam2Id) return;

      const request = createRequest("/api/v1/matches", {
        method: "POST",
        body: {
          winner_team_id: testTeamId,
          loser_team_id: testTeam2Id,
          played_at: new Date().toISOString(),
          is_fanny: false,
          notes: "API test match",
        },
      });

      const response = await matchesPost(request);
      const data = await response.json();

      expect(response.status).toBe(201);
      expect(data.match_id).toBeTypeOf("number");
      expect(data.elo_changes).toBeDefined();
      expect(Object.keys(data.elo_changes).length).toBe(4);

      testMatchId = data.match_id;
    });

    it("GET /matches returns match list", async () => {
      const request = createRequest("/api/v1/matches");
      const response = await matchesGet(request);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(Array.isArray(data)).toBe(true);
    });

    it("GET /matches/[id] returns match details", async () => {
      if (!testMatchId) return;

      const response = await matchGet(
        createRequest(`/api/v1/matches/${testMatchId}`),
        createContext({ matchId: String(testMatchId) }),
      );
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.match_id).toBe(testMatchId);
    });
  });
});
