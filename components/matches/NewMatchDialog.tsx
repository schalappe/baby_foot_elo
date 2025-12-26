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
import { useState, ReactNode } from "react";
import { Swords } from "lucide-react";

interface NewMatchDialogProps {
  trigger?: ReactNode;
}

/**
 * NewMatchDialog component provides a dialog for creating a new match.
 * Accepts an optional custom trigger element.
 *
 * @param trigger - Optional custom trigger element. Defaults to outline button.
 * @returns The rendered NewMatchDialog component.
 */
export function NewMatchDialog({ trigger }: NewMatchDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleMatchCreated = () => {
    setIsOpen(false);
  };

  const defaultTrigger = (
    <Button
      variant="outline"
      size="lg"
      className="gap-2 border-2 hover:border-primary transition-colors"
    >
      <Swords className="h-5 w-5" />
      Ajouter une Partie
    </Button>
  );

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{trigger || defaultTrigger}</DialogTrigger>
      <DialogContent className="w-full max-w-lg sm:max-w-2xl max-h-[90vh] overflow-y-auto p-2 sm:p-6">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Swords className="h-5 w-5 text-primary" />
            Créer un nouveau match
          </DialogTitle>
          <DialogDescription>
            Remplissez les informations suivantes pour créer un nouveau match.
          </DialogDescription>
        </DialogHeader>
        <NewMatchPage onMatchCreated={handleMatchCreated} isDialog={true} />
      </DialogContent>
    </Dialog>
  );
}
