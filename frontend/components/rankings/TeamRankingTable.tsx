'use client';

import React, { useState, useMemo } from 'react';
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  VisibilityState,
  useReactTable,
  ColumnFiltersState,
} from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Team } from '@/types/team.types';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"

// --- Helper to get Team Name ---
const getTeamName = (team: Team): string => {
    const p1Name = team.player1?.name || `Player ${team.player1_id}`;
    const p2Name = team.player2?.name || `Player ${team.player2_id}`;
    // Sort names alphabetically for consistency
    return [p1Name, p2Name].sort().join(' & ');
};

// --- Column Definitions ---
export const columns: ColumnDef<Team>[] = [
  {
    accessorKey: 'rank',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Rank
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{row.getValue('rank') ?? '-'}</div>,
    enableSorting: true,
  },
  {
    // Custom accessor for team name derived from players
    id: 'teamName',
    accessorFn: (row) => getTeamName(row),
    header: 'Team',
    cell: ({ row }) => <div>{getTeamName(row.original)}</div>,
    enableSorting: false, // Sorting by combined name might be complex/less useful
  },
  {
    accessorKey: 'global_elo',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Elo
        <ArrowUpDown className="ml-2 h-4 w-4" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-right">{Math.round(row.getValue('global_elo'))}</div>,
    filterFn: (row, columnId, filterValue) => {
        const range = filterValue as [number | undefined, number | undefined];
        if (!Array.isArray(range)) {
            return true;
        }
        const [minElo, maxElo] = range;
        const elo = row.getValue('global_elo') as number;
        if (typeof elo !== 'number') {
            return false;
        }
        const minCheck = minElo === undefined || elo >= minElo;
        const maxCheck = maxElo === undefined || elo <= maxElo;
        return minCheck && maxCheck;
     },
  },
];

// --- Component Props Interface ---
interface TeamRankingTableProps {
  data: Team[];
  isLoading: boolean;
  error: Error | null;
}

// --- TeamRankingTable Component ---
export function TeamRankingTable({ data = [], isLoading, error }: TeamRankingTableProps) {
  const [sorting, setSorting] = useState<SortingState>([{ id: 'rank', desc: false }]); // Default sort by rank ascending
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});

  const memoizedData = useMemo(() => data, [data]);

  const table = useReactTable({
    data: memoizedData,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      globalFilter,
      columnVisibility,
      rowSelection,
    },
    initialState: {
        pagination: {
            pageSize: 10,
        }
    }
  });

  return (
    <div className="w-full">
      {/* --- Filters --- */}
      <div className="flex flex-wrap items-center gap-4 py-4">
        <Input
          placeholder="Filter by player name..."
          value={globalFilter ?? ''}
          onChange={(event) => setGlobalFilter(event.target.value)}
          className="max-w-xs flex-grow"
        />
        <Input
          placeholder="Min Elo"
          type="number"
          value={(table.getColumn('global_elo')?.getFilterValue() as [number, number])?.[0] ?? ''}
          onChange={(event) => {
            const value = event.target.value;
            const currentFilter = table.getColumn('global_elo')?.getFilterValue() as [number | undefined, number | undefined] | undefined;
            const minElo = value === '' ? undefined : Number(value);
            const maxElo = currentFilter?.[1];
            table.getColumn('global_elo')?.setFilterValue([minElo, maxElo]);
          }}
          className="max-w-[100px]"
        />
        <Input
          placeholder="Max Elo"
          type="number"
          value={(table.getColumn('global_elo')?.getFilterValue() as [number, number])?.[1] ?? ''}
          onChange={(event) => {
            const value = event.target.value;
            const currentFilter = table.getColumn('global_elo')?.getFilterValue() as [number | undefined, number | undefined] | undefined;
            const minElo = currentFilter?.[0];
            const maxElo = value === '' ? undefined : Number(value);
            table.getColumn('global_elo')?.setFilterValue([minElo, maxElo]);
          }}
          className="max-w-[100px]"
        />
      </div>

      {/* --- Table --- */}
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: table.getState().pagination.pageSize }).map((_, i) => (
                <TableRow key={`skeleton-${i}`}>
                  {columns.map((col, j) => (
                    <TableCell key={`skeleton-cell-${i}-${j}`}>
                      <Skeleton className="h-6 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : error ? (
                 <TableRow>
                    <TableCell colSpan={columns.length} className="h-24 text-center">
                         <Alert variant="destructive">
                            <AlertCircle className="h-4 w-4" />
                            <AlertTitle>Error Fetching Data</AlertTitle>
                            <AlertDescription>
                            {error.message || "Could not load team rankings."}
                            </AlertDescription>
                        </Alert>
                    </TableCell>
                 </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.original.team_id} // Use team_id for key
                  data-state={row.getIsSelected() && 'selected'}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* --- Pagination --- */}
      <div className="flex items-center justify-between space-x-2 py-4">
         <div className="flex-1 text-sm text-muted-foreground">
            {/* Selection count might not be needed for teams */}
         </div>
         <Pagination>
            <PaginationContent>
               <PaginationItem>
                  <PaginationPrevious
                     href="#"
                     onClick={(e) => { e.preventDefault(); table.previousPage(); }}
                     className={!table.getCanPreviousPage() ? "pointer-events-none opacity-50" : "cursor-pointer"}
                     aria-disabled={!table.getCanPreviousPage()}
                  />
               </PaginationItem>
               {/* TODO: Add page number links */}
               <PaginationItem>
                  <PaginationNext
                     href="#"
                     onClick={(e) => { e.preventDefault(); table.nextPage(); }}
                     className={!table.getCanNextPage() ? "pointer-events-none opacity-50" : "cursor-pointer"}
                     aria-disabled={!table.getCanNextPage()}
                  />
               </PaginationItem>
            </PaginationContent>
         </Pagination>
       </div>
    </div>
  );
}
