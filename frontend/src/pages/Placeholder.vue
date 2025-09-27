<template>
  <section class="workflow-plaza">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="title-section">
        <h1 class="page-title">工作流广场</h1>
        <p class="page-subtitle">智能工作流模板，提升您的工作效率</p>
      </div>
    </div>

    <!-- 即将推出的工作流 -->
    <div class="coming-soon-section">
      <div class="section-header">
        <h2 class="section-title">即将推出</h2>
        <p class="section-desc">我们正在为您准备更多强大的工作流工具</p>
      </div>

      <div class="workflow-grid">
        <div
          v-for="workflow in comingSoonWorkflows"
          :key="workflow.id"
          class="workflow-card coming-soon"
        >
          <div class="card-header">
            <div class="workflow-icon">
              <component :is="workflow.icon" />
            </div>
            <div class="coming-soon-badge">即将推出</div>
          </div>
          <div class="card-content">
            <h3 class="workflow-name">{{ workflow.name }}</h3>
            <p class="workflow-desc">{{ workflow.description }}</p>
            <div class="workflow-features">
              <span
                v-for="feature in workflow.features"
                :key="feature"
                class="feature-tag"
              >
                {{ feature }}
              </span>
            </div>
          </div>
          <!-- 去除开发进度显示，保留功能提示 -->
        </div>
      </div>
    </div>

    <!-- 敬请期待区域 -->
    <div class="stay-tuned-section">
      <div class="stay-tuned-content">
        <div class="stay-tuned-icon">
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
            <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" fill="#74b9ff"/>
            <path d="M19 15L20.09 18.26L24 19L20.09 19.74L19 23L17.91 19.74L14 19L17.91 18.26L19 15Z" fill="#a29bfe"/>
            <path d="M5 6L5.5 7.5L7 8L5.5 8.5L5 10L4.5 8.5L3 8L4.5 7.5L5 6Z" fill="#fd79a8"/>
          </svg>
        </div>
        <h2 class="stay-tuned-title">更多精彩工具正在路上</h2>
        <p class="stay-tuned-desc">
          我们的团队正在努力开发更多智能化工作流工具，包括数据分析、文档处理、自动化任务等功能。
          <br>
          敬请期待，让AI为您的工作带来更多可能！
        </p>
        <div class="notification-signup">
          <a-input
            v-model:value="email"
            placeholder="输入邮箱地址，第一时间获取更新通知"
            size="large"
            class="email-input"
          >
            <template #suffix>
              <a-button type="primary" @click="subscribeNotification">
                订阅通知
              </a-button>
            </template>
          </a-input>
        </div>
      </div>
    </div>

    <!-- 联系我们 -->
    <div class="contact-section">
      <div class="contact-content">
        <h3 class="contact-title">有想法？联系我们</h3>
        <p class="contact-desc">如果您有特定的工作流需求或建议，欢迎与我们联系</p>
        <div class="contact-buttons">
          <a-button size="large" @click="openFeedback">
            <template #icon>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M20,2H4A2,2 0 0,0 2,4V22L6,18H20A2,2 0 0,0 22,16V4C0,2.89 21.1,2 20,2Z"/>
              </svg>
            </template>
            提交反馈
          </a-button>
          <a-button type="primary" size="large" @click="contactSupport">
            <template #icon>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M7.07,18.28C7.5,17.38 10.12,16.5 12,16.5C13.88,16.5 16.5,17.38 16.93,18.28C15.57,19.36 13.86,20 12,20C10.14,20 8.43,19.36 7.07,18.28M18.36,16.83C16.93,15.09 13.46,14.5 12,14.5C10.54,14.5 7.07,15.09 5.64,16.83C4.62,15.5 4,13.82 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,13.82 19.38,15.5 18.36,16.83M12,6C10.06,6 8.5,7.56 8.5,9.5C8.5,11.44 10.06,13 12,13C13.94,13 15.5,11.44 15.5,9.5C15.5,7.56 13.94,6 12,6M12,11A1.5,1.5 0 0,1 10.5,9.5A1.5,1.5 0 0,1 12,8A1.5,1.5 0 0,1 13.5,9.5A1.5,1.5 0 0,1 12,11Z"/>
              </svg>
            </template>
            联系客服
          </a-button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, h } from 'vue'
import { message } from 'ant-design-vue'

const email = ref('')

