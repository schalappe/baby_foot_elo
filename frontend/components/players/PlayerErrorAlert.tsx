import React from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface PlayerErrorAlertProps {
  error?: string;
  notFound?: boolean;
}

const PlayerErrorAlert: React.FC<PlayerErrorAlertProps> = ({ error, notFound }) => {
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
        <AlertDescription>Le joueur n'a pas été trouvé.</AlertDescription>
      </Alert>
    );
  }
  return null;
};

export default PlayerErrorAlert;
