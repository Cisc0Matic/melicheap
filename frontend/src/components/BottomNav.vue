<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const tabs = [
  { path: '/', icon: '🏠', label: 'Inicio' },
  { path: '/deals', icon: '🔥', label: 'Ofertas' },
  { path: '/search', icon: '🔍', label: 'Buscar' },
]
</script>

<template>
  <nav class="bottom-nav">
    <button v-for="t in tabs" :key="t.path"
            :class="{ active: route.path === t.path }"
            @click="router.push(t.path)">
      <span class="nav-icon">{{ t.icon }}</span>
      <span class="nav-label">{{ t.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.bottom-nav {
  display: flex;
  background: #fff;
  border-top: 1px solid #e0e0e0;
  padding: 6px 0;
  padding-bottom: env(safe-area-inset-bottom, 6px);
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
}
.bottom-nav button {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px;
  border: none;
  background: none;
  font-size: 10px;
  color: #999;
  cursor: pointer;
  transition: color .2s;
}
.bottom-nav button.active { color: #3483fa; }
.nav-icon { font-size: 22px; line-height: 1; }
.nav-label { font-weight: 600; }
</style>
