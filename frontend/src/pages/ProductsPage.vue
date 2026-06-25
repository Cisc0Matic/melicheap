<script setup lang="ts">
import { onMounted, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCategories } from '@/composables/useCategories'
import { useProducts } from '@/composables/useProducts'
import { useRefresh } from '@/composables/useRefresh'
import CategoryChips from '@/components/CategoryChips.vue'
import ProductCard from '@/components/ProductCard.vue'

const route = useRoute()
const router = useRouter()
const { categories, fetchCategories } = useCategories()
const { products, total, loading, fetchProducts, loadMore } = useProducts()
const { progress, running, startRefresh } = useRefresh()
const selectedCat = ref('')
const selectedName = ref('')

onMounted(async () => {
  await fetchCategories()
  const cat = (route.query.cat as string) || categories.value[0]?.id
  if (cat) {
    selectedCat.value = cat
    const found = categories.value.find(c => c.id === cat)
    if (found) selectedName.value = found.name
    await fetchProducts(cat, true)
  }
})

watch(() => route.query.cat, async (id) => {
  if (id && id !== selectedCat.value) {
    selectedCat.value = id as string
    const found = categories.value.find(c => c.id === id)
    if (found) selectedName.value = found.name
    await fetchProducts(id as string, true)
  }
})

async function onSelectCat(id: string, name: string) {
  selectedCat.value = id
  selectedName.value = name
  await fetchProducts(id, true)
}

function showHistory(productId: string) {
  router.push({ path: '/search', query: { pid: productId } })
}
</script>

<template>
  <div class="page">
    <div v-if="running" class="progress-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progress.total ? `${(progress.done/progress.total)*100}%` : '0%' }"></div>
      </div>
      <span class="progress-text">
        <span v-if="progress.current">Actualizando: {{ progress.current }}</span>
        <span v-else>{{ progress.done }}/{{ progress.total }}</span>
      </span>
    </div>

    <div class="header-bar">
      <h2 class="page-title">{{ selectedName || 'Productos' }}</h2>
      <div class="header-actions">
        <span class="count">{{ total }} productos</span>
        <button class="btn-icon" @click="startRefresh" :disabled="running" title="Actualizar">🔄</button>
      </div>
    </div>

    <CategoryChips :categories="categories" :active-id="selectedCat" @select="onSelectCat" />

    <div class="product-list">
      <template v-if="products.length">
        <ProductCard v-for="p in products" :key="p.id" :product="p" @history="showHistory" />
      </template>
      <div v-else-if="!loading" class="empty">
        <p>No hay productos en esta categoría.</p>
      </div>
    </div>

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

    <button v-if="products.length < total && !loading" class="load-more" @click="loadMore(selectedCat)">
      Cargar más ({{ products.length }}/{{ total }}) ▼
    </button>
  </div>
</template>

<style scoped>
.page { padding-bottom: 80px; }
.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px 0;
}
.page-title { font-size: 20px; font-weight: 700; margin: 0; }
.header-actions { display: flex; align-items: center; gap: 8px; }
.count { font-size: 12px; color: #999; }
.btn-icon { background: none; border: 1px solid #e0e0e0; border-radius: 8px; padding: 6px 10px; font-size: 16px; cursor: pointer; transition: background .2s; }
.btn-icon:hover { background: #f5f5f5; }
.btn-icon:disabled { opacity: .4; cursor: not-allowed; }
.product-list { display: flex; flex-direction: column; gap: 8px; padding: 8px 16px; }
.empty { text-align: center; padding: 40px 16px; color: #999; font-size: 14px; }

.loading-box { display: flex; flex-direction: column; gap: 8px; padding: 8px 16px; }
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

.load-more {
  display: block;
  margin: 16px auto;
  padding: 12px 32px;
  border: none;
  border-radius: 10px;
  background: #3483fa;
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background .2s;
}
.load-more:hover { background: #2968c8; }

.progress-container {
  margin: 8px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.progress-bar { flex: 1; height: 6px; background: #e0e0e0; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #3483fa, #5a9bff); border-radius: 3px; transition: width .3s ease; }
.progress-text { font-size: 11px; color: #666; white-space: nowrap; }
</style>
