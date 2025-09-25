<template>
  <div class="auth">
    <div class="left">
      <div class="brand">knowledge-horizon</div>
      <div class="subtitle">新一代知识库管理平台</div>
      <div class="lines">
        <div class="l l1"></div>
        <div class="l l2"></div>
        <div class="l l3"></div>
        <div class="l l4"></div>
      </div>
    </div>
    <div class="right">
      <a-card style="max-width:420px;width:100%" :tab-list="tabList" :active-tab-key="activeTab" @tabChange="onTab">
        <template #customTab="{ key, name }">
          <span>{{ name }}</span>
        </template>
        <template #tabBarExtraContent></template>
        <template #default>
          <LoginForm v-if="activeTab==='login'" @success="onLoginSuccess" />
          <RegisterForm v-else @success="onRegisterSuccess" />
        </template>
      </a-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import LoginForm from '../sections/LoginForm.vue'
import RegisterForm from '../sections/RegisterForm.vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const activeTab = ref('login')
const tabList = [
  { key: 'login', name: '登录' },
  { key: 'register', name: '注册' }
]
const onTab = (key) => { activeTab.value = key }
const onLoginSuccess = () => router.push('/app')
const onRegisterSuccess = () => router.push('/app')
</script>

<style scoped>
.auth { display: grid; grid-template-columns: 1fr 1fr; min-height: 100vh; }
.left { position: relative; padding: 48px; border-right: 1px solid #eee; display:flex; flex-direction:column; justify-content:center; }
.brand { font-size: 28px; font-weight: 700; }
.subtitle { margin-top: 8px; color: #666; }
.lines { position: absolute; bottom: 32px; left: 48px; right: 48px; height: 8px; display:flex; gap: 8px; }
.l { flex:1; border-radius: 6px; }
.l1 { background: linear-gradient(90deg,#60a5fa,#34d399); }
.l2 { background: linear-gradient(90deg,#f472b6,#f59e0b); }
.l3 { background: linear-gradient(90deg,#a78bfa,#22d3ee); }
.l4 { background: linear-gradient(90deg,#ef4444,#f97316); }
.right { display:flex; align-items:center; justify-content:center; padding: 24px; }
@media (max-width: 920px){ .auth{ grid-template-columns:1fr; } .left{ display:none; } }
</style>

