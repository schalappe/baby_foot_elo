import React, { useState, FormEvent } from "react";
import { useRouter } from 'next/navigation';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Terminal, Loader2 } from "lucide-react"; 
import { registerPlayer } from '@/services/playerService'; 

const PlayerRegistrationForm: React.FC = () => {
  const router = useRouter();
  const [name, setName] = useState("");
  const [initialElo, setInitialElo] = useState<number | string>("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false); 

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    setLoading(true); 

    if (!name.trim()) {
      setError("Le nom est requis.");
      setLoading(false);
      return;
    }

    const eloValue = initialElo === "" ? undefined : Number(initialElo);
    if (initialElo !== "" && isNaN(eloValue!)) {
      setError("L'ELO initial doit être un nombre valide.");
      setLoading(false);
      return;
    }

    try {
      await registerPlayer(name.trim(), eloValue);
      setName("");
      setInitialElo("");
      setSuccess(true);
      setTimeout(() => {
        router.push('/players');
      }, 1500);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "Une erreur est survenue lors de l'enregistrement du joueur.";
      setError(errorMessage);
    } finally {
      setLoading(false); 
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
            <Alert variant="default"> 
              <Terminal className="h-4 w-4" /> 
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
        <CardFooter className="mt-4">
          <Button type="submit" className="w-full" disabled={loading}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {loading ? 'Enregistrement...' : 'Enregistrer le joueur'}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
};

export default PlayerRegistrationForm;
