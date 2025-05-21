<script setup lang="ts">
  const navLinks = [
    { path: '/', to: '/', label: 'Home' },
    { path: '/players', to: '/players', label: 'Players' },
    { path: '/matches', to: '/matches', label: 'Matches' },
  ]
</script>

<template>
  <nav class="navbar">
    <NuxtLink v-for="(link, index) in navLinks" :key="index" :to="link.to" class="nav-link" active-class="active-nav-link">
      {{ link.label }}
    </NuxtLink>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-around;
  background-color: #44d437;
  padding: 12px;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 10px 20px;
}

.active-nav-link {
  color: #4CAF50;
}
</style>