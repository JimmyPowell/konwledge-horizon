<template>
  <section class="wrap">
    <!-- 面包屑导航 -->
    <div class="breadcrumb">
      <a-breadcrumb>
        <a-breadcrumb-item>
          <router-link to="/app/knowledge">知识库管理</router-link>
        </a-breadcrumb-item>
        <a-breadcrumb-item>{{ knowledgeBase.name }}</a-breadcrumb-item>
      </a-breadcrumb>
    </div>

    <!-- 知识库信息 -->
    <div class="kb-header">
      <div class="kb-info">
        <div class="kb-icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
            <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z" fill="#74b9ff"/>
          </svg>
        </div>
        <div class="kb-meta">
          <h1 class="kb-name">{{ knowledgeBase.name }}</h1>
          <p class="kb-desc">{{ knowledgeBase.description }}</p>
          <div class="kb-stats">
            <span class="stat-item">{{ knowledgeBase.docCount }} 个文件</span>
            <span class="stat-item">{{ knowledgeBase.totalSize }}</span>
            <span class="stat-item">创建于 {{ knowledgeBase.createdAt }}</span>
          </div>
        </div>
      </div>
      <div class="kb-actions">
        <a-button type="primary" size="large" @click="triggerFileSelect">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </template>
          上传文件
        </a-button>
        <input ref="fileInput" type="file" @change="onFileSelected" style="display:none" accept=".pdf,.doc,.docx,.txt,.md" />
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="file-list">
      <div class="list-header">
        <div class="list-title">文件列表</div>
        <div class="list-actions">
          <a-input-search
            v-model:value="searchText"
            placeholder="搜索文件..."
            style="width: 300px"
            @search="onSearch"
          />
        </div>
      </div>

      <div class="table-container">
        <a-table
          :columns="columns"
          :data-source="filteredFiles"
          :pagination="{ pageSize: 10, showSizeChanger: true }"
          row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'name'">
              <div class="file-name">
                <div class="file-icon">
                  <svg v-if="getFileType(record.name) === 'pdf'" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#e74c3c"/>
                  </svg>
                  <svg v-else-if="getFileType(record.name) === 'doc'" width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#2980b9"/>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#95a5a6"/>
                  </svg>
                </div>
                <span>{{ record.name }}</span>
              </div>
            </template>
            <template v-else-if="column.key === 'size'">
              {{ formatFileSize(record.size) }}
            </template>
            <template v-else-if="column.key === 'status'">
              <a-tag :color="getStatusColor(record.status)">
                {{ getStatusText(record.status) }}
              </a-tag>
            </template>
            <template v-else-if="column.key === 'actions'">
              <div class="action-buttons">
                <a-button type="text" size="small" @click="previewFile(record)">
                  <template #icon>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z"/>
                    </svg>
                  </template>
                </a-button>
                <a-button type="text" size="small" @click="downloadFile(record)">
                  <template #icon>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M5,20H19V18H5M19,9H15V3H9V9H5L12,16L19,9Z"/>
                    </svg>
                  </template>
                </a-button>
                <a-button type="text" size="small" @click="deleteFile(record)" danger>
                  <template #icon>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                    </svg>
                  </template>
                </a-button>
              </div>
            </template>
          </template>
        </a-table>
      </div>
    </div>

    
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { getKB, listKBDocuments, deleteKBDocument, uploadKBDocument } from '../services/api'

const route = useRoute()
const router = useRouter()

// 响应式数据
const knowledgeBaseId = ref(route.params.id)
const searchText = ref('')
// 移除上传按钮相关

// 知识库信息
const knowledgeBase = ref({
  id: '',
  name: '',
  description: '',
  docCount: 0,
  totalSize: '0 B',
  createdAt: ''
})

const formatFileSize = (bytes) => {
  const n = Number(bytes || 0)
  if (n <= 0) return '0 B'
  const units = ['B','KB','MB','GB','TB']
  const i = Math.floor(Math.log(n) / Math.log(1024))
  return `${(n / Math.pow(1024, i)).toFixed(2)} ${units[i]}`
}

const formatDate = (s) => {
  if (!s) return ''
  try { return new Date(s).toLocaleDateString('zh-CN') } catch { return '' }
}

const loadKB = async () => {
  try {
    const id = Number(knowledgeBaseId.value)
    const { data } = await getKB(id)
    const kb = data?.data || {}
    knowledgeBase.value = {
      id: kb.id,
      name: kb.name,
      description: kb.description || '',
      docCount: kb.doc_count || 0,
      totalSize: formatFileSize(kb.total_size_bytes || 0),
      createdAt: formatDate(kb.created_at)
    }
  } catch (e) {
    message.error(e?.response?.data?.message || '加载知识库失败')
  }
}

onMounted(async () => { await loadKB(); await loadDocuments() })

// 文件列表（后端加载）
const files = ref([])

