<script setup lang="ts">
    import type { TeamModel } from '@/models/TeamModel';
    import { inject, type Ref } from 'vue';
    const teams =  inject<Ref<TeamModel[]>>('teams');
</script>

<template>
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
</template>