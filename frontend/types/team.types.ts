// frontend/types/team.types.ts
import { Player } from './player.types';

export interface Team {
  team_id: number;
  player1_id: number;
  player2_id: number;
  global_elo: number;
  created_at: string;
  last_match_at?: string | null;
  player1?: Player | null;
  player2?: Player | null;
  rank?: number | null;
}
