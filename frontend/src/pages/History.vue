<template>
  <section class="wrap">
    <div class="page-head">
      <div class="title">
        <div class="h2">历史任务</div>
        <div class="sub">查看您的以往对话与任务</div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="filters">
        <a-input-search
          v-model:value="searchText"
          placeholder="搜索历史对话..."
          style="width: 300px"
          @search="onSearch"
        />
        <a-select v-model:value="filterType" style="width: 120px" placeholder="全部类型">
          <a-select-option value="">全部类型</a-select-option>
          <a-select-option value="qa">知识问答</a-select-option>
          <a-select-option value="analysis">数据分析</a-select-option>
          <a-select-option value="chat">普通对话</a-select-option>
        </a-select>
      </div>
    </div>

    <div class="page-body">
      <!-- 历史任务列表 -->
      <div class="list" v-if="filteredItems.length > 0">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="card"
        @click="openChat(item)"
      >
        <div class="thumb">
          <div class="icon">
            <svg v-if="item.type === 'qa'" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z" fill="#74b9ff"/>
            </svg>
            <svg v-else-if="item.type === 'analysis'" width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="#00b894"/>
            </svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M20 2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h14l4 4V4c0-1.1-.9-2-2-2zm-2 12H6v-2h12v2zm0-3H6V9h12v2zm0-3H6V6h12v2z" fill="#6c5ce7"/>
            </svg>
          </div>
        </div>
        <div class="meta">
          <div class="name">{{ item.title }}</div>
          <div class="desc">{{ item.desc }}</div>
          <div class="stats">
            <span class="message-count">{{ item.messageCount }} 条对话</span>
            <span v-if="item.lastActive" class="last-active">最后活跃：{{ item.lastActive }}</span>
          </div>
        </div>
        <div class="actions">
          <div class="date">{{ item.date }}</div>
          <div class="action-buttons">
            <a-button type="text" size="small" @click.stop="shareChat(item)">
              <template #icon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.50-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/>
                </svg>
              </template>
            </a-button>
            <a-button type="text" size="small" @click.stop="deleteChat(item)" danger>
              <template #icon>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>
              </template>
            </a-button>
          </div>
        </div>
      </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" fill="#ddd"/>
          </svg>
        </div>
        <div class="empty-title">暂无历史对话</div>
        <div class="empty-desc">开始您的第一次对话吧</div>
        <a-button type="primary" @click="goToHome">开始对话</a-button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { listConversations, deleteConversation } from '../services/api'

const router = useRouter()

// 查询与状态
const searchText = ref('')
const filterType = ref('')
const loading = ref(false)
const items = ref([])

const formatDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}.${m}.${day}`
}

const formatDateTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${y}.${m}.${day} ${hh}:${mm}`
}

const mapItem = (it) => {
  const title = it.title || '未命名对话'
  const messageCount = Number(it.message_count || 0)
  const type = (Array.isArray(it.kb_ids) && it.kb_ids.length > 0) ? 'qa' : 'chat'
  const lastActive = formatDateTime(it.last_message_at || it.first_message_at)
  const desc = `共 ${messageCount} 条对话`
  return {
    id: it.id,
    title,
    desc,
    date: formatDate(it.last_message_at || it.first_message_at),
    type,
    messageCount,
    lastActive
  }
}

const fetchItems = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchText.value) params.q = searchText.value
    const { data } = await listConversations(params)
    const arr = data?.data || []
    items.value = arr.map(mapItem)
  } catch (e) {
    message.error(e?.response?.data?.message || '加载失败')
  } finally {
    loading.value = false
  }
}

onMounted(fetchItems)

// 过滤
const filteredItems = computed(() => {
  let result = items.value
  if (filterType.value) {
    result = result.filter(item => item.type === filterType.value)
  }
  return result
})

// 交互
const onSearch = async () => {
  await fetchItems()
}

const openChat = (item) => {
  try { localStorage.setItem('kh_conversation_id', String(item.id)) } catch {}
  router.push('/app')
}

const shareChat = () => {
  message.info('分享功能稍后支持')
}

const deleteChat = async (item) => {
  if (!item?.id) return
  const ok = window.confirm(`确定删除对话《${item.title}》吗？`)
  if (!ok) return
  try {
    await deleteConversation(item.id)
    items.value = items.value.filter(i => i.id !== item.id)
    message.success('已删除')
  } catch (e) {
    message.error(e?.response?.data?.message || '删除失败')
  }
}

const goToHome = () => { router.push('/app') }
</script>

<style scoped>
.wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 16px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  min-height: 0; /* 使子元素可滚动 */
  overflow: hidden;
}

.page-head {
  flex: 0 0 auto;
  background: transparent;
}

.page-body {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  padding-bottom: 24px;
}

.title {
  text-align: center;
  margin-bottom: 32px;
}

.h2 {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.sub {
  color: #666;
  font-size: 16px;
}

.filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px 0;
}

.list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  display: grid;
  grid-template-columns: 72px 1fr auto;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border-color: #74b9ff;
  transform: translateY(-2px);
}

.thumb {
  width: 72px;
  height: 56px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.name {
  font-weight: 600;
  font-size: 16px;
  color: #2c3e50;
}

.desc {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.stats {
  display: flex;
  gap: 16px;
  margin-top: 4px;
}

.message-count,
.last-active {
  font-size: 12px;
  color: #999;
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
}

.date {
  color: #999;
  font-size: 13px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.card:hover .action-buttons {
  opacity: 1;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  margin-bottom: 24px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.empty-desc {
  color: #666;
  margin-bottom: 24px;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .wrap {
    padding: 0 12px;
  }

  .filters {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .card {
    grid-template-columns: 56px 1fr;
    gap: 12px;
  }

  .actions {
    grid-column: 1 / -1;
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid #f0f0f0;
  }

  .thumb {
    width: 56px;
    height: 44px;
  }
}
</style>
