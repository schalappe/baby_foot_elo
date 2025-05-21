/**
 * TeamErrorAlert.tsx
 *
 * Displays an error or not-found alert specific to team detail pages.
 * Wraps EntityErrorAlert with team-specific messaging.
 *
 * Exports:
 *   - TeamErrorAlert: React.FC for team error display.
 */
import React from "react";
import EntityErrorAlert from "@/components/common/EntityErrorAlert";

interface TeamErrorAlertProps {
  error?: string;
  notFound?: boolean;
}

const TeamErrorAlert: React.FC<TeamErrorAlertProps> = ({ error, notFound }) => (
  <EntityErrorAlert
    error={error}
    notFound={notFound}
    notFoundText={"L'équipe n'a pas été trouvée."}
  />
);

export default TeamErrorAlert;
