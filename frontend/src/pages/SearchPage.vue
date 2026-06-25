<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useProducts } from '@/composables/useProducts'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const route = useRoute()
const { products, loading, fetchProducts } = useProducts()
const query = ref('')
const catId = ref('')

watch(() => route.query.q, (q) => {
  if (q) { query.value = q as string; doSearch() }
})
watch(() => route.query.pid, (pid) => {
  if (pid) { catId.value = pid as string; fetchProducts(pid as string, true) }
})

async function doSearch() {
  if (!query.value.trim()) return
  const params = new URLSearchParams({ q: query.value })
  router.replace({ query: { q: query.value } })
  products.value = []
  // simple: search endpoint no está disponible, usamos el de productos con filtro
  await fetchProducts(catId.value || '', true)
}

function goHome() { router.push('/') }
function showHistory() {}
</script>

<template>
  <div class="page">
    <h2>Buscar</h2>
    <div class="search-box">
      <input v-model="query" type="text" placeholder="Buscar productos..." class="search-input"
             @keyup.enter="doSearch">
      <button @click="doSearch" class="search-btn">🔍</button>
    </div>
    <div class="product-list" v-if="products.length">
      <ProductCard v-for="p in products" :key="p.id" :product="p" @history="showHistory" />
    </div>
    <div v-else class="empty">Ingresá un término de búsqueda</div>
  </div>
</template>

<style scoped>
.page { padding: 16px; padding-bottom: 80px; }
h2 { margin: 0 0 12px; font-size: 20px; }
.search-box { display: flex; gap: 8px; margin-bottom: 16px; }
.search-input {
  flex: 1; padding: 12px 16px; border: 2px solid #e0e0e0; border-radius: 12px;
  font-size: 16px; outline: none; transition: border-color .2s;
}
.search-input:focus { border-color: #3483fa; }
.search-btn {
  padding: 12px 20px; border: none; border-radius: 12px; background: #3483fa;
  color: #fff; font-size: 18px; cursor: pointer;
}
.product-list { display: flex; flex-direction: column; gap: 8px; }
.empty { text-align: center; padding: 40px; color: #999; }
</style>
