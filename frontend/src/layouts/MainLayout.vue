<template>
  <a-layout class="app-shell">
    <!-- 顶部 Header，覆盖全宽 -->
    <a-layout-header class="header">
      <div class="header-left">
        <div class="logo">
          <div class="logo-icon">N</div>
          <div class="brand-info">
            <span class="brand">NEUSteel Agent</span>
            <span class="subtitle">钢铁智能，冶铸未来</span>
          </div>
        </div>
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
    <a-layout class="main-area">
      <a-layout-sider width="220" theme="dark" class="sidebar">
        <a-menu theme="dark" mode="inline" v-model:selectedKeys="selectedKeys" @click="onMenu" class="steel-menu">
          <a-menu-item key="home">
            <span class="menu-icon">💬</span>
            <span>新建对话</span>
          </a-menu-item>
          <a-menu-item key="history">
            <span class="menu-icon">📋</span>
            <span>历史任务</span>
          </a-menu-item>
          <a-menu-item key="knowledge">
            <span class="menu-icon">📚</span>
            <span>我的知识库</span>
          </a-menu-item>
          <a-menu-item key="workflow">
            <span class="menu-icon">⚙️</span>
            <span>工作流广场</span>
          </a-menu-item>
        </a-menu>
      </a-layout-sider>
      <a-layout class="content-wrap">
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
import { useSettingsStore } from '../stores/settings'

const router = useRouter()
const route = useRoute()
const selectedKeys = ref(['home'])
const identifier = ref('')
const avatarUrl = ref('') // 未来可由 /me 接口返回
const auth = useAuthStore()
const settings = useSettingsStore()

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
      settings.resetLocal()
      router.push('/auth')
    }
  }
}
</script>

<style scoped>
.app-shell {
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
}

.header {
  background: var(--steel-gradient);
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-dark);
  padding: 0 16px;
  height: 68px;
  box-shadow: var(--shadow-steel);
  min-width: 0; /* 允许收缩 */
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0; /* 允许收缩 */
  overflow: hidden;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  min-width: 0; /* 允许收缩 */
}

.logo-icon {
  width: 36px;
  height: 36px;
  background: var(--accent-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: var(--text-primary);
  font-size: 16px;
  flex-shrink: 0; /* 不允许收缩 */
}

.brand-info {
  display: flex;
  flex-direction: column;
  min-width: 0; /* 允许文字收缩 */
  flex: 1;
}

.brand {
  font-weight: 700;
  font-size: 15px;
  color: var(--text-light);
  line-height: 1.1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.subtitle {
  color: var(--accent-color);
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}

.user {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-light);
}

.avatar-trigger {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-wrapper {
  width: 40px;
  height: 40px;
  display: inline-flex;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--accent-color);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-gradient);
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.avatar:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.avatar.placeholder {
  font-size: 14px;
}

.main-area {
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}

.sidebar {
  background: var(--steel-gradient) !important;
  border-right: 1px solid var(--border-dark) !important;
}

.content-wrap {
  display: flex;
  flex: 1 1 auto;
  min-height: 0;
  overflow: hidden;
}

.content {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
  min-width: 0;
  overscroll-behavior: contain;
  background: var(--bg-primary);
}

/* 菜单样式：深色钢铁风格 */
:deep(.ant-menu-inline) {
  border-inline-end: 0 !important;
}

:deep(.steel-menu) {
  background: transparent !important;
  border: none !important;
}

:deep(.steel-menu .ant-menu-item) {
  margin: 4px 8px !important;
  height: 48px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  border-radius: var(--radius-lg) !important;
  font-size: 14px !important;
  color: var(--text-light) !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  transition: all var(--transition-fast) !important;
  padding: 0 16px !important;
}

:deep(.steel-menu .ant-menu-item:hover) {
  background: rgba(214, 158, 46, 0.1) !important;
  border-color: var(--accent-color) !important;
  color: var(--accent-color) !important;
}

:deep(.steel-menu .ant-menu-item-selected),
:deep(.steel-menu .ant-menu-item-active) {
  background: var(--accent-gradient) !important;
  color: var(--text-primary) !important;
  font-weight: 600 !important;
  border-color: var(--accent-color) !important;
}

.menu-icon {
  margin-right: 8px;
  font-size: 16px;
  width: 20px;
  text-align: center;
}
</style>
