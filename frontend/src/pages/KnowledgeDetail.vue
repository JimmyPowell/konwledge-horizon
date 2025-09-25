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
            <span class="stat-item">{{ files.length }} 个文件</span>
            <span class="stat-item">{{ knowledgeBase.totalSize }}</span>
            <span class="stat-item">创建于 {{ knowledgeBase.createdAt }}</span>
          </div>
        </div>
      </div>
      <div class="kb-actions">
        <a-button @click="showUploadModal = true" type="primary" size="large">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </template>
          上传文件
        </a-button>
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

    <!-- 上传文件模态框 -->
    <a-modal
      v-model:open="showUploadModal"
      title="上传文件"
      width="600px"
      :footer="null"
    >
      <FileUpload
        :knowledge-base-id="knowledgeBaseId"
        @success="onUploadSuccess"
        @cancel="showUploadModal = false"
      />
    </a-modal>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import FileUpload from '../components/FileUpload.vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const knowledgeBaseId = ref(route.params.id)
const searchText = ref('')
const showUploadModal = ref(false)

// 知识库信息
const knowledgeBase = ref({
  id: '1',
  name: '冶金工艺手册',
  description: '详细介绍各种冶金工艺流程和技术要求',
  totalSize: '15.2MB',
  createdAt: '2025.09.12'
})

// 文件列表
const files = ref([
  {
    id: '1',
    name: '冶金工艺手册.pdf',
    size: 15728640,
    type: 'pdf',
    status: 'processed',
    uploadedAt: '2025.09.12 14:30',
    processedAt: '2025.09.12 14:35'
  },
  {
    id: '2',
    name: '钢铁生产流程.docx',
    size: 2048000,
    type: 'doc',
    status: 'processing',
    uploadedAt: '2025.09.12 15:20',
    processedAt: null
  },
  {
    id: '3',
    name: '质量控制标准.txt',
    size: 512000,
    type: 'txt',
    status: 'failed',
    uploadedAt: '2025.09.12 16:10',
    processedAt: null
  }
])

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

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

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

const deleteFile = (file) => {
  message.info(`删除文件: ${file.name}`)
}

const onUploadSuccess = () => {
  showUploadModal.value = false
  message.success('文件上传成功')
  // 刷新文件列表
}

onMounted(() => {
  // 加载知识库详情和文件列表
})
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
