import React, { useState, FormEvent } from "react";

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
    <form onSubmit={handleSubmit} className="max-w-md mx-auto bg-white dark:bg-zinc-800 p-6 rounded shadow flex flex-col gap-4">
      {error && <div className="text-red-500">{error}</div>}
      {success && <div className="text-green-500">Joueur enregistré avec succès!</div>}
      <div className="flex flex-col">
        <label htmlFor="name" className="mb-1 font-medium">Nom</label>
        <input
          id="name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full border border-gray-300 dark:border-zinc-600 p-2 rounded bg-white dark:bg-zinc-700 text-black dark:text-white"
        />
      </div>
      <div className="flex flex-col">
        <label htmlFor="initialElo" className="mb-1 font-medium">ELO initial (optionnel)</label>
        <input
          id="initialElo"
          type="number"
          value={initialElo}
          onChange={(e) => setInitialElo(e.target.value === "" ? "" : Number(e.target.value))}
          className="w-full border border-gray-300 dark:border-zinc-600 p-2 rounded bg-white dark:bg-zinc-700 text-black dark:text-white"
        />
      </div>
      <button
        type="submit"
        className="bg-primary text-white py-2 px-4 rounded font-semibold hover:bg-primary-dark transition"
      >
        Enregistrer le joueur
      </button>
    </form>
  );
};

export default PlayerRegistrationForm;
