/**
 * teams/[id]/page.tsx
 *
 * Displays detailed information about a specific team in the Baby Foot ELO app.
 *
 * - Fetches and renders team details based on dynamic route 'id'.
 * - Handles invalid or missing team IDs with error messaging.
 *
 * Usage: Routed to '/teams/[id]' by Next.js.
 */
"use client";

import React from "react";
import TeamDetail from "../../../components/teams/TeamDetail";
import { useParams } from "next/navigation";
import {
  Alert,
  AlertDescription,
  AlertTitle,
} from "../../../components/ui/alert";

const TeamDetailPage: React.FC = () => {
  const params = useParams();
  const teamIdString = params?.id;

  let teamId: number | undefined = undefined;

  if (typeof teamIdString === "string") {
    const parsedId = parseInt(teamIdString, 10);
    if (!isNaN(parsedId)) {
      teamId = parsedId;
    }
  }

  if (teamId === undefined) {
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
      <TeamDetail teamId={teamId} />
    </div>
  );
};

export default TeamDetailPage;
