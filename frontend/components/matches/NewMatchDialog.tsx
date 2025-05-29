"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import { Button } from "../ui/button";
import NewMatchPage from "./NewMatchPage";
import { useState } from "react";

/**
 * NewMatchDialog component provides a dialog for creating a new match.
 *
 * @returns The rendered NewMatchDialog component.
 */
export function NewMatchDialog() {
  const [isOpen, setIsOpen] = useState(false);

  const handleMatchCreated = () => {
    setIsOpen(false);
    // Optionally, add a toast notification or re-fetch data if needed
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="lg">
          Ajouter une Partie
        </Button>
      </DialogTrigger>
      <DialogContent className="w-full max-w-lg sm:max-w-2xl max-h-[90vh] overflow-y-auto p-2 sm:p-6">
        <DialogHeader>
          <DialogTitle>Créer un nouveau match</DialogTitle>
          <DialogDescription>
            Remplissez les informations suivantes pour créer un nouveau match.
          </DialogDescription>
        </DialogHeader>
        <NewMatchPage onMatchCreated={handleMatchCreated} isDialog={true} />
      </DialogContent>
    </Dialog>
  );
}
