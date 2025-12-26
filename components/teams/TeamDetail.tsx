/**
 * TeamDetail.tsx
 *
 * Displays the detailed view for a single team, including stats and matches.
 * Fetches team data and renders TeamStatsCards and TeamMatchesSection.
 * Handles loading and error states.
 *
 * Exports:
 *   - TeamDetail: React.FC for team detail view.
 */
"use client";

import React, { useState, useEffect } from "react";
import { Team, TeamStatistics } from "@/types/team.types";
import { BackendMatchWithEloResponse } from "@/types/match.types";
import TeamStatsCards from "./TeamStatsCards";
import TeamMatchesSection from "./TeamMatchesSection";
import TeamLoadingSkeleton from "./TeamLoadingSkeleton";
import TeamErrorAlert from "./TeamErrorAlert";
import {
  getTeamStatistics,
  getTeamMatches,
} from "@/lib/api/client/teamService";

interface TeamDetailProps {
  teamId: number;
}

const ITEMS_PER_PAGE = 10;

const TeamDetail: React.FC<TeamDetailProps> = ({ teamId }) => {
  const [team, setTeam] = useState<Team | null>(null);
  const [stats, setStats] = useState<TeamStatistics | null>(null);
  const [matches, setMatches] = useState<BackendMatchWithEloResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [matchesLoading, setMatchesLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalMatches, setTotalMatches] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);
    getTeamStatistics(teamId)
      .then((data) => {
        if (!isMounted) return;
        setStats(data);
        // [>]: Build team object from statistics response.
        setTeam({
          team_id: data.team_id,
          global_elo: data.global_elo,
          player1_id: data.player1_id,
          player2_id: data.player2_id,
          created_at: data.created_at,
          player1: data.player1,
          player2: data.player2,
          last_match_at: data.last_match_at,
          matches_played: data.matches_played,
          wins: data.wins,
          losses: data.losses,
          win_rate: data.win_rate,
        });
      })
      .catch(() => {
        if (!isMounted) return;
        setError("Failed to fetch team statistics.");
      })
      .finally(() => {
        if (!isMounted) return;
        setLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, [teamId]);

  useEffect(() => {
    if (teamId) {
      const fetchTeamMatches = async () => {
        try {
          setMatchesLoading(true);
          setError(null);
          const offset = (currentPage - 1) * ITEMS_PER_PAGE;
          const matchesData = await getTeamMatches(teamId, {
            limit: ITEMS_PER_PAGE,
            skip: offset,
          });

          setMatches(matchesData);
          setTotalMatches((prev) => {
            const calculatedTotal =
              matchesData.length === ITEMS_PER_PAGE
                ? currentPage * ITEMS_PER_PAGE + 1
                : (currentPage - 1) * ITEMS_PER_PAGE + matchesData.length;
            return Math.max(prev, calculatedTotal);
          });
          setTotalPages(Math.ceil(totalMatches / ITEMS_PER_PAGE) || 1);
        } catch (err) {
          console.error("Failed to fetch team matches:", err);
          setError("Failed to fetch team matches.");
        } finally {
          setMatchesLoading(false);
        }
      };
      fetchTeamMatches();
    }
  }, [teamId, currentPage, totalMatches]);

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  if (loading) {
    return <TeamLoadingSkeleton />;
  }

  if (error) {
    return <TeamErrorAlert error={error} />;
  }
  if (!team) {
    return <TeamErrorAlert notFound />;
  }

  return (
    <div className="w-full max-w-6xl mx-auto p-4 text-foreground space-y-8">
      <h1 className="text-4xl sm:text-5xl font-bold text-center animate-hero-fade-in">
        {team.player1.name} & {team.player2.name}
      </h1>
      {stats && <TeamStatsCards stats={stats} />}
      <div className="mt-12 flex flex-col lg:flex-row gap-8">
        <div className="flex-1 w-full">
          <TeamMatchesSection
            matches={matches}
            teamId={teamId}
            matchesLoading={matchesLoading}
            currentPage={currentPage}
            totalPages={totalPages}
            totalMatches={totalMatches}
            handlePageChange={handlePageChange}
          />
        </div>
      </div>
    </div>
  );
};

export default TeamDetail;
