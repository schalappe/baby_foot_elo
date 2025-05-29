/**
 * PlayerMatchesSection.tsx
 *
 * Displays a paginated list of matches for a player, with stats and navigation.
 * Used in player detail pages to show match history.
 *
 * Exports:
 *   - PlayerMatchesSection: React.FC for player match list.
 */
import React from "react";
import {
  TrophyIcon,
  SkullIcon,
  PartyPopperIcon,
  CircleXIcon,
} from "lucide-react";
import Link from "next/link";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";
import { BackendMatchWithEloResponse } from "@/types/match.types";

/**
 * Props for PlayerMatchesSection component.
 * @property matches - Array of match objects for the player
 * @property playerId - The ID of the player
 * @property matchesLoading - Whether the matches are loading
 * @property currentPage - Current page number
 * @property totalPages - Total number of pages
 * @property totalMatches - Total number of matches
 * @property handlePageChange - Callback to change the page
 */
interface PlayerMatchesSectionProps {
  matches: BackendMatchWithEloResponse[];
  playerId: number;
  matchesLoading: boolean;
  currentPage: number;
  totalPages: number;
  totalMatches: number;
  handlePageChange: (page: number) => void;
}

/**
 * Displays a paginated list of matches for a player, with stats and navigation.
 *
 * @param matches - Array of match objects for the player
 * @param playerId - The ID of the player
 * @param matchesLoading - Whether the matches are loading
 * @param currentPage - Current page number
 * @param totalPages - Total number of pages
 * @param totalMatches - Total number of matches
 * @param handlePageChange - Callback to change the page
 * @returns The rendered player matches section
 */
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
          <div
            key={i}
            className="h-20 w-full rounded-xl bg-muted animate-pulse"
          />
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
        matches.reduce(
          (acc, match) => {
            const dateKey = new Date(match.played_at).toLocaleDateString(
              "fr-FR",
              { day: "numeric", month: "long" },
            );
            if (!acc[dateKey]) acc[dateKey] = [];
            acc[dateKey].push(match);
            return acc;
          },
          {} as Record<string, typeof matches>,
        ),
      ).map(([date, matchesForDate]) => (
        <div key={date}>
          <div className="text-md font-semibold mb-3 text-muted-foreground">
            {date}
          </div>
          <div className="flex flex-col gap-4">
            {matchesForDate.map((match) => {
              const isWinner =
                match.winner_team.player1.player_id === playerId ||
                match.winner_team.player2.player_id === playerId;
              const playerTeam = isWinner
                ? match.winner_team
                : match.loser_team;
              const opponentTeam = isWinner
                ? match.loser_team
                : match.winner_team;
              const eloChange = match.elo_changes[playerId]?.difference ?? 0;
              const isFanny = match.is_fanny;
              const cardStyle = isWinner
                ? {
                    background: "var(--secondary)",
                    borderColor: "var(--match-win-border)",
                  }
                : {
                    background: "var(--secondary)",
                    borderColor: "var(--match-lose-border)",
                  };
              return (
                <div
                  key={match.match_id}
                  className="relative border-2 shadow-lg rounded-xl overflow-hidden transition-colors min-h-[72px] w-full"
                  style={cardStyle}
                >
                  <div className="flex flex-row items-center justify-between gap-2 px-4 py-3">
                    {/* ELO Change */}
                    <div className="flex flex-col items-center min-w-[70px]">
                      <span
                        className="font-extrabold text-3xl leading-none"
                        style={{
                          color:
                            eloChange >= 0
                              ? "var(--match-win-border)"
                              : "var(--match-lose-border)",
                        }}
                      >
                        {eloChange > 0 ? "+" : ""}
                        {eloChange}
                      </span>
                    </div>
                    {/* Teams */}
                    <div className="flex flex-1 flex-col gap-1 items-center">
                      <div className="flex items-center gap-2 justify-center">
                        {/* Player's team clickable */}
                        <Link
                          href={`/teams/${playerTeam.team_id}`}
                          className="flex items-center gap-2 group"
                          prefetch={false}
                        >
                          <span
                            className="px-4 py-2 text-lg font-semibold group-hover:underline"
                            style={{
                              color: isWinner
                                ? "var(--match-win-border)"
                                : "var(--match-lose-border)",
                            }}
                          >
                            {playerTeam.player1.name} &{" "}
                            {playerTeam.player2.name}
                          </span>
                        </Link>
                        <span
                          className="mx-2 text-lg font-bold"
                          style={{ color: "var(--primary)" }}
                        >
                          VS
                        </span>
                        {/* Opponent team clickable */}
                        <Link
                          href={`/teams/${opponentTeam.team_id}`}
                          className="flex items-center gap-2 group"
                          prefetch={false}
                        >
                          <span
                            className="px-4 py-2 text-lg font-semibold group-hover:underline"
                            style={{
                              color: isWinner
                                ? "var(--match-lose-border)"
                                : "var(--match-win-border)",
                            }}
                          >
                            {opponentTeam.player1.name} &{" "}
                            {opponentTeam.player2.name}
                          </span>
                        </Link>
                      </div>
                    </div>
                    {/* Outcome: Only show Fanny icon if relevant */}
                    <div className="flex flex-col items-end min-w-[90px]">
                      {isFanny && !isWinner && (
                        <SkullIcon
                          className="w-8 h-8"
                          style={{ color: "var(--match-lose-border)" }}
                        />
                      )}
                      {isFanny && isWinner && (
                        <PartyPopperIcon
                          className="w-8 h-8"
                          style={{ color: "var(--match-win-border)" }}
                        />
                      )}
                      {!isFanny && isWinner && (
                        <TrophyIcon
                          className="w-8 h-8"
                          style={{ color: "var(--match-win-border)" }}
                        />
                      )}
                      {!isFanny && !isWinner && (
                        <CircleXIcon
                          className="w-8 h-8"
                          style={{ color: "var(--match-lose-border)" }}
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
            Affichage de{" "}
            <span className="font-medium">
              {Math.min((currentPage - 1) * 5 + 1, totalMatches)}
            </span>{" "}
            à{" "}
            <span className="font-medium">
              {Math.min(currentPage * 5, totalMatches)}
            </span>{" "}
            sur <span className="font-medium">{totalMatches}</span> matchs
          </div>
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious
                  href="#"
                  aria-label="Page précédente"
                  aria-disabled={currentPage === 1}
                  onClick={(e) => {
                    e.preventDefault();
                    if (currentPage > 1) handlePageChange(currentPage - 1);
                  }}
                ></PaginationPrevious>
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
                        onClick={(e) => {
                          e.preventDefault();
                          handlePageChange(1);
                        }}
                      >
                        1
                      </PaginationLink>
                    </PaginationItem>,
                  );
                  if (currentPage > 4) {
                    items.push(
                      <PaginationItem key="start-ellipsis">
                        <PaginationEllipsis />
                      </PaginationItem>,
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
                        onClick={(e) => {
                          e.preventDefault();
                          handlePageChange(page);
                        }}
                      >
                        {page}
                      </PaginationLink>
                    </PaginationItem>,
                  );
                }
                // Show end ellipsis and last page
                if (currentPage < totalPages - 2) {
                  if (currentPage < totalPages - 3) {
                    items.push(
                      <PaginationItem key="end-ellipsis">
                        <PaginationEllipsis />
                      </PaginationItem>,
                    );
                  }
                  items.push(
                    <PaginationItem key={totalPages}>
                      <PaginationLink
                        href="#"
                        isActive={currentPage === totalPages}
                        onClick={(e) => {
                          e.preventDefault();
                          handlePageChange(totalPages);
                        }}
                      >
                        {totalPages}
                      </PaginationLink>
                    </PaginationItem>,
                  );
                }
                return items;
              })()}
              <PaginationItem>
                <PaginationNext
                  href="#"
                  aria-label="Page suivante"
                  aria-disabled={currentPage === totalPages}
                  onClick={(e) => {
                    e.preventDefault();
                    if (currentPage < totalPages)
                      handlePageChange(currentPage + 1);
                  }}
                ></PaginationNext>
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
};

export default PlayerMatchesSection;
