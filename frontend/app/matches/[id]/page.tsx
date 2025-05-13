// frontend/app/matches/[id]/page.tsx
"use client";

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Match, MatchPlayerInfo, getMatchById } from '@/services/matchService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { ArrowLeft, AlertCircle, CalendarDays, Trophy, Flame, StickyNote } from 'lucide-react';
import { format } from 'date-fns';

const MatchDetailPage = () => {
  const params = useParams();
  const router = useRouter();
  const matchId = typeof params.id === 'string' ? params.id : undefined;

  const [match, setMatch] = useState<Match | null | undefined>(undefined); // undefined for initial, null for not found
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!matchId) {
      setError('Match ID is missing.');
      setLoading(false);
      return;
    }

    const fetchMatchDetails = async () => {
      setLoading(true);
      try {
        const fetchedMatch = await getMatchById(matchId);
        setMatch(fetchedMatch);
        if (!fetchedMatch) {
            setError('Match not found.');
        }
      } catch (err) {
        console.error(`Error fetching match ${matchId}:`, err);
        setError('Failed to fetch match details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchMatchDetails();
  }, [matchId]);

  const renderPlayerInfo = (player: MatchPlayerInfo) => (
    <div className="flex flex-col">
      <span className="font-semibold">{player.name}</span>
      <span className={`text-sm ${player.elo_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
        {player.elo_before_match} → {player.elo_after_match} ({player.elo_change >= 0 ? '+' : ''}{player.elo_change} ELO)
      </span>
    </div>
  );

  const renderTeam = (teamLabel: string, teamInfo: Match['team_a'], teamScore: number) => (
    <Card className="flex-1">
      <CardHeader>
        <CardTitle className="text-xl">Team {teamLabel}</CardTitle>
        <CardDescription>Score: <Badge variant="secondary" className="text-lg">{teamScore}</Badge></CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {renderPlayerInfo(teamInfo.player1)}
        {teamInfo.player2 && renderPlayerInfo(teamInfo.player2)}
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <Skeleton className="h-8 w-1/4 mb-4" />
        <Skeleton className="h-4 w-1/2 mb-6" />
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <Skeleton className="h-48 w-full" />
          <Skeleton className="h-48 w-full" />
        </div>
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  if (error || !match) {
    return (
      <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
        <Button variant="outline" onClick={() => router.push('/matches')} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Retour à l'historique des matchs
        </Button>
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Erreur</AlertTitle>
          <AlertDescription>{error || 'Le match n\'a pas pu être trouvé.'}</AlertDescription>
        </Alert>
      </div>
    );
  }

  const getOutcomeText = () => {
    if (match.winning_team_id === 'A') return 'Team A Wins';
    if (match.winning_team_id === 'B') return 'Team B Wins';
    return 'Draw';
  };

  return (
    <div className="container mx-auto py-8 px-4 md:px-6 lg:px-8">
      <Button variant="outline" onClick={() => router.push('/matches')} className="mb-6 print:hidden">
        <ArrowLeft className="mr-2 h-4 w-4" /> Retour à l'historique des matchs
      </Button>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="text-3xl">Détails du match</CardTitle>
          <div className="flex items-center text-muted-foreground text-sm mt-1">
            <CalendarDays className="mr-2 h-4 w-4" />
            <span>{format(new Date(match.match_date), 'MMMM d, yyyy - HH:mm')}</span>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex flex-col md:flex-row gap-6">
            {renderTeam('A', match.team_a, match.team_a_score)}
            {renderTeam('B', match.team_b, match.team_b_score)}
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Résultat du match</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center">
                <Trophy className="mr-2 h-5 w-5 text-yellow-500" />
                <span className="text-lg font-semibold">{getOutcomeText()}</span>
              </div>
              {match.is_fanny && (
                <div className="flex items-center text-red-600">
                  <Flame className="mr-2 h-5 w-5" />
                  <span className="text-lg font-semibold">Fanny!</span>
                </div>
              )}
            </CardContent>
          </Card>

          {match.notes && (
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">Notes</CardTitle>
              </CardHeader>
              <CardContent className="flex items-start">
                <StickyNote className="mr-3 h-5 w-5 text-muted-foreground flex-shrink-0 mt-1" />
                <p className="text-sm text-muted-foreground whitespace-pre-wrap">{match.notes}</p>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default MatchDetailPage;
