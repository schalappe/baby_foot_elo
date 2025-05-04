import React from "react";

export default function Footer() {
  return (
    <footer className="w-full px-6 py-4 mt-10 bg-primary text-white dark:bg-background-dark dark:text-foreground-dark flex items-center justify-between">
      <span>&copy; {new Date().getFullYear()} Baby Foot Elo</span>
      <span className="text-xs opacity-80">Fait avec ❤️ par l'équipe</span>
    </footer>
  );
}
