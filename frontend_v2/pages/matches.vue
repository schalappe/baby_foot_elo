<script setup lang="ts">
    import type { MatchModel } from '@/models/MatchModel';
    import { inject, type Ref } from 'vue';
    const matches =  inject<Ref<MatchModel[]>>('players');
</script>

<template>
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
</template>