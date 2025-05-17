<template>
  <div>
    <h1>Test API</h1>
    <p v-if="response">Réponse : {{ response }}</p>
    <p v-if="error" class="text-red-500">Erreur : {{ error }}</p>
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
