<script setup lang="ts">
import { RouterView } from 'vue-router'
import BottomNav from '@/components/BottomNav.vue'
</script>

<template>
  <div class="app-shell">
    <main>
      <RouterView />
    </main>
    <BottomNav />
  </div>
</template>

<style>
.app-shell { min-height: 100vh; display: flex; flex-direction: column; }
main { flex: 1; }
</style>
