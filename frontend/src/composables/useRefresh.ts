import { ref } from 'vue'
import { api } from '@/services/api'

export function useRefresh() {
  const progress = ref({ total: 0, done: 0, current: '' })
  const running = ref(false)

  async function startRefresh() {
    running.value = true
    await api('/api/refresh', { method: 'POST' })
    const es = new EventSource(`/api/refresh/progress/stream`)
    es.onmessage = (e) => {
      const data = JSON.parse(e.data)
      progress.value = data
      if (data.done >= data.total && data.total > 0) {
        es.close()
        running.value = false
      }
    }
    es.onerror = () => {
      es.close()
      running.value = false
    }
  }

  return { progress, running, startRefresh }
}
