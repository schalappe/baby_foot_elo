'use client';

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import NewMatchPage from "@/app/matches/new/page";
import { useState } from "react";

interface NewMatchDialogProps {
  children: React.ReactNode;
}

export function NewMatchDialog({ children }: NewMatchDialogProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleMatchCreated = () => {
    setIsOpen(false);
    // Optionally, add a toast notification or re-fetch data if needed
  };

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>{children}</DialogTrigger>
      <DialogContent className="sm:max-w-[700px] md:max-w-[900px] lg:max-w-[1200px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Ajouter une nouvelle partie</DialogTitle>
        </DialogHeader>
        <NewMatchPage onMatchCreated={handleMatchCreated} isDialog={true} />
      </DialogContent>
    </Dialog>
  );
}
