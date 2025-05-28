<script lang="ts" setup>
  import type { PlayerModel } from '@/models/PlayerModel';
  import type { TeamModel } from '@/models/TeamModel';
  import type { MatchModel } from '@/models/MatchModel';
  import { inject, type Ref } from 'vue';

  const players =  inject<Ref<PlayerModel[]>>('players');
  const teams = inject<Ref<TeamModel[]>>('teams');
  const matches = inject<Ref<MatchModel[]>>('matches');  
</script>

<template>
  <div>
    <div>
      <h1 class="text-2xl font-bold mb-4">Bienvenue sur la page d’accueil</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="player in players" :key="String(player.player_id)" class="bg-white p-4 rounded shadow">
          <h2 class="text-xl font-semibold">{{ player.name }}</h2>
          <p class="text-gray-600">EloScore: {{ player.global_elo }}</p>
          <p class="text-gray-600">Victoires {{ player.wins }}</p>
          <p class="text-gray-600">Défaites: {{ player.losses }}</p>
          <!-- Ajoutez d'autres détails du joueur ici si nécessaire -->
        </div>
      </div>
    </div>
    <div>
      <h1 class="text-2xl font-bold mb-4">Liste des équipes</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="team in teams" :key="String(team.team_id)" class="bg-white p-4 rounded shadow">
          <h2 class="text-xl font-semibold">{{ team.rank }}</h2>  
          <p class="text-gray-600">Joueur 1: {{ team.player1.name }}</p>
          <p class="text-gray-600">Joueur 2: {{ team.player2.name }}</p>
          <p class="text-gray-600">EloScore: {{ team.global_elo }}</p>
          <p class="text-gray-600">Last Match: {{ team.last_match_at }}</p>
        </div>
      </div>
    </div>
    <div>
      <h1 class="text-2xl font-bold mb-4">Liste des matches</h1>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="match in matches" :key="String(match.match_id)" class="bg-white p-4 rounded shadow">
          <h2 class="text-xl font-semibold">Winner: {{ match.winner_team }}</h2>
          <p class="text-gray-600">Losser: {{ match.loser_team }}</p>
          <p class="text-gray-600">Date: {{ match.day, match.month, match.year }}</p>
          <p class="text-gray-600">ID {{ match.match_id }}</p>
          <!-- Ajoutez d'autres détails du joueur ici si nécessaire -->
        </div>
      </div>
    </div>
    <br />
    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      Click it !
    </button>
  </div>
</template>