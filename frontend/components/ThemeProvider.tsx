"use client";

import * as React from "react";
import { ThemeProvider as NextThemesProvider } from "next-themes";

export function ThemeProvider({ children, ...props }: React.ComponentProps<typeof NextThemesProvider>) {
  return <NextThemesProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange {...props}>{children}</NextThemesProvider>;
}

// Re-export useTheme from next-themes for convenience if other components were using the custom one.
export { useTheme } from "next-themes";
