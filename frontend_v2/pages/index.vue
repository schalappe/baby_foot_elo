<!-- pages/index.vue -->
<script lang="ts" setup>
  import { useApi } from '../composable/useApi';
  import type { PlayerModel } from '../models/player';

  const { create, read, readOne, update, remove } = useApi();
  const fetchData = async () => {
  const data = await read<PlayerModel>('/players');
  console.log(data);
  };

  const fetchSingleData = async (id: number) => {
    const data = await readOne<PlayerModel>('/players', id);
    console.log(data);
  };

  const createData = async () => {
    const newData = await create<PlayerModel>('/players', { name: 'New Item' });
    console.log(newData);
  };
  createData();

  const updateData = async (id: number) => {
    const updatedData = await update<PlayerModel>('/players', id, { name: 'Updated Item' });
    console.log(updatedData);
  };

  const deleteData = async (id: number) => {
    await remove('/players', id);
    console.log('Item deleted');
  };
</script>

<template>
  <div>
    <p>Bienvenue sur la page d’accueil</p>
    <p v-if="fetchData">Réponse : {{ fetchData() }}</p>
  </div>
</template>