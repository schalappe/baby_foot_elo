import type { PlayerModel } from "./PlayerModel";

export interface TeamModel {
    team_id: number;
    global_elo: number;
    created_at: Date;
    last_match_at: Date | null;
    player1: PlayerModel;
    player2: PlayerModel;
    rank: number
}