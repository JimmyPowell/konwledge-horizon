<template>
  <a-form layout="vertical" :model="form" @submit.prevent="onSubmit">
    <a-form-item label="用户名或邮箱" name="identifier" :rules="[{ required: true, message: '请输入用户名或邮箱' }]">
      <a-input v-model:value="form.identifier" placeholder="username 或 email" />
    </a-form-item>
    <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]">
      <a-input-password v-model:value="form.password" />
    </a-form-item>
    <a-form-item>
      <a-button type="primary" html-type="submit" :loading="loading" block>登录</a-button>
    </a-form-item>
    <a-alert v-if="message" :type="msgType" :message="message" show-icon />
  </a-form>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { setTokens, setIdentifier } from '../utils/tokens'

const emit = defineEmits(['success'])
const store = useAuthStore()
const form = reactive({ identifier: '', password: '' })
const loading = ref(false)
const message = ref('')
const msgType = ref('info')

const onSubmit = async () => {
  loading.value = true
  message.value = ''
  msgType.value = 'info'
  try {
    const res = await store.login(form.identifier, form.password)
    message.value = res?.message || '登录成功'
    msgType.value = 'success'
    // 保证 localStorage 持久化
    const payload = res?.data || {}
    const tokenData = payload?.data || payload
    if (tokenData?.access_token) setTokens(tokenData.access_token, tokenData.refresh_token || null)
    setIdentifier(form.identifier)
    emit('success')
  } catch (e) {
    message.value = store.error || '登录失败'
    msgType.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

