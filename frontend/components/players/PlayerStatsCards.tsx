import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartContainer, ChartTooltip, ChartTooltipContent } from '@/components/ui/chart';
import { LineChart, Line, YAxis, CartesianGrid } from 'recharts';
import { ResponsiveContainer, PieChart, Pie, Label } from 'recharts';
import { Skeleton } from '@/components/ui/skeleton';
import { PlayerStats } from '@/types/player.types';

interface PlayerStatsCardsProps {
  player: PlayerStats;
}

const PlayerStatsCards: React.FC<PlayerStatsCardsProps> = ({ player }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* ELO Card */}
      <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
        <CardContent className="flex flex-col items-center justify-center p-6 h-full text-center">
          <div className="text-5xl sm:text-6xl font-bold">{player.global_elo}</div>
          <div className="text-sm text-muted-foreground mb-2">ELO GLOBAL</div>
          {player.recent && player.recent.elo_changes && player.recent.elo_changes.length > 0 ? (
            (() => {
              const lastChange = player.recent.elo_changes[0];
              return (
                <div className={`text-lg font-medium ${lastChange >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                  {lastChange >= 0 ? '+' : ''}
                  {lastChange.toFixed(0)} ELO (dernier match)
                </div>
              );
            })()
          ) : (
            <div className="text-lg text-muted-foreground">- ELO (dernier match)</div>
          )}
        </CardContent>
      </Card>

      {/* ELO Evolution & Stats Card */}
      <div>
        <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
          <CardHeader className="flex flex-col items-center gap-2 pt-6 pb-2">
            <CardTitle>Évolution ELO</CardTitle>
          </CardHeader>
          <CardContent className="pb-6 pt-0 px-2">
            {/* ELO Evolution Line Chart */}
            {player?.elo_values && player.elo_values.length > 1 ? (
              <ChartContainer config={{ elo: { label: 'ELO', color: 'hsl(220,70%,50%)' } }} className="w-full h-40">
                <LineChart data={[...player.elo_values].reverse().map((elo, idx) => ({ match: idx + 1, elo }))} margin={{ top: 0, right: 16, left: 12, bottom: 0 }}>
                  <CartesianGrid vertical={false} />
                  <YAxis domain={['auto', 'auto']} tickMargin={8} axisLine={false} tickLine={false} />
                  <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                  <Line type="monotone" dataKey="elo" stroke="hsl(220,70%,50%)" strokeWidth={2} dot={false} />
                </LineChart>
              </ChartContainer>
            ) : (
              <div className="h-40 flex items-center justify-center text-muted-foreground">Pas d'historique ELO</div>
            )}
            {/* Stats summary below chart */}
            <div className="flex justify-between mt-4 px-2">
              <div className="flex flex-col items-center">
                <span className="text-lg font-bold text-green-400">{player?.wins ?? 0}</span>
                <span className="text-xs text-muted-foreground">Victoires</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-lg font-bold text-red-400">{player?.losses ?? 0}</span>
                <span className="text-xs text-muted-foreground">Défaites</span>
              </div>
              <div className="flex flex-col items-center">
                <span
                  className={`text-lg font-bold ${player ? (player.win_rate >= 0.5 ? 'text-green-400' : 'text-red-400') : 'text-blue-300'}`}
                >
                  {player ? `${Math.round(player.win_rate*100)}%` : '--'}
                </span>
                <span className="text-xs text-muted-foreground">Winrate</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Win Rate Card */}
      <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
        <CardContent className="flex flex-col items-center justify-center p-6 h-full space-y-2 text-center">
          <div className="relative w-32 h-32 sm:w-36 sm:h-36"> 
            {(() => {
              const currentWinRate = player.recent?.win_rate ?? 0;
              const chartConfig = {
                winSegment: {
                  label: 'Win Rate',
                  color: currentWinRate < 50 ? 'hsl(0 72.2% 50.6%)' : 'hsl(142.1 70.6% 45.3%)',
                },
                remainderSegment: {
                  label: 'Remainder',
                  color: 'hsl(var(--muted))',
                },
              };
              const chartData = [
                { segment: 'winSegment', value: currentWinRate, fill: 'var(--color-winSegment)' },
                { segment: 'remainderSegment', value: 100 - currentWinRate, fill: 'var(--color-remainderSegment)' },
              ];
              return (
                <ChartContainer config={chartConfig} className="w-full h-full aspect-square">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData}
                        dataKey="value"
                        nameKey="segment"
                        cx="50%"
                        cy="50%"
                        innerRadius="70%"
                        outerRadius="100%"
                        startAngle={225}
                        endAngle={-45}
                        paddingAngle={0}
                        cornerRadius={8}
                      >
                        <Label
                          value={`${Math.round(currentWinRate)}%`}
                          position="center"
                          dy={4} 
                          className="fill-foreground text-2xl sm:text-3xl font-semibold"
                        />
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </ChartContainer>
              );
            })()}
          </div>
          <div className="text-sm text-muted-foreground uppercase tracking-wider">TAUX DE VICTOIRE</div>
          <div>
            <span className="text-lg sm:text-xl font-bold text-green-500">{player.recent?.wins ?? 0}W</span>
            <span className="text-lg sm:text-xl font-bold"> - </span>
            <span className="text-lg sm:text-xl font-bold text-red-500">{player.recent?.losses ?? 0}L</span>
          </div>
          <div className="text-xs text-muted-foreground">{player.recent?.matches_played ?? 0} dernières parties</div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PlayerStatsCards;
