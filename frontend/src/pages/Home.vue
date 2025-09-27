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
            <div class="message-text">
              <!-- AI消息加载状态 -->
              <div v-if="message.type === 'ai' && message.isLoading" class="loading-container">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="loading-text">正在思考中...</span>
              </div>
              <!-- 正常消息内容 -->
              <template v-else>
                <MarkdownRenderer
                  v-if="message.type === 'ai'"
                  :content="message.content"
                />
                <span v-else>{{ message.content }}</span>
              </template>
            </div>
            <div class="message-time">{{ message.time }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部控制区域 -->
    <div class="bottom">
      <div class="pills">
        <a-button
          size="small"
          shape="round"
          type="default"
          :class="{ 'config-button': true, 'active': isStreamMode }"
          @click="toggleStreamMode"
        >
          {{ isStreamMode ? '流式输出' : '普通模式' }}
        </a-button>
        <a-button
          size="small"
          shape="round"
          type="default"
          :class="{ 'config-button': true }"
          @click="openKbConfig"
        >
          知识库配置
        </a-button>
        <div class="kb-tags" v-if="currentKbLabels.length">
          <span class="kb-label">本会话知识库：</span>
          <a-tag v-for="(name, idx) in currentKbLabels" :key="idx" style="margin-right:6px;">{{ name }}</a-tag>
        </div>
        <a-button
          size="small"
          shape="round"
          type="default"
          :class="{ 'config-button': true, 'active': active === 'mcp' }"
          @click="active='mcp'"
        >
          MCP
        </a-button>
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
            :disabled="!text.trim() || isGenerating"
            :loading="isGenerating"
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

    <!-- KB 绑定与检索设置弹窗 -->
    <a-modal v-model:open="kbModalVisible" title="知识库配置" ok-text="确定" cancel-text="取消" @ok="confirmKbConfig">
      <div style="display:flex; flex-direction: column; gap: 12px;">
        <div>
          <div style="margin-bottom:6px;color:#666;">选择要绑定到会话的知识库（可多选）</div>
          <a-select v-model:value="selectedKbIds" mode="multiple" style="width: 100%" placeholder="请选择知识库">
            <a-select-option v-for="opt in kbOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</a-select-option>
          </a-select>
        </div>
        <div>
          <a-checkbox v-model:checked="setAsDefaultKb">设为默认知识库（默认仅保存第一个）</a-checkbox>
        </div>
        <div style="margin-top:8px;color:#999;">检索设置（可选）</div>
        <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
          <div>Top K: <a-input-number v-model:value="retrieveTopK" :min="1" :max="20" /></div>
          <div>
            <a-switch v-model:checked="useRerank" /> 重排序
          </div>
          <div v-if="useRerank">Rerank Top N: <a-input-number v-model:value="rerankTopN" :min="1" :max="20" /></div>
        </div>
        <div style="color:#999; font-size:12px;">注意：保存后将创建一个新会话并绑定所选知识库。</div>
      </div>
    </a-modal>
  </section>
</template>

<script setup>
import { ref, onMounted, nextTick, watch, computed } from 'vue'
import { message as antdMsg } from 'ant-design-vue'
import { useRoute } from 'vue-router'
import { createConversation, listMessages, sendMessage, sendMessageStream, listKBs, listConversations } from '../services/api'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'
import { useSettingsStore } from '../stores/settings'

const active = ref('config')
const settingsStore = useSettingsStore()
const settingsLoaded = computed(() => settingsStore.loaded)
const webEnabled = computed(() => settingsStore.web_search)
const isStreamMode = computed(() => settingsStore.streaming)
const text = ref('')
const messages = ref([])
const messagesContainer = ref(null)
const conversationId = ref(null)
const isGenerating = ref(false) // 添加生成状态

// KB 绑定与检索设置
const kbModalVisible = ref(false)
const kbOptions = ref([]) // [{label, value}]
const selectedKbIds = ref([])
const setAsDefaultKb = ref(false)
const kbNameMap = ref({}) // { id: name }
const currentKbIds = ref([]) // 当前会话绑定的 KB ids
const currentKbLabels = computed(() => (currentKbIds.value || []).map(id => kbNameMap.value[id] || `KB #${id}`))
const retrieveTopK = ref(6)
const useRerank = ref(false)
const rerankTopN = ref(6)

const openKbConfig = async () => {
  try {
    const { data } = await listKBs({ limit: 100, offset: 0 })
    const items = data?.data?.items || []
    kbOptions.value = items.map(it => ({ label: it.name, value: it.id }))
    const mp = {}
    for (const it of items) mp[it.id] = it.name
    kbNameMap.value = mp
  } catch (e) {
    antdMsg.error(e?.response?.data?.message || '加载知识库失败')
  }
  kbModalVisible.value = true
}

const confirmKbConfig = async () => {
  try {
    const payload = { kb_ids: selectedKbIds.value }
    // 若用户勾选“设为默认知识库”，将多选中的第一个持久化到用户设置
    if (Array.isArray(selectedKbIds.value) && selectedKbIds.value.length > 0 && setAsDefaultKb.value) {
      const first = selectedKbIds.value[0]
      const res = await settingsStore.update({ default_kb_id: first })
      if (!res?.ok) {
        antdMsg.warning(res?.error || '默认知识库保存失败，但会话将继续创建')
      } else {
        antdMsg.success('已将默认知识库保存为你的偏好')
      }
    }
    const { data } = await createConversation(payload)
    const conv = data?.data
    if (!conv?.id) throw new Error('创建新会话失败')
    conversationId.value = conv.id
    currentKbIds.value = Array.isArray(conv.kb_ids) ? conv.kb_ids : []
    try { localStorage.setItem('kh_conversation_id', String(conv.id)) } catch {}
    // 重置消息并提示
    messages.value = [{ type: 'ai', content: '已绑定知识库，开始提问吧。', time: formatTime(new Date()) }]
    kbModalVisible.value = false
    setAsDefaultKb.value = false
    antdMsg.success('知识库绑定成功，已创建新会话')
  } catch (e) {
    antdMsg.error(e?.response?.data?.message || e?.message || '绑定失败')
  }
}

const btnType = (key) => (active.value === key ? 'primary' : 'default')
const toggleWeb = async () => {
  if (!settingsLoaded.value) {
    await settingsStore.load()
  }
  const next = !webEnabled.value
  const res = await settingsStore.update({ web_search: next })
  if (!res?.ok) antdMsg.error(res?.error || '更新联网偏好失败')
}
const toggleStreamMode = async () => {
  if (!settingsLoaded.value) {
    await settingsStore.load()
  }
  const next = !isStreamMode.value
  const res = await settingsStore.update({ streaming: next })
  if (!res?.ok) antdMsg.error(res?.error || '更新流式偏好失败')
}

const formatTime = (date) => date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const route = useRoute()

// 当消息为空时插入欢迎语
const insertWelcomeIfEmpty = () => {
  if (!messages.value || messages.value.length === 0) {
    messages.value.push({
      type: 'ai',
      content: '欢迎使用 Knowledge-Horizon 智能知识库系统！请输入您的问题。',
      time: formatTime(new Date())
    })
  }
}

const ensureConversation = async () => {
  console.log('🔄 [ensureConversation] 开始初始化会话')
  const forceNew = route.query?.new === '1' || route.query?.new === 'true'
  const saved = !forceNew ? localStorage.getItem('kh_conversation_id') : null
  console.log('💾 [ensureConversation] 检查本地存储:', { forceNew, saved })

  if (saved) {
    conversationId.value = Number(saved)
    console.log('📋 [ensureConversation] 使用已存在的会话ID:', conversationId.value)
    await loadHistory()
    // 加载当前会话绑定的 KB 信息
    try {
      const { data } = await listConversations({ limit: 100, offset: 0 })
      const arr = data?.data || []
      const found = arr.find(it => Number(it.id) === Number(conversationId.value))
      currentKbIds.value = found?.kb_ids || []
    } catch (e) {
      console.debug('[ensureConversation] load conv info failed:', e?.message)
    }
    return
  }

  // 如有默认 KB，创建会话时自动绑定
  const kbIds = settingsStore.default_kb_id ? [settingsStore.default_kb_id] : []
  if (kbIds.length === 0) {
    console.log('🧩 [ensureConversation] 未设置默认知识库，弹出配置')
    await openKbConfig()
    return
  }

  console.log('🆕 [ensureConversation] 创建新会话...', { kbIds })
  const { data } = await createConversation({ kb_ids: kbIds })
  const conv = data?.data
  conversationId.value = conv?.id
  currentKbIds.value = Array.isArray(conv?.kb_ids) ? conv.kb_ids : []
  console.log('✅ [ensureConversation] 新会话创建成功:', conversationId.value)
  if (conversationId.value) localStorage.setItem('kh_conversation_id', String(conversationId.value))
}

const loadHistory = async () => {
  if (!conversationId.value) {
    console.log('⚠️ [loadHistory] 没有会话ID，跳过加载历史')
    return
  }

  console.log('📚 [loadHistory] 加载会话历史:', conversationId.value)
  try {
    const { data } = await listMessages(conversationId.value, { limit: 50 })
    const arr = data?.data || []
    console.log('📥 [loadHistory] 收到历史消息:', arr.length, '条')
    messages.value = arr.map(it => ({
      type: it.role === 'assistant' ? 'ai' : 'user',
      content: it.content || '',
      time: formatTime(new Date(it.created_at || Date.now()))
    }))
  } catch (e) {
    console.error('❌ [loadHistory] 加载历史失败:', e)
  }
}

onMounted(async () => {
  // 先加载用户设置（用于默认 KB、流式/联网偏好）
  if (!settingsLoaded.value) {
    await settingsStore.load()
  }
  // 预取 KB 列表用于名称映射
  try {
    const { data } = await listKBs({ limit: 100, offset: 0 })
    const items = data?.data?.items || []
    kbOptions.value = items.map(it => ({ label: it.name, value: it.id }))
    const mp = {}
    for (const it of items) mp[it.id] = it.name
    kbNameMap.value = mp
  } catch {}
  await ensureConversation()
  insertWelcomeIfEmpty()
})

// 监听路由参数变化：当收到 new=1 时强制新建一个会话
watch(
  () => route.query?.new,
  async (val, oldVal) => {
    if (val === '1' || val === 'true') {
      try { localStorage.removeItem('kh_conversation_id') } catch {}
      // 重置页面状态
      conversationId.value = null
      messages.value = []
      isGenerating.value = false
      if (!settingsLoaded.value) {
        await settingsStore.load()
      }
      await ensureConversation()
      insertWelcomeIfEmpty()
      // 清理 URL，避免反复触发
      try { window.history.replaceState({}, '', '/app') } catch {}
    }
  }
)

const onSend = async () => {
  console.log('🚀 [onSend] 开始发送消息', {
    hasText: !!text.value.trim(),
    conversationId: conversationId.value,
    isGenerating: isGenerating.value,
    isStreamMode: isStreamMode.value
  })

  if (!text.value.trim() || !conversationId.value || isGenerating.value) {
    console.warn('❌ [onSend] 发送条件不满足，退出')
    return
  }

  const content = text.value
  text.value = ''
  isGenerating.value = true // 设置生成状态

  console.log('📝 [onSend] 准备发送内容:', content)

  // 添加用户消息
  messages.value.push({ type: 'user', content, time: formatTime(new Date()) })
  console.log('👤 [onSend] 用户消息已添加，当前消息数:', messages.value.length)
  scrollToBottom()

  if (!isStreamMode.value) {
    // 非流式模式
    console.log('📡 [onSend] 使用非流式模式')
    let aiMsgIndex = -1
    try {
      // 先插入占位的“生成中”气泡
      const aiMsg = {
        type: 'ai',
        content: '',
        isLoading: true,
        time: formatTime(new Date())
      }
      messages.value.push(aiMsg)
      aiMsgIndex = messages.value.length - 1
      scrollToBottom()

      console.log('📤 [onSend] 发送非流式请求...')
      const { data } = await sendMessage(conversationId.value, { content, retrieve_top_k: retrieveTopK.value, use_rerank: useRerank.value, rerank_top_n: rerankTopN.value })
      console.log('📥 [onSend] 收到非流式响应:', data)
      const payload = data?.data || {}
      const asst = payload.assistant_message || {}

      // 使用响应式更新：替换整个消息对象而不是修改属性
      if (aiMsgIndex >= 0) {
        messages.value[aiMsgIndex] = {
          type: 'ai',
          content: asst.content || '抱歉，没有收到回复内容',
          isLoading: false,
          time: formatTime(new Date())
        }
      }
      scrollToBottom()
    } catch (e) {
      // 错误处理：更新错误消息
      if (aiMsgIndex >= 0) {
        messages.value[aiMsgIndex] = {
          type: 'ai',
          content: '抱歉，发生了错误，请重试',
          isLoading: false,
          time: formatTime(new Date())
        }
      }
      antdMsg.error(e?.response?.data?.message || e?.message || '发送失败')
    } finally {
      isGenerating.value = false
    }
    return
  }

  // 流式模式
  console.log('🌊 [onSend] 使用流式模式')
  let aiMsgIndex = -1
  try {
    const aiMsg = {
      type: 'ai',
      content: '',
      isLoading: true,
      time: formatTime(new Date())
    }
    messages.value.push(aiMsg)
    aiMsgIndex = messages.value.length - 1
    scrollToBottom()

    console.log('📤 [onSend] 发送流式请求...')
    await sendMessageStream(conversationId.value, { content, retrieve_top_k: retrieveTopK.value, use_rerank: useRerank.value, rerank_top_n: rerankTopN.value }, (evt) => {
      console.log('📥 [onSend] 收到流式数据:', evt)
      if (evt?.text && aiMsgIndex >= 0) {
        // 使用响应式更新：创建新对象
        const currentMsg = messages.value[aiMsgIndex]
        messages.value[aiMsgIndex] = {
          ...currentMsg,
          content: currentMsg.content + evt.text,
          isLoading: false // 开始接收内容时取消加载状态
        }
        scrollToBottom()
      }
      if (evt?.done) {
        // 流式输出结束
        console.log('✅ [onSend] 流式输出完成')
        isGenerating.value = false

        // 如果没有内容，显示提示
        if (aiMsgIndex >= 0 && !messages.value[aiMsgIndex].content.trim()) {
          messages.value[aiMsgIndex] = {
            ...messages.value[aiMsgIndex],
            content: '抱歉，没有收到回复内容',
            isLoading: false
          }
        } else if (aiMsgIndex >= 0) {
          // 确保加载状态被清除
          messages.value[aiMsgIndex] = {
            ...messages.value[aiMsgIndex],
            isLoading: false
          }
        }
      }
    })
  } catch (e) {
    // 错误处理：更新错误消息
    if (aiMsgIndex >= 0) {
      const currentMsg = messages.value[aiMsgIndex]
      messages.value[aiMsgIndex] = {
        ...currentMsg,
        content: currentMsg.content || '抱歉，流式输出发生错误，请重试'
      }
    }
    antdMsg.error(e?.message || '流式输出失败')
  } finally {
    isGenerating.value = false
  }
}

const onNewLine = () => { text.value += '\n' }
</script>

<style scoped>
.home {
  max-width: 920px;
  margin: 0 auto;
  height: calc(100vh - 68px - 32px); /* 固定高度 */
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden; /* 防止整体横向滚动 */
}

/* 对话容器 */
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #f5f5f5;
  overflow: hidden; /* 防止整体滚动 */
  position: relative;
}

