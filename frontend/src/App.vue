<template>
  <a-config-provider :locale="zhCN">
    <div class="app">
      <NavBar v-if="!isAuth" />
      <main class="container" :class="{ full: isAuth }">
        <router-view />
      </main>
    </div>
  </a-config-provider>
  
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import NavBar from './components/NavBar.vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'

const route = useRoute()
const isAuth = computed(() => route.path.startsWith('/auth'))
</script>

<style>
:root {
  --fg: #222;
  --bg: #fff;
  --accent: #3b82f6;
}
html, body, #app { height: 100%; margin: 0; }
body { color: var(--fg); background: var(--bg); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol'; }
.container { max-width: 960px; margin: 24px auto; padding: 0 16px; }
.container.full { max-width: none; margin: 0; padding: 0; }
a { color: var(--accent); text-decoration: none; }
a.router-link-active { text-decoration: underline; }
button { cursor: pointer; }
</style>
