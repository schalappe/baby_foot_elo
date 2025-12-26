/**
 * TeamStatsCards.tsx
 *
 * Displays a statistics card for a team. Wraps EntityStatsCards for team-specific stats.
 * Used in team detail pages.
 *
 * Exports:
 *   - TeamStatsCards: React.FC for team statistics display.
 */
import React from "react";
import EntityStatsCards from "../common/EntityStatsCards";
import { TeamStatistics } from "@/types/team.types";

/**
 * Props for TeamStatsCards component.
 * @property stats - Team statistics object
 */
interface TeamStatsCardsProps {
  stats: TeamStatistics;
}

/**
 * Displays a statistics card for a team. Wraps EntityStatsCards for team-specific stats.
 *
 * @param stats - Team statistics object
 * @returns The rendered team statistics card
 */
const TeamStatsCards: React.FC<TeamStatsCardsProps> = ({ stats }) => (
  <EntityStatsCards stats={stats} />
);

export default TeamStatsCards;
