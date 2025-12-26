// [>]: Single team endpoints: GET, DELETE.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  parseIdParam,
  type RouteContext,
} from "@/lib/api/handle-request";
import { getTeam, deleteTeam } from "@/lib/services/teams";

type TeamRouteContext = RouteContext<"teamId">;

// [>]: GET /api/v1/teams/[teamId] - get team with stats and players.
export const GET = handleApiRequest(
  async (_request: NextRequest, context?: TeamRouteContext) => {
    const { teamId } = await context!.params;
    const id = parseIdParam(teamId, "teamId");
    const team = await getTeam(id);
    return NextResponse.json(team);
  },
);

// [>]: DELETE /api/v1/teams/[teamId] - delete team.
export const DELETE = handleApiRequest(
  async (_request: NextRequest, context?: TeamRouteContext) => {
    const { teamId } = await context!.params;
    const id = parseIdParam(teamId, "teamId");
    await deleteTeam(id);
    return new NextResponse(null, { status: 204 });
  },
);
