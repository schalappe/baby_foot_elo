"use client";

import React from 'react';
import PlayersList from '@/components/players/PlayersList';

const PlayersPage: React.FC = () => {
  return (
    <div className="container mx-auto p-4">
      <PlayersList />
    </div>
  );
};

export default PlayersPage;
