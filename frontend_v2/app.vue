<script setup lang="ts">

// Typage explicite de `nav`
interface NavLink {
  label: string
  to: string
}

const nav: NavLink[] = [
  { label: 'ranking', to: '/' },
  { label: 'players', to: '/players' },
  { label: 'matchs', to: '/matchs' },
  { label: 'test', to: '/test' },
]
</script>


<template>
  <div class="p-4 bg-green-200">
    <h1 class="text-2xl font-bold">Babyfoot Contest</h1>
    <NuxtLoadingIndicator />
    <nav>
      <ul class="flex gap-4">
        <li v-for="link in nav" :key="link.to">
          <NuxtLink :to="link.to" class="text-blue-600 hover:underline">
            {{ link.label }}
          </NuxtLink>
        </li>
      </ul>
    </nav>
  </div>
  <NuxtPage />
</template>
