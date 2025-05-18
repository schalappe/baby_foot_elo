import React from 'react';
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { BackendMatchWithEloResponse } from '@/types/match.types';

interface PlayerMatchesSectionProps {
  matches: BackendMatchWithEloResponse[];
  playerId: number;
  matchesLoading: boolean;
  currentPage: number;
  totalPages: number;
  totalMatches: number;
  handlePageChange: (page: number) => void;
}

const PlayerMatchesSection: React.FC<PlayerMatchesSectionProps> = ({
  matches,
  playerId,
  matchesLoading,
  currentPage,
  totalPages,
  totalMatches,
  handlePageChange,
}) => {
  if (matchesLoading) {
    return (
      <div className="p-6 space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="h-20 w-full rounded-xl bg-muted animate-pulse" />
        ))}
      </div>
    );
  }
  if (matches.length === 0) {
    return (
      <div className="p-6 text-center text-muted-foreground">
        Aucun match trouvé pour ce joueur.
      </div>
    );
  }
  return (
    <div className="space-y-8">
      {/* Group matches by date */}
      {Object.entries(
        matches.reduce((acc, match) => {
          const dateKey = new Date(match.played_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long' });
          if (!acc[dateKey]) acc[dateKey] = [];
          acc[dateKey].push(match);
          return acc;
        }, {} as Record<string, typeof matches>)
      ).map(([date, matchesForDate]) => (
        <div key={date}>
          <div className="text-md font-semibold mb-3 text-muted-foreground">{date}</div>
          <div className="flex flex-col gap-4">
            {matchesForDate.map((match) => {
              const isWinner = match.winner_team.player1.player_id === playerId || match.winner_team.player2.player_id === playerId;
              const playerTeam = isWinner ? match.winner_team : match.loser_team;
              const opponentTeam = isWinner ? match.loser_team : match.winner_team;
              const eloChange = match.elo_changes[playerId]?.difference ?? 0;
              const isFanny = match.is_fanny;
              const cardStyle = isWinner
                ? { background: 'var(--match-win-bg)', borderColor: 'var(--match-win-border)' }
                : { background: 'var(--match-lose-bg)', borderColor: 'var(--match-lose-border)' };
              return (
                <div
                  key={match.match_id}
                  className="relative border-2 shadow-lg rounded-xl overflow-hidden transition-colors min-h-[72px] w-full"
                  style={cardStyle}
                >
                  <div className="flex flex-row items-center justify-between gap-2 px-4 py-3">
                    {/* ELO Change */}
                    <div className="flex flex-col items-center min-w-[70px]">
                      <span className="font-extrabold text-3xl leading-none" style={{ color: eloChange >= 0 ? 'var(--win-text)' : 'var(--lose-text)' }}>{eloChange > 0 ? '+' : ''}{eloChange}</span>
                    </div>
                    {/* Teams */}
                    <div className="flex flex-1 flex-col gap-1 items-center">
                      <div className="flex items-center gap-2 justify-center">
                        {[playerTeam.player1, playerTeam.player2].map((p) => (
                          <span
                            key={p.player_id}
                            className={`rounded-full px-3 py-1 font-semibold text-sm transition-all duration-100 ${p.player_id === playerId ? 'bg-white text-black shadow font-bold border border-gray-200' : 'bg-neutral-800 text-neutral-200'}`}
                          >
                            {p.name}
                          </span>
                        ))}
                        <span className="mx-2 text-lg font-bold" style={{ color: 'var(--primary)'}}>VS</span>
                        {[opponentTeam.player1, opponentTeam.player2].map((p) => (
                          <span
                            key={p.player_id}
                            className="rounded-full px-3 py-1 font-semibold text-sm bg-neutral-800 text-neutral-200"
                          >
                            {p.name}
                          </span>
                        ))}
                      </div>
                    </div>
                    {/* Outcome: Only show Fanny icon if relevant */}
                    <div className="flex flex-col items-end min-w-[90px]">
                      {isFanny && (
                        <img
                          src={isWinner ? '/icons/fanny-victory.png' : '/icons/fanny-defeat.png'}
                          alt="Fanny icon"
                          className="w-12 h-12 rounded-full"
                        />
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex flex-col gap-2 px-4 py-3 border-t mt-8">
          <div className="text-sm text-muted-foreground mb-1">
            Affichage de <span className="font-medium">{Math.min((currentPage - 1) * 5 + 1, totalMatches)}</span> à <span className="font-medium">{Math.min(currentPage * 5, totalMatches)}</span> sur <span className="font-medium">{totalMatches}</span> matchs
          </div>
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  href="#"
                  aria-label="Page précédente"
                  aria-disabled={currentPage === 1}
                  onClick={e => {
                    e.preventDefault();
                    if (currentPage > 1) handlePageChange(currentPage - 1);
                  }}
                >
                </PaginationPrevious>
              </PaginationItem>
              {/* Page numbers logic with ellipsis */}
              {(() => {
                const items = [];
                // Show first page
                if (currentPage > 3) {
                  items.push(
                    <PaginationItem key={1}>
                      <PaginationLink
                        href="#"
                        isActive={currentPage === 1}
                        onClick={e => {
                          e.preventDefault();
                          handlePageChange(1);
                        }}
                      >
                        1
                      </PaginationLink>
                    </PaginationItem>
                  );
                  if (currentPage > 4) {
                    items.push(
                      <PaginationItem key="start-ellipsis">
                        <PaginationEllipsis />
                      </PaginationItem>
                    );
                  }
                }
                // Main page numbers
                const start = Math.max(1, currentPage - 2);
                const end = Math.min(totalPages, currentPage + 2);
                for (let page = start; page <= end; page++) {
                  items.push(
                    <PaginationItem key={page}>
                      <PaginationLink
                        href="#"
                        isActive={currentPage === page}
                        onClick={e => {
                          e.preventDefault();
                          handlePageChange(page);
                        }}
                      >
                        {page}
                      </PaginationLink>
                    </PaginationItem>
                  );
                }
                // Show end ellipsis and last page
                if (currentPage < totalPages - 2) {
                  if (currentPage < totalPages - 3) {
                    items.push(
                      <PaginationItem key="end-ellipsis">
                        <PaginationEllipsis />
                      </PaginationItem>
                    );
                  }
                  items.push(
                    <PaginationItem key={totalPages}>
                      <PaginationLink
                        href="#"
                        isActive={currentPage === totalPages}
                        onClick={e => {
                          e.preventDefault();
                          handlePageChange(totalPages);
                        }}
                      >
                        {totalPages}
                      </PaginationLink>
                    </PaginationItem>
                  );
                }
                return items;
              })()}
              <PaginationItem>
                <PaginationNext
                  href="#"
                  aria-label="Page suivante"
                  aria-disabled={currentPage === totalPages}
                  onClick={e => {
                    e.preventDefault();
                    if (currentPage < totalPages) handlePageChange(currentPage + 1);
                  }}
                >
                </PaginationNext>
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
};

export default PlayerMatchesSection;
