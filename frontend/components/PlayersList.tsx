import React, { useState, useEffect, useMemo, useCallback } from 'react';

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
  const [sortKey, setSortKey] = useState<SortKey>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
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
      if (a[sortKey] < b[sortKey]) return sortOrder === 'asc' ? -1 : 1;
      if (a[sortKey] > b[sortKey]) return sortOrder === 'asc' ? 1 : -1;
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

  const getSortIndicator = (key: SortKey) => {
    if (sortKey === key) {
      return sortOrder === 'asc' ? ' ▲' : ' ▼';
    }
    return '';
  };

  if (loading) return <div className="text-center p-4">Chargement des joueurs...</div>;
  if (error) return <div className="text-center p-4 text-red-500">Erreur: {error}</div>;

  return (
    <div className="container mx-auto p-4 bg-white dark:bg-zinc-900 rounded shadow">
      <h2 className="text-2xl font-semibold mb-4 text-zinc-800 dark:text-zinc-100">Liste des Joueurs</h2>
      
      <div className="mb-4">
        <input
          type="text"
          placeholder="Rechercher un joueur..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1); // Reset to first page on search
          }}
          className="w-full p-2 border border-gray-300 dark:border-zinc-600 rounded bg-white dark:bg-zinc-700 text-black dark:text-white"
        />
      </div>

      {paginatedPlayers.length === 0 && !loading ? (
        <p className="text-zinc-600 dark:text-zinc-400">Aucun joueur trouvé.</p>
      ) : (
        <table className="min-w-full divide-y divide-gray-200 dark:divide-zinc-700">
          <thead className="bg-gray-50 dark:bg-zinc-800">
            <tr>
              <th onClick={() => handleSort('name')} className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-zinc-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-700">
                Nom{getSortIndicator('name')}
              </th>
              <th onClick={() => handleSort('elo')} className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-zinc-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-700">
                ELO{getSortIndicator('elo')}
              </th>
              <th onClick={() => handleSort('matches_played')} className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-zinc-300 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-zinc-700">
                Matchs Joués{getSortIndicator('matches_played')}
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-zinc-300 uppercase tracking-wider">Victoires</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-zinc-300 uppercase tracking-wider">Défaites</th>
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-zinc-800 divide-y divide-gray-200 dark:divide-zinc-700">
            {paginatedPlayers.map((player) => (
              <tr key={player.id} className="hover:bg-gray-50 dark:hover:bg-zinc-700">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-zinc-100">{player.name}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-zinc-300">{player.elo}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-zinc-300">{player.matches_played}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-500 dark:text-green-400">{player.wins}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-500 dark:text-red-400">{player.losses}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {totalPages > 1 && (
        <div className="py-3 flex items-center justify-between">
          <div className="flex-1 flex justify-between sm:hidden">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-zinc-600 text-sm font-medium rounded-md text-gray-700 dark:text-zinc-300 bg-white dark:bg-zinc-800 hover:bg-gray-50 dark:hover:bg-zinc-700 disabled:opacity-50"
            >
              Précédent
            </button>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-zinc-600 text-sm font-medium rounded-md text-gray-700 dark:text-zinc-300 bg-white dark:bg-zinc-800 hover:bg-gray-50 dark:hover:bg-zinc-700 disabled:opacity-50"
            >
              Suivant
            </button>
          </div>
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700 dark:text-zinc-300">
                Page <span className="font-medium">{currentPage}</span> sur <span className="font-medium">{totalPages}</span>
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button
                  onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-sm font-medium text-gray-500 dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-700 disabled:opacity-50"
                >
                  <span className="sr-only">Précédent</span>
                  &lt;
                </button>
                <button
                  onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-zinc-600 bg-white dark:bg-zinc-800 text-sm font-medium text-gray-500 dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-700 disabled:opacity-50"
                >
                  <span className="sr-only">Suivant</span>
                  &gt;
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlayersList;
