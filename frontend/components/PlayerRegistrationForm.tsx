import React, { useState, FormEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal } from "lucide-react"; // For Alert icon

const PlayerRegistrationForm: React.FC = () => {
  const [name, setName] = useState("");
  const [initialElo, setInitialElo] = useState<number | string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    if (!name.trim()) {
      setError("Le nom est requis.");
      return;
    }

    if (initialElo !== "" && isNaN(Number(initialElo))) {
      setError("L'ELO initial doit être un nombre valide.");
      return;
    }

    const payload: any = { name: name.trim() };
    if (initialElo !== "") payload.initial_elo = Number(initialElo);

    try {
      const res = await fetch("http://localhost:8000/api/players/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Une erreur est survenue lors de l'enregistrement du joueur.");
      } else {
        setName("");
        setInitialElo("");
        setSuccess(true);
      }
    } catch {
      setError("Une erreur réseau est survenue lors de l'enregistrement du joueur.");
    }
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Enregistrer un Nouveau Joueur</CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="flex flex-col gap-4">
          {error && (
            <Alert variant="destructive">
              <Terminal className="h-4 w-4" />
              <AlertTitle>Erreur</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          {success && (
            <Alert variant="default"> {/* Or a 'success' variant if you define one */}
              <Terminal className="h-4 w-4" /> {/* Consider a success icon */}
              <AlertTitle>Succès</AlertTitle>
              <AlertDescription>Joueur enregistré avec succès!</AlertDescription>
            </Alert>
          )}
          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="name">Nom</Label>
            <Input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nom du joueur"
            />
          </div>
          <div className="flex flex-col space-y-1.5">
            <Label htmlFor="initialElo">ELO initial (optionnel)</Label>
            <Input
              id="initialElo"
              type="number"
              value={initialElo}
              onChange={(e) => setInitialElo(e.target.value === "" ? "" : Number(e.target.value))}
              placeholder="ex: 1200"
            />
          </div>
        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full">
            Enregistrer le joueur
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default PlayerRegistrationForm;
