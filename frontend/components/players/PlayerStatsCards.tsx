import React from "react";
import EntityStatsCards from "@/components/common/EntityStatsCards";
import { PlayerStats } from "@/types/player.types";

interface PlayerStatsCardsProps {
  player: PlayerStats;
}

const PlayerStatsCards: React.FC<PlayerStatsCardsProps> = ({ player }) => (
  <EntityStatsCards stats={player} entityType="player" />
);

export default PlayerStatsCards;
