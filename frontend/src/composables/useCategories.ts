import { ref } from 'vue'
import type { Category } from '@/models/Category'
import { api } from '@/services/api'

export function useCategories() {
  const categories = ref<Category[]>([])
  const loading = ref(false)

  async function fetchCategories() {
    loading.value = true
    try {
      categories.value = await api<Category[]>('/api/categories')
    } finally {
      loading.value = false
    }
  }

  return { categories, loading, fetchCategories }
}
