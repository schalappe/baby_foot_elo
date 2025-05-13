// frontend/app/matches/page.tsx
"use client";

import React, { useEffect, useState, useMemo } from 'react';
import Link from 'next/link'; 
import { Match, getMatches, MatchPlayerInfo } from '@/services/matchService';
import { Player, getPlayers as getPlayerList } from '@/services/playerService'; 
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button'; 
import { Select, SelectContent, SelectGroup, SelectItem, SelectLabel, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertCircle, CalendarDays, UserSearch, Users, Trophy, Eye, Download } from 'lucide-react'; 
import { format, startOfDay, endOfDay } from 'date-fns'; 
import { DateRange } from 'react-day-picker'; 
import { DateRangePicker } from '@/components/ui/date-range-picker'; 

const MatchHistoryPage = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [allPlayers, setAllPlayers] = useState<Player[]>([]); 
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRangeFilter, setDateRangeFilter] = useState<DateRange | undefined>(undefined);
  const [selectedPlayerIdFilter, setSelectedPlayerIdFilter] = useState<string | undefined>(undefined); 
  const [teamCompPlayer1IdFilter, setTeamCompPlayer1IdFilter] = useState<string | undefined>(undefined); 
  const [teamCompPlayer2IdFilter, setTeamCompPlayer2IdFilter] = useState<string | undefined>(undefined); 
  const [matchOutcomeFilter, setMatchOutcomeFilter] = useState<"win" | "loss" | "draw" | undefined>(undefined);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [fetchedMatches, fetchedPlayers] = await Promise.all([
          getMatches(),
          getPlayerList()
        ]);
        setMatches(fetchedMatches);
        setAllPlayers(fetchedPlayers);
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to fetch match history or players. Please try again later.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleDateRangeChange = (range: DateRange | undefined) => {
    setDateRangeFilter(range);
  };

  const handlePlayerFilterChange = (playerId: string) => {
    setSelectedPlayerIdFilter(playerId === "all" ? undefined : playerId);
  };

  const handleTeamCompPlayer1Change = (playerId: string) => {
    const newP1Id = playerId === "all" ? undefined : playerId;
    setTeamCompPlayer1IdFilter(newP1Id);
    if (!newP1Id || (teamCompPlayer2IdFilter && newP1Id === teamCompPlayer2IdFilter)) {
      setTeamCompPlayer2IdFilter(undefined);
    }
  };

  const handleTeamCompPlayer2Change = (playerId: string) => {
    setTeamCompPlayer2IdFilter(playerId === "all" ? undefined : playerId);
  };

  const handleMatchOutcomeChange = (outcome: string) => {
    setMatchOutcomeFilter(outcome === "any" ? undefined : outcome as "win" | "loss" | "draw");
  };

  const handleExportJSON = () => {
    if (filteredMatches.length === 0) {
      // Optionally show an alert or toast that there's nothing to export
      console.warn('No matches to export.');
      return;
    }
    const jsonString = `data:application/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(filteredMatches, null, 2) // null, 2 for pretty print
    )}`;
    const link = document.createElement("a");
    link.href = jsonString;
    link.download = "match_history.json";
    link.click();
  };

  const availableTeamCompPlayer2Options = useMemo(() => {
    if (!teamCompPlayer1IdFilter) {
      return allPlayers; 
    }
    return allPlayers.filter(p => p.id.toString() !== teamCompPlayer1IdFilter);
  }, [allPlayers, teamCompPlayer1IdFilter]);

  const filteredMatches = useMemo(() => {
    let tempMatches = matches;

    if (dateRangeFilter && dateRangeFilter.from) {
      const fromDate = startOfDay(dateRangeFilter.from);
      const toDate = dateRangeFilter.to ? endOfDay(dateRangeFilter.to) : endOfDay(dateRangeFilter.from);
      tempMatches = tempMatches.filter(match => {
        const matchDate = new Date(match.match_date);
        return matchDate >= fromDate && matchDate <= toDate;
      });
    }

    if (selectedPlayerIdFilter) {
      const playerIdNum = parseInt(selectedPlayerIdFilter, 10);
      tempMatches = tempMatches.filter(match => {
        const teamAPlayerIds = [match.team_a.player1.id, match.team_a.player2?.id].filter(Boolean);
        const teamBPlayerIds = [match.team_b.player1.id, match.team_b.player2?.id].filter(Boolean);
        return teamAPlayerIds.includes(playerIdNum) || teamBPlayerIds.includes(playerIdNum);
      });
    }

    if (teamCompPlayer1IdFilter) {
      const p1Id = parseInt(teamCompPlayer1IdFilter, 10);
      if (teamCompPlayer2IdFilter) {
        const p2Id = parseInt(teamCompPlayer2IdFilter, 10);
        tempMatches = tempMatches.filter(match => {
          const teamAHasBoth = 
            (match.team_a.player1.id === p1Id && match.team_a.player2?.id === p2Id) ||
            (match.team_a.player1.id === p2Id && match.team_a.player2?.id === p1Id);
          const teamBHasBoth = 
            (match.team_b.player1.id === p1Id && match.team_b.player2?.id === p2Id) ||
            (match.team_b.player1.id === p2Id && match.team_b.player2?.id === p1Id);
          return teamAHasBoth || teamBHasBoth;
        });
      } else {
        tempMatches = tempMatches.filter(match => {
          const p1SoloOnTeamA = match.team_a.player1.id === p1Id && !match.team_a.player2;
          const p1SoloOnTeamB = match.team_b.player1.id === p1Id && !match.team_b.player2;
          return p1SoloOnTeamA || p1SoloOnTeamB;
        });
      }
    }

    // Apply match outcome filter (only if a specific player is selected for individual filtering)
    if (selectedPlayerIdFilter && matchOutcomeFilter) {
      const playerIdNum = parseInt(selectedPlayerIdFilter, 10);
      tempMatches = tempMatches.filter(match => {
        let playerTeam: 'A' | 'B' | null = null;
        if (match.team_a.player1.id === playerIdNum || match.team_a.player2?.id === playerIdNum) {
          playerTeam = 'A';
        } else if (match.team_b.player1.id === playerIdNum || match.team_b.player2?.id === playerIdNum) {
          playerTeam = 'B';
        }

        if (!playerTeam) return false; // Should not happen if player filter is applied correctly before

        const teamAScore = match.team_a_score;
        const teamBScore = match.team_b_score;

        if (matchOutcomeFilter === 'win') {
          return (playerTeam === 'A' && teamAScore > teamBScore) || (playerTeam === 'B' && teamBScore > teamAScore);
        }
        if (matchOutcomeFilter === 'loss') {
          return (playerTeam === 'A' && teamAScore < teamBScore) || (playerTeam === 'B' && teamBScore < teamAScore);
        }
        if (matchOutcomeFilter === 'draw') {
          return teamAScore === teamBScore;
        }
        return true; // Should not reach here if outcome is win/loss/draw
      });
    }

    return tempMatches;
  }, [matches, dateRangeFilter, selectedPlayerIdFilter, teamCompPlayer1IdFilter, teamCompPlayer2IdFilter, matchOutcomeFilter]);

  const renderPlayerEloChange = (player: MatchPlayerInfo) => {
    if (!player || 
        typeof player.name !== 'string' || // Ensure name is a string
        typeof player.elo_before_match !== 'number' || 
        typeof player.elo_after_match !== 'number' || 
        typeof player.elo_change !== 'number'
        ) {
      return <span>{player?.name || 'Player Data Incomplete'}</span>;
    }
    const eloChangeText = `${player.elo_change >= 0 ? '+' : ''}${player.elo_change.toFixed(0)}`;
    return (
      <div className="text-xs">
        <span>{player.elo_before_match}</span>
        <Badge 
          variant={player.elo_change >= 0 ? 'default' : 'destructive'}
          className="ml-1 mr-1 text-xs p-0.5 h-auto leading-tight"
        >
          {eloChangeText}
        </Badge>
        <span>➔ {player.elo_after_match}</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <CardHeader className="px-0">
          <CardTitle>Historique des matches</CardTitle>
          <CardDescription>Consultez les résultats des matches passés et les changements d'ELO.</CardDescription>
        </CardHeader>
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <Skeleton key={i} className="h-12 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-10">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (filteredMatches.length === 0 && !loading && !error) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <CardHeader className="px-0">
          <CardTitle>Historique des matches</CardTitle>
          <CardDescription>Consultez les résultats des matches passés et les changements d'ELO.</CardDescription>
        </CardHeader>
        <div className="mb-6 flex flex-col md:flex-row gap-4">
          <DateRangePicker 
            onUpdateFilter={handleDateRangeChange} 
            className="w-full md:w-auto"
          />
          <Select onValueChange={handlePlayerFilterChange} defaultValue="all">
            <SelectTrigger className="w-full md:w-[280px]">
              <UserSearch className="mr-2 h-4 w-4 text-muted-foreground" />
              <SelectValue placeholder="Filtrer par joueur..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Joueurs</SelectLabel>
                <SelectItem value="all">Tous les joueurs</SelectItem>
                {allPlayers
                  .filter(player => player && typeof player.id !== 'undefined' && player.name)
                  .map((player) => (
                    <SelectItem key={player.id} value={player.id.toString()}>
                      {player.name}
                    </SelectItem>
                  ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          <Select onValueChange={handleTeamCompPlayer1Change} value={teamCompPlayer1IdFilter || "all"}>
            <SelectTrigger className="w-full md:w-[280px]">
              <Users className="mr-2 h-4 w-4 text-muted-foreground" />
              <SelectValue placeholder="Joueur 1 du team..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Joueur 1 du team</SelectLabel>
                <SelectItem value="all">N'importe quel joueur 1</SelectItem>
                {allPlayers
                  .filter(player => player && typeof player.id !== 'undefined' && player.name)
                  .map((player) => (
                    <SelectItem key={player.id} value={player.id.toString()}>
                      {player.name}
                    </SelectItem>
                  ))}
              </SelectGroup>
            </SelectContent>
          </Select>

          <Select onValueChange={handleTeamCompPlayer2Change} value={teamCompPlayer2IdFilter || "all"} disabled={!teamCompPlayer1IdFilter}>
            <SelectTrigger className="w-full md:w-[280px]">
              <Users className="mr-2 h-4 w-4 text-muted-foreground" />
              <SelectValue placeholder="Joueur 2 du team..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Joueur 2 du team (Optionnel)</SelectLabel>
                <SelectItem value="all">N'importe quel joueur 2 / Aucun</SelectItem>
                {availableTeamCompPlayer2Options
                  .filter(player => player && typeof player.id !== 'undefined' && player.name)
                  .map((player) => (
                    <SelectItem key={player.id} value={player.id.toString()}>
                      {player.name}
                    </SelectItem>
                  ))}
              </SelectGroup>
            </SelectContent>
          </Select>

          {/* Match Outcome Filter (enabled only if a player is selected) */}
          <Select 
            onValueChange={handleMatchOutcomeChange} 
            value={matchOutcomeFilter || "any"} 
            disabled={!selectedPlayerIdFilter}
          >
            <SelectTrigger className="w-full md:w-[280px]">
              <Trophy className="mr-2 h-4 w-4 text-muted-foreground" />
              <SelectValue placeholder="Résultat du match..." />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel>Résultat du match (pour le joueur sélectionné)</SelectLabel>
                <SelectItem value="any">N'importe quel résultat</SelectItem>
                <SelectItem value="win">Win</SelectItem>
                <SelectItem value="loss">Loss</SelectItem>
                <SelectItem value="draw">Draw</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>

          <Button onClick={handleExportJSON} variant="outline" className="w-full md:w-auto">
            <Download className="mr-2 h-4 w-4" /> Exporter en JSON
          </Button>

        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-10">
                <CalendarDays className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun match trouvé</h3>
                <p className="mt-1 text-sm text-gray-500">Commencez par enregistrer un nouveau match.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
      <CardHeader className="px-0 mb-4">
        <CardTitle>Historique des matches</CardTitle>
        <CardDescription>Consultez les résultats des matches passés et les changements d'ELO.</CardDescription>
      </CardHeader>
      <div className="mb-6 flex flex-col md:flex-row gap-4">
        <DateRangePicker 
          onUpdateFilter={handleDateRangeChange} 
          className="w-full md:w-auto"
        />
        <Select onValueChange={handlePlayerFilterChange} defaultValue="all">
          <SelectTrigger className="w-full md:w-[280px]">
            <UserSearch className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Filtrer par joueur..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Joueurs</SelectLabel>
              <SelectItem value="all">Tous les joueurs</SelectItem>
              {allPlayers
                .filter(player => player && typeof player.id !== 'undefined' && player.name)
                .map((player) => (
                  <SelectItem key={player.id} value={player.id.toString()}>
                    {player.name}
                  </SelectItem>
                ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <Select onValueChange={handleTeamCompPlayer1Change} value={teamCompPlayer1IdFilter || "all"}>
          <SelectTrigger className="w-full md:w-[280px]">
            <Users className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Joueur 1 du team..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Joueur 1 du team</SelectLabel>
              <SelectItem value="all">N'importe quel joueur 1</SelectItem>
              {allPlayers
                .filter(player => player && typeof player.id !== 'undefined' && player.name)
                .map((player) => (
                  <SelectItem key={player.id} value={player.id.toString()}>
                    {player.name}
                  </SelectItem>
                ))}
            </SelectGroup>
          </SelectContent>
        </Select>

        <Select onValueChange={handleTeamCompPlayer2Change} value={teamCompPlayer2IdFilter || "all"} disabled={!teamCompPlayer1IdFilter}>
          <SelectTrigger className="w-full md:w-[280px]">
            <Users className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Joueur 2 du team..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Joueur 2 du team (Optionnel)</SelectLabel>
              <SelectItem value="all">N'importe quel joueur 2 / Aucun</SelectItem>
              {availableTeamCompPlayer2Options
                .filter(player => player && typeof player.id !== 'undefined' && player.name)
                .map((player) => (
                  <SelectItem key={player.id} value={player.id.toString()}>
                    {player.name}
                  </SelectItem>
                ))}
            </SelectGroup>
          </SelectContent>
        </Select>

        {/* Match Outcome Filter (enabled only if a player is selected) */}
        <Select 
          onValueChange={handleMatchOutcomeChange} 
          value={matchOutcomeFilter || "any"} 
          disabled={!selectedPlayerIdFilter}
        >
          <SelectTrigger className="w-full md:w-[280px]">
            <Trophy className="mr-2 h-4 w-4 text-muted-foreground" />
            <SelectValue placeholder="Résultat du match..." />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Résultat du match (pour le joueur sélectionné)</SelectLabel>
              <SelectItem value="any">N'importe quel résultat</SelectItem>
              <SelectItem value="win">Victoire</SelectItem>
              <SelectItem value="loss">Défaite</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>

        <Button onClick={handleExportJSON} variant="outline" className="w-full md:w-auto">
          <Download className="mr-2 h-4 w-4" /> Exporter en JSON
        </Button>

      </div>
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Date</TableHead>
                <TableHead>Équipe A</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Équipe B</TableHead>
                <TableHead>Résultat</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredMatches.map((match) => {
                if (!match || typeof match.id === 'undefined' || match.id === null) {
                  console.error('Match object or match.id is invalid:', match);
                  return (
                    <TableRow key={Math.random().toString()}> {/* Use a random key for invalid items */}
                      <TableCell colSpan={6}> {/* Adjusted to 6 columns */}
                        <Alert variant="destructive">
                          <AlertCircle className="h-4 w-4" />
                          <AlertTitle>Erreur de données</AlertTitle>
                          <AlertDescription>
                            Erreur de données: match invalide.
                          </AlertDescription>
                        </Alert>
                      </TableCell>
                    </TableRow>
                  );
                }
                return (
                  <TableRow key={match.id}>
                    <TableCell>{format(new Date(match.match_date), 'MMM d, yyyy - HH:mm')}</TableCell>
                    <TableCell>
                      <div>{match.team_a.player1.name}</div>
                      <div>{renderPlayerEloChange(match.team_a.player1)}</div>
                      {match.team_a.player2 && (
                        <div className="mt-1 pt-1 border-t border-dashed">
                          <div>{match.team_a.player2.name}</div>
                          <div>{renderPlayerEloChange(match.team_a.player2)}</div>
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="font-semibold">
                      {match.team_a_score} - {match.team_b_score}
                    </TableCell>
                    <TableCell>
                      <div>{match.team_b.player1.name}</div>
                      <div>{renderPlayerEloChange(match.team_b.player1)}</div>
                      {match.team_b.player2 && (
                        <div className="mt-1 pt-1 border-t border-dashed">
                          <div>{match.team_b.player2.name}</div>
                          <div>{renderPlayerEloChange(match.team_b.player2)}</div>
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      {match.winning_team_id === 'A' && <Badge variant="default" className="bg-green-500 hover:bg-green-600">Équipe A Victoire</Badge>}
                      {match.winning_team_id === 'B' && <Badge variant="default" className="bg-blue-500 hover:bg-blue-600">Équipe B Victoire</Badge>}
                      {match.is_fanny && <Badge variant="destructive" className="ml-2">Fanny!</Badge>}
                    </TableCell>
                    <TableCell className="text-right">
                      <Link href={`/matches/${match.id}`} passHref>
                        <Button variant="outline" size="sm">
                          <Eye className="mr-2 h-4 w-4" /> Voir les détails
                        </Button>
                      </Link>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      {/* TODO: Add pagination component here later */}
    </div>
  );
};

export default MatchHistoryPage;
