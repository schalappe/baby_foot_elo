<script setup lang="ts">
import { ref } from 'vue';

    const players = ref([
        { id: 1, name: 'Joueur 1', team: 'Équipe A' },
        { id: 2, name: 'Joueur 2', team: 'Équipe B' },
        { id: 3, name: 'Joueur 3', team: 'Équipe C' },
    ]);
</script>

<template>
    <div>
        <h1 class="text-2xl font-bold">Liste des joueurs</h1>
        <ul class="list-disc pl-5">
        <li v-for="player in players" :key="player.id">
            {{ player.name }} - {{ player.team }}
        </li>
        </ul>
    </div>
</template>