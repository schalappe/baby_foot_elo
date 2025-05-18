<!-- pages/index.vue -->
<script lang="ts" setup>
  import type { PlayerModel } from '../models/player';
  import { useApi } from '../composable/useApi';
import { onMounted, ref } from 'vue';

  const { create, read, readOne, update, remove } = useApi();
  const players = ref<PlayerModel[]>([]);

  const fetchData = async () => {
    const data = await read<PlayerModel>('/players');
    players.value = data;
    console.log(data);
    return data;
  };

  const fetchSingleData = async (id: number) => {
    const data = await readOne<PlayerModel>('/players', id);
    console.log(data);
  };

  const createData = async (name: string) => {
    const newData = await create<PlayerModel>('/players', { name });
    console.log(newData);
  };

  const updateData = async (id: number, player: PlayerModel) => {
    const updatedData = await update<PlayerModel>('/players', id, player);
    console.log(updatedData);
  };

  const deleteData = async (id: number) => {
    await remove('/players', id);
    console.log('Item deleted');
  };
  onMounted(fetchData)
</script>

<template>
  <div>
    <div>
      <h1 class="text-2xl font-bold mb-4">Bienvenue sur la page d’accueil</h1>
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
    <br />
    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      Click it !
    </button>
  </div>
</template>