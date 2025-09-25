<template>
  <section class="home">
    <!-- 对话区域 -->
    <div class="chat-container">
      <div class="messages" ref="messagesContainer">
        <div
          v-for="(message, index) in messages"
          :key="index"
          :class="['message', message.type]"
        >
          <div class="message-avatar">
            <span v-if="message.type === 'ai'">🤖</span>
            <span v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
              </svg>
            </span>
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部控制区域 -->
    <div class="bottom">
      <div class="pills">
        <a-popover trigger="hover" placement="top">
          <template #content>
            <a-segmented v-model:value="mode" :options="['普通模式','流式输出']" />
          </template>
          <a-button size="small" shape="round" :type="btnType('model')" @mouseenter="active='model'">对话模式</a-button>
        </a-popover>
        <a-button size="small" shape="round" :type="webEnabled ? 'primary' : 'default'" @click="toggleWeb">联网搜索</a-button>
        <a-button size="small" shape="round" :type="btnType('config')" @click="active='config'">知识库配置</a-button>
        <a-button size="small" shape="round" :type="btnType('mcp')" @click="active='mcp'">MCP</a-button>
      </div>

      <!-- 输入区域 -->
      <div class="input-container">
        <div class="input-wrapper">
          <a-textarea
            v-model:value="text"
            class="chat-input"
            placeholder="输入您的问题..."
            :auto-size="{ minRows: 1, maxRows: 6 }"
            @keydown.enter.exact.prevent="onSend"
            @keydown.enter.shift.exact="onNewLine"
          />
          <a-button
            type="primary"
            shape="circle"
            class="send-button"
            :disabled="!text.trim()"
            @click="onSend"
          >
            <template #icon>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
              </svg>
            </template>
          </a-button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { message as antdMsg } from 'ant-design-vue'
import { createConversation, listMessages, sendMessage, sendMessageStream } from '../services/api'

const active = ref('model')
const webEnabled = ref(false)
const mode = ref('普通模式')
const text = ref('')
const messages = ref([])
const messagesContainer = ref(null)
const conversationId = ref(null)

const btnType = (key) => (active.value === key ? 'primary' : 'default')
const toggleWeb = () => { webEnabled.value = !webEnabled.value }

const formatTime = (date) => date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const ensureConversation = async () => {
  const saved = localStorage.getItem('kh_conversation_id')
  if (saved) {
    conversationId.value = Number(saved)
    await loadHistory()
    return
  }
  const { data } = await createConversation({ title: '新的对话' })
  const conv = data?.data
  conversationId.value = conv?.id
  if (conversationId.value) localStorage.setItem('kh_conversation_id', String(conversationId.value))
}

const loadHistory = async () => {
  if (!conversationId.value) return
  try {
    const { data } = await listMessages(conversationId.value, { limit: 50 })
    const arr = data?.data || []
    messages.value = arr.map(it => ({
      type: it.role === 'assistant' ? 'ai' : 'user',
      content: it.content || '',
      time: formatTime(new Date(it.created_at || Date.now()))
    }))
  } catch (e) {}
}

onMounted(async () => {
  await ensureConversation()
  if (messages.value.length === 0) {
    messages.value.push({
      type: 'ai',
      content: '欢迎使用 Knowledge-Horizon 智能知识库系统！请输入您的问题。',
      time: formatTime(new Date())
    })
  }
})

const onSend = async () => {
  if (!text.value.trim() || !conversationId.value) return
  const content = text.value
  text.value = ''

  messages.value.push({ type: 'user', content, time: formatTime(new Date()) })
  scrollToBottom()

  if (mode.value === '普通模式') {
    try {
      // 先插入占位的“生成中”气泡
      const aiMsg = { type: 'ai', content: '正在生成…', time: formatTime(new Date()) }
      messages.value.push(aiMsg)
      const { data } = await sendMessage(conversationId.value, { content })
      const payload = data?.data || {}
      const asst = payload.assistant_message || {}
      aiMsg.content = asst.content || ''
      scrollToBottom()
    } catch (e) {
      antdMsg.error(e?.response?.data?.message || e?.message || '发送失败')
    }
    return
  }

  const aiMsg = { type: 'ai', content: '', time: formatTime(new Date()) }
  messages.value.push(aiMsg)
  scrollToBottom()
  try {
    await sendMessageStream(conversationId.value, { content }, (evt) => {
      if (evt?.text) {
        aiMsg.content += evt.text
        scrollToBottom()
      }
      if (evt?.done) {
        // 结束
      }
    })
  } catch (e) {
    antdMsg.error(e?.message || '流式输出失败')
  }
}

const onNewLine = () => { text.value += '\n' }
</script>

<style scoped>
.home {
  max-width: 920px;
  margin: 0 auto;
  min-height: calc(100vh - 68px - 32px);
  display: flex;
  flex-direction: column;
}

/* 对话容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  margin-bottom: 0;
  background: #f5f5f5;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 16px;
  scroll-behavior: smooth;
}

/* 消息样式 */
.message {
  display: flex;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease-in;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  margin: 0 12px;
}

.message.ai .message-avatar {
  background: #ffffff;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.message.user .message-avatar {
  background: #f0f2f5;
  color: #666;
}

.message-content {
  max-width: 75%;
  min-width: 160px;
}

.message.user .message-content {
  text-align: right;
}

.message-text {
  background: #ffffff;
  padding: 16px 20px;
  border-radius: 16px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
  font-size: 15px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border: 1px solid #e8e8e8;
}

.message.user .message-text {
  background: #ffffff;
  color: #555;
  border: 1px solid #e8e8e8;
  font-size: 14px;
  padding: 12px 16px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
  padding: 0 6px;
}

.message.user .message-time {
  color: #bbb;
  font-size: 11px;
}

/* 底部控制区域 */
.bottom {
  padding: 16px 20px 20px;
  border-top: 1px solid #e8e8e8;
  background: #f5f5f5;
}

.pills {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 0 0 16px;
}

/* 输入区域 */
.input-container {
  position: relative;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: flex-end;
  background: #ffffff;
  border: 1px solid #d9d9d9;
  border-radius: 16px;
  padding: 12px 56px 12px 16px;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.input-wrapper:hover {
  border-color: #40a9ff;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
}

.input-wrapper:focus-within {
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.chat-input {
  flex: 1;
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 0 !important;
  resize: none;
}

.chat-input :deep(.ant-input) {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  padding: 6px 0 !important;
  font-size: 15px;
  line-height: 1.5;
}

.chat-input :deep(.ant-input:focus) {
  border: none !important;
  box-shadow: none !important;
}

.send-button {
  position: absolute;
  right: 12px;
  bottom: 12px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 滚动条样式 */
.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home {
    max-width: 100%;
    padding: 0 16px;
  }

  .message-content {
    max-width: 85%;
  }

  .pills {
    flex-wrap: wrap;
    gap: 6px;
  }
}
</style>
