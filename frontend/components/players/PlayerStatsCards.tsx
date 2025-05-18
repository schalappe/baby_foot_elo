import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUpIcon, TrendingDownIcon } from 'lucide-react';

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
      <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden relative">
        <CardContent className="flex flex-col items-center justify-center p-6 h-full text-left">
          {/* Top right badge with trending icon and percent */}
          {player.recent && player.recent.elo_changes && player.recent.elo_changes.length > 0 ? (() => {
            const changes = player.recent.elo_changes.slice(0, 5);
            const sum = changes.reduce((acc: number, val: number) => acc + val, 0);
            const trendingUp = sum >= 0;
            return (
              <>
                <div className="absolute top-4 right-4">
                  <Badge variant="outline" className="flex items-center gap-1 px-2 py-1 text-base">
                    {trendingUp ? <TrendingUpIcon className="w-4 h-4 text-green-500" /> : <TrendingDownIcon className="w-4 h-4 text-red-500" />}
                    {sum !== null ? `${trendingUp ? '+' : ''}${sum.toFixed(0)}` : (trendingUp ? '+0' : '-0')}
                  </Badge>
                </div>
                <div className="text-4xl sm:text-5xl font-bold mt-2 mb-1">{player.global_elo}</div>
                <div className="text-sm text-muted-foreground mb-4">ELO GLOBAL</div>
                <div className="text-base font-medium mb-1 flex items-center gap-1">
                  {trendingUp ? <TrendingUpIcon className="w-4 h-4 text-green-500" /> : <TrendingDownIcon className="w-4 h-4 text-red-500" />}
                  <span className={trendingUp ? 'text-green-500' : 'text-red-500'}>
                    Tendance à la {trendingUp ? 'hausse' : 'baisse'}
                  </span>
                </div>
                <div className="text-lg font-medium" style={{ color: sum >= 0 ? 'var(--win-text)' : 'var(--lose-text)' }}>
                  Sur les 5 derniers résultats
                </div>
              </>
            );
          })() : (
            <>
              <div className="absolute top-4 right-4">
                <Badge variant="outline" className="flex items-center gap-1 px-2 py-1 text-base">
                  <TrendingUpIcon className="w-4 h-4 text-muted-foreground" />
                  +0
                </Badge>
              </div>
              <div className="text-4xl sm:text-5xl font-bold mt-2 mb-1">{player.global_elo}</div>
              <div className="text-sm text-muted-foreground mb-4">ELO GLOBAL</div>
              <div className="text-base font-medium mb-1 flex items-center gap-1">
                <TrendingUpIcon className="w-4 h-4 text-muted-foreground" />
                <span className="text-muted-foreground">Stable</span>
              </div>
              <div className="text-lg text-muted-foreground">Sur les 5 derniers résultats</div>
            </>
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
              <ChartContainer config={{ elo: { label: 'ELO', color: 'var(--chart-1)' } }} className="w-full h-40">
                <LineChart data={[...player.elo_values].reverse().map((elo, idx) => ({ match: idx + 1, elo }))} margin={{ top: 0, right: 16, left: 12, bottom: 0 }}>
                  <CartesianGrid vertical={false} />
                  <YAxis domain={['auto', 'auto']} tickMargin={8} axisLine={false} tickLine={false} />
                  <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
                  <Line type="monotone" dataKey="elo" stroke="var(--chart-1)" strokeWidth={2} dot={false} />
                </LineChart>
              </ChartContainer>
            ) : (
              <div className="h-40 flex items-center justify-center text-muted-foreground">Pas d'historique ELO</div>
            )}
            {/* Stats summary below chart */}
            <div className="flex justify-between mt-4 px-2">
              <div className="flex flex-col items-center">
                <span className="text-lg font-bold" style={{ color: 'var(--win-text)' }}>{player?.wins ?? 0}</span>
                <span className="text-xs text-muted-foreground">Victoires</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-lg font-bold" style={{ color: 'var(--lose-text)' }}>{player?.losses ?? 0}</span>
                <span className="text-xs text-muted-foreground">Défaites</span>
              </div>
              <div className="flex flex-col items-center">
                <span
                  className="text-lg font-bold" style={{ color: player ? (player.win_rate >= 0.5 ? 'var(--win-text)' : 'var(--lose-text)') : 'var(--muted)' }}
                >
                  {player ? `${Math.round(player.win_rate*100)}%` : '--'}
                </span>
                <span className="text-xs text-muted-foreground">Taux de victoire</span>
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
                  color: currentWinRate < 50 ? 'var(--lose)' : 'var(--win)',
                },
                remainderSegment: {
                  label: 'Remainder',
                  color: 'var(--muted)',
                },
              };
              const chartData = [
                { segment: 'winSegment', value: currentWinRate, fill: currentWinRate < 50 ? 'var(--lose)' : 'var(--win)', },
                { segment: 'remainderSegment', value: 100 - currentWinRate, fill: 'var(--muted)' },
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
            <span className="text-lg sm:text-xl font-bold" style={{ color: 'var(--win-text)' }}>{player.recent?.wins ?? 0}W</span>
            <span className="text-lg sm:text-xl font-bold"> - </span>
            <span className="text-lg sm:text-xl font-bold" style={{ color: 'var(--lose-text)' }}>{player.recent?.losses ?? 0}L</span>
          </div>
          <div className="text-xs text-muted-foreground">{player.recent?.matches_played ?? 0} dernières parties</div>
        </CardContent>
      </Card>
    </div>
  );
};

export default PlayerStatsCards;
