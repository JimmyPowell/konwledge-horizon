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
          @search="onSearch"
        />
      </div>
      <div class="toolbar-right">
        <a-button @click="openCreateKB">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
              <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/>
            </svg>
          </template>
          新建知识库
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

    <!-- 新建/编辑弹窗 -->
    <a-modal v-model:open="createVisible" title="新建知识库" :confirm-loading="createLoading" @ok="handleCreate">
      <a-form layout="vertical">
        <a-form-item label="名称" required>
          <a-input v-model:value="createForm.name" maxlength="200" placeholder="请输入名称" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="createForm.description" :auto-size="{ minRows: 2, maxRows: 4 }" placeholder="可选" />
        </a-form-item>
        <a-form-item label="可见性">
          <a-select v-model:value="createForm.visibility" style="width: 200px">
            <a-select-option value="private">私有</a-select-option>
            <a-select-option value="org">我的组织</a-select-option>
            <a-select-option value="public">公开</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:open="editVisible" title="编辑知识库" :confirm-loading="editLoading" @ok="handleEdit">
      <a-form layout="vertical">
        <a-form-item label="名称" required>
          <a-input v-model:value="editForm.name" maxlength="200" placeholder="请输入名称" />
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="editForm.description" :auto-size="{ minRows: 2, maxRows: 4 }" placeholder="可选" />
        </a-form-item>
        <a-form-item label="可见性">
          <a-select v-model:value="editForm.visibility" style="width: 200px">
            <a-select-option value="private">私有</a-select-option>
            <a-select-option value="org">我的组织</a-select-option>
            <a-select-option value="public">公开</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

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
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
              <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z" fill="#74b9ff"/>
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
          <div class="desc">{{ item.description || '（无描述）' }}</div>
          <div class="file-info">
            <span class="file-size">{{ formatBytes(item.total_size_bytes || 0) }}</span>
            <span class="file-pages">{{ item.doc_count || 0 }} 个文档</span>
          </div>
        </div>

        <div class="card-footer">
          <div class="date">{{ formatDate(item.created_at) }}</div>
          <div class="owner">
            <div class="owner-avatar">KB</div>
            <span>{{ item.visibility }}</span>
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
      <a-button type="primary" @click="openCreateKB">新建知识库</a-button>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { listKBs, createKB, updateKB as apiUpdateKB, deleteKB as apiDeleteKB } from '../services/api'

const router = useRouter()

// 过滤器（与后端 visibility 对应：private/org/public）
const filters = [
  { label: '全部', value: '全部' },
  { label: '个人', value: 'private' },
  { label: '我的组织', value: 'org' },
  { label: '公开', value: 'public' }
]
const filter = ref('全部')
const q = ref('')
// 移除上传相关

// 列表数据
const items = ref([])
const listLoading = ref(false)

// 新建/编辑
const createVisible = ref(false)
const createLoading = ref(false)
const createForm = ref({ name: '', description: '', visibility: 'private' })

const editVisible = ref(false)
const editLoading = ref(false)
const currentEditId = ref(null)
const editForm = ref({ name: '', description: '', visibility: 'private' })

const formatBytes = (bytes) => {
  const n = Number(bytes || 0)
  if (n <= 0) return '0 B'
  const units = ['B','KB','MB','GB','TB']
  const i = Math.floor(Math.log(n) / Math.log(1024))
  return `${(n / Math.pow(1024, i)).toFixed(2)} ${units[i]}`
}

const formatDate = (s) => {
  if (!s) return ''
  try {
    const d = new Date(s)
    return d.toLocaleDateString('zh-CN')
  } catch { return '' }
}

const fetchKBs = async () => {
  listLoading.value = true
  try {
    const { data } = await listKBs({ q: q.value || undefined, limit: 50, offset: 0 })
    const payload = data?.data || {}
    items.value = Array.isArray(payload.items) ? payload.items : []
  } catch (e) {
    message.error(e?.response?.data?.message || '加载知识库失败')
  } finally {
    listLoading.value = false
  }
}

const onSearch = () => fetchKBs()

onMounted(fetchKBs)

// 统计信息
const totalFiles = computed(() => items.value.reduce((sum, it) => sum + (it.doc_count || 0), 0))
const totalSize = computed(() => formatBytes(items.value.reduce((sum, it) => sum + (it.total_size_bytes || 0), 0)))
const recentUploads = computed(() => {
  const now = new Date()
  const y = now.getFullYear()
  const m = now.getMonth()
  return items.value.filter(it => {
    try {
      const d = new Date(it.created_at)
      return d.getFullYear() === y && d.getMonth() === m
    } catch { return false }
  }).length
})

const filtered = computed(() => {
  const kw = q.value.trim().toLowerCase()
  return items.value.filter(it => {
    const okVis = filter.value === '全部' || (it.visibility || '').toLowerCase() === filter.value
    const okKw = !kw || it.name?.toLowerCase().includes(kw) || (it.description || '').toLowerCase().includes(kw)
    return okVis && okKw
  })
})

const openCreateKB = () => {
  createForm.value = { name: '', description: '', visibility: 'private' }
  createVisible.value = true
}

const handleCreate = async () => {
  if (!createForm.value.name?.trim()) {
    message.warning('请输入名称')
    return
  }
  createLoading.value = true
  try {
    await createKB(createForm.value)
    message.success('已创建')
    createVisible.value = false
    await fetchKBs()
  } catch (e) {
    message.error(e?.response?.data?.message || '创建失败')
  } finally {
    createLoading.value = false
  }
}

const editKnowledge = (item) => {
  currentEditId.value = item.id
  editForm.value = {
    name: item.name,
    description: item.description || '',
    visibility: item.visibility || 'private',
  }
  editVisible.value = true
}

const handleEdit = async () => {
  if (!currentEditId.value) return
  editLoading.value = true
  try {
    await apiUpdateKB(currentEditId.value, editForm.value)
    message.success('已更新')
    editVisible.value = false
    await fetchKBs()
  } catch (e) {
    message.error(e?.response?.data?.message || '更新失败')
  } finally {
    editLoading.value = false
  }
}

const openKnowledge = (item) => {
  router.push(`/app/knowledge/${item.id}`)
}

const shareKnowledge = (item) => {
  message.info('分享功能稍后提供')
}

const deleteKnowledge = async (item) => {
  try {
    await new Promise((resolve, reject) => {
      Modal.confirm({
        title: '确认删除',
        content: `确定要删除知识库「${item.name}」吗？该操作不可恢复。`,
        okText: '删除',
        okButtonProps: { danger: true },
        cancelText: '取消',
        onOk: async () => {
          try {
            await apiDeleteKB(item.id)
            message.success('已删除')
            await fetchKBs()
            resolve()
          } catch (e) { message.error('删除失败'); reject(e) }
        },
        onCancel: () => resolve()
      })
    })
  } catch {}
}

// 移除上传相关方法
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
