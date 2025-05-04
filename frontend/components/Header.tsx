import React from "react";
import { useTheme } from "./ThemeProvider";

export default function Header() {
  const { theme, toggleTheme } = useTheme();
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between bg-primary text-white dark:bg-background-dark dark:text-foreground-dark shadow-md">
      <div className="flex items-center gap-2">
        {/* Logo or Icon */}
        <span className="font-bold text-xl tracking-tight">Baby Foot Elo</span>
      </div>
      <nav className="flex gap-4">
        <a href="#" className="hover:underline">Accueil</a>
        <a href="#" className="hover:underline">Classement</a>
        <a href="#" className="hover:underline">À propos</a>
      </nav>
      <button
        onClick={toggleTheme}
        className="ml-4 px-3 py-1 rounded bg-foreground-light text-primary dark:bg-foreground-dark dark:text-primary border border-primary hover:bg-primary hover:text-white dark:hover:bg-primary dark:hover:text-white transition"
        aria-label="Toggle theme"
      >
        {theme === "light" ? "🌙" : "☀️"}
      </button>
    </header>
  );
}
