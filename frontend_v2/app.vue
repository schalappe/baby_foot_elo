<script setup lang="ts">
  import { computed, provide } from 'vue';
  import type { NavLinkModel } from './models/NavLinkModel';
  import type { PlayerModel } from './models/PlayerModel';
  import type { TeamModel } from './models/TeamModel';
  import type { MatchModel } from './models/MatchModel';
  import { useApi } from './composable/useApi';

  const nav: NavLinkModel[] = [
    { label: 'ranking', to: '/' },
    { label: 'players', to: '/players' },
    { label: 'teams', to: '/teams' },
    { label: 'matches', to: '/matches' },
    { label: 'test', to: '/test' },
  ]

  const { read } = useApi();
  const { data: players, pending: playersPending, error: playersError } = read<PlayerModel[]>('/players');
  const { data: teams, pending: teamsPending, error: teamsError } = read<TeamModel[]>('/teams');
  const { data: matches, pending: matchesPending, error: matchesError } = read<MatchModel[]>('/matches');

  const allPending = computed(() => playersPending.value || teamsPending.value || matchesPending.value);
  const anyError = computed(() => playersError.value || teamsError.value || matchesError.value);

  provide('players', players);
  provide('teams', teams);
  provide('matches', matches);
  provide('pending', allPending);
  provide('errors', anyError);
</script>


<template>
  <div class="p-4 bg-green-200">
    <h1 class="text-2xl font-bold">Babyfoot Contest</h1>
    <NuxtLoadingIndicator />
    <nav>
      <ul class="flex gap-4">
        <li v-for="link in nav" :key="link.to">
          <NuxtLink :to="link.to" class="text-blue-600 hover:underline">
            {{ link.label }}
          </NuxtLink>
        </li>
      </ul>
    </nav>
  </div>
    <div v-if="playersPending || teamsPending || matchesPending" class="loading-indicator">
    Chargement des données...
  </div>
  <div v-if="playersError || teamsError || matchesError" class="error-indicator">
    Une erreur est survenue lors du chargement des données initiales.
    <p v-if="playersError">Joueurs: {{ playersError?.message }}</p>
    <p v-if="teamsError">Équipes: {{ teamsError?.message }}</p>
    <p v-if="matchesError">Matchs: {{ matchesError?.message }}</p>
  </div>
  <NuxtPage />
</template>

<style scoped>
  .loading-indicator {
    padding: 10px;
    background-color: #e0f2fe;
    color: #0c4a6e;
    border-radius: 5px;
    margin-top: 10px;
    text-align: center;
  }

  .error-indicator {
    padding: 10px;
    background-color: #fee2e2;
    color: #991b1b;
    border-radius: 5px;
    margin-top: 10px;
  }
</style>