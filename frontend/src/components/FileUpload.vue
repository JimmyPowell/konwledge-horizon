<template>
  <div class="file-upload">
    <!-- 上传区域 -->
    <div class="upload-section">
      <a-upload-dragger
        v-model:fileList="fileList"
        name="file"
        :multiple="true"
        :before-upload="beforeUpload"
        @change="handleChange"
        @drop="handleDrop"
      >
        <div class="upload-content">
          <div class="upload-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none">
              <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" fill="#74b9ff"/>
            </svg>
          </div>
          <div class="upload-text">
            <p class="upload-hint">点击或拖拽文件到此区域上传</p>
            <p class="upload-desc">支持 PDF、Word、TXT、Markdown 等格式，单个文件不超过 100MB</p>
          </div>
        </div>
      </a-upload-dragger>
    </div>

    <!-- 处理设置 -->
    <div class="settings-section">
      <h3 class="section-title">处理设置</h3>
      
      <div class="setting-group">
        <label class="setting-label">分页大小</label>
        <a-select v-model:value="settings.chunkSize" style="width: 200px">
          <a-select-option value="small">小 (500字符)</a-select-option>
          <a-select-option value="medium">中 (1000字符)</a-select-option>
          <a-select-option value="large">大 (2000字符)</a-select-option>
        </a-select>
        <span class="setting-desc">控制文档分割的粒度，影响检索精度</span>
      </div>

      <div class="setting-group">
        <label class="setting-label">重合片大小</label>
        <a-select v-model:value="settings.overlapSize" style="width: 200px">
          <a-select-option value="none">无重合</a-select-option>
          <a-select-option value="small">小 (50字符)</a-select-option>
          <a-select-option value="medium">中 (100字符)</a-select-option>
          <a-select-option value="large">大 (200字符)</a-select-option>
        </a-select>
        <span class="setting-desc">分页间的重叠部分，提高上下文连贯性</span>
      </div>

      <div class="setting-group">
        <label class="setting-label">解析策略</label>
        <a-select v-model:value="settings.parseStrategy" style="width: 200px">
          <a-select-option value="auto">自动检测</a-select-option>
          <a-select-option value="text">纯文本</a-select-option>
          <a-select-option value="structured">结构化</a-select-option>
          <a-select-option value="table">表格优先</a-select-option>
        </a-select>
        <span class="setting-desc">选择最适合文档类型的解析方式</span>
      </div>

      <div class="setting-group">
        <label class="setting-label">预处理选项</label>
        <div class="checkbox-group">
          <a-checkbox v-model:checked="settings.removeHeaders">移除页眉页脚</a-checkbox>
          <a-checkbox v-model:checked="settings.cleanWhitespace">清理多余空白</a-checkbox>
          <a-checkbox v-model:checked="settings.extractImages">提取图片描述</a-checkbox>
          <a-checkbox v-model:checked="settings.preserveFormatting">保留格式信息</a-checkbox>
        </div>
      </div>
    </div>

    <!-- 预览区域 -->
    <div class="preview-section" v-if="fileList.length > 0">
      <h3 class="section-title">文件预览</h3>
      <div class="file-preview-list">
        <div
          v-for="file in fileList"
          :key="file.uid"
          class="file-preview-item"
        >
          <div class="file-info">
            <div class="file-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z" :fill="getFileColor(file.name)"/>
              </svg>
            </div>
            <div class="file-details">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-meta">
                {{ formatFileSize(file.size) }} • {{ getFileType(file.name) }}
              </div>
            </div>
          </div>
          <div class="file-actions">
            <a-button type="text" size="small" @click="removeFile(file)">
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

    <!-- 操作按钮 -->
    <div class="action-buttons">
      <a-button @click="$emit('cancel')">取消</a-button>
      <a-button
        type="primary"
        :loading="uploading"
        :disabled="fileList.length === 0"
        @click="handleUpload"
      >
        {{ uploading ? '上传中...' : '开始上传' }}
      </a-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { message } from 'ant-design-vue'

const props = defineProps({
  knowledgeBaseId: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['success', 'cancel'])

// 响应式数据
const fileList = ref([])
const uploading = ref(false)

// 处理设置
const settings = reactive({
  chunkSize: 'medium',
  overlapSize: 'small',
  parseStrategy: 'auto',
  removeHeaders: true,
  cleanWhitespace: true,
  extractImages: false,
  preserveFormatting: false
})

// 支持的文件类型
const supportedTypes = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
  'text/markdown'
]

// 方法
const beforeUpload = (file) => {
  // 检查文件类型
  if (!supportedTypes.includes(file.type)) {
    message.error(`不支持的文件格式: ${file.name}`)
    return false
  }

  // 检查文件大小 (100MB)
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    message.error('文件大小不能超过 100MB')
    return false
  }

  return false // 阻止自动上传
}

const handleChange = (info) => {
  // 文件列表变化处理
}

const handleDrop = (e) => {
  console.log('Dropped files', e.dataTransfer.files)
}

const removeFile = (file) => {
  const index = fileList.value.findIndex(item => item.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
  }
}

const getFileType = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  const typeMap = {
    pdf: 'PDF',
    doc: 'Word',
    docx: 'Word',
    txt: 'Text',
    md: 'Markdown'
  }
  return typeMap[ext] || 'Unknown'
}

const getFileColor = (filename) => {
  const ext = filename.split('.').pop().toLowerCase()
  const colorMap = {
    pdf: '#e74c3c',
    doc: '#2980b9',
    docx: '#2980b9',
    txt: '#95a5a6',
    md: '#27ae60'
  }
  return colorMap[ext] || '#74b9ff'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleUpload = async () => {
  if (fileList.value.length === 0) {
    message.warning('请选择要上传的文件')
    return
  }

  uploading.value = true

  try {
    // 模拟上传过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    message.success(`成功上传 ${fileList.value.length} 个文件`)
    emit('success')
  } catch (error) {
    message.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.file-upload {
  padding: 24px 0;
}

.upload-section {
  margin-bottom: 32px;
}

.upload-content {
  padding: 40px 20px;
  text-align: center;
}

.upload-icon {
  margin-bottom: 16px;
}

.upload-hint {
  font-size: 16px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.upload-desc {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.settings-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 20px 0;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.setting-label {
  min-width: 100px;
  font-weight: 500;
  color: #2c3e50;
}

.setting-desc {
  font-size: 13px;
  color: #666;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preview-section {
  margin-bottom: 32px;
}

.file-preview-list {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.file-preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.file-preview-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-name {
  font-weight: 500;
  color: #2c3e50;
}

.file-meta {
  font-size: 13px;
  color: #666;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}
</style>
