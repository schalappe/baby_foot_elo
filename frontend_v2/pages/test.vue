<template>
  <div class="bg-accent p-4 opacity-90 rounded-lg shadow-md">
    <h1 class="text-h4 p-4 text-info text-uppercase text-center">TEST INFO API</h1>
    <p v-if="response" class="text-success text-h7 p-4 text-center"> Réponse : {{ response }}</p>
    <p v-if="error" class="text-error text-h7 p-4 text-center">Erreur : {{ error }}</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
const response = ref(null);
const error = ref(null);

onMounted(async () => {
  try {
    const res = await $fetch('http://localhost:8000/health');
    response.value = res;
  } catch (err) {
    error.value = err.message;
    console.error('API error:', err);
  }
});
</script>
