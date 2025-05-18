"use client"; 
import React from "react";
import Link from "next/link"; 
import { ThemeToggle } from "@/components/ThemeToggle"; 
import { NavigationMenu, NavigationMenuItem, NavigationMenuLink, NavigationMenuList, navigationMenuTriggerStyle } from "@/components/ui/navigation-menu";

export default function Header() {
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b bg-background dark:bg-zinc-900 dark:text-foreground-dark shadow-md">
      <div className="flex items-center gap-2">
        <Link href="/">
          <h1 className="font-bold text-xl tracking-tight">Baby Foot</h1>
        </Link>
      </div>
      <NavigationMenu>
        <NavigationMenuList>
          <NavigationMenuItem>
            <Link href="/" legacyBehavior passHref>
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                Accueil
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/teams" legacyBehavior passHref>
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                Équipes
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/matches" legacyBehavior passHref>
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                Parties
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
          <NavigationMenuItem>
            <Link href="/about" legacyBehavior passHref> 
              <NavigationMenuLink className={navigationMenuTriggerStyle()}>
                À propos
              </NavigationMenuLink>
            </Link>
          </NavigationMenuItem>
        </NavigationMenuList>
      </NavigationMenu>
      <ThemeToggle />
    </header>
  );
}
