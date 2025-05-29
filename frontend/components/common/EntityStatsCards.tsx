/**
 * EntityStatsCards.tsx
 *
 * Displays a statistics card for player/team entity pages.
 * Used to show ELO, win rate, and other stats in a card format for entities.
 *
 * Exports:
 *   - EntityStatsCards: React.FC for entity statistics display.
 */
import React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { TrendingUpIcon, TrendingDownIcon } from "lucide-react";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "../ui/chart";
import { LineChart, Line, YAxis, CartesianGrid } from "recharts";
import { ResponsiveContainer, PieChart, Pie, Label } from "recharts";
import { EntityStats } from "@/types/stats.types";

interface EntityStatsCardsProps {
  stats: EntityStats;
}

/**
 * Generic stats card for player/team entity.
 *
 * Parameters
 * ----------
 * stats : EntityStats
 *     The statistics object for the entity.
 *
 * Returns
 * -------
 * JSX.Element
 *     The rendered stats cards.
 */
const EntityStatsCards: React.FC<EntityStatsCardsProps> = ({ stats }) => {
  // Trending calculation
  const changes = stats.recent?.elo_changes?.slice(0, 5) || [];
  const sum = changes.reduce((acc: number, val: number) => acc + val, 0);
  const trendingUp = sum >= 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* ELO Card */}
      <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden relative">
        <CardContent className="flex flex-col items-center justify-center p-6 h-full text-left">
          {/* Top right badge with trending icon and percent */}
          <div className="absolute top-4 right-4">
            <Badge
              variant="outline"
              className="flex items-center gap-1 px-2 py-1 text-base"
            >
              {trendingUp ? (
                <TrendingUpIcon style={{ color: "var(--win-text)" }} />
              ) : (
                <TrendingDownIcon style={{ color: "var(--lose-text)" }} />
              )}
              {sum !== null
                ? `${trendingUp ? "+" : ""}${sum.toFixed(0)}`
                : trendingUp
                  ? "+0"
                  : "-0"}
            </Badge>
          </div>
          <div className="text-4xl sm:text-5xl font-bold mt-2 mb-1">
            {stats.global_elo}
          </div>
          <div className="text-sm text-muted-foreground mb-4">ELO GLOBAL</div>
          <div className="text-base font-medium mb-1 flex items-center gap-1">
            {trendingUp ? (
              <TrendingUpIcon style={{ color: "var(--win-text)" }} />
            ) : (
              <TrendingDownIcon style={{ color: "var(--lose-text)" }} />
            )}
            <span
              style={{
                color: trendingUp ? "var(--win-text)" : "var(--lose-text)",
              }}
            >
              Tendance à la {trendingUp ? "hausse" : "baisse"}
            </span>
          </div>
          <div
            className="text-lg font-medium"
            style={{ color: sum >= 0 ? "var(--win-text)" : "var(--lose-text)" }}
          >
            Sur les 5 derniers résultats
          </div>
        </CardContent>
      </Card>

      {/* ELO Evolution Line Chart */}
      <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
        <CardHeader className="flex flex-col items-center gap-2 pt-6 pb-2">
          <CardTitle>Évolution ELO</CardTitle>
        </CardHeader>
        <CardContent className="pb-6 pt-0 px-2">
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
                <CartesianGrid vertical={false} />
                <YAxis
                  domain={["auto", "auto"]}
                  tickMargin={8}
                  axisLine={false}
                  tickLine={false}
                />
                <ChartTooltip
                  cursor={false}
                  content={<ChartTooltipContent />}
                />
                <Line
                  type="monotone"
                  dataKey="elo"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ChartContainer>
          ) : (
            <div className="h-40 flex items-center justify-center text-muted-foreground">
              Pas d&apos;historique ELO
            </div>
          )}
          {/* Stats summary below chart */}
          <div className="flex justify-between mt-4 px-2">
            <div className="flex flex-col items-center">
              <span
                className="text-lg font-bold"
                style={{ color: "var(--win-text)" }}
              >
                {stats?.wins ?? 0}
              </span>
              <span className="text-xs text-muted-foreground">Victoires</span>
            </div>
            <div className="flex flex-col items-center">
              <span
                className="text-lg font-bold"
                style={{ color: "var(--lose-text)" }}
              >
                {stats?.losses ?? 0}
              </span>
              <span className="text-xs text-muted-foreground">Défaites</span>
            </div>
            <div className="flex flex-col items-center">
              <span
                className="text-lg font-bold"
                style={{
                  color: stats
                    ? stats.win_rate >= 0.5
                      ? "var(--win-text)"
                      : "var(--lose-text)"
                    : "var(--muted)",
                }}
              >
                {stats ? `${Math.round(stats.win_rate ?? 0)}%` : "--"}
              </span>
              <span className="text-xs text-muted-foreground">
                Taux de victoire
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Win Rate Pie Chart Card */}
      <Card className="bg-card text-card-foreground shadow-lg rounded-xl overflow-hidden">
        <CardContent className="flex flex-col items-center justify-center p-6 h-full space-y-2 text-center">
          <div className="relative w-32 h-32 sm:w-36 sm:h-36">
            {(() => {
              const currentWinRate =
                stats.recent?.win_rate ?? stats.win_rate ?? 0;
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
                          className="fill-foreground text-2xl sm:text-3xl font-semibold"
                        />
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </ChartContainer>
              );
            })()}
          </div>
          <div className="text-sm text-muted-foreground uppercase tracking-wider">
            TAUX DE VICTOIRE
          </div>
          <div>
            <span
              className="text-lg sm:text-xl font-bold"
              style={{ color: "var(--win-text)" }}
            >
              {stats.recent?.wins ?? stats.wins ?? 0}W
            </span>
            <span className="text-lg sm:text-xl font-bold"> - </span>
            <span
              className="text-lg sm:text-xl font-bold"
              style={{ color: "var(--lose-text)" }}
            >
              {stats.recent?.losses ?? stats.losses ?? 0}L
            </span>
          </div>
          <div className="text-xs text-muted-foreground">
            {stats.recent?.matches_played ?? stats.matches_played ?? 0}{" "}
            dernières parties
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EntityStatsCards;
