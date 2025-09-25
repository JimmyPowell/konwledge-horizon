<template>
  <section class="wrap">
    <div class="title">
      <div class="h2">知识库管理</div>
      <div class="sub">查看和添加知识库</div>
    </div>

    <div class="toolbar">
      <div class="toolbar-left">
        <a-segmented v-model:value="filter" :options="filters" />
        <a-input-search
          v-model:value="q"
          class="search"
          placeholder="搜索知识库..."
          allow-clear
        />
      </div>
      <div class="toolbar-right">
        <a-button @click="onCreateFolder">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/>
            </svg>
          </template>
          新建文件夹
        </a-button>
        <a-button type="primary" @click="onUpload">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
            </svg>
          </template>
          上传文件
        </a-button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="stats">
      <div class="stat-item">
        <div class="stat-number">{{ totalFiles }}</div>
        <div class="stat-label">总文件数</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ totalSize }}</div>
        <div class="stat-label">总大小</div>
      </div>
      <div class="stat-item">
        <div class="stat-number">{{ recentUploads }}</div>
        <div class="stat-label">本月上传</div>
      </div>
    </div>

    <!-- 知识库网格 -->
    <div class="grid" v-if="filtered.length > 0">
      <div
        v-for="item in filtered"
        :key="item.id"
        class="kcard"
        @click="openKnowledge(item)"
      >
        <div class="card-header">
          <div class="file-icon">
            <svg v-if="item.type === 'folder'" width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z" fill="#FFA726"/>
            </svg>
            <svg v-else-if="item.type === 'pdf'" width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#F44336"/>
            </svg>
            <svg v-else-if="item.type === 'doc'" width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#2196F3"/>
            </svg>
            <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#4CAF50"/>
            </svg>
          </div>
          <div class="card-actions">
            <a-dropdown :trigger="['click']">
              <a-button type="text" size="small" @click.stop>
                <template #icon>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z"/>
                  </svg>
                </template>
              </a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item @click="editKnowledge(item)">
                    <template #icon>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z"/>
                      </svg>
                    </template>
                    编辑
                  </a-menu-item>
                  <a-menu-item @click="shareKnowledge(item)">
                    <template #icon>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.50-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z"/>
                      </svg>
                    </template>
                    分享
                  </a-menu-item>
                  <a-menu-divider />
                  <a-menu-item @click="deleteKnowledge(item)" danger>
                    <template #icon>
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                      </svg>
                    </template>
                    删除
                  </a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
          </div>
        </div>

        <div class="card-content">
          <div class="name">{{ item.name }}</div>
          <div class="desc">{{ item.desc }}</div>
          <div class="file-info" v-if="item.type !== 'folder'">
            <span class="file-size">{{ item.size }}</span>
            <span class="file-pages" v-if="item.pages">{{ item.pages }} 页</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="date">{{ item.date }}</div>
          <div class="owner">
            <div class="owner-avatar">{{ item.owner.charAt(0) }}</div>
            <span>{{ item.owner }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none">
          <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z" fill="#ddd"/>
        </svg>
      </div>
      <div class="empty-title">暂无知识库文件</div>
      <div class="empty-desc">上传您的第一个文件开始构建知识库</div>
      <a-button type="primary" @click="onUpload">上传文件</a-button>
    </div>

    <!-- 上传文件模态框 -->
    <a-modal
      v-model:open="uploadModalVisible"
      title="上传文件"
      @ok="handleUpload"
      @cancel="uploadModalVisible = false"
    >
      <a-upload-dragger
        v-model:fileList="fileList"
        name="file"
        :multiple="true"
        :before-upload="beforeUpload"
        @change="handleChange"
      >
        <p class="ant-upload-drag-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="#1890ff">
            <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
          </svg>
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p class="ant-upload-hint">
          支持单个或批量上传。支持 PDF、Word、Excel、PPT、TXT 等格式
        </p>
      </a-upload-dragger>
    </a-modal>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'

const router = useRouter()

const filters = [ '全部', '个人', '我的组织' ]
const filter = ref('全部')
const q = ref('')
const uploadModalVisible = ref(false)
const fileList = ref([])

// 模拟知识库数据
const items = ref([
  {
    id: 1,
    name: '冶金工艺手册',
    desc: '详细介绍各种冶金工艺流程和技术要点',
    date: '2025.09.12',
    owner: '张工程师',
    scope: '个人',
    type: 'pdf',
    size: '15.2MB',
    pages: 245
  },
  {
    id: 2,
    name: '钢铁生产数据',
    desc: '2024年钢铁生产相关数据统计',
    date: '2025.09.11',
    owner: '李分析师',
    scope: '我的组织',
    type: 'folder',
    size: '128MB',
    files: 23
  },
  {
    id: 3,
    name: '环保技术报告',
    desc: '绿色冶金技术发展现状与趋势分析',
    date: '2025.09.10',
    owner: '王研究员',
    scope: '个人',
    type: 'doc',
    size: '8.7MB',
    pages: 89
  },
  {
    id: 4,
    name: '设备维护手册',
    desc: '高炉设备日常维护和故障排除指南',
    date: '2025.09.09',
    owner: '赵技师',
    scope: '我的组织',
    type: 'pdf',
    size: '22.1MB',
    pages: 156
  },
  {
    id: 5,
    name: '质量控制标准',
    desc: '钢材质量检测标准和控制流程',
    date: '2025.09.08',
    owner: '孙质检员',
    scope: '个人',
    type: 'doc',
    size: '5.3MB',
    pages: 67
  },
  {
    id: 6,
    name: '安全操作规程',
    desc: '冶金车间安全操作规程和应急预案',
    date: '2025.09.07',
    owner: '刘安全员',
    scope: '我的组织',
    type: 'pdf',
    size: '12.8MB',
    pages: 98
  }
])

// 计算统计信息
const totalFiles = computed(() => items.value.length)
const totalSize = computed(() => '192.1MB')
const recentUploads = computed(() => 12)

const filtered = computed(() => {
  const kw = q.value.trim().toLowerCase()
  return items.value.filter(it => {
    const okScope = filter.value === '全部' || it.scope === filter.value
    const okKw = !kw || it.name.toLowerCase().includes(kw) || it.desc.toLowerCase().includes(kw)
    return okScope && okKw
  })
})

// 方法
const onUpload = () => {
  uploadModalVisible.value = true
}

const onCreateFolder = () => {
  message.info('创建文件夹功能开发中...')
}

const openKnowledge = (item) => {
  // 跳转到知识库详情页面
  router.push(`/app/knowledge/${item.id}`)
}

const editKnowledge = (item) => {
  message.info(`编辑: ${item.name}`)
}

const shareKnowledge = (item) => {
  message.success(`分享: ${item.name}`)
}

const deleteKnowledge = (item) => {
  message.warning(`删除: ${item.name}`)
  // 实现删除逻辑
}

const handleUpload = () => {
  if (fileList.value.length === 0) {
    message.warning('请选择要上传的文件')
    return
  }

  message.loading('正在上传文件...', 2)

  // 模拟上传过程
  setTimeout(() => {
    message.success(`成功上传 ${fileList.value.length} 个文件`)
    fileList.value = []
    uploadModalVisible.value = false
  }, 2000)
}

const beforeUpload = (file) => {
  const isValidType = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'].includes(file.type)
  if (!isValidType) {
    message.error('只支持 PDF、Word、TXT 格式的文件!')
    return false
  }

  const isLt50M = file.size / 1024 / 1024 < 50
  if (!isLt50M) {
    message.error('文件大小不能超过 50MB!')
    return false
  }

  return false // 阻止自动上传
}

const handleChange = (info) => {
  fileList.value = info.fileList
}
</script>

<style scoped>
.wrap {
  max-width: 1120px;
  margin: 0 auto;
  padding: 0 16px;
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

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0 24px;
  border-bottom: 1px solid #eee;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search {
  width: 280px;
}

/* 统计信息 */
.stats {
  display: flex;
  gap: 24px;
  padding: 24px 0;
  border-bottom: 1px solid #f0f0f0;
}

.stat-item {
  text-align: center;
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 知识库网格 */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 24px 0;
}

.kcard {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  height: 220px;
  overflow: hidden;
}

.kcard:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
  border-color: #74b9ff;
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: #f8f9fa;
}

