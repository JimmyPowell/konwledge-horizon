<template>
  <a-steps :current="step" style="margin-bottom:16px">
    <a-step title="邮箱" />
    <a-step title="验证码" />
    <a-step title="设置账户" />
  </a-steps>

  <div v-if="step===0">
    <a-form layout="vertical" :model="emailForm" @submit.prevent="onRequestCode">
      <a-form-item label="邮箱" name="email" :rules="[{ required: true, type: 'email', message: '请输入有效邮箱' }]"><a-input v-model:value="emailForm.email" placeholder="you@example.com" /></a-form-item>
      <a-form-item><a-button type="primary" html-type="submit" :loading="loading" block>发送验证码</a-button></a-form-item>
    </a-form>
  </div>

  <div v-else-if="step===1">
    <a-form layout="vertical" :model="codeForm" @submit.prevent="onVerifyCode">
      <a-form-item label="邮箱" name="email"><a-input v-model:value="codeForm.email" disabled /></a-form-item>
      <a-form-item label="验证码" name="code" :rules="[{ required: true, message: '请输入验证码' }]"><a-input v-model:value="codeForm.code" maxlength="6" /></a-form-item>
      <a-form-item>
        <a-space>
          <a-button @click="step=0">上一步</a-button>
          <a-button type="primary" html-type="submit" :loading="loading">验证</a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>

  <div v-else>
    <a-form layout="vertical" :model="accountForm" @submit.prevent="onRegister">
      <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]"><a-input v-model:value="accountForm.username" /></a-form-item>
      <a-form-item label="密码" name="password" :rules="[{ required: true, message: '请输入密码' }]"><a-input-password v-model:value="accountForm.password" /></a-form-item>
      <a-form-item>
        <a-space>
          <a-button @click="step=1">上一步</a-button>
          <a-button type="primary" html-type="submit" :loading="loading">完成注册</a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </div>

  <a-alert v-if="message" :type="msgType" :message="message" show-icon />
</template>

<script setup>
import { reactive, ref } from 'vue'
import { requestCode, verifyCode, registerUser, login } from '../services/api'
import { setTokens, setIdentifier } from '../utils/tokens'
import { useAuthStore } from '../stores/auth'

const emit = defineEmits(['success'])
const store = useAuthStore()
const step = ref(0)
const loading = ref(false)
const message = ref('')
const msgType = ref('info')

const emailForm = reactive({ email: '' })
const codeForm = reactive({ email: '', code: '' })
const accountForm = reactive({ username: '', password: '' })
let sessionToken = ''

const onRequestCode = async () => {
  loading.value = true; message.value = ''
  try {
    const { data } = await requestCode(emailForm.email)
    message.value = data?.message || '验证码已发送'
    msgType.value = 'success'
    codeForm.email = emailForm.email
    step.value = 1
  } catch (e) {
    message.value = e?.response?.data?.message || e?.message || '发送失败'
    msgType.value = 'error'
  } finally { loading.value = false }
}

const onVerifyCode = async () => {
  loading.value = true; message.value = ''
  try {
    const { data } = await verifyCode(codeForm.email, codeForm.code)
    const payload = data?.data || {}
    sessionToken = payload?.session || ''
    if (!sessionToken) throw new Error('会话无效')
    message.value = '验证成功，请设置账户信息'
    msgType.value = 'success'
    step.value = 2
  } catch (e) {
    message.value = e?.response?.data?.message || e?.message || '验证失败'
    msgType.value = 'error'
  } finally { loading.value = false }
}

const onRegister = async () => {
  loading.value = true; message.value = ''
  try {
    const { data } = await registerUser(sessionToken, accountForm.username, accountForm.password)
    msgType.value = 'success'
    message.value = data?.message || '注册成功，正在自动登录…'
    // Auto login
    const res = await login(accountForm.username, accountForm.password)
    const p = res?.data || {}
    const tokens = p?.data || p
    if (tokens?.access_token) {
      setTokens(tokens.access_token, tokens.refresh_token || null)
      setIdentifier(accountForm.username)
      await store.setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token || null })
    }
    emit('success')
  } catch (e) {
    message.value = e?.response?.data?.message || e?.message || '注册失败'
    msgType.value = 'error'
  } finally { loading.value = false }
}
</script>

