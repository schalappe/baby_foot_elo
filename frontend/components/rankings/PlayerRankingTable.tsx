"use client";

import React from "react";
import { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Player } from "@/types/player.types";
import Link from "next/link";
import { RankingTable } from "./common/RankingTable";

// --- Column Definitions ---
/**
 * Column definitions for the Player Ranking Table.
 *
 * - Player name is rendered as a clickable link to the player's profile page.
 * - Uses ShadCN UI components for styling and consistency.
 */
export const columns: ColumnDef<Player>[] = [
  {
    accessorKey: "name",
    header: () => <Button variant="ghost">Nom</Button>,
    cell: ({ row }) => {
      const playerId = row.original.player_id;
      const playerName = String(row.getValue("name"));
      return (
        <div className="text-center">
          <Link
            href={`/players/${playerId}`}
            className="text-primary underline focus:outline-none"
          >
            {playerName}
          </Link>
        </div>
      );
    },
  },
  {
    accessorKey: "global_elo",
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
      >
        Elo
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-center">{row.getValue("global_elo")}</div>
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
        <ArrowUpDown className="ml-2 h-2 w-2" />
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
        <ArrowUpDown className="ml-2 h-2 w-2" />
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
        <ArrowUpDown className="ml-2 h-2 w-2" />
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
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => (
      <div className="text-center">{Math.round(row.getValue("win_rate"))}%</div>
    ),
  },
];

// --- Component Props Interface ---
interface PlayerRankingTableProps {
  data: Player[];
  isLoading: boolean;
  error: Error | null;
}

// --- PlayerRankingTable Component ---
export function PlayerRankingTable({
  data = [],
  isLoading,
  error,
}: PlayerRankingTableProps) {
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