.card-actions {
  opacity: 0;
  transition: opacity 0.2s ease;
}

.kcard:hover .card-actions {
  opacity: 1;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.name {
  font-weight: 600;
  font-size: 16px;
  color: #2c3e50;
  line-height: 1.4;
}

.desc {
  color: #666;
  font-size: 14px;
  line-height: 1.4;
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.file-info {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.file-size,
.file-pages {
  font-size: 12px;
  color: #999;
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 4px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
  min-height: 40px;
}

.date {
  color: #999;
  font-size: 13px;
}

.owner {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
  flex-shrink: 0;
  max-width: 120px;
  overflow: hidden;
}

.owner-avatar {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(135deg, #74b9ff, #4da6ff);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  font-weight: 600;
  flex-shrink: 0;
}

.owner span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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

  .toolbar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .toolbar-left,
  .toolbar-right {
    justify-content: center;
  }

  .search {
    width: 100%;
  }

  .stats {
    flex-direction: column;
    gap: 16px;
  }

  .grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

/* 上传模态框样式 */
:deep(.ant-upload-drag) {
  background: #fafbfc !important;
  border: 2px dashed #d9d9d9 !important;
  border-radius: 8px !important;
}

:deep(.ant-upload-drag:hover) {
  border-color: #40a9ff !important;
}

:deep(.ant-upload-drag-icon) {
  margin-bottom: 16px !important;
}

:deep(.ant-upload-text) {
  font-size: 16px !important;
  color: #666 !important;
  margin-bottom: 8px !important;
}

:deep(.ant-upload-hint) {
  color: #999 !important;
  font-size: 14px !important;
}
</style>

