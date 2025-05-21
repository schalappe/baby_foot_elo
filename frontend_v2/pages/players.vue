<script setup lang="ts">
  import type { PlayerModel } from '@/models/PlayerModel';
  import { useApi } from '@/composable/useApi';
  import { inject, ref, type Ref} from 'vue';

  const players =  inject<Ref<PlayerModel[] | null>>('players');
  const createError = ref<Error | null>(null);
  const playerName = ref('');

  const { create, remove } = useApi();

  const addPlayer = async () => {
    createError.value = null;
    if(!playerName.value.trim()) {
      createError.value = new Error('Le nom du joueur ne peut pas être vide.')
      return;
    }
    try {
      const newPlayer = await create<PlayerModel>('/players', { name: playerName.value });
      if (players?.value) {
        players.value.push(newPlayer);
        console.log('Nouveau joueur ajouté:', newPlayer);
        playerName.value = '';
      }
    } catch (err) {
      console.error('Erreur lors de l\'ajout du joueur:', err);
      createError.value = err as Error;
    }
  };

  const deletePlayer = async (id: number) => {
    try {
      await remove('players', id);
      console.log('Joueur supprimé:', id);
      if (players?.value) {
        players.value = players.value.filter((player) => player.player_id !== id);
      }
    } catch (err) {
      console.error('Erreur lors de la suppression du joueur:', err);
      // Gérer l'erreur de suppression, par exemple afficher un toast spécifique
    }
};
</script>

<template>
    <div>
        <h1 class="text-2xl font-bold mb-4">Liste des joueurs</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="player in players" :key="String(player.player_id)" class="bg-white p-4 rounded shadow">
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
        <p v-if="createError" class="error-message">Erreur lors de l'ajout: {{ createError.message }}</p>
    </div>
</template>

<style scoped>
  .error-message {
  color: red;
  margin-top: 10px;
  }
</style>