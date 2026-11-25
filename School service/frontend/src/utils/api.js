/**
 * api.js — Central API utility.
 * Resolves the backend API URL dynamically:
 * 1. import.meta.env.VITE_API_URL if configured during build/runtime.
 * 2. If loaded over HTTPS, defaults to origin + '/api' to avoid mixed-content blocks.
 * 3. Fallback to host port 8001 for local development.
 */

import { loadToken } from './auth.js'

export const API_URL = import.meta.env.VITE_API_URL || (
  typeof window !== 'undefined' && window.location.protocol === 'https:'
    ? `${window.location.origin}/api`
    : (typeof window !== 'undefined' ? `http://${window.location.hostname}:8001` : 'http://localhost:8001')
)

/**
 * Perform a fetch and return parsed JSON.
 * Throws an Error with a human-readable message on failure.
 *
 * @param {string} path - URL path (relative to API_URL).
 * @param {RequestInit} [options] - Fetch options (method, body, etc.).
 * @param {string|null} [token] - JWT bearer token, if authenticated.
 */
export async function apiFetch(path, options = {}, token = null) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers ?? {}) }

  const effectiveToken = token || loadToken()
  if (effectiveToken) {
    headers['Authorization'] = `Bearer ${effectiveToken}`
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (!response.ok) {
    let detail = `Request failed (${response.status})`
    try {
      const body = await response.json()
      if (body?.detail) {
        if (typeof body.detail === 'string') {
          detail = body.detail
        } else if (Array.isArray(body.detail)) {
          detail = body.detail
            .map((item) => {
              if (typeof item === 'string') return item
              const loc = Array.isArray(item?.loc) ? item.loc.filter(x => x !== 'body').join('.') : ''
              const msg = item?.msg || item?.message || JSON.stringify(item)
              return loc ? `${loc}: ${msg}` : msg
            })
            .join('; ')
        } else if (typeof body.detail === 'object') {
          detail = body.detail.message || body.detail.msg || JSON.stringify(body.detail)
        }
      } else if (body?.message) {
        detail = body.message
      }
    } catch {
      // ignore JSON parse error
    }
    throw new Error(detail)
  }

  // 204 No Content
  if (response.status === 204) return null

  return response.json()
}

/**
 * Shorthand for a GET request.
 */
export function apiGet(path, token = null) {
  return apiFetch(path, { method: 'GET' }, token)
}

/**
 * Shorthand for a POST request with a JSON body.
 */
export function apiPost(path, body, token = null) {
  return apiFetch(path, { method: 'POST', body: JSON.stringify(body) }, token)
}

/**
 * Shorthand for a PUT request with a JSON body.
 */
export function apiPut(path, body, token = null) {
  return apiFetch(path, { method: 'PUT', body: JSON.stringify(body) }, token)
}

