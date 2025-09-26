import { defineStore } from 'pinia'
import { login as loginApi } from '../services/api'
import { setTokens, clearTokens, setIdentifier, clearIdentifier, getIdentifier, getAccessToken, getRefreshToken } from '../utils/tokens'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: getAccessToken(),
    refreshToken: getRefreshToken(),
    user: null,
    loading: false,
    error: null
  }),
  actions: {
    async login(identifier, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await loginApi(identifier, password)
        // API returns unified response: { code, message, data: { access_token, refresh_token } }
        const tokenData = data?.data || data
        this.accessToken = tokenData?.access_token || null
        this.refreshToken = tokenData?.refresh_token || null
        setTokens(this.accessToken, this.refreshToken)
        setIdentifier(identifier)
        return data
      } catch (e) {
        this.error = e?.response?.data?.message || e?.message || '登录失败'
        throw e
      } finally {
        this.loading = false
      }
    },
    setTokens({ accessToken, refreshToken }) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      setTokens(accessToken, refreshToken)
    },
    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      clearTokens()
      try { clearIdentifier() } catch {}
    }
  }
})
