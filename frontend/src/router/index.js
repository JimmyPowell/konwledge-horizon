import { createRouter, createWebHistory } from 'vue-router'
import { getAccessToken } from '../utils/tokens'
import Auth from '../pages/Auth.vue'
import MainLayout from '../layouts/MainLayout.vue'
import Home from '../pages/Home.vue'

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
      { path: 'history', name: 'history1', component: () => import('../pages/Placeholder.vue') },
      { path: 'history2', name: 'history2', component: () => import('../pages/Placeholder.vue') },
      { path: 'knowledge', name: 'knowledge', component: () => import('../pages/Placeholder.vue') },
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
