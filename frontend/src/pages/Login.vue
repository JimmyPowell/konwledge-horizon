<template>
  <section>
    <a-typography-title :level="2">登录</a-typography-title>
    <a-form :model="form" layout="vertical" @submit.prevent="onSubmit" class="form">
      <a-form-item label="用户名或邮箱" name="identifier" :rules="[{ required: true, message: '请输入用户名或邮箱' }]">
        <a-input v-model:value="form.identifier" placeholder="username 或 email" />
      </a-form-item>
      <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]">
        <a-input-password v-model:value="form.password" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" html-type="submit" :loading="loading">登录</a-button>
      </a-form-item>
    </a-form>
    <a-alert v-if="message" class="msg" :type="msgType" :message="message" show-icon />
    <a-card v-if="tokens" style="margin-top: 12px" size="small" title="返回 Tokens">
      <pre style="white-space: pre-wrap; word-break: break-all">{{ tokens }}</pre>
    </a-card>
  </section>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const store = useAuthStore()
const form = reactive({ identifier: '', password: '' })
const loading = ref(false)
const message = ref('')
const msgType = ref('info')
const tokens = ref('')

const onSubmit = async () => {
  loading.value = true
  message.value = ''
  tokens.value = ''
  msgType.value = 'info'
  try {
    const res = await store.login(form.identifier, form.password)
    message.value = res?.message || '登录成功'
    msgType.value = 'success'
    tokens.value = JSON.stringify(res?.data || res)
  } catch (e) {
    message.value = store.error || '登录失败'
    msgType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.form { max-width: 420px; }
.msg { margin-top: 12px; }
</style>
