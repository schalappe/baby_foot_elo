import type { PlayerModel } from "./PlayerModel";

export interface TeamModel {
    team_id: Number;
    global_elo: Number;
    created_at: Date;
    last_match_at: Date | null;
    player1: PlayerModel;
    player2: PlayerModel;
    rank: Number
}