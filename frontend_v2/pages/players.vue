<script setup lang="ts">
  import type { PlayerModel } from '@/models/PlayerModel';
  import { useApi } from '@/composable/useApi';
  import { inject, ref, type Ref} from 'vue';
  import { VCard } from 'vuetify/components';

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
        console.log('Nouveau joueur ajouté :', newPlayer);
        playerName.value = '';
      }
    } catch (err) {
      console.error('Erreur lors de l\'ajout du joueur :', err);
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
      console.error('Erreur lors de la suppression du joueur :', err);
      createError.value = err as Error;
    }
};
</script>

<template>
    <v-container class="mb-4">
        <v-form @submit.prevent="addPlayer" class="mt-6">
            <div class="bg-secondary mb-4 p-4 rounded-md items-center shadow">
                <label for="playerName" class="text-primary font-bold text-base md:text-lg">AJOUTER UN NOUVEAU JOUEUR</label>
                <div class="mt-2 flex flex-col md:flex-row md:space-x-4">
                    <input type="text" id="playerName" v-model="playerName" required class="h-9 pl-3 bg-primary w-full rounded-lg shadow-md shadow-black/20">
                    <v-btn class="mt-3 md:mt-0 w-full md:w-auto items-center bg-primary text-secondary text-2xl px-7 rounded-lg" type="submit"><b>+</b></v-btn>
                </div>
            </div>
        </v-form>
        <p v-if="createError" class="error-message text-error">Erreur lors de l'ajout : {{ createError.message }}</p>
    </v-container>
    <v-container class="w-full">
        <v-card-title class="w-full mb-4">
            <div class="text-xl md:text-2xl text-center font-bold">LISTE DES JOUEURS</div>
        </v-card-title>
        <v-card class="bg-primary shadow-none">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6 shadow-secondary">
                <v-card-item v-for="player in players" :key="String(player.player_id)" class="text-center bg-secondary p-4 rounded-lg">
                    <v-card-title class="m-4 text-primary text-2xl font-bold text-center uppercase">{{ player.name }}</v-card-title>
                    <v-card-item class="mt-4 p-0 text-primary text-lg">Taux de victoires :<br/>  {{
                        player.matches_played && player.matches_played > 0 ?
                        (((player.wins ?? 0) / (player.matches_played ?? 0)) * 100).toFixed(2) : 0 
                        }}%
                    </v-card-item>
                    <v-card-item class="p-0 text-primary text-lg">EloScore :<br/> {{ player.global_elo }}</v-card-item>
                    <v-card-item class="p-0 text-primary text-lg">Victoires :<br/>  {{ player.wins }}</v-card-item>
                    <v-card-item class="p-0 text-primary text-lg">Défaites :<br/>  {{ player.losses }}</v-card-item>
                    <v-card-item class="p-0 text-primary text-lg">Matchs joués :<br/>  {{ player.matches_played }}</v-card-item>
                    <v-card-actions class="m-1 justify-center">
                      <v-btn text>
                        <v-icon class="mr-1">mdi-account-box</v-icon>
                        Détails joueur
                      </v-btn>
                  </v-card-actions>
                  </v-card-item>
            </div>
        </v-card>
    </v-container>
</template>

<style scoped>
  .error-message {
    padding: 12px;
    font-size: smaller;
    border-radius: 12px;
    margin-top: 12px;
  }
</style>