/**
 * EntityMatchesSection.tsx
 *
 * Displays a paginated matches section for player/team entity pages.
 * Used to show a list of matches with pagination controls in entity detail views.
 *
 * Exports:
 *   - EntityMatchesSection: React.FC for paginated match lists.
 */
import React from "react";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "../ui/pagination";
import { BackendMatchWithEloResponse } from "@/types/match.types";

interface EntityMatchesSectionProps {
  matches: BackendMatchWithEloResponse[];
  matchesLoading: boolean;
  currentPage: number;
  totalPages: number;
  handlePageChange: (page: number) => void;
  notFoundText: string;
}

/**
 * Generic matches section for player/team entities with pagination.
 *
 * Parameters
 * ----------
 * matches : BackendMatchWithEloResponse[]
 *     Array of match objects.
 * matchesLoading : boolean
 *     Whether the matches are loading.
 * currentPage : number
 *     Current page number.
 * totalPages : number
 *     Total number of pages.
 * handlePageChange : function
 *     Callback to change the page.
 * notFoundText : string
 *     Text to display if no matches found.
 *
 * Returns
 * -------
 * JSX.Element
 *     The rendered matches section.
 */
const EntityMatchesSection: React.FC<EntityMatchesSectionProps> = ({
  matches,
  matchesLoading,
  currentPage,
  totalPages,
  handlePageChange,
  notFoundText,
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
        {notFoundText}
      </div>
    );
  }
  // Group matches by date
  const groupedMatches = Object.entries(
    matches.reduce(
      (acc, match) => {
        const dateKey = new Date(match.played_at).toLocaleDateString("fr-FR", {
          day: "numeric",
          month: "long",
        });
        if (!acc[dateKey]) acc[dateKey] = [];
        acc[dateKey].push(match);
        return acc;
      },
      {} as Record<string, typeof matches>,
    ),
  );

  return (
    <div className="space-y-8">
      {groupedMatches.map(([date, matchesForDate]) => (
        <div key={date}>
          <div className="font-semibold text-lg mb-2">{date}</div>
          <div className="space-y-4">
            {matchesForDate.map((match) => (
              <div
                key={match.match_id}
                className="bg-card rounded-lg shadow p-4 flex flex-col md:flex-row md:items-center md:justify-between"
              >
                <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4">
                  <span className="font-bold">Match #{match.match_id}</span>
                  {/* Add more match info here as needed */}
                </div>
                {/* Add more details, links, or actions as needed */}
              </div>
            ))}
          </div>
        </div>
      ))}
      <Pagination className="mt-6">
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => handlePageChange(Math.max(1, currentPage - 1))}
              aria-disabled={currentPage === 1}
            />
          </PaginationItem>
          {Array.from({ length: totalPages }, (_, i) => (
            <PaginationItem key={i + 1}>
              <PaginationLink
                isActive={i + 1 === currentPage}
                onClick={() => handlePageChange(i + 1)}
              >
                {i + 1}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationNext
              onClick={() =>
                handlePageChange(Math.min(totalPages, currentPage + 1))
              }
              aria-disabled={currentPage === totalPages}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default EntityMatchesSection;
