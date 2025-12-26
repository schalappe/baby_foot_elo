/**
 * PodiumGrid.tsx
 *
 * Displays a championship-style podium for the top 3 entities (player, team, etc).
 * Features medal-themed cards with gold/silver/bronze gradients, animations, and trophy icons.
 *
 * Exports:
 *   - PodiumGrid: Generic React.FC for podium display.
 *   - PodiumGridProps: Props interface for PodiumGrid.
 */
import React from "react";
import { Card, CardTitle } from "../ui/card";
import Link from "next/link";
import { Trophy, Medal, Award } from "lucide-react";

/**
 * PodiumGridProps
 * @template T - Entity type (player, team, etc)
 * @param items - Array of top 3 entities
 * @param getKey - Function to get unique key for entity
 * @param getLink - Function to get href for entity
 * @param getName - Function to get display name
 * @param getElo - Function to get ELO value
 * @param getWinrate - Function to get winrate percentage
 * @param renderExtra - Optional: Render additional info below ELO
 */
export interface PodiumGridProps<T> {
  items: T[];
  getKey: (item: T, index: number) => React.Key;
  getLink: (item: T) => string;
  getName: (item: T) => React.ReactNode;
  getElo: (item: T) => React.ReactNode;
  getWinrate: (item: T) => React.ReactNode;
  renderExtra?: (item: T) => React.ReactNode;
}

// [>]: Medal configuration for each podium position.
const PODIUM_CONFIG = [
  {
    cardClass: "podium-gold podium-champion",
    rankClass: "rank-gold",
    badgeClass: "medal-badge",
    badgeBg: "bg-gradient-to-r from-yellow-400 via-amber-400 to-yellow-500",
    Icon: Trophy,
    label: "Champion",
    scale: "md:scale-105 md:z-10",
  },
  {
    cardClass: "podium-silver",
    rankClass: "rank-silver",
    badgeClass: "medal-badge",
    badgeBg: "bg-gradient-to-r from-slate-300 via-gray-400 to-slate-400",
    Icon: Medal,
    label: "2nd",
    scale: "",
  },
  {
    cardClass: "podium-bronze",
    rankClass: "rank-bronze",
    badgeClass: "medal-badge",
    badgeBg: "bg-gradient-to-r from-orange-400 via-amber-600 to-orange-500",
    Icon: Award,
    label: "3rd",
    scale: "",
  },
];

export function PodiumGrid<T>({
  items,
  getKey,
  getLink,
  getName,
  getElo,
  getWinrate,
  renderExtra,
}: PodiumGridProps<T>) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 md:items-end">
      {items.map((item, index) => {
        const config = PODIUM_CONFIG[index] || PODIUM_CONFIG[0];
        const { cardClass, rankClass, badgeBg, Icon, scale } = config;

        return (
          <Card
            key={getKey(item, index)}
            className={`podium-card relative flex flex-col justify-between p-6 border-2 min-h-[280px] md:min-h-[320px] ${cardClass} ${scale}`}
          >
            {/* Top row: Rank number and Winrate badge */}
            <div className="flex justify-between items-start w-full mb-4">
              <div className="flex items-center gap-2">
                <span
                  className={`text-5xl md:text-6xl font-black ${rankClass} elo-score`}
                >
                  {index + 1}
                </span>
                <Icon
                  className={`trophy-icon w-6 h-6 md:w-8 md:h-8 ${rankClass}`}
                />
              </div>
              <div
                className={`${badgeBg} text-xs md:text-sm font-bold px-3 py-1.5 rounded-full shadow-lg`}
              >
                <span className="text-white drop-shadow-sm">
                  {getWinrate(item)}
                </span>
              </div>
            </div>

            {/* Name - Centered and prominent */}
            <Link
              href={getLink(item)}
              className="block text-center group flex-grow flex flex-col justify-center"
            >
              <CardTitle
                className={`text-xl md:text-2xl font-bold ${rankClass} mb-3 truncate group-hover:scale-105 transition-transform duration-200`}
              >
                {getName(item)}
              </CardTitle>

              {/* ELO Score - The hero number */}
              <div className="flex flex-col items-center">
                <span
                  className={`text-4xl md:text-5xl font-black ${rankClass} elo-score tracking-tight`}
                >
                  {getElo(item)}
                </span>
                <span
                  className={`text-sm md:text-base font-semibold ${rankClass} opacity-80 tracking-widest uppercase mt-1`}
                >
                  ELO
                </span>
              </div>
            </Link>

            {/* Extra content (W-L, matches, etc) */}
            {renderExtra && (
              <div className="mt-4 pt-4 border-t border-current/10">
                {renderExtra(item)}
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}
