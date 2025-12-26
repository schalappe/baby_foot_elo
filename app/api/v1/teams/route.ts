// [>]: Team collection endpoints: GET list, POST create.

import { NextRequest, NextResponse } from "next/server";

import { handleApiRequest, getNumericParam } from "@/lib/api/handle-request";
import { getAllTeamsWithStats, createNewTeam } from "@/lib/services/teams";
import { TeamCreateSchema } from "@/lib/types/schemas/team";

// [>]: GET /api/v1/teams - list all teams with stats.
export const GET = handleApiRequest(async (request: NextRequest) => {
  const { searchParams } = new URL(request.url);
  const skip = getNumericParam(searchParams, "skip", 0);
  const limit = getNumericParam(searchParams, "limit", 100);

  const teams = await getAllTeamsWithStats({ skip, limit });
  return NextResponse.json(teams);
});

// [>]: POST /api/v1/teams - create new team.
export const POST = handleApiRequest(async (request: NextRequest) => {
  const body = await request.json();
  const validated = TeamCreateSchema.parse(body);
  const team = await createNewTeam(validated);
  return NextResponse.json(team, { status: 201 });
});
