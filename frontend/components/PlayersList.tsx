import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpDown, ArrowDown, ArrowUp } from 'lucide-react';

interface Player {
  id: number;
  name: string;
  elo: number;
  matches_played: number;
  wins: number;
  losses: number;
}

type SortKey = keyof Pick<Player, 'name' | 'elo' | 'matches_played'>;

const PlayersList: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortKey, setSortKey] = useState<SortKey>('elo'); // Default sort by ELO
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc'); // Default ELO descending
  const [currentPage, setCurrentPage] = useState<number>(1);
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchPlayers = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch('http://localhost:8000/api/players/');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Player[] = await response.json();
        setPlayers(data);
      } catch (err: any) {
        setError(err.message || 'Failed to fetch players.');
      }
      setLoading(false);
    };
    fetchPlayers();
  }, []);

  const filteredPlayers = useMemo(() => {
    return players.filter(player =>
      player.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [players, searchTerm]);

  const sortedPlayers = useMemo(() => {
    return [...filteredPlayers].sort((a, b) => {
      if (sortKey) {
        if (a[sortKey] < b[sortKey]) return sortOrder === 'asc' ? -1 : 1;
        if (a[sortKey] > b[sortKey]) return sortOrder === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }, [filteredPlayers, sortKey, sortOrder]);

  const paginatedPlayers = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    return sortedPlayers.slice(startIndex, startIndex + itemsPerPage);
  }, [sortedPlayers, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(sortedPlayers.length / itemsPerPage);

  const handleSort = useCallback((key: SortKey) => {
    if (sortKey === key) {
      setSortOrder(prevOrder => prevOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('asc');
    }
    setCurrentPage(1); // Reset to first page on sort
  }, [sortKey]);

  const getSortIcon = (key: SortKey) => {
    if (sortKey === key) {
      return sortOrder === 'asc' ? <ArrowUp className="ml-2 h-4 w-4 inline" /> : <ArrowDown className="ml-2 h-4 w-4 inline" />;
    }
    return <ArrowUpDown className="ml-2 h-4 w-4 inline opacity-50" />;
  };

  if (loading) return <div className="text-center p-4">Chargement des joueurs...</div>;
  if (error) return <div className="text-center p-4 text-red-500">Erreur: {error}</div>;

  return (
    <Card className="container mx-auto p-4">
      <CardHeader>
        <CardTitle className="text-2xl font-semibold mb-4">Liste des Joueurs</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Input
            type="text"
            placeholder="Rechercher un joueur..."
            value={searchTerm}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1); // Reset to first page on search
            }}
            className="w-full"
          />
        </div>

        {paginatedPlayers.length === 0 && !loading ? (
          <p className="text-zinc-600 dark:text-zinc-400">Aucun joueur trouvé.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead onClick={() => handleSort('name')} className="cursor-pointer hover:bg-muted/50">
                  Nom{getSortIcon('name')}
                </TableHead>
                <TableHead onClick={() => handleSort('elo')} className="cursor-pointer hover:bg-muted/50">
                  ELO{getSortIcon('elo')}
                </TableHead>
                <TableHead onClick={() => handleSort('matches_played')} className="cursor-pointer hover:bg-muted/50">
                  Matchs Joués{getSortIcon('matches_played')}
                </TableHead>
                <TableHead>Victoires</TableHead>
                <TableHead>Défaites</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedPlayers.map((player) => (
                <TableRow key={player.id}>
                  <TableCell className="font-medium">{player.name}</TableCell>
                  <TableCell>{player.elo}</TableCell>
                  <TableCell>{player.matches_played}</TableCell>
                  <TableCell className="text-green-500 dark:text-green-400">{player.wins}</TableCell>
                  <TableCell className="text-red-500 dark:text-red-400">{player.losses}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}

        {totalPages > 1 && (
          <div className="py-3 flex items-center justify-between">
            <div className="flex-1 flex justify-between sm:hidden">
              <Button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                variant="outline"
              >
                Précédent
              </Button>
              <Button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                variant="outline"
                className="ml-3"
              >
                Suivant
              </Button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-muted-foreground">
                  Page <span className="font-medium">{currentPage}</span> sur <span className="font-medium">{totalPages}</span>
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <Button
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    disabled={currentPage === 1}
                    variant="outline"
                    size="icon"
                    className="rounded-r-none"
                  >
                    <span className="sr-only">Précédent</span>
                    &lt;
                  </Button>
                  <Button
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    disabled={currentPage === totalPages}
                    variant="outline"
                    size="icon"
                    className="rounded-l-none"
                  >
                    <span className="sr-only">Suivant</span>
                    &gt;
                  </Button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default PlayersList;
