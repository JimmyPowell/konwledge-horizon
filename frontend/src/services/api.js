import axios from 'axios'
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens
} from '../utils/tokens'

// Main API instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

// Bare instance (no interceptors) for refresh/logout flows
const bare = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: { 'Content-Type': 'application/json' }
})

let isRefreshing = false
let refreshSubscribers = []

const subscribeTokenRefresh = (cb) => {
  refreshSubscribers.push(cb)
}

const onRrefreshed = (newToken) => {
  refreshSubscribers.forEach((cb) => cb(newToken))
  refreshSubscribers = []
}

// Attach Authorization header
api.interceptors.request.use((config) => {
  if (!config.headers) config.headers = {}
  // Allow opt-out
  if (config.__skipAuth) return config
  const token = getAccessToken()
  if (token && !config.headers.Authorization) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 handling + refresh queue
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const { response, config } = error || {}
    if (!response) throw error

    if (response.status === 401 && !config.__skipAuth && !config.__isRetry) {
      const refreshToken = getRefreshToken()
      if (!refreshToken) {
        clearTokens()
        // Optional: redirect to /auth
        try { window?.location && (window.location.href = '/auth') } catch {}
        return Promise.reject(error)
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          subscribeTokenRefresh((newToken) => {
            if (!newToken) {
              reject(error)
              return
            }
            const newConfig = { ...config, __isRetry: true }
            newConfig.headers = newConfig.headers || {}
            newConfig.headers.Authorization = `Bearer ${newToken}`
            resolve(api(newConfig))
          })
        })
      }

      // Start refresh
      isRefreshing = true
      try {
        const { data } = await bare.post(
          '/api/v1/auth/refresh',
          { refresh_token: refreshToken },
          { __skipAuth: true }
        )
        // Unified response wrapper
        const payload = data?.data || data
        const newAccess = payload?.access_token
        const maybeNewRefresh = payload?.refresh_token || null
        if (!newAccess) throw new Error('No access token in refresh response')
        setTokens(newAccess, maybeNewRefresh ?? undefined)
        isRefreshing = false
        onRrefreshed(newAccess)

        const retryConfig = { ...config, __isRetry: true }
        retryConfig.headers = retryConfig.headers || {}
        retryConfig.headers.Authorization = `Bearer ${newAccess}`
        return api(retryConfig)
      } catch (e) {
        isRefreshing = false
        onRrefreshed(null)
        clearTokens()
        try { window?.location && (window.location.href = '/auth') } catch {}
        return Promise.reject(e)
      }
    }

    throw error
  }
)

// Simple helpers
export const pingRoot = () => api.get('/')
export const login = (identifier, password) =>
  api.post('/api/v1/auth/login', { identifier, password })
export const requestCode = (email) =>
  bare.post('/api/v1/auth/request-code', { email }, { __skipAuth: true })
export const verifyCode = (email, code) =>
  bare.post('/api/v1/auth/verify-code', { email, code }, { __skipAuth: true })
export const registerUser = (session, username, password) =>
  bare.post('/api/v1/auth/register', { session, username, password }, { __skipAuth: true })
export const refreshToken = (refresh_token) =>
  bare.post('/api/v1/auth/refresh', { refresh_token }, { __skipAuth: true })
export const logout = (refresh_token) =>
  bare.post('/api/v1/auth/logout', { refresh_token })

// Chat APIs
export const createConversation = (payload = {}) =>
  api.post('/api/v1/chat/conversations', payload)

export const listConversations = (params = {}) =>
  api.get('/api/v1/chat/conversations', { params })

export const listMessages = (conversationId, params = {}) =>
  api.get(`/api/v1/chat/conversations/${conversationId}/messages`, { params })

export const sendMessage = (conversationId, payload) =>
  api.post(`/api/v1/chat/conversations/${conversationId}/messages`, payload)

// Streaming via fetch (SSE)
export const sendMessageStream = async (conversationId, payload, onChunk) => {
  const url = `${import.meta.env.VITE_API_BASE_URL}/api/v1/chat/conversations/${conversationId}/messages/stream`
  const token = getAccessToken()
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(payload)
  })
  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `HTTP ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value, { stream: true })
    buffer += chunk
    // SSE frames are separated by double newlines
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const frame = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      const line = frame.trim()
      if (!line) continue
      if (!line.startsWith('data:')) continue
      const data = line.slice(5).trim()
      if (data === '[DONE]') {
        onChunk({ done: true })
        return
      }
      // Parse JSON; only append text content, never raw JSON
      try {
        const obj = JSON.parse(data)
        const choice = (obj.choices && obj.choices[0]) || {}
        const m = choice.message || {}
        const delta = choice.delta || {}
        const text = m.content || delta.content || ''
        if (text) onChunk({ text })
      } catch {
        // ignore non-JSON or malformed frames
      }
    }
  }
  onChunk({ done: true })
}

export default api
