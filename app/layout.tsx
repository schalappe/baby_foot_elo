/**
 * layout.tsx
 *
 * Root layout component for the Baby Foot ELO Next.js app.
 *
 * - Sets up global fonts, theme provider, sidebar, and header.
 * - Wraps all pages with shared UI and providers.
 * - Imports global styles.
 *
 * Props: None (used as the root layout in Next.js app directory).
 *
 * Usage: Do not import directly. Used automatically by Next.js as the root layout.
 */
import type { Metadata } from "next";
import { Delius, Inter } from "next/font/google";
import { Toaster } from "../components/ui/sonner";
import { SidebarProvider, SidebarInset } from "../components/ui/sidebar";
import { AppSidebar } from "../components/app-sidebar";
import { ThemeProvider } from "../components/ThemeProvider";
import "./globals.css";
import { SiteHeader } from "../components/Header";

// [>]: Delius for headers - playful, handwritten feel for championship app.
const delius = Delius({
  variable: "--font-delius",
  weight: "400",
  subsets: ["latin"],
});

// [>]: Inter as a clean, modern body font (replacing Google Sans Text which isn't available in next/font).
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Baby Foot ELO",
  description:
    "Un championnat de baby-foot avec un système de classement ELO hybride.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <body className={`${delius.variable} ${inter.variable} antialiased`}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <SidebarProvider>
            <AppSidebar variant="inset" />
            <SidebarInset>
              <div className="flex flex-1 flex-col">
                <div className="@container/main flex flex-1 flex-col gap-2">
                  <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
                    <SiteHeader />
                    {children}
                  </div>
                </div>
              </div>
            </SidebarInset>
          </SidebarProvider>
        </ThemeProvider>
        <Toaster />
      </body>
    </html>
  );
}