const loadDocuments = async () => {
  try {
    const id = Number(knowledgeBaseId.value)
    const { data } = await listKBDocuments(id, { limit: 50, offset: 0 })
    const payload = data?.data || {}
    const items = Array.isArray(payload.items) ? payload.items : []
    files.value = items.map(it => ({
      id: String(it.id),
      name: it.filename,
      size: it.size_bytes || 0,
      type: (it.file_ext || '').toLowerCase(),
      status: it.status || 'uploaded',
      uploadedAt: it.created_at || null,
      processedAt: it.processed_at || null,
    }))
  } catch (e) {
    message.error(e?.response?.data?.message || '加载文件列表失败')
  }
}

// 表格列定义
const columns = [
  {
    title: '编号',
    dataIndex: 'id',
    key: 'id',
    width: 80
  },
  {
    title: 'UUID',
    dataIndex: 'uuid',
    key: 'uuid',
    width: 120,
    customRender: ({ record }) => record.id.padStart(8, '0')
  },
  {
    title: '文件名',
    dataIndex: 'name',
    key: 'name',
    width: 300
  },
  {
    title: '文件格式',
    dataIndex: 'type',
    key: 'type',
    width: 100,
    customRender: ({ record }) => getFileType(record.name).toUpperCase()
  },
  {
    title: '解析状态',
    dataIndex: 'status',
    key: 'status',
    width: 120
  },
  {
    title: '可用状态',
    key: 'available',
    width: 100,
    customRender: ({ record }) => record.status === 'processed' ? '可用' : '不可用'
  },
  {
    title: '操作',
    key: 'actions',
    width: 150
  }
]

// 计算属性：过滤后的文件
const filteredFiles = computed(() => {
  if (!searchText.value) return files.value
  return files.value.filter(file =>
    file.name.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

// 方法
const getFileType = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  if (['pdf'].includes(ext)) return 'pdf'
  if (['doc', 'docx'].includes(ext)) return 'doc'
  if (['txt', 'md'].includes(ext)) return 'txt'
  return 'file'
}

// 复用 formatFileSize（已上移）

const getStatusColor = (status) => {
  switch (status) {
    case 'processed': return 'success'
    case 'processing': return 'processing'
    case 'failed': return 'error'
    default: return 'default'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'processed': return '已处理'
    case 'processing': return '处理中'
    case 'failed': return '处理失败'
    default: return '未知'
  }
}

const onSearch = () => {
  // 搜索逻辑已通过计算属性实现
}

const previewFile = (file) => {
  message.info(`预览文件: ${file.name}`)
}

const downloadFile = (file) => {
  message.info(`下载文件: ${file.name}`)
}

const deleteFile = async (file) => {
  await new Promise((resolve) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除文件「${file.name}」吗？该操作不可恢复。`,
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteKBDocument(Number(knowledgeBaseId.value), Number(file.id))
          message.success('已删除')
          await Promise.all([loadDocuments(), loadKB()])
        } catch (e) {
          message.error(e?.response?.data?.message || '删除失败')
        } finally {
          resolve()
        }
      },
      onCancel: () => resolve()
    })
  })
}

// 上传相关逻辑暂移除
const fileInput = ref(null)
const triggerFileSelect = () => {
  fileInput.value?.click()
}

const onFileSelected = async (e) => {
  const f = e.target.files && e.target.files[0]
  if (!f) return
  // 前端校验大小和类型
  const allowed = ['application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'text/markdown']
  const okType = !f.type || allowed.includes(f.type) || ['pdf','doc','docx','txt','md'].includes((f.name.split('.').pop()||'').toLowerCase())
  if (!okType) { message.error('不支持的文件类型'); e.target.value = ''; return }
  const isLt50M = f.size / 1024 / 1024 < 50
  if (!isLt50M) { message.error('文件大小不能超过 50MB'); e.target.value = ''; return }
  try {
    message.loading('上传中...', 1)
    await uploadKBDocument(Number(knowledgeBaseId.value), f)
    message.success('上传成功')
    await Promise.all([loadDocuments(), loadKB()])
  } catch (err) {
    message.error(err?.response?.data?.message || '上传失败')
  } finally {
    e.target.value = ''
  }
}

// 第二个 onMounted 清理，主初始化在上方已处理
</script>

<style scoped>
.wrap {
  padding: 0 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 24px;
}

.kb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px;
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.kb-info {
  display: flex;
  gap: 16px;
}

.kb-icon {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.kb-meta {
  flex: 1;
}

.kb-name {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.kb-desc {
  color: #666;
  font-size: 16px;
  margin: 0 0 12px 0;
}

.kb-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  font-size: 14px;
  color: #999;
}

.file-list {
  background: #fff;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.list-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.table-container {
  padding: 0;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-buttons {
  display: flex;
  gap: 4px;
}
</style>
