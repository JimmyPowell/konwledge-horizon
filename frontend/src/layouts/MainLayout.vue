<template>
  <a-layout style="min-height:100vh">
    <a-layout-sider collapsible v-model:collapsed="collapsed" width="200">
      <div class="logo">knowledge-horizon</div>
      <a-menu theme="light" mode="inline" v-model:selectedKeys="selectedKeys" @click="onMenu">
        <a-menu-item key="home">首页</a-menu-item>
        <a-menu-item key="history">历史任务</a-menu-item>
        <a-menu-item key="history2">历史任务</a-menu-item>
        <a-menu-item key="knowledge">我的知识库</a-menu-item>
        <a-menu-item key="workflow">工作流广场</a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <div class="title">新一代知识库管理平台</div>
        <div class="user">
          <span>欢迎您，{{ identifier || '用户' }}</span>
          <span class="avatar"></span>
        </div>
      </a-layout-header>
      <a-layout-content style="padding:16px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getIdentifier } from '../utils/tokens'

const router = useRouter()
const route = useRoute()
const collapsed = ref(false)
const selectedKeys = ref(['home'])
const identifier = ref('')

onMounted(() => {
  const p = route.name
  selectedKeys.value = [String(p || 'home')]
  identifier.value = getIdentifier()
})

const onMenu = ({ key }) => {
  selectedKeys.value = [key]
  if (key === 'home') router.push('/app')
  else router.push(`/app/${key}`)
}
</script>

<style scoped>
.logo { height: 48px; display:flex; align-items:center; justify-content:center; font-weight: 600; border-bottom: 1px solid #eee; }
.header { background: #fff; display:flex; align-items:center; justify-content:space-between; border-bottom: 1px solid #eee; }
.title { margin-left: 8px; }
.user { display:flex; align-items:center; gap: 12px; }
.avatar { width: 36px; height: 36px; border-radius: 999px; border: 1px solid #e5e7eb; display:inline-block; }
</style>

