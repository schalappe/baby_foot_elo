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
  <NuxtLayout >
    <NuxtLoadingIndicator />
    <div v-if="playersPending || teamsPending || matchesPending" class="loading-indicator">
      Chargement des données...
    </div>
    <div v-if="playersError || teamsError || matchesError" class="error-indicator">
      Une erreur est survenue lors du chargement des données initiales.
      <p v-if="playersError">Joueurs: {{ playersError?.message }}</p>
      <p v-if="teamsError">Équipes: {{ teamsError?.message }}</p>
      <p v-if="matchesError">Matchs: {{ matchesError?.message }}</p>
    </div>
    <v-app>
      <v-app-bar class="d-flex align-center">
        <v-bottom-navigation       
          v-model="value"
          style="height: 64px;"
          active
        >
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
          <v-switch class="theme-toggle-btn"
              v-model="isDarkMode"
              :icon="isDarkMode ? 'mdi-weather-sunny' : 'mdi-weather-night'"
              :label="isDarkMode ? 'Dark' : 'Light'"
              @change="toggleTheme"
              color="secondary"
          ></v-switch>
        </v-bottom-navigation>
      </v-app-bar>

      <v-main>
        <v-container>
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
        <v-col>
          <span>© 2023 - All rights reserved</span>
        </v-col>
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