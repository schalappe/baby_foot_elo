/**
 * stats.types.ts
 *
 * TypeScript interfaces for generic statistical data.
 * Provides a base structure for player and team statistics.
 */

/**
 * Generic interface for statistical data of an entity (e.g., player or team).
 * Includes ELO, win/loss records, and recent performance metrics.
 * Allows for additional properties via index signature for extensibility.
 */
export interface EntityStats {
  global_elo: number;
  elo_values: number[];
  wins: number;
  losses: number;
  win_rate: number;
  matches_played?: number;
  recent: {
    elo_changes: number[];
    win_rate: number;
    wins: number;
    losses: number;
    matches_played?: number;
  };
  [key: string]: unknown;
}
