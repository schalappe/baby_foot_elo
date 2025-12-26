/**
 * ThemeToggle.tsx
 *
 * Displays a button to toggle between light and dark themes.
 * Uses ShadCN Button and lucide-react icons.
 *
 * Exports:
 *   - ThemeToggle: React.FC for theme toggle button.
 */
"use client";
import * as React from "react";
import { useTheme } from "next-themes";
import { Button } from "./ui/button";
import { Moon, Sun } from "lucide-react";

/**
 * ThemeToggle component for switching between light and dark themes.
 * Uses ShadCN Button and lucide-react icons.
 *
 * Returns
 * -------
 * JSX.Element
 *     The theme toggle button.
 */
export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <Button
      variant="ghost"
      size="icon"
      aria-label="Toggle theme"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      style={{ transition: "background 0.4s, color 0.4s, border-color 0.4s" }}
    >
      {theme === "dark" ? (
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </Button>
  );
}
