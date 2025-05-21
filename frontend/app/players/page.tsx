/**
 * players/page.tsx
 *
 * Displays a list of all players in the Baby Foot ELO app.
 *
 * - Renders the PlayersList component.
 * - Used for browsing and managing players.
 *
 * Usage: Routed to '/players' by Next.js.
 */
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
