<script setup lang="ts">
  import { useApi } from './composable/useApi';
  import { onMounted, provide, ref } from 'vue';
  import type { NavLinkModel } from './models/NavLinkModel';
  import type { PlayerModel } from './models/PlayerModel';
  import type { TeamModel } from './models/TeamModel';
  import type { MatchModel } from './models/MatchModel';


  const nav: NavLinkModel[] = [
    { label: 'ranking', to: '/' },
    { label: 'players', to: '/players' },
    { label: 'teams', to: '/teams' },
    { label: 'matches', to: '/matches' },
    { label: 'test', to: '/test' },
  ]

  const { read } = useApi();
  const players = ref<PlayerModel[]>([]);
  const teams = ref<TeamModel[]>([]);
  const matches = ref<MatchModel[]>([]);

  onMounted(async () => {
      const playersData = await read<PlayerModel>('/players');
      const teamsData = await read<TeamModel>('/teams');
      const matchsData = await read<MatchModel>('/matches');
      players.value = playersData;
      teams.value = teamsData;
      matches.value = matchsData;
  });

  provide('players', players);
  provide('teams', teams);
  provide('matches', matches);
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
  <NuxtPage />
</template>