.messages {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden; /* 防止横向滚动 */
  padding: 16px 12px 140px 16px; /* 减少上下padding */
  scroll-behavior: smooth;
  /* 滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 transparent;
  word-wrap: break-word; /* 强制换行 */
}

/* Webkit浏览器滚动条样式 */
.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-track {
  background: transparent;
  margin: 4px 0; /* 上下留出一点空间 */
}

.messages::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
  transition: background-color 0.2s;
}

.messages::-webkit-scrollbar-thumb:hover {
  background-color: #a8a8a8;
}

.messages::-webkit-scrollbar-corner {
  background: transparent;
}

/* 消息样式 */
.message {
  display: flex;
  margin-bottom: 16px; /* 减少消息间距 */
  animation: fadeIn 0.3s ease-in;
  width: 100%; /* 确保消息占满容器宽度 */
}

.message.user {
  flex-direction: row-reverse;
  justify-content: flex-start; /* 用户消息在右侧 */
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
  max-width: 65%; /* 减少最大宽度，让布局更紧凑 */
  min-width: 120px; /* 设置最小宽度，避免过窄 */
  overflow: hidden; /* 防止内容溢出 */
  flex-shrink: 1; /* 允许内容收缩 */
}

.message.user .message-content {
  text-align: left; /* 用户消息文字左对齐，避免气泡内空白 */
  display: flex;
  flex-direction: column;
  align-items: flex-end; /* 整个内容区域靠右 */
}

