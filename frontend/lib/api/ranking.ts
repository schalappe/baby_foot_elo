// [>]: Shared ranking utilities for API endpoints.

const MS_PER_DAY = 24 * 60 * 60 * 1000;

interface HasActivity {
  matches_played: number;
  last_match_at?: string | null;
}

interface HasElo {
  global_elo: number;
}

interface HasActivityAndElo extends HasActivity, HasElo {}

// [>]: Filter entities to those with recent activity.
// Entities with 0 matches or no last_match_at are excluded.
export function filterActiveEntities<T extends HasActivityAndElo>(
  entities: T[],
  daysSinceLastMatch: number,
): T[] {
  const now = Date.now();
  const cutoffMs = daysSinceLastMatch * MS_PER_DAY;

  return entities.filter((entity) => {
    if (entity.matches_played === 0) return false;
    if (!entity.last_match_at) return false;
    const lastMatchMs = new Date(entity.last_match_at).getTime();
    return now - lastMatchMs <= cutoffMs;
  });
}

// [>]: Sort entities by ELO descending, slice to limit, and add rank.
export function rankByElo<T extends HasElo>(
  entities: T[],
  limit: number,
): Array<T & { rank: number }> {
  return entities
    .sort((a, b) => b.global_elo - a.global_elo)
    .slice(0, limit)
    .map((entity, i) => ({ ...entity, rank: i + 1 }));
}