// 即将推出的工作流
const comingSoonWorkflows = ref([
  {
    id: 1,
    name: '智能数据分析',
    description: '面向自动化的数据管道与持续建模（MLOps），支持定时/事件驱动的ETL、特征计算与模型滚动更新',
    features: ['自动化管道', '持续建模', '模型监控'],
    progress: 75,
    icon: () => h('svg', {
      width: '32',
      height: '32',
      viewBox: '0 0 24 24',
      fill: 'none'
    }, [
      h('path', {
        d: 'M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z',
        fill: '#00b894'
      })
    ])
  },
  {
    id: 2,
    name: '深化文档解析',
    description: '面向复杂文档的版面理解、结构化抽取与语义切分，支持批量处理与格式转换',
    features: ['版面分析', '结构化抽取', '语义切分'],
    progress: 60,
    icon: () => h('svg', {
      width: '32',
      height: '32',
      viewBox: '0 0 24 24',
      fill: 'none'
    }, [
      h('path', {
        d: 'M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z',
        fill: '#2980b9'
      })
    ])
  },
  {
    id: 3,
    name: '自动化任务调度',
    description: '定时执行各种任务，支持条件触发和多步骤工作流',
    features: ['定时任务', '条件触发', '流程编排'],
    progress: 45,
    icon: () => h('svg', {
      width: '32',
      height: '32',
      viewBox: '0 0 24 24',
      fill: 'none'
    }, [
      h('path', {
        d: 'M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M16.2,16.2L11,13V7H12.5V12.2L17,14.9L16.2,16.2Z',
        fill: '#e17055'
      })
    ])
  }
])

// 方法
const subscribeNotification = () => {
  if (!email.value) {
    message.warning('请输入邮箱地址')
    return
  }

  // 简单的邮箱格式验证
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email.value)) {
    message.error('请输入有效的邮箱地址')
    return
  }

  message.success('订阅成功！我们会第一时间通知您最新功能')
  email.value = ''
}

const openFeedback = () => {
  message.info('反馈功能开发中，您可以通过客服联系我们')
}

const contactSupport = () => {
  message.info('客服功能开发中，敬请期待')
}
</script>

<style scoped>
.workflow-plaza {
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  text-align: center;
  padding: 40px 0 60px;
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 16px 0;
  background: linear-gradient(135deg, #74b9ff, #0984e3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 18px;
  color: #666;
  margin: 0;
}

/* 即将推出区域 */
.coming-soon-section {
  margin-bottom: 80px;
}

.section-header {
  text-align: center;
  margin-bottom: 48px;
}

.section-title {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.section-desc {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.workflow-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.workflow-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.1);
  border-color: #74b9ff;
}

.workflow-card.coming-soon::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #74b9ff, #0984e3);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.workflow-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  display: flex;
  align-items: center;
  justify-content: center;
}

.coming-soon-badge {
  background: linear-gradient(135deg, #fd79a8, #e84393);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.card-content {
  margin-bottom: 24px;
}

.workflow-name {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.workflow-desc {
  color: #666;
  line-height: 1.6;
  margin: 0 0 16px 0;
}

.workflow-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  background: #f1f3f4;
  color: #5f6368;
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.card-footer {
  border-top: 1px solid #f0f0f0;
  padding-top: 16px;
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  height: 6px;
  background: #f0f0f0;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #74b9ff, #0984e3);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 13px;
  color: #666;
  text-align: center;
}

/* 敬请期待区域 */
.stay-tuned-section {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 24px;
  padding: 60px 40px;
  text-align: center;
  margin-bottom: 60px;
}

.stay-tuned-icon {
  margin-bottom: 24px;
}

.stay-tuned-title {
  font-size: 32px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 16px 0;
}

.stay-tuned-desc {
  font-size: 16px;
  color: #666;
  line-height: 1.8;
  margin: 0 0 40px 0;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.notification-signup {
  max-width: 500px;
  margin: 0 auto;
}

.email-input :deep(.ant-input) {
  border-radius: 25px;
  padding: 12px 20px;
  font-size: 16px;
}

.email-input :deep(.ant-input-suffix) {
  margin-right: 4px;
}

.email-input :deep(.ant-btn) {
  border-radius: 20px;
  height: 36px;
  padding: 0 20px;
}

/* 联系我们区域 */
.contact-section {
  text-align: center;
  padding: 40px 0;
}

.contact-content {
  max-width: 600px;
  margin: 0 auto;
}

.contact-title {
  font-size: 24px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 12px 0;
}

.contact-desc {
  font-size: 16px;
  color: #666;
  margin: 0 0 32px 0;
}

.contact-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  flex-wrap: wrap;
}

.contact-buttons .ant-btn {
  border-radius: 25px;
  padding: 0 24px;
  height: 48px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .workflow-plaza {
    padding: 0 16px;
  }

  .page-header {
    padding: 24px 0 40px;
  }

  .page-title {
    font-size: 28px;
  }

  .workflow-grid {
    grid-template-columns: 1fr;
  }

  .stay-tuned-section {
    padding: 40px 24px;
  }

  .stay-tuned-title {
    font-size: 24px;
  }

  .contact-buttons {
    flex-direction: column;
    align-items: center;
  }

  .contact-buttons .ant-btn {
    width: 200px;
  }
}
</style>
