/**
 * EntityStatsCards.tsx
 *
 * Displays championship-styled statistics cards for player/team entity pages.
 * Features enhanced visuals with glowing effects, improved charts, and better hierarchy.
 *
 * Exports:
 *   - EntityStatsCards: React.FC for entity statistics display.
 */
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { TrendingUpIcon, TrendingDownIcon, Zap, Target } from "lucide-react";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../ui/chart";
import { LineChart, Line, YAxis, CartesianGrid } from "recharts";
import { ResponsiveContainer, PieChart, Pie, Label } from "recharts";
import { EntityStats } from "@/types/stats.types";

interface EntityStatsCardsProps {
  stats: EntityStats;
}

/**
 * Championship-styled stats cards for player/team entity.
 */
const EntityStatsCards: React.FC<EntityStatsCardsProps> = ({ stats }) => {
  // Trending calculation based on last 5 results.
  const changes = stats.recent?.elo_changes?.slice(0, 5) || [];
  const sum = changes.reduce((acc: number, val: number) => acc + val, 0);
  const trendingUp = sum >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* ELO Card - The Hero Card */}
      <Card className="stats-card bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden relative border-2">
        {/* Top accent bar */}
        <div
          className="absolute top-0 left-0 right-0 h-1"
          style={{
            background: trendingUp
              ? "linear-gradient(90deg, var(--win) 0%, hsl(145, 70%, 55%) 100%)"
              : "linear-gradient(90deg, var(--lose) 0%, hsl(0, 70%, 65%) 100%)",
          }}
        />
        <CardContent className="flex flex-col items-center justify-center p-6 h-full text-center relative">
          {/* Trending badge */}
          <div className="absolute top-4 right-4">
            <div
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-bold shadow-md"
              style={{
                background: trendingUp
                  ? "var(--match-win-bg)"
                  : "var(--match-lose-bg)",
                color: trendingUp ? "var(--win-text)" : "var(--lose-text)",
              }}
            >
              {trendingUp ? (
                <TrendingUpIcon className="w-4 h-4" />
              ) : (
                <TrendingDownIcon className="w-4 h-4" />
              )}
              {sum !== null
                ? `${trendingUp ? "+" : ""}${sum.toFixed(0)}`
                : trendingUp
                  ? "+0"
                  : "-0"}
            </div>
          </div>

          {/* ELO Score - Hero number */}
          <div className="mt-4">
            <div className="text-5xl sm:text-6xl font-black elo-score tracking-tight text-foreground">
              {stats.global_elo}
            </div>
            <div className="text-sm text-muted-foreground font-semibold tracking-widest uppercase mt-1">
              ELO GLOBAL
            </div>
          </div>

          {/* Trend indicator */}
          <div className="mt-6 flex flex-col items-center gap-1">
            <div className="flex items-center gap-2">
              <Zap
                className="w-4 h-4"
                style={{
                  color: trendingUp ? "var(--win-text)" : "var(--lose-text)",
                }}
              />
              <span
                className="text-base font-semibold"
                style={{
                  color: trendingUp ? "var(--win-text)" : "var(--lose-text)",
                }}
              >
                Tendance à la {trendingUp ? "hausse" : "baisse"}
              </span>
            </div>
            <span className="text-sm text-muted-foreground">
              Sur les 5 derniers résultats
            </span>
          </div>
        </CardContent>
      </Card>

      {/* ELO Evolution Chart */}
      <Card className="stats-card bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden border-2">
        <CardHeader className="flex flex-col items-center gap-2 pt-6 pb-2 border-b bg-muted/30">
          <CardTitle className="text-lg font-bold tracking-tight">
            Évolution ELO
          </CardTitle>
        </CardHeader>
        <CardContent className="pb-6 pt-4 px-2">
          {stats.elo_values && stats.elo_values.length > 1 ? (
            <ChartContainer
              config={{ elo: { label: "ELO", color: "var(--chart-1)" } }}
              className="w-full h-40"
            >
              <LineChart
                data={[...stats.elo_values]
                  .reverse()
                  .map((elo: number, idx: number) => ({ match: idx + 1, elo }))}
                margin={{ top: 0, right: 16, left: 12, bottom: 0 }}
              >
                <CartesianGrid
                  vertical={false}
                  strokeDasharray="3 3"
                  stroke="var(--border)"
                />
                <YAxis
                  domain={["auto", "auto"]}
                  tickMargin={8}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
                />
                <ChartTooltip
                  cursor={false}
                  content={<ChartTooltipContent />}
                />
                <Line
                  type="monotone"
                  dataKey="elo"
                  stroke="var(--chart-1)"
                  strokeWidth={2.5}
                  dot={false}
                  activeDot={{
                    r: 6,
                    fill: "var(--chart-1)",
                    stroke: "var(--background)",
                    strokeWidth: 2,
                  }}
                />
              </LineChart>
            </ChartContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-muted-foreground">
              Pas d&apos;historique ELO
            </div>
          )}

          {/* Stats summary below chart */}
          <div className="flex justify-between mt-4 px-4 pt-4 border-t border-border/50">
            <div className="flex flex-col items-center">
              <span
                className="text-xl font-bold"
                style={{ color: "var(--win-text)" }}
              >
                {stats?.wins ?? 0}
              </span>
              <span className="text-xs text-muted-foreground font-medium">
                Victoires
              </span>
            </div>
            <div className="flex flex-col items-center">
              <span
                className="text-xl font-bold"
                style={{ color: "var(--lose-text)" }}
              >
                {stats?.losses ?? 0}
              </span>
              <span className="text-xs text-muted-foreground font-medium">
                Défaites
              </span>
            </div>
            <div className="flex flex-col items-center">
              <span
                className="text-xl font-bold"
                style={{
                  color: stats
                    ? stats.win_rate >= 0.5
                      ? "var(--win-text)"
                      : "var(--lose-text)"
                    : "var(--muted)",
                }}
              >
                {stats ? `${Math.round((stats.win_rate ?? 0) * 100)}%` : "--"}
              </span>
              <span className="text-xs text-muted-foreground font-medium">
                Taux
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Win Rate Donut Chart */}
      <Card className="stats-card bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden border-2">
        <CardContent className="flex flex-col items-center justify-center p-6 h-full space-y-3 text-center">
          {/* Target icon */}
          <div className="flex items-center gap-2 text-muted-foreground">
            <Target className="w-4 h-4" />
            <span className="text-xs font-semibold tracking-widest uppercase">
              TAUX DE VICTOIRE
            </span>
          </div>

          {/* Donut chart */}
          <div
            className={`relative w-36 h-36 sm:w-40 sm:h-40 ${
              (stats.recent?.win_rate ?? stats.win_rate ?? 0) >= 0.5
                ? "winrate-circle-win"
                : "winrate-circle-lose"
            }`}
          >
            {(() => {
              // [>]: Convert decimal win_rate (0-1) to percentage (0-100) for pie chart.
              const currentWinRate =
                (stats.recent?.win_rate ?? stats.win_rate ?? 0) * 100;
              const chartConfig = {
                winSegment: {
                  label: "Win Rate",
                  color: currentWinRate < 50 ? "var(--lose)" : "var(--win)",
                },
                remainderSegment: {
                  label: "Remainder",
                  color: "var(--muted)",
                },
              };
              const chartData = [
                {
                  segment: "winSegment",
                  value: currentWinRate,
                  fill: currentWinRate < 50 ? "var(--lose)" : "var(--win)",
                },
                {
                  segment: "remainderSegment",
                  value: 100 - currentWinRate,
                  fill: "var(--muted)",
                },
              ];
              return (
                <ChartContainer
                  config={chartConfig}
                  className="w-full h-full aspect-square"
                >
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
                          className="fill-foreground text-3xl sm:text-4xl font-black"
                        />
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </ChartContainer>
              );
            })()}
          </div>

          {/* W-L record */}
          <div className="flex items-center gap-2 text-lg font-bold">
            <span style={{ color: "var(--win-text)" }}>
              {stats.recent?.wins ?? stats.wins ?? 0}W
            </span>
            <span className="text-muted-foreground">-</span>
            <span style={{ color: "var(--lose-text)" }}>
              {stats.recent?.losses ?? stats.losses ?? 0}L
            </span>
          </div>

          <div className="text-xs text-muted-foreground font-medium">
            {stats.recent?.matches_played ?? stats.matches_played ?? 0} dernières
            parties
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EntityStatsCards;
