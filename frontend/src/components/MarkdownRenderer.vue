<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script setup>
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

const props = defineProps({
  content: {
    type: String,
    default: ''
  }
})

// 配置markdown-it
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return '<pre class="hljs"><code>' +
               hljs.highlight(str, { language: lang, ignoreIllegals: true }).value +
               '</code></pre>'
      } catch (__) {}
    }
    return '<pre class="hljs"><code>' + md.utils.escapeHtml(str) + '</code></pre>'
  }
})

const renderedContent = computed(() => {
  if (!props.content) return ''
  return md.render(props.content)
})
</script>

<style scoped>
.markdown-content {
  line-height: 1.6;
  color: #333;
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  overflow-x: hidden; /* 防止横向滚动 */
}

/* 标题样式 */
.markdown-content :deep(h1) {
  font-size: 1.8em;
  font-weight: 600;
  margin: 1.2em 0 0.8em 0;
  padding-bottom: 0.3em;
  border-bottom: 2px solid #eee;
  color: #2c3e50;
}

.markdown-content :deep(h2) {
  font-size: 1.5em;
  font-weight: 600;
  margin: 1em 0 0.6em 0;
  color: #34495e;
}

.markdown-content :deep(h3) {
  font-size: 1.3em;
  font-weight: 600;
  margin: 0.8em 0 0.5em 0;
  color: #34495e;
}

.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  font-size: 1.1em;
  font-weight: 600;
  margin: 0.6em 0 0.4em 0;
  color: #34495e;
}

/* 段落样式 */
.markdown-content :deep(p) {
  margin: 0.8em 0;
  line-height: 1.7;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.8em 0;
  padding-left: 2em;
}

.markdown-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
}

.markdown-content :deep(ul li) {
  list-style-type: disc;
}

.markdown-content :deep(ol li) {
  list-style-type: decimal;
}

/* 代码样式 */
.markdown-content :deep(code) {
  background: #f8f8f8;
  border: 1px solid #e1e1e8;
  border-radius: 3px;
  padding: 2px 6px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
  color: #e83e8c;
}

.markdown-content :deep(pre) {
  background: #f8f8f8;
  border: 1px solid #e1e1e8;
  border-radius: 6px;
  padding: 1em;
  margin: 1em 0;
  overflow-x: auto;
  max-width: 100%; /* 限制最大宽度 */
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.85em; /* 稍微减少代码字体大小 */
  line-height: 1.4;
  white-space: pre-wrap; /* 允许代码换行 */
  word-break: break-all; /* 强制长代码行换行 */
}

.markdown-content :deep(pre code) {
  background: none;
  border: none;
  padding: 0;
  color: inherit;
}

/* 引用样式 */
.markdown-content :deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 1em;
  margin: 1em 0;
  color: #666;
  font-style: italic;
  background: #f9f9f9;
  padding: 0.8em 1em;
  border-radius: 0 4px 4px 0;
}

/* 链接样式 */
.markdown-content :deep(a) {
  color: #1890ff;
  text-decoration: none;
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

/* 表格样式 */
.markdown-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  max-width: 100%; /* 限制表格最大宽度 */
  margin: 1em 0;
  border: 1px solid #ddd;
  overflow-x: auto; /* 表格横向滚动 */
  display: block; /* 使表格可滚动 */
  white-space: nowrap; /* 防止表格内容换行 */
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px 12px;
  text-align: left;
}

.markdown-content :deep(th) {
  background-color: #f5f5f5;
  font-weight: 600;
}

.markdown-content :deep(tr:nth-child(even)) {
  background-color: #f9f9f9;
}

/* 分隔线样式 */
.markdown-content :deep(hr) {
  border: none;
  border-top: 1px solid #eee;
  margin: 2em 0;
}

/* 强调样式 */
.markdown-content :deep(strong) {
  font-weight: 600;
  color: #2c3e50;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: #34495e;
}

/* 删除线 */
.markdown-content :deep(del) {
  text-decoration: line-through;
  color: #999;
}

/* 高亮代码块样式 */
.markdown-content :deep(.hljs) {
  background: #f8f8f8 !important;
  color: #333 !important;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .markdown-content :deep(pre) {
    font-size: 0.8em;
    padding: 0.8em;
  }
  
  .markdown-content :deep(table) {
    font-size: 0.9em;
  }
  
  .markdown-content :deep(th),
  .markdown-content :deep(td) {
    padding: 6px 8px;
  }
}
</style>
