<script setup lang="ts">
import type { Product } from '@/models/Product'

const props = defineProps<{ product: Product }>()
const emit = defineEmits<{ history: [id: string] }>()

const thumbSrc = props.product.thumbnail?.replace('http://', 'https://')
</script>

<template>
  <div class="card">
    <img :src="thumbSrc" :alt="product.title" class="thumb" loading="lazy"
         @error="($event.target as HTMLImageElement).src = 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%2280%22 height=%2280%22><rect fill=%22%23eee%22 width=%2280%22 height=%2280%22/></svg>'">
    <div class="info">
      <a :href="product.permalink" target="_blank" class="title" @click.stop>{{ product.title }}</a>
      <div class="tags">
        <span v-if="product.free_shipping" class="tag tag-ship">🚚 Envío gratis</span>
        <span v-if="product.installments" class="tag tag-install">{{ product.installments }}</span>
      </div>
    </div>
    <div class="price-block">
      <span v-if="product.original_price && product.original_price > product.price" class="orig">
        ${{ product.original_price.toLocaleString('es-AR') }}
      </span>
      <span class="price">
        ${{ product.price.toLocaleString('es-AR') }}
        <span v-if="product.discount_percentage" class="badge">-{{ product.discount_percentage }}%</span>
      </span>
    </div>
    <button class="hist-btn" @click.stop="emit('history', product.id)" title="Historial">📈</button>
  </div>
</template>

<style scoped>
.card {
  display: flex;
  gap: 12px;
  background: #fff;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,.06);
  transition: box-shadow .2s;
  align-items: center;
}
.thumb {
  width: 80px; height: 80px;
  object-fit: contain;
  border-radius: 8px;
  background: #fafafa;
  flex-shrink: 0;
  border: 1px solid #f0f0f0;
}
.info { flex: 1; min-width: 0; }
.title {
  font-size: 13px;
  font-weight: 500;
  color: #333;
  text-decoration: none;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
}
.tags { display: flex; gap: 4px; margin-top: 6px; flex-wrap: wrap; }
.tag { font-size: 10px; font-weight: 600; padding: 2px 6px; border-radius: 10px; }
.tag-ship { background: #e8f5e9; color: #2e7d32; }
.tag-install { background: #f3e5f5; color: #7b1fa2; }
.price-block { text-align: right; flex-shrink: 0; min-width: 90px; }
.orig { display: block; font-size: 12px; color: #999; text-decoration: line-through; }
.price { font-size: 18px; font-weight: 700; color: #00a650; white-space: nowrap; }
.badge { font-size: 10px; background: #00a650; color: #fff; padding: 1px 5px; border-radius: 4px; margin-left: 4px; vertical-align: middle; }
.hist-btn {
  background: none;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  width: 36px;
  height: 36px;
  font-size: 16px;
  cursor: pointer;
  flex-shrink: 0;
  transition: background .2s;
}
.hist-btn:hover { background: #f5f5f5; }
</style>
