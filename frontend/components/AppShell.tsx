"use client";
import React, { ReactNode } from "react";
import { ThemeProvider } from "./ThemeProvider";
import Header from "./Header";
import Footer from "./Footer";

export default function AppShell({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <div className="min-h-screen flex flex-col bg-background-light text-foreground-light dark:bg-zinc-900 dark:text-foreground-dark transition-colors duration-300">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">{children}</main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}
