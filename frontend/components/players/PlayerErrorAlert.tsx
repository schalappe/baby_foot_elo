import React from "react";
import EntityErrorAlert from "@/components/common/EntityErrorAlert";

interface PlayerErrorAlertProps {
  error?: string;
  notFound?: boolean;
}

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
