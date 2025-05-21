import React from "react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface EntityErrorAlertProps {
  error?: string;
  notFound?: boolean;
  notFoundText: string;
}

/**
 * Generic error alert for entity details (player, team, etc).
 *
 * Parameters
 * ----------
 * error : string, optional
 *     Error message to display.
 * notFound : boolean, optional
 *     If true, displays a not found message.
 * notFoundText : string
 *     The text to display when not found.
 *
 * Returns
 * -------
 * JSX.Element | null
 *     The rendered alert or null if no error.
 */
const EntityErrorAlert: React.FC<EntityErrorAlertProps> = ({
  error,
  notFound,
  notFoundText,
}) => {
  if (error) {
    return (
      <Alert variant="destructive" className="max-w-4xl mx-auto">
        <AlertTitle>Erreur</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }
  if (notFound) {
    return (
      <Alert variant="default" className="max-w-4xl mx-auto">
        <AlertTitle>Non Trouvé</AlertTitle>
        <AlertDescription>{notFoundText}</AlertDescription>
      </Alert>
    );
  }
  return null;
};

export default EntityErrorAlert;