.message-text {
  background: #ffffff;
  padding: 12px 16px; /* 减少内边距 */
  border-radius: 12px; /* 减少圆角 */
  line-height: 1.5; /* 减少行高 */
  word-wrap: break-word;
  word-break: break-word; /* 强制长单词换行 */
  overflow-wrap: break-word; /* 兼容性 */
  font-size: 14px; /* 减少字体大小 */
  box-shadow: 0 1px 4px rgba(0,0,0,0.1); /* 减少阴影 */
  border: 1px solid #e8e8e8;
  max-width: 100%; /* 确保不超出容器 */
}

.message.user .message-text {
  background: #ffffff;
  color: #555;
  border: 1px solid #e8e8e8;
  font-size: 14px;
  padding: 10px 14px; /* 减少用户消息内边距 */
  white-space: pre-wrap; /* 用户消息保持换行 */
  word-break: break-word; /* 强制长单词换行 */
  text-align: left; /* 气泡内文字左对齐，避免空白 */
}

.message.ai .message-text {
  white-space: normal; /* AI消息使用Markdown渲染 */
  overflow-wrap: break-word; /* 确保长文本换行 */
  hyphens: auto; /* 自动断词 */
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

/* 加载状态样式 */
.loading-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #1890ff;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

.loading-text {
  color: #666;
  font-size: 14px;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 底部控制区域 */
.bottom {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 20px 20px;
  border-top: 1px solid #e8e8e8;
  background: #f5f5f5;
  z-index: 10;
}

  .pills {
    display: flex;
    justify-content: center;
    gap: 8px;
    padding: 0 0 16px;
  }
  .kb-tags { display:flex; align-items:center; gap:6px; }
  .kb-label { color:#666; font-size:12px; }

/* 配置按钮样式 */
.config-button {
  transition: all 0.2s ease !important;
  position: relative;
  overflow: hidden;
}

.config-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

.config-button.active {
  background: #f0f8ff !important;
  border-color: #91caff !important;
  color: #1677ff !important;
  transform: scale(1.02);
}

.config-button.active::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
  animation: shimmer 0.6s ease-out;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
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
  padding: 12px 52px 12px 16px; /* 调整右侧padding为按钮留出空间 */
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
  right: 8px;
  bottom: 50%;
  transform: translateY(50%);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  min-width: 32px; /* 确保按钮不会被压缩 */
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
    padding: 0 8px; /* 减少移动端边距 */
  }

  .message-content {
    max-width: 80%; /* 移动端进一步减少宽度 */
  }

  .message-text {
    font-size: 13px; /* 移动端减少字体 */
    padding: 10px 12px; /* 移动端减少内边距 */
  }

  .messages {
    padding: 12px 8px 140px 12px; /* 移动端减少边距 */
  }

  .pills {
    flex-wrap: wrap;
    gap: 6px;
  }
}

/* 超小屏幕优化 */
@media (max-width: 480px) {
  .message-content {
    max-width: 90%;
  }

  .message-text {
    font-size: 12px;
    padding: 8px 10px;
  }
}
</style>
