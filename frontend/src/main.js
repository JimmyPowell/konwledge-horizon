import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import 'highlight.js/styles/github.css' // 代码高亮样式

const app = createApp(App)

// Stores
const pinia = createPinia()
app.use(pinia)

// UI Library
app.use(Antd)

// Global Icons: Element Plus Icons
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// Router
app.use(router)

// Mount
app.mount('#app')
