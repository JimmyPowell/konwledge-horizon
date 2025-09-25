const ACCESS_KEY = 'kh_access_token'
const REFRESH_KEY = 'kh_refresh_token'
const IDENTIFIER_KEY = 'kh_identifier'

export const getAccessToken = () => localStorage.getItem(ACCESS_KEY) || null
export const getRefreshToken = () => localStorage.getItem(REFRESH_KEY) || null
export const getIdentifier = () => localStorage.getItem(IDENTIFIER_KEY) || ''

export const setTokens = (accessToken, refreshToken) => {
  if (accessToken) localStorage.setItem(ACCESS_KEY, accessToken)
  if (typeof refreshToken !== 'undefined' && refreshToken !== null) {
    localStorage.setItem(REFRESH_KEY, refreshToken)
  }
}

export const setIdentifier = (identifier) => {
  if (identifier) localStorage.setItem(IDENTIFIER_KEY, identifier)
}

export const clearTokens = () => {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

