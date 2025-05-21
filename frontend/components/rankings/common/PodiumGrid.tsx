import React from 'react';
import { Card, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

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

export function PodiumGrid<T>({
  items,
  getKey,
  getLink,
  getName,
  getElo,
  getWinrate,
  renderExtra,
}: PodiumGridProps<T>) {
  const borderColors = ["border-yellow-500", "border-blue-400", "border-rose-500"];
  const rankColors = ["text-yellow-400", "text-blue-400", "text-rose-500"];
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {items.map((item, index) => {
        const borderColor = borderColors[index] || borderColors[0];
        const rankColor = rankColors[index] || rankColors[0];
        const scale = index === 0 ? "scale-105 z-10" : "";
        return (
          <Card
            key={getKey(item, index)}
            className={`relative flex flex-col justify-between p-6 shadow-xl border-2 ${borderColor} ${scale} min-h-[300px]`}
            style={{ background: 'var(--color-podium-card)' }}
          >
            {/* Rank and Winrate Row */}
            <div className="flex justify-between items-start w-full mb-2">
              <span className={`text-4xl font-extrabold ${rankColor} drop-shadow-sm`}>{index + 1}</span>
              <Badge className="text-xs font-semibold px-2 py-1 rounded-lg ml-auto">{getWinrate(item)}</Badge>
            </div>
            {/* Name */}
            <Link href={getLink(item)} className="block text-center">
              <CardTitle className={`text-lg md:text-xl font-bold ${rankColor} mb-1 truncate`}>
                {getName(item)}
              </CardTitle>
            </Link>
            {/* ELO */}
            <div className="flex flex-col items-center my-2">
              <span className={`text-3xl md:text-4xl font-extrabold ${rankColor} tracking-wide`}>
                {getElo(item)} <span className={`text-lg font-medium ${rankColor}`}>ELO</span>
              </span>
            </div>
            {/* Extra (W-L, matches, etc) */}
            {renderExtra && (
              <div className="mt-2">{renderExtra(item)}</div>
            )}
          </Card>
        );
      })}
    </div>
  );
}
