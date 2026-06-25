<script setup lang="ts">
import type { Category } from '@/models/Category'

defineProps<{ categories: Category[]; activeId?: string }>()
const emit = defineEmits<{ select: [id: string, name: string] }>()

const iconMap: Record<string, string> = {
  celulares: '📱', computacion: '💻', electronica: '🎵',
  hogar: '🏠', electrodomesticos: '🔌', herramientas: '🔧',
  deportes: '⚽', bebes: '🍼', juegos: '🎮', moda: '👔',
  salud: '💊', industria: '🏢', accesorios: '🚗', mascotas: '🐾',
  antiguedades: '🏺', arte: '🎨', musica: '🎸', joyas: '💎',
  libros: '📚', souvenirs: '🎉', inmuebles: '🏠', agro: '🌾',
  servicios: '🔧', camaras: '📷', consolas: '🎮', alimentos: '🍔',
  autos: '🚘', entradas: '🎫', instrumentos: '🎸', otras: '📦',
  construccion: '🏗️', belleza: '💄',
}

function iconOf(id: string) {
  for (const [k, v] of Object.entries(iconMap))
    if (id.includes(k)) return v
  return '📦'
}
</script>

<template>
  <div class="chips">
    <button v-for="c in categories" :key="c.id"
            :class="{ active: c.id === activeId }"
            @click="emit('select', c.id, c.name)">
      <span>{{ iconOf(c.id) }}</span>
      <span>{{ c.name }}</span>
    </button>
  </div>
</template>

<style scoped>
.chips {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 12px 16px;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
}
.chips::-webkit-scrollbar { display: none; }
.chips button {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid #e0e0e0;
  background: #fff;
  font-size: 13px;
  font-weight: 500;
  color: #444;
  cursor: pointer;
  transition: all .2s;
  white-space: nowrap;
}
.chips button.active { background: #ebf4ff; border-color: #3483fa; color: #3483fa; }
</style>
