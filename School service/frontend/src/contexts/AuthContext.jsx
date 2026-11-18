import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { apiGet, apiPost } from '../utils/api.js'
import { isTokenExpired, loadToken, loadUser, removeToken, saveToken, saveUser } from '../utils/auth.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken]   = useState(() => loadToken())
  const [user,  setUser]    = useState(() => loadUser())
  const [loading, setLoading] = useState(true)

  // On mount, verify stored token is still valid.
  useEffect(() => {
    async function verify() {
      const stored = loadToken()
      if (!stored || isTokenExpired(stored)) {
        removeToken()
        setToken(null)
        setUser(null)
        setLoading(false)
        return
      }
      try {
        const me = await apiGet('/auth/me', stored)
        setUser(me)
        saveUser(me)
      } catch {
        removeToken()
        setToken(null)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }
    verify()
  }, [])

  const login = useCallback(async (identifier, password, institutionId = null) => {
    const formData = new URLSearchParams()
    formData.set('username', identifier)
    formData.set('password', password)

    const query = institutionId ? `?institution_id=${encodeURIComponent(institutionId)}` : ''
    let response
    try {
      response = await fetch(`${import.meta.env.VITE_API_URL ?? `http://${window.location.hostname}:8001`}/auth/login${query}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData.toString(),
      })
    } catch (fetchErr) {
      throw new Error('Unable to connect to NagrikSetu authentication server. Please check network connectivity or backend status.')
    }

    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      throw new Error(body?.detail ?? 'Incorrect username or password.')
    }

    const data = await response.json()
    if (data.requires_workspace_selection) {
      return data
    }

    const { access_token } = data
    saveToken(access_token)
    setToken(access_token)

    const me = await apiGet('/auth/me', access_token)
    const mergedUser = { ...me, school_id: data.school_id || me.school_id, role: data.role || me.role }
    saveUser(mergedUser)
    setUser(mergedUser)

    return mergedUser
  }, [])

  const selectWorkspace = useCallback(async (tempToken, institutionId) => {
    const data = await apiPost('/auth/select-workspace', {
      temp_token: tempToken,
      institution_id: institutionId
    })
    const { access_token } = data
    saveToken(access_token)
    setToken(access_token)

    const me = await apiGet('/auth/me', access_token)
    saveUser(me)
    setUser(me)
    return me
  }, [])

  const logout = useCallback(() => {
    removeToken()
    setToken(null)
    setUser(null)
  }, [])

  const register = useCallback(async (payload) => {
    return apiPost('/auth/register', payload)
  }, [])

  const sendOtp = useCallback(async (phone, purpose = 'register') => {
    return apiPost('/auth/otp/send', { phone, purpose })
  }, [])

  const registerWithOtp = useCallback(async ({ phone, otp, full_name, email }) => {
    const data = await apiPost('/auth/otp/register', { phone, otp, full_name, email })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const loginWithOtp = useCallback(async (phone, otp) => {
    const data = await apiPost('/auth/otp/login', { phone, otp })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const sendEmailOtp = useCallback(async (email, purpose = 'register', full_name = null) => {
    return apiPost('/auth/email/otp/send', { email, purpose, full_name })
  }, [])

  const registerWithEmail = useCallback(async ({ email, otp, password, full_name, phone }) => {
    const data = await apiPost('/auth/email/register', { email, otp, password, full_name, phone })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const loginWithEmail = useCallback(async (email, password) => {
    const data = await apiPost('/auth/email/login', { email, password })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const sendUnifiedOtp = useCallback(async (fullName, contact, purpose = 'login') => {
    return apiPost('/auth/unified/otp/send', { full_name: fullName, contact, purpose })
  }, [])

  const unifiedLogin = useCallback(async (fullName, contact, otp) => {
    const data = await apiPost('/auth/unified/login', { full_name: fullName, contact, otp })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const unifiedRegister = useCallback(async (fullName, contact, otp) => {
    const data = await apiPost('/auth/unified/register', { full_name: fullName, contact, otp })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const getOAuthConfig = useCallback(async () => {
    return apiGet('/auth/config/oauth')
  }, [])

  const sendGoogleOtp = useCallback(async (idToken, purpose = 'login', fullName = '') => {
    return apiPost('/auth/google/otp/send', { id_token: idToken, purpose, full_name: fullName })
  }, [])

  const googleLogin = useCallback(async (idToken, otp) => {
    const data = await apiPost('/auth/google/login', { id_token: idToken, otp })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const googleRegister = useCallback(async (idToken, otp, fullName = '') => {
    const data = await apiPost('/auth/google/register', { id_token: idToken, otp, full_name: fullName })
    if (data.access_token) {
      saveToken(data.access_token)
      setToken(data.access_token)
      const me = await apiGet('/auth/me', data.access_token)
      const merged = { ...me, ...data }
      saveUser(merged)
      setUser(merged)
      return merged
    }
    return data
  }, [])

  const value = {
    token,
    user,
    loading,
    isAuthenticated: !!token && !!user,
    role: user?.role ?? null,
    login,
    logout,
    register,
    sendOtp,
    registerWithOtp,
    loginWithOtp,
    sendEmailOtp,
    registerWithEmail,
    loginWithEmail,
    sendUnifiedOtp,
    unifiedLogin,
    unifiedRegister,
    getOAuthConfig,
    sendGoogleOtp,
    googleLogin,
    googleRegister,
    selectWorkspace,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
