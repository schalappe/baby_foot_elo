/**
 * PlayerStatsCards.tsx
 *
 * Displays a statistics card for a player. Wraps EntityStatsCards for player-specific stats.
 * Used in player detail pages.
 *
 * Exports:
 *   - PlayerStatsCards: React.FC for player statistics display.
 */
import React from "react";
import EntityStatsCards from "@/components/common/EntityStatsCards";
import { PlayerStats } from "@/types/player.types";

/**
 * Props for PlayerStatsCards component.
 * @property player - Player statistics object
 */
interface PlayerStatsCardsProps {
  player: PlayerStats;
}

/**
 * Displays a statistics card for a player. Wraps EntityStatsCards for player-specific stats.
 *
 * @param player - Player statistics object
 * @returns The rendered player statistics card
 */
const PlayerStatsCards: React.FC<PlayerStatsCardsProps> = ({ player }) => (
  <EntityStatsCards stats={player} />
);

export default PlayerStatsCards;
