<script setup lang="ts">
  import { useFetch } from 'nuxt/app';
  const { data } = await useFetch('http://localhost:8000/health')
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-4"> Page d'accueil </h1>
    <p>{{ data }}</p>
  </div>
</template>

<style scoped>
</style>