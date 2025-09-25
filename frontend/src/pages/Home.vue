<template>
  <section>
    <a-typography-title :level="2">前端已就绪</a-typography-title>
    <a-typography-paragraph>
      当前 API Base URL: <code>{{ apiBase }}</code>
    </a-typography-paragraph>
    <a-space>
      <a-button type="primary" @click="checkApi" :loading="loading">检查后端连通性</a-button>
    </a-space>
    <a-alert v-if="result" style="margin-top:12px" type="success" :message="'响应：' + result" show-icon />
    <a-alert v-if="error" style="margin-top:12px" type="error" :message="'错误：' + error" show-icon />
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { pingRoot } from '../services/api'

const apiBase = import.meta.env.VITE_API_BASE_URL
const loading = ref(false)
const result = ref('')
const error = ref('')

const checkApi = async () => {
  loading.value = true
  result.value = ''
  error.value = ''
  try {
    const { data } = await pingRoot()
    result.value = JSON.stringify(data)
  } catch (e) {
    error.value = e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}
</script>
