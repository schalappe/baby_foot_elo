"use client";

import React from "react";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Team } from "@/types/team.types";
import { RankingTable } from "./common/RankingTable";

// --- Helper to get Team Name ---
const getTeamName = (team: Team): string => {
  const p1Name = team.player1?.name || `Player ${team.player1_id}`;
  const p2Name = team.player2?.name || `Player ${team.player2_id}`;
  // Sort names alphabetically for consistency
  return [p1Name, p2Name].sort().join(" & ");
};

// --- Column Definitions ---
export const columns: ColumnDef<Team>[] = [
  {
    accessorKey: "rank",
    header: ({}) => <Button variant="ghost">Rank</Button>,
    cell: ({ row }) => (
      <div className="text-center">{row.getValue("rank") ?? "-"}</div>
    ),
    enableSorting: true,
  },
  {
    // Custom accessor for team name derived from players
    id: "teamName",
    accessorFn: (row) => getTeamName(row),
    header: "Team",
    cell: ({ row }) => {
      const teamId = row.original.team_id;
      const teamName = getTeamName(row.original);
      return (
        <div className="text-center">
          <Link
            href={`/teams/${teamId}`}
            className="text-primary underline focus:outline-none"
          >
            {teamName}
          </Link>
        </div>
      );
    },
    enableSorting: false,
  },
  {
    accessorKey: "global_elo",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Elo
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-right">{Math.round(row.getValue("global_elo"))}</div>
    ),
  },
  {
    accessorKey: "matches_played",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Matchs joués
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-center">{row.getValue("matches_played")}</div>
    ),
  },
  {
    accessorKey: "wins",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Victoires
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-center">{row.getValue("wins")}</div>
    ),
  },
  {
    accessorKey: "losses",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Défaites
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-center">{row.getValue("losses")}</div>
    ),
  },
  {
    accessorKey: "win_rate",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Taux de victoires
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-center">{Math.round(row.getValue("win_rate"))}%</div>
    ),
  },
];

// --- Component Props Interface ---
interface TeamRankingTableProps {
  data: Team[];
  isLoading: boolean;
  error: Error | null;
}

// --- TeamRankingTable Component ---
export function TeamRankingTable({
  data = [],
  isLoading,
  error,
}: TeamRankingTableProps) {
  return (
    <>
      <RankingTable
        data={data}
        columns={columns}
        isLoading={isLoading}
        error={error}
      />
    </>
  );
}
