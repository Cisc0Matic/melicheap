import { createRouter, createWebHistory } from 'vue-router'
import ProductsPage from '@/pages/ProductsPage.vue'
import SearchPage from '@/pages/SearchPage.vue'
import DealsPage from '@/pages/DealsPage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'products',
      component: ProductsPage,
    },
    {
      path: '/deals',
      name: 'deals',
      component: DealsPage,
    },
    {
      path: '/search',
      name: 'search',
      component: SearchPage,
    },
  ],
})

export default router
