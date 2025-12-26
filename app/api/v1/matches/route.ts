// [>]: Match collection endpoints: GET list, POST create.

import { NextRequest, NextResponse } from "next/server";

import {
  handleApiRequest,
  getNumericParam,
  getBooleanParam,
} from "@/lib/api/handle-request";
import { getMatches, createNewMatch } from "@/lib/services/matches";
import { MatchCreateSchema } from "@/lib/types/schemas/match";

// [>]: GET /api/v1/matches - list matches with filtering.
export const GET = handleApiRequest(async (request: NextRequest) => {
  const { searchParams } = new URL(request.url);

  const skip = getNumericParam(searchParams, "skip", 0);
  const limit = getNumericParam(searchParams, "limit", 100);
  const teamIdParam = searchParams.get("team_id");
  const teamId = teamIdParam ? Number(teamIdParam) : undefined;
  const startDate = searchParams.get("start_date") ?? undefined;
  const endDate = searchParams.get("end_date") ?? undefined;
  const isFanny = getBooleanParam(searchParams, "is_fanny");

  const matches = await getMatches({
    skip,
    limit,
    teamId,
    startDate,
    endDate,
    isFanny,
  });

  return NextResponse.json(matches);
});

// [>]: POST /api/v1/matches - create match with ELO updates.
export const POST = handleApiRequest(async (request: NextRequest) => {
  const body = await request.json();
  const validated = MatchCreateSchema.parse(body);
  const match = await createNewMatch(validated);
  return NextResponse.json(match, { status: 201 });
});
