"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import NewMatchPage from "@/app/matches/new/page";
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
          <DialogTitle>Ajouter une Partie</DialogTitle>
        </DialogHeader>
        <NewMatchPage onMatchCreated={handleMatchCreated} isDialog={true} />
      </DialogContent>
    </Dialog>
  );
}
