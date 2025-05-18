import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface TeamErrorAlertProps {
  error?: string;
  notFound?: boolean;
}

/**
 * Alert component for displaying team-related errors.
 *
 * Parameters
 * ----------
 * error : string, optional
 *     Error message to display.
 * notFound : boolean, optional
 *     If true, displays a not found message for the team.
 *
 * Returns
 * -------
 * JSX.Element | null
 *     The rendered alert or null if no error.
 */
const TeamErrorAlert: React.FC<TeamErrorAlertProps> = ({ error, notFound }) => {
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
        <AlertDescription>L'équipe n'a pas été trouvée.</AlertDescription>
      </Alert>
    );
  }
  return null;
};

export default TeamErrorAlert;
