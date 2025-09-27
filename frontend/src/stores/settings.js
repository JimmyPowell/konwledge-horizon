import { defineStore } from 'pinia'
import { getMySettings, updateMySettings } from '../services/api'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: null,
    version: 1,
    loading: false,
    error: null,
    loaded: false,
    updatedAt: null,
  }),
  getters: {
    streaming(state) {
      return state.settings?.streaming ?? true
    },
    web_search(state) {
      return state.settings?.web_search ?? false
    },
    default_kb_id(state) {
      return state.settings?.default_kb_id ?? null
    },
    model(state) {
      return state.settings?.model || null
    },
  },
  actions: {
    async load() {
      if (this.loading) return
      this.loading = true
      this.error = null
      try {
        const { data } = await getMySettings()
        const payload = data?.data || data
        if (payload) {
          this.settings = payload
          this.version = payload.version || 1
          this.updatedAt = payload.updated_at || null
          this.loaded = true
        }
        return { ok: true, data: this.settings }
      } catch (e) {
        this.error = e?.response?.data?.message || e?.message || '加载设置失败'
        return { ok: false, error: this.error }
      } finally {
        this.loading = false
      }
    },
    async update(patch) {
      if (!this.loaded) {
        const res = await this.load()
        if (!res?.ok) return res
      }
      const payload = { ...patch, version: this.version }
      try {
        const { data } = await updateMySettings(payload)
        const out = data?.data || data
        if (out) {
          this.settings = out
          this.version = out.version || this.version + 1
          this.updatedAt = out.updated_at || null
        }
        return { ok: true, data: this.settings }
      } catch (e) {
        const msg = e?.response?.data?.message || e?.message || ''
        // Handle optimistic lock conflict by refreshing
        if (typeof msg === 'string' && msg.toLowerCase().includes('version conflict')) {
          await this.load()
          return { ok: false, conflict: true, error: '版本冲突，已刷新设置' }
        }
        return { ok: false, error: msg || '更新设置失败' }
      }
    },
    resetLocal() {
      this.settings = null
      this.version = 1
      this.loading = false
      this.error = null
      this.loaded = false
      this.updatedAt = null
    },
  },
})

