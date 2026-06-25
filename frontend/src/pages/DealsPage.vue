<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '@/services/api'
import type { Product } from '@/models/Product'
import { useRouter } from 'vue-router'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const deals = ref<Product[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const data = await api<{ products: Product[] }>('/api/deals')
    deals.value = data.products
  } catch { /* ignore */ } finally { loading.value = false }
})

function showHistory(id: string) {
  router.push({ path: '/search', query: { pid: id } })
}
</script>

<template>
  <div class="page">
    <h2>🔥 Ofertas</h2>
    <p class="sub">Productos con descuento</p>

    <div v-if="loading" class="loading-box">
      <div class="skeleton" v-for="i in 3" :key="i">
        <div class="sk-img"></div>
        <div class="sk-lines">
          <div class="sk-line" style="width:70%"></div>
          <div class="sk-line" style="width:45%"></div>
        </div>
        <div class="sk-price"></div>
      </div>
    </div>

    <div v-else-if="deals.length" class="product-list">
      <ProductCard v-for="p in deals" :key="p.id" :product="p" @history="showHistory" />
    </div>
    <div v-else class="empty">No hay ofertas disponibles</div>
  </div>
</template>

<style scoped>
.page { padding: 16px; padding-bottom: 80px; }
h2 { margin: 0; font-size: 22px; }
.sub { color: #999; font-size: 13px; margin: 4px 0 16px; }
.product-list { display: flex; flex-direction: column; gap: 8px; }
.empty { text-align: center; padding: 40px; color: #999; }
.loading-box { display: flex; flex-direction: column; gap: 8px; }
.skeleton { display: flex; gap: 12px; background: #fff; padding: 12px; border-radius: 12px; align-items: center; }
.sk-img { width: 80px; height: 80px; border-radius: 8px; background: #f0f0f0; flex-shrink: 0; }
.sk-lines { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.sk-line { height: 14px; border-radius: 4px; background: #f0f0f0; }
.sk-price { width: 80px; height: 20px; border-radius: 4px; background: #f0f0f0; }
.sk-img, .sk-line, .sk-price {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
