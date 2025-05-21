import React from 'react';
import EntityStatsCards from '@/components/common/EntityStatsCards';
import { TeamStatistics } from '@/types/team.types';

interface TeamStatsCardsProps {
  stats: TeamStatistics;
}

const TeamStatsCards: React.FC<TeamStatsCardsProps> = ({ stats }) => (
  <EntityStatsCards stats={stats} entityType="team" />
);

export default TeamStatsCards;
