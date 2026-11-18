login_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx"

with open(login_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Clean GoogleIcon at top
clean_icon = """import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import { apiPost } from '../../utils/api.js'

// Google 'G' Icon Component
function GoogleIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" style={{ display: 'inline-block', verticalAlign: 'middle' }}>
      <path
        fill="#4285F4"
        d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.82-2.4 3.68v3.05h3.88c2.27-2.09 3.66-5.17 3.66-9.17z"
      />
      <path
        fill="#34A853"
        d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.25v3.15C3.26 21.36 7.33 24 12 24z"
      />
      <path
        fill="#FBBC05"
        d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.25C.45 8.17 0 9.97 0 12s.45 3.83 1.25 5.42l4.03-3.15z"
      />
      <path
        fill="#EA4335"
        d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.25 6.58l4.03 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
      />
    </svg>
  )
}

export default function LoginPage() {
"""

# Find export default function LoginPage()
idx = content.find("export default function LoginPage() {")
assert idx != -1, "export default function LoginPage() not found"
body = content[idx + len("export default function LoginPage() {"):]

handlers = """
  // Google GIS & OTP Handlers
  async function handleGoogleCredentialResponse(idToken) {
    if (!idToken) return
    setGoogleIdToken(idToken)
    setGoogleSending(true)
    setError('')
    setSuccess('')
    try {
      const res = await sendGoogleOtp(idToken, 'login')
      setGoogleEmailMasked(res.masked_email || 'your Google email')
      setGoogleOtpSent(true)
      setGoogleCooldown(res.resend_cooldown_seconds || 60)
      setSuccess(`Verification code sent to ${res.masked_email || 'your Google email'}.`)
    } catch (err) {
      setError(err.message || 'Failed to dispatch email verification code.')
    } finally {
      setGoogleSending(false)
    }
  }

  async function handleDevGoogleSendOtp(e) {
    if (e) e.preventDefault()
    const email = devGoogleEmail.trim().toLowerCase()
    if (!email || !email.includes('@')) {
      setError('Please enter a valid Google email address.')
      return
    }
    const simulatedToken = `dev_test_token:${email}:Google Citizen`
    await handleGoogleCredentialResponse(simulatedToken)
  }

  async function handleVerifyGoogleOtp(e) {
    if (e) e.preventDefault()
    const trimmed = googleOtp.trim()
    if (trimmed.length !== 6 || !/^\\d{6}$/.test(trimmed)) {
      setError('Please enter the complete 6-digit verification code.')
      return
    }
    setGoogleVerifying(true)
    setError('')
    try {
      await googleLogin(googleIdToken, trimmed)
      setSuccess('Verification successful! Signing in...')
      const redirectUrl = searchParams.get('redirect')
      setTimeout(() => {
        if (redirectUrl) navigate(redirectUrl, { replace: true })
        else navigate('/parent', { replace: true })
      }, 600)
    } catch (err) {
      setError(err.message || 'Invalid or expired OTP. Please try again.')
    } finally {
      setGoogleVerifying(false)
    }
  }

  // Mobile SMS OTP Handlers
  async function handleSendMobileOtp(e) {
    if (e) e.preventDefault()
    let digits = mobileNumber.replace(/\\D/g, '')
    if (digits.length === 12 && digits.startsWith('91')) digits = digits.slice(2)
    if (digits.length === 11 && digits.startsWith('0')) digits = digits.slice(1)
    if (!/^[6-9]\\d{9}$/.test(digits)) {
      setError('Please enter a valid 10-digit Indian mobile number (e.g. 9876543210).')
      return
    }
    setMobileSending(true)
    setError('')
    setSuccess('')
    try {
      const res = await sendOtp(digits, 'login')
      setMobileOtpSent(true)
      setMobileMasked(res.masked_phone || `+91 ******${digits.slice(-4)}`)
      setMobileCooldown(res.resend_cooldown_seconds || 60)
      if (res.dev_mode && res.dev_otp) {
        setMobileDevInfo(res)
      } else {
        setMobileDevInfo(null)
      }
      setSuccess(res.message || 'SMS OTP dispatched successfully.')
    } catch (err) {
      setError(err.message || 'No active account found for this mobile number or dispatch failed.')
    } finally {
      setMobileSending(false)
    }
  }

  async function handleVerifyMobileOtp(e) {
    if (e) e.preventDefault()
    const trimmed = mobileOtp.trim()
    if (trimmed.length !== 6 || !/^\\d{6}$/.test(trimmed)) {
      setError('Please enter the 6-digit numeric verification code.')
      return
    }
    let digits = mobileNumber.replace(/\\D/g, '')
    if (digits.length === 12 && digits.startsWith('91')) digits = digits.slice(2)
    if (digits.length === 11 && digits.startsWith('0')) digits = digits.slice(1)
    setMobileVerifying(true)
    setError('')
    try {
      await loginWithOtp(digits, trimmed)
      setSuccess('Verification successful! Signing in...')
      const redirectUrl = searchParams.get('redirect')
      setTimeout(() => {
        if (redirectUrl) navigate(redirectUrl, { replace: true })
        else navigate('/parent', { replace: true })
      }, 600)
    } catch (err) {
      setError(err.message || 'Invalid or expired OTP. Please try again.')
    } finally {
      setMobileVerifying(false)
    }
  }

  function handleResetCitizenState() {
    setCitizenMethod(null)
    setGoogleIdToken('')
    setGoogleEmailMasked('')
    setGoogleOtp('')
    setGoogleOtpSent(false)
    setGoogleSending(false)
    setGoogleVerifying(false)
    setGoogleCooldown(0)
    setDevGoogleEmail('')
    setMobileNumber('')
    setMobileOtp('')
    setMobileOtpSent(false)
    setMobileSending(false)
    setMobileVerifying(false)
    setMobileCooldown(0)
    setMobileDevInfo(null)
    setError('')
    setSuccess('')
  }
"""

main_return_marker = '  return (\n    <div className="login-page-wrapper"'
assert main_return_marker in body, "main_return_marker not found"
body = body.replace(main_return_marker, handlers + "\n" + main_return_marker, 1)

new_full_content = clean_icon + body

with open(login_path, "w", encoding="utf-8") as f:
    f.write(new_full_content)

print("LoginPage.jsx structure cleanly reconstructed!")
