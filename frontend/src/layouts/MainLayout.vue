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
        <div class="avatar-trigger">
          <a-dropdown placement="bottomRight" trigger="['click']">
            <div class="avatar-wrapper">
              <img v-if="avatarUrl" :src="avatarUrl" alt="avatar" class="avatar" />
              <div v-else class="avatar placeholder">{{ initials }}</div>
            </div>
            <template #overlay>
              <a-menu @click="onUserMenu">
                <a-menu-item key="logout">退出登录</a-menu-item>
              </a-menu>
            </template>
          </a-dropdown>
        </div>
      </div>
    </a-layout-header>

    <!-- 下方主体布局：左侧侧栏 + 右侧内容 -->
    <a-layout>
      <a-layout-sider width="220" theme="light" :style="{ background: '#fff', borderRight: '1px solid #eee' }">
        <a-menu theme="light" mode="inline" v-model:selectedKeys="selectedKeys" @click="onMenu">
          <a-menu-item key="home">新建对话</a-menu-item>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getIdentifier, getRefreshToken } from '../utils/tokens'
import { logout as apiLogout } from '../services/api'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const selectedKeys = ref(['home'])
const identifier = ref('')
const avatarUrl = ref('') // 未来可由 /me 接口返回
const auth = useAuthStore()

const initials = computed(() => {
  const id = identifier.value || ''
  if (!id) return '用户'.slice(0, 1)
  // 如果是邮箱，取 @ 前首字母；否则取第一个字符
  const base = id.includes('@') ? id.split('@')[0] : id
  return base.slice(0, 1).toUpperCase()
})

onMounted(() => {
  const p = route.name
  selectedKeys.value = [String(p || 'home')]
  identifier.value = getIdentifier()
})

const onMenu = ({ key }) => {
  selectedKeys.value = [key]
  if (key === 'home') {
    try { localStorage.removeItem('kh_conversation_id') } catch {}
    router.push('/app?new=1')
  } else {
    router.push(`/app/${key}`)
  }
}

const onUserMenu = async ({ key }) => {
  if (key === 'logout') {
    try {
      const rt = getRefreshToken()
      if (rt) {
        await apiLogout(rt).catch(() => {})
      }
    } finally {
      auth.logout()
      router.push('/auth')
    }
  }
}
</script>

<style scoped>
.header { background: #fff; display:flex; align-items:center; justify-content:space-between; border-bottom: 1px solid #eee; padding: 0 16px; height: 68px; }
.header-left { display:flex; align-items:center; gap: 16px; }
.brand { font-weight: 700; font-size: 20px; }
.subtitle { color: #555; font-size: 16px; }
.user { display:flex; align-items:center; gap: 12px; }
.avatar-trigger { width: 40px; height: 40px; display:flex; align-items:center; justify-content:center; }
.avatar-wrapper { width: 40px; height: 40px; display:inline-flex; }
.avatar { width: 40px; height: 40px; border-radius: 999px; border: 1px solid #e5e7eb; display:inline-flex; align-items:center; justify-content:center; background:#f3f4f6; font-weight: 600; color:#6b7280; cursor: pointer; }
.avatar.placeholder { font-size: 14px; }
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
