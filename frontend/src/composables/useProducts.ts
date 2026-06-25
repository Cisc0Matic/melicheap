import { ref, reactive } from 'vue'
import type { Product } from '@/models/Product'
import { api } from '@/services/api'

export function useProducts() {
  const products = ref<Product[]>([])
  const total = ref(0)
  const page = ref(1)
  const loading = ref(false)
  const perPage = 50

  async function fetchProducts(categoryId: string, reset = false) {
    if (reset) { page.value = 1; products.value = [] }
    loading.value = true
    try {
      const data = await api<{ products: Product[]; total: number }>(
        `/api/products?category_id=${categoryId}&page=${page.value}&per_page=${perPage}`
      )
      if (reset) products.value = data.products
      else products.value.push(...data.products)
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  function loadMore(categoryId: string) {
    page.value++
    fetchProducts(categoryId)
  }

  return { products, total, page, loading, perPage, fetchProducts, loadMore }
}
