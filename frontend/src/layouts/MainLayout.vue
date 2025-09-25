<template>
  <a-layout style="min-height:100vh">
    <!-- 顶部 Header，覆盖全宽 -->
    <a-layout-header class="header">
      <div class="header-left">
        <span class="brand">knowledge-horizon</span>
        <span class="subtitle">新一代知识库管理平台</span>
      </div>
      <div class="user">
        <span>欢迎您，{{ identifier || '用户' }}</span>
        <span class="avatar"></span>
      </div>
    </a-layout-header>

    <!-- 下方主体布局：左侧侧栏 + 右侧内容 -->
    <a-layout>
      <a-layout-sider width="220" theme="light" :style="{ background: '#fff', borderRight: '1px solid #eee' }">
        <a-menu theme="light" mode="inline" v-model:selectedKeys="selectedKeys" @click="onMenu">
          <a-menu-item key="home">首页</a-menu-item>
          <a-menu-item key="history">历史任务</a-menu-item>
          <a-menu-item key="knowledge">我的知识库</a-menu-item>
          <a-menu-item key="workflow">工作流广场</a-menu-item>
        </a-menu>
      </a-layout-sider>
      <a-layout>
        <a-layout-content class="content">
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getIdentifier } from '../utils/tokens'

const router = useRouter()
const route = useRoute()
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
.header { background: #fff; display:flex; align-items:center; justify-content:space-between; border-bottom: 1px solid #eee; padding: 0 16px; height: 68px; }
.header-left { display:flex; align-items:center; gap: 16px; }
.brand { font-weight: 700; font-size: 20px; }
.subtitle { color: #555; font-size: 16px; }
.user { display:flex; align-items:center; gap: 12px; }
.avatar { width: 40px; height: 40px; border-radius: 999px; border: 1px solid #e5e7eb; display:inline-block; }
.content { padding: 16px; }

/* 菜单样式：浅色、条目分隔线、居中 */
:deep(.ant-menu-inline) { border-inline-end: 0 !important; }
:deep(.ant-menu-light) { background: transparent; }
:deep(.ant-menu-light .ant-menu-item) {
  margin: 0 !important;
  height: 58px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #eee;
  font-size: 16px;
}
:deep(.ant-menu-light .ant-menu-item-selected),
:deep(.ant-menu-light .ant-menu-item-active) {
  background: transparent !important;
  font-weight: 600;
}
</style>
