import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowUpDown, ArrowDown, ArrowUp, AlertCircle, Loader2 } from 'lucide-react';
import { getPlayers, Player } from '@/services/playerService';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogDescription,
} from "@/components/ui/dialog";
import { PlayerRegistrationForm } from "./PlayerRegistrationForm";

type SortKey = keyof Pick<Player, 'name' | 'elo' | 'matches_played'>;

const PlayersList: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortKey, setSortKey] = useState<SortKey>('elo');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [isRegisterDialogOpen, setIsRegisterDialogOpen] = useState<boolean>(false);
  const itemsPerPage = 10;

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getPlayers();
      setPlayers(Array.isArray(data) ? data : []);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Erreur lors de la récupération des joueurs.';
      setError(errorMessage);
      setPlayers([]);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const handlePlayerRegistered = () => {
    setIsRegisterDialogOpen(false);
    fetchPlayers(); // Refresh the list
  };

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
    setCurrentPage(1);
  }, [sortKey]);

  const getSortIcon = (key: SortKey) => {
    if (sortKey === key) {
      return sortOrder === 'asc' ? <ArrowUp className="ml-2 h-4 w-4 inline" /> : <ArrowDown className="ml-2 h-4 w-4 inline" />;
    }
    return <ArrowUpDown className="ml-2 h-4 w-4 inline opacity-50" />;
  };

  if (loading) return (
    <div className="flex items-center justify-center p-10">
      <Loader2 className="h-8 w-8 animate-spin text-primary" />
      <span className="ml-2">Chargement des joueurs...</span>
    </div>
  );

  if (error) return (
    <Card className="container mx-auto p-4">
      <CardHeader>
        <CardTitle className="text-2xl font-semibold mb-4">Liste des Joueurs</CardTitle>
      </CardHeader>
      <CardContent>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </CardContent>
    </Card>
  );

  return (
    <Card className="container mx-auto p-4">
      <CardHeader className="flex flex-row items-center justify-between pb-4">
        <CardTitle className="text-3xl font-bold">Liste des Joueurs</CardTitle>
        <Dialog open={isRegisterDialogOpen} onOpenChange={setIsRegisterDialogOpen}>
          <DialogTrigger asChild>
            <Button>Ajouter un Joueur</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Nouveau Joueur</DialogTitle>
              <DialogDescription>
                Entrez le nom du nouveau joueur.
              </DialogDescription>
            </DialogHeader>
            <PlayerRegistrationForm onPlayerRegistered={handlePlayerRegistered} />
          </DialogContent>
        </Dialog>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Input
            type="text"
            placeholder="Rechercher un joueur..."
            value={searchTerm}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
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
                  <TableCell className="font-medium">
                    <Link href={`/players/${player.id}`} className="hover:underline text-blue-600 dark:text-blue-400">
                      {player.name}
                    </Link>
                  </TableCell>
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
