<script setup lang="ts">
  import type { PlayerModel } from '../models/player';
  import { useApi } from '@/composable/useApi';
  import { onMounted, ref } from 'vue';

  const { create, read, readOne, update, remove } = useApi();
  const players = ref<PlayerModel[]>([]);
  const playerName = ref('');

  const fetchPlayers = async () => {
      const data = await read<PlayerModel>('/players');
      players.value = data;
      console.log(data);
      return data;
  };

  const addPlayer = async () => {
    try {
      const newPlayer = await create<PlayerModel>('/players', { name: playerName.value });
      console.log('Nouveau joueur ajouté:', newPlayer);
      await fetchPlayers();
    } catch (error) {
      console.error('Erreur lors de l\'ajout du joueur:', error);
    }
  };

  onMounted(fetchPlayers);
</script>

<template>
    <div>
        <h1 class="text-2xl font-bold mb-4">Liste des joueurs</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="player in players" :key="player.player_id" class="bg-white p-4 rounded shadow">
                <h2 class="text-xl font-semibold">{{ player.name }}</h2>
                <p class="text-gray-600">ID: {{ player.player_id }}</p>
                <p class="text-gray-600">EloScore: {{ player.global_elo }}</p>
                <p class="text-gray-600">Victoires {{ player.wins }}</p>
                <p class="text-gray-600">Défaites: {{ player.losses }}</p>
                <!-- Ajoutez d'autres détails du joueur ici si nécessaire -->
            </div>
        </div>
    </div>
    <div>
        <h1 class="text-xl font-bold mt-8">Ajouter un Nouveau Joueur</h1>
        <form @submit.prevent="addPlayer" class="mt-4">
            <div class="mb-4">
                <label for="playerName" class="block text-sm font-medium text-gray-700">Nom du Joueur:</label>
                <input type="text" id="playerName" v-model="playerName" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2">
            </div>
            <button class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" type="submit">Ajouter Joueur</button>
        </form>
    </div>
</template>