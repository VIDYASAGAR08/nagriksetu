/**
 * auth.js — Token storage helpers.
 * Uses localStorage; note XSS risk — acceptable for a demo.
 */

const TOKEN_KEY = 'nagriksetu_token'
const USER_KEY  = 'nagriksetu_user'

export function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function loadToken() {
  return localStorage.getItem(TOKEN_KEY) ?? null
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function loadUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function isTokenExpired(token) {
  if (!token) return true
  try {
    const [, payloadB64] = token.split('.')
    const payload = JSON.parse(atob(payloadB64))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}
