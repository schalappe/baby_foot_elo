/**
 * app-sidebar.tsx
 *
 * Championship-styled sidebar with sports theme navigation.
 * Features enhanced visuals, trophy icon, and active state highlighting.
 *
 * Exports:
 *   - AppSidebar: React.FC for sidebar navigation.
 */
"use client";

import { Library, Home, Users, Trophy } from "lucide-react";
import { usePathname } from "next/navigation";
import Link from "next/link";

import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarFooter,
} from "./ui/sidebar";

// Navigation items with icons.
const items = [
  {
    title: "Accueil",
    url: "/",
    icon: Home,
    description: "Classement des joueurs",
  },
  {
    title: "Équipes",
    url: "/teams",
    icon: Users,
    description: "Classement des équipes",
  },
  {
    title: "Parties",
    url: "/matches",
    icon: Library,
    description: "Historique des matchs",
  },
];

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const pathname = usePathname();

  // Check if current path matches item URL.
  const isActive = (url: string) => {
    if (url === "/") {
      return pathname === "/" || pathname.startsWith("/players");
    }
    return pathname.startsWith(url);
  };

  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader className="border-b border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" asChild>
              <Link href="/" className="group">
                <div className="flex aspect-square size-10 items-center justify-center rounded-xl bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-500 text-white shadow-lg group-hover:shadow-xl transition-shadow duration-200">
                  <Trophy className="size-5" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-bold text-sidebar-foreground">
                    Baby Foot ELO
                  </span>
                  <span className="truncate text-xs text-sidebar-foreground/60">
                    Championship Tracker
                  </span>
                </div>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent className="py-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {items.map((item) => {
                const active = isActive(item.url);
                return (
                  <SidebarMenuItem key={item.title}>
                    <SidebarMenuButton
                      asChild
                      className={`relative transition-all duration-200 ${
                        active
                          ? "bg-sidebar-accent text-sidebar-accent-foreground font-semibold"
                          : "hover:bg-sidebar-accent/50"
                      }`}
                    >
                      <Link href={item.url} className="flex items-center gap-3">
                        {/* Active indicator bar */}
                        {active && (
                          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full bg-gradient-to-b from-yellow-400 to-amber-500" />
                        )}
                        <item.icon
                          className={`size-5 ${
                            active
                              ? "text-sidebar-primary"
                              : "text-sidebar-foreground/70"
                          }`}
                        />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border p-4">
        <div className="text-xs text-sidebar-foreground/50 text-center">
          <span className="font-medium">BMIF</span> Championship
        </div>
      </SidebarFooter>
    </Sidebar>
  );
}
