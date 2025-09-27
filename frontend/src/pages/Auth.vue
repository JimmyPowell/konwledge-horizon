<template>
  <div class="auth">
    <!-- 返回首页按钮 -->
    <div class="back-to-home" @click="goToHome">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M9 22V12H15V22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>返回首页</span>
    </div>
    <div class="left">
      <div class="logo-section">
        <div class="logo-icon">N</div>
        <div class="brand-info">
          <div class="brand">NEUSteel Agent</div>
          <div class="subtitle">钢铁智能，冶铸未来</div>
        </div>
      </div>
      <div class="description">
        <p>东北大学冶金行业知识智能体</p>
        <p>融合人工智能与行业专业知识</p>
        <p>为冶金行业提供智能化解决方案</p>
      </div>
      <div class="steel-decorations">
        <div class="steel-bar bar1"></div>
        <div class="steel-bar bar2"></div>
        <div class="steel-bar bar3"></div>
        <div class="steel-bar bar4"></div>
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
const goToHome = () => router.push('/')
</script>

<style scoped>
.auth {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 100vh;
  background: var(--bg-primary);
  position: relative;
}

/* 返回首页按钮 */
.back-to-home {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  color: var(--text-light);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  z-index: 10;
  box-shadow: var(--shadow-md);
}

.back-to-home:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: var(--accent-color);
  color: var(--accent-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.back-to-home svg {
  width: 18px;
  height: 18px;
  transition: transform var(--transition-fast);
}

.back-to-home:hover svg {
  transform: scale(1.1);
}

.left {
  position: relative;
  padding: 48px;
  background: var(--steel-gradient);
  color: var(--text-light);
  display: flex;
  flex-direction: column;
  justify-content: center;
  overflow: hidden;
}

.left::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 Z" fill="rgba(214,158,46,0.1)"/></svg>');
  background-size: cover;
}

.logo-section {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 32px;
}

.logo-icon {
  width: 60px;
  height: 60px;
  background: var(--accent-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: var(--text-primary);
  font-size: 24px;
  box-shadow: var(--shadow-lg);
}

.brand-info {
  display: flex;
  flex-direction: column;
}

.brand {
  font-size: 32px;
  font-weight: 700;
  color: var(--text-light);
  line-height: 1.2;
}

.subtitle {
  margin-top: 4px;
  color: var(--accent-color);
  font-size: 16px;
  font-weight: 500;
}

.description {
  position: relative;
  z-index: 1;
  margin-bottom: 40px;
}

.description p {
  margin: 8px 0;
  font-size: 16px;
  color: var(--text-light);
  opacity: 0.9;
  line-height: 1.6;
}

.steel-decorations {
  position: absolute;
  bottom: 32px;
  left: 48px;
  right: 48px;
  height: 12px;
  display: flex;
  gap: 12px;
  z-index: 1;
}

.steel-bar {
  flex: 1;
  border-radius: var(--radius-sm);
  transform: skewX(-15deg);
  transition: all var(--transition-fast);
}

.steel-bar:hover {
  transform: skewX(-15deg) scale(1.05);
}

.bar1 { background: var(--accent-gradient); }
.bar2 { background: var(--danger-gradient); }
.bar3 { background: linear-gradient(135deg, #4a5568, #718096); }
.bar4 { background: linear-gradient(135deg, #2d3748, #4a5568); }

.right {
  padding: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
}

/* 卡片样式覆盖 */
:deep(.ant-card) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-steel);
}

:deep(.ant-card-head) {
  background: var(--steel-gradient);
  border-bottom: 1px solid var(--border-dark);
  border-radius: var(--radius-xl) var(--radius-xl) 0 0;
}

:deep(.ant-card-head .ant-tabs-tab) {
  color: var(--text-light);
  font-weight: 500;
}

:deep(.ant-card-head .ant-tabs-tab-active) {
  color: var(--accent-color);
  font-weight: 600;
}

:deep(.ant-card-head .ant-tabs-ink-bar) {
  background: var(--accent-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .auth {
    grid-template-columns: 1fr;
  }

  .left {
    min-height: 40vh;
    padding: 32px;
  }

  .logo-section {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .brand {
    font-size: 24px;
  }

  .description {
    text-align: center;
  }

  .steel-decorations {
    left: 32px;
    right: 32px;
  }

  .right {
    padding: 32px 16px;
  }
}
</style>

