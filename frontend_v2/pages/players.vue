<template>
  <div>
    <h1>Liste des Utilisateurs</h1>
    <ul>
      <li v-for="user in users" :key="user.id">
        {{ user.name }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import useApi from '~/composables/useApi';

interface User {
  id: string;
  name: string;
}

const { data: users, error, getAll } = useApi<User>('players');

onMounted(async () => {
  await getAll();
  if (error.value) {
    console.error('Erreur lors de la récupération des utilisateurs:', error.value);
  }
});
</script>
