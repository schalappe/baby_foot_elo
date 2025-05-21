/**
 * players/[id]/page.tsx
 *
 * Displays detailed information about a specific player in the Baby Foot ELO app.
 *
 * - Fetches and renders player details based on dynamic route 'id'.
 * - Handles invalid or missing player IDs with error messaging.
 *
 * Usage: Routed to '/players/[id]' by Next.js.
 */
"use client";

import React from 'react';
import PlayerDetail from '@/components/players/PlayerDetail';
import { useParams } from 'next/navigation';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

const PlayerDetailPage: React.FC = () => {
  const params = useParams();
  const playerIdString = params?.id;

  let playerId: number | undefined = undefined;

  if (typeof playerIdString === 'string') {
    const parsedId = parseInt(playerIdString, 10);
    if (!isNaN(parsedId)) {
      playerId = parsedId;
    }
  }

  if (playerId === undefined) {
    return (
      <div className="container mx-auto p-4">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>Identifiant invalide.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <PlayerDetail playerId={playerId} />
    </div>
  );
};

export default PlayerDetailPage;
