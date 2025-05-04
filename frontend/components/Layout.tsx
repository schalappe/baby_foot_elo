import React, { ReactNode } from "react";
import Header from "./Header";
import Footer from "./Footer";
import { ThemeProvider } from "./ThemeProvider";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <div className="min-h-screen flex flex-col bg-background-light text-foreground-light dark:bg-background-dark dark:text-foreground-dark transition-colors duration-300">
        <Header />
        <main className="flex-1 container mx-auto px-4 py-8">{children}</main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}
