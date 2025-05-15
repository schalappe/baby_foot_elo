import React from "react";

export default function Footer() {
  return (
    <footer className="w-full px-6 py-4 mt-auto border-t bg-muted text-muted-foreground flex items-center justify-between">
      <span>&copy; {new Date().getFullYear()} Baby Foot</span>
      <span className="text-xs opacity-80">Fait avec ❤️ par la BMIF</span>
    </footer>
  );
}
