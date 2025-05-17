<script setup lang="ts">
import { ref } from 'vue';

    const matchs = ref([
        { id: 1, score: '3-2', team: 'Équipe A vs Équipe B' },
        { id: 2, score: '1-4', team: 'Équipe C vs Équipe D' },
        { id: 3, score: '2-2', team: 'Équipe E vs Équipe F' },
        { id: 4, score: '0-1', team: 'Équipe G vs Équipe H' },
        { id: 5, score: '5-3', team: 'Équipe I vs Équipe J' },
        { id: 6, score: '2-2', team: 'Équipe K vs Équipe L' },
    ]);
</script>

<template>
    <div>
        <h1 class="text-2xl font-bold">Liste des matchs</h1>
        <ul class="list-disc pl-5">
        <li v-for="match in matchs" :key="match.id">
            {{ match.score }} - {{ match.team }}
        </li>
        </ul>
    </div>
</template>