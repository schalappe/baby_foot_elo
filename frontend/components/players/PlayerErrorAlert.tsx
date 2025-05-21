/**
 * PlayerErrorAlert.tsx
 *
 * Displays an error or not-found alert specific to player detail pages.
 * Wraps EntityErrorAlert with player-specific messaging.
 *
 * Exports:
 *   - PlayerErrorAlert: React.FC for player error display.
 */
import React from "react";
import EntityErrorAlert from "@/components/common/EntityErrorAlert";

/**
 * Props for PlayerErrorAlert component.
 * @property error - Error message to display (optional)
 * @property notFound - Whether the player was not found (optional)
 */
interface PlayerErrorAlertProps {
  error?: string;
  notFound?: boolean;
}

/**
 * Displays an error or not-found alert for player detail pages.
 *
 * @param error - Error message to display (optional)
 * @param notFound - Whether the player was not found (optional)
 * @returns The rendered player error alert
 */
const PlayerErrorAlert: React.FC<PlayerErrorAlertProps> = ({
  error,
  notFound,
}) => (
  <EntityErrorAlert
    error={error}
    notFound={notFound}
    notFoundText={"Le joueur n'a pas été trouvé."}
  />
);

export default PlayerErrorAlert;
