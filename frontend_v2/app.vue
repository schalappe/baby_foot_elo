<script setup lang="ts">
  import { computed, provide, ref, watch } from 'vue';
  import type { PlayerModel } from './models/PlayerModel';
  import type { TeamModel } from './models/TeamModel';
  import type { MatchModel } from './models/MatchModel';
  import { useApi } from './composable/useApi';
  import { useTheme } from 'vuetify';
  import '@mdi/font/css/materialdesignicons.css';


  const { read } = useApi();
  const { data: players, pending: playersPending, error: playersError } = read<PlayerModel[]>('/players');
  const { data: teams, pending: teamsPending, error: teamsError } = read<TeamModel[]>('/teams');
  const { data: matches, pending: matchesPending, error: matchesError } = read<MatchModel[]>('/matches');

  const allPending = computed(() => playersPending.value || teamsPending.value || matchesPending.value);
  const anyError = computed(() => playersError.value || teamsError.value || matchesError.value);

  const value = ref(0);
  const theme = useTheme();
  const isDarkMode = ref(theme.global.current.value.dark);
  watch(() => theme.global.current.value.dark, (newVal: boolean) => {
    isDarkMode.value = newVal;
  });
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
    <v-app class="bg-primary text-secondary">
      <v-app-bar app class="custom-app-bar bg-primary d-flex items-center" >
        <!-- Menu pour les grands écrans -->
        <v-bottom-navigation class="custom-bottom-nav bg-primary text-secondary d-none d-md-flex w-full" v-model="value" active>
          <v-btn class="px-4 custom-btn-width" value="ranking" :to="'/'">
            <v-icon size="1.2em" left>mdi-chevron-triple-up</v-icon>
            <span>Ranking</span>
          </v-btn>
          <v-btn class="px-4 custom-btn-width" value="players" :to="'/players'">
            <v-icon size="1.2em" left>mdi-account</v-icon>
            <span>Players</span>
          </v-btn>
          <v-btn class="px-4 custom-btn-width" value="teams" :to="'/teams'">
            <v-icon size="1.2em" left>mdi-account-multiple</v-icon>
            <span>Teams</span>
          </v-btn>
          <v-btn class="px-4 custom-btn-width" value="matches" :to="'/matches'">
            <v-icon size="1.2em" left>mdi-mixed-martial-arts</v-icon>
            <span>Matches</span>
          </v-btn>
          <v-btn class="px-4 theme-toggle-btn text-secondry" 
            :icon="isDarkMode ? 'mdi-weather-sunny' : 'mdi-weather-night'"
            @click="toggleTheme">
          </v-btn>
        </v-bottom-navigation>   
        <!-- Menu pour les petits écrans -->
        <div class="custom-bottom-nav d-flex d-md-none items-center" >
          <v-menu>
            <template v-slot:activator="{ props }">
              <v-btn class="bottom-1.5  theme-toggle-btn text-secondary" v-bind="props" icon="mdi-menu"></v-btn>
            </template>
            <v-list class="bg-primary" style="height: auto;">
              <v-list-item :to="'/'">
                <v-list-item-title class="custom-btn-width text-secondary" > 
                  <v-icon size="1.2em" left>mdi-chevron-triple-up</v-icon>
                  Ranking
                </v-list-item-title>
              </v-list-item>
              <v-list-item :to="'/players'">
                <v-list-item-title class="custom-btn-width text-secondary" >
                  <v-icon size="1.2em" left>mdi-account</v-icon>
                  Players
                </v-list-item-title>
              </v-list-item>
              <v-list-item :to="'/teams'">
                <v-list-item-title class="custom-btn-width text-secondary" >
                  <v-icon size="1.2em" left>mdi-account-multiple</v-icon>
                  Teams
                </v-list-item-title>
              </v-list-item>
              <v-list-item :to="'/matches'">
                <v-list-item-title class="custom-btn-width text-secondary" icon="mdi-mixed-martial-arts">
                  <v-icon size="1.2em" left>mdi-mixed-martial-arts</v-icon>
                  Matches
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </div>
        <v-btn class="bottom-1.5 theme-toggle-btn text-secondary" 
          :icon="isDarkMode ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          @click="toggleTheme">
        </v-btn>
      </v-app-bar>

      <v-main class="fill-height">
        <v-container >
          <NuxtLoadingIndicator />
          <div v-if="allPending" class="loading-indicator">
            Chargement des données...
          </div>
          <div class="color-container" style="margin: 30px;">
            <v-btn class="color-box" color="primary">primary</v-btn>
            <v-btn class="color-box" color="secondary">secondary</v-btn>
            <v-btn class="color-box" color="accent">accent</v-btn>
            <v-btn class="color-box" color="error">error</v-btn>
            <v-btn class="color-box" color="info">info</v-btn>
            <v-btn class="color-box" color="success">success</v-btn>
            <v-btn class="color-box" color="warning">warning</v-btn>
          </div>
          <NuxtPage style="margin: 21px;" />
        </v-container>
      </v-main>

      <v-footer class="text-center elevation-21 bg-primary text-secondary">
        <v-container class="pa-3 opacity-85">
          <v-row  v-if="anyError" class="error-indicator pa-3 bg-error rounded-lg justify-center">
            <div class="font-bold pa-3 text-warning rounded-lg" >
              Une erreur est survenue lors du chargement des données initiales
              <br>
              <p class="font-normal font-italic" v-if="playersError">Joueurs: {{ playersError?.message }}</p>
              <p class="font-normal font-italic" v-if="teamsError">Équipes: {{ teamsError?.message }}</p>
              <p class="font-normal font-italic" v-if="matchesError">Matchs: {{ matchesError?.message }}</p>
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
  .custom-app-bar {
    height: 54px !important;
    box-shadow: none;
  }

  .custom-bottom-nav {
    height: 54px !important;
    box-shadow: none;
  }

  .theme-toggle-btn {
    width: 54px !important;
    height: 54px !important;
    margin-left: auto !important;
    border-radius: 21px !important;
  }

  .custom-btn-width {
    min-width: 120px !important;
    text-transform: uppercase !important;
    font-weight: bold !important;
    font-size: 14px !important;
    font-weight: 500 !important;
  }

  .color-container {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-bottom: 24px;
  }
  .color-box {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      text-align: center;
  }

  .loading-indicator {
    padding: 12px;
    background-color: #e0f2fe;
    color: #0c4a6e;
    border-radius: 12px;
    margin-top: 12px;
    text-align: center;
  }

  .error-indicator {
    padding: 12px;
    font-size: smaller;
    border-radius: 12px;
    margin-top: 12px;
  }
</style>