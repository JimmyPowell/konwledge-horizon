import { createRouter, createWebHistory } from 'vue-router'
import { getAccessToken } from '../utils/tokens'
import Auth from '../pages/Auth.vue'
import MainLayout from '../layouts/MainLayout.vue'
import Home from '../pages/Home.vue'
import History from '../pages/History.vue'
import Knowledge from '../pages/Knowledge.vue'
import KnowledgeDetail from '../pages/KnowledgeDetail.vue'

const routes = [
  { path: '/', redirect: () => (getAccessToken() ? '/app' : '/auth') },
  { path: '/login', redirect: '/auth' },
  { path: '/auth', name: 'auth', component: Auth },
  {
    path: '/app',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'home', component: Home },
      { path: 'history', name: 'history', component: History },
      { path: 'knowledge', name: 'knowledge', component: Knowledge },
      { path: 'knowledge/:id', name: 'knowledge-detail', component: KnowledgeDetail },
      { path: 'workflow', name: 'workflow', component: () => import('../pages/Placeholder.vue') }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  if (to.meta?.requiresAuth && !getAccessToken()) {
    next({ path: '/auth' })
  } else if (to.path === '/auth' && getAccessToken()) {
    next({ path: '/app' })
  } else {
    next()
  }
})

export default router
