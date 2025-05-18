'use client';

import React, { useState, useMemo } from 'react';
import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  VisibilityState,
  useReactTable,
} from '@tanstack/react-table';
import { ArrowUpDown, ChevronDown, MoreHorizontal } from 'lucide-react';

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
import { Player } from '@/types/player.types';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle } from "lucide-react"
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"

// --- Column Definitions ---
export const columns: ColumnDef<Player>[] = [
  {
    accessorKey: 'name',
    header: () => (
      <Button variant="ghost">
        Nom
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{row.getValue('name')}</div>,
  },
  {
    accessorKey: 'global_elo',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Elo
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{row.getValue('global_elo')}</div>,
    filterFn: (row, columnId, filterValue) => {
        // Type guard for the filter value
        const range = filterValue as [number | undefined, number | undefined];
        if (!Array.isArray(range)) {
            return true;
        }
        const [minElo, maxElo] = range;

        // Ensure row value is a number
        const elo = row.getValue('global_elo') as number;
        if (typeof elo !== 'number') {
            return false;
        }

        const minCheck = minElo === undefined || elo >= minElo;
        const maxCheck = maxElo === undefined || elo <= maxElo;

        return minCheck && maxCheck;
    },
  },
  {
    accessorKey: 'matches_played',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Matchs joués
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{row.getValue('matches_played')}</div>,
  },
  {
    accessorKey: 'wins',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Victoires
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{row.getValue('wins')}</div>,
  },
  {
    accessorKey: 'losses',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Défaites
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{row.getValue('losses')}</div>,
  },
  {
    accessorKey: 'win_rate',
    header: ({ column }) => (
      <Button
        variant="ghost"
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
      >
        Taux de victoires
        <ArrowUpDown className="ml-2 h-2 w-2" />
      </Button>
    ),
    cell: ({ row }) => <div className="text-center">{Math.round(row.getValue('win_rate'))}%</div>,
  },
];

// --- Component Props Interface ---
interface PlayerRankingTableProps {
  data: Player[];
  isLoading: boolean;
  error: Error | null;
}

// --- PlayerRankingTable Component ---
export function PlayerRankingTable({ data = [], isLoading, error }: PlayerRankingTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [globalFilter, setGlobalFilter] = useState('');
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = useState({});

  // Memoize data to prevent unnecessary recalculations
  console.log("Data:", data);
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
            pageSize: 10, // Default page size
        }
    }
  });

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-4 py-4">
        <Input
          placeholder="Filter players by name..."
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
        {/* Add more filters (e.g., Select for period) here later */}
      </div>
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
              // Loading Skeleton
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
                            <AlertTitle>Erreur</AlertTitle>
                            <AlertDescription>
                            {error.message || "Impossible de charger le classement des joueurs."}
                            </AlertDescription>
                        </Alert>
                    </TableCell>
                 </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
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
                  Aucun résultat.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      {/* --- Pagination Controls --- */}
      <div className="flex items-center justify-between space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
           {/* Kept the selection count as it's useful, though not strictly pagination */}
           {table.getFilteredSelectedRowModel().rows.length} de{" "}
           {table.getFilteredRowModel().rows.length} ligne(s) sélectionnée(s).
        </div>
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  table.previousPage();
                }}
                className={!table.getCanPreviousPage() ? "pointer-events-none opacity-50" : "cursor-pointer"}
                aria-disabled={!table.getCanPreviousPage()}
              />
            </PaginationItem>
            <PaginationItem>
              <PaginationNext
                 href="#"
                 onClick={(e) => {
                    e.preventDefault();
                    table.nextPage();
                 }}
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
