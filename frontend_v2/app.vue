<script setup lang="ts">
  import { computed, provide, ref } from 'vue';
  import type { PlayerModel } from './models/PlayerModel';
  import type { TeamModel } from './models/TeamModel';
  import type { MatchModel } from './models/MatchModel';
  import { useApi } from './composable/useApi';
  import { useTheme } from 'vuetify';
  import '@mdi/font/css/materialdesignicons.css'


  const { read } = useApi();
  const { data: players, pending: playersPending, error: playersError } = read<PlayerModel[]>('/players');
  const { data: teams, pending: teamsPending, error: teamsError } = read<TeamModel[]>('/teams');
  const { data: matches, pending: matchesPending, error: matchesError } = read<MatchModel[]>('/matches');

  const allPending = computed(() => playersPending.value || teamsPending.value || matchesPending.value);
  const anyError = computed(() => playersError.value || teamsError.value || matchesError.value);

  const value = ref(0);
  const theme = useTheme();
  const isDarkMode = ref(theme.global.current.value.dark);
  function toggleTheme ()  {
    theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark';
  };  
  
  provide('players', players);
  provide('teams', teams);
  provide('matches', matches);
  provide('pending', allPending);
  provide('errors', anyError);
</script>


<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <NuxtLayout>
    <v-app>
      <v-app-bar app class="d-flex items-center">
        <!-- Menu pour les grands écrans -->
        <v-bottom-navigation class="d-none d-md-flex w-full" v-model="value" style="height: 64px;" active>
          <v-btn class="custom-btn-width" value="ranking" :to="'/'">
            <span>Ranking</span>
          </v-btn>
          <v-btn class="custom-btn-width" value="players" :to="'/players'">
            <span>Players</span>
          </v-btn>
          <v-btn class="custom-btn-width" value="teams" :to="'/teams'">
            <span>Teams</span>
          </v-btn>
          <v-btn class="custom-btn-width" value="matches" :to="'/matches'">
            <span>Matches</span>
          </v-btn>
          <v-btn class="theme-toggle-btn" color="secondary" :icon="theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night'" @click="toggleTheme">
          </v-btn>
        </v-bottom-navigation>
        
        <!-- Menu pour les petits écrans -->
        <div class="d-flex d-md-none">
          <v-menu>
            <template v-slot:activator="{ props }">
              <v-btn v-bind="props" icon="mdi-menu"></v-btn>
            </template>
            <v-list>
              <v-list-item :to="'/'">
                <v-list-item-title>Ranking</v-list-item-title>
              </v-list-item>
              <v-list-item :to="'/players'">
                <v-list-item-title>Players</v-list-item-title>
              </v-list-item>
              <v-list-item :to="'/teams'">
                <v-list-item-title>Teams</v-list-item-title>
              </v-list-item>
              <v-list-item :to="'/matches'">
                <v-list-item-title>Matches</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>

        <v-btn class="theme-toggle-btn" color="secondary" :icon="theme.global.current.value.dark ? 'mdi-weather-sunny' : 'mdi-weather-night'" @click="toggleTheme">
        </v-btn>
      </v-app-bar>

      <v-main>
        <v-container>
          <NuxtLoadingIndicator />
          <div v-if="allPending" class="loading-indicator">
            Chargement des données...
          </div>
          <div class="color-container" style="margin-top: 60px;">
            <v-btn class="theme-title" color="purple">Thème Clair & Sombre</v-btn>
            <v-btn class="color-box" color="primary">primary</v-btn>
            <v-btn class="color-box" color="secondary">secondary</v-btn>
            <v-btn class="color-box" color="accent">accent</v-btn>
            <v-btn class="color-box" color="error">error</v-btn>
            <v-btn class="color-box" color="info">info</v-btn>
            <v-btn class="color-box" color="success">success</v-btn>
            <v-btn class="color-box" color="warning">warning</v-btn>
          </div>
          <NuxtPage style="margin-top: 0px;" />
        </v-container>
      </v-main>

      <v-footer class="text-center">
        <v-container>
          <v-row v-if="anyError" class="error-indicator">
            <div class="theme-title">
              Une erreur est survenue lors du chargement des données initiales
              <br>
              <p v-if="playersError">Joueurs: {{ playersError?.message }}</p>
              <p v-if="teamsError">Équipes: {{ teamsError?.message }}</p>
              <p v-if="matchesError">Matchs: {{ matchesError?.message }}</p>
            </div>
          </v-row>
          <v-row>
            <span>© 2023 - All rights reserved</span>
          </v-row>
        </v-container>
      </v-footer>
    </v-app>
  </NuxtLayout>
</template>



<style scoped>

  .theme-toggle-btn {
    width: 180px !important;
    height: auto !important;
    justify-content: center !important;
    align-items: center !important;
    color: "secondary" !important;
  }

  .custom-btn-width {
    min-width: 160px !important;
    vertical-align: center !important;
    text-transform: uppercase !important;
    font-weight: bold !important;
    font-size: 16px !important;
  }

  .color-container {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 20px;
  }
  .color-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      text-align: center;
  }
  .theme-title {
      width: 100%;
      font-weight: bold;
      margin-bottom: 5px;
  }

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