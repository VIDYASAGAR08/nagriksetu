import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { apiGet, apiPost } from '../../utils/api.js'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const navigate = useNavigate()

  const [loadingVerify, setLoadingVerify] = useState(true)
  const [userInfo, setUserInfo] = useState(null)
  const [verifyError, setVerifyError] = useState('')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')

  useEffect(() => {
    async function verify() {
      if (!token) {
        setVerifyError('Missing password reset token.')
        setLoadingVerify(false)
        return
      }

      try {
        setLoadingVerify(true)
        setVerifyError('')
        const info = await apiGet(`/auth/verify-reset-token?token=${encodeURIComponent(token)}`)
        setUserInfo(info)
      } catch (err) {
        setVerifyError(err.message || 'Password reset token is invalid, expired, or has already been used.')
      } finally {
        setLoadingVerify(false)
      }
    }
    verify()
  }, [token])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!password || !confirmPassword) {
      setSubmitError('Please enter and confirm your new password.')
      return
    }

    if (password.length < 8) {
      setSubmitError('Password must be at least 8 characters in length.')
      return
    }

    if (password !== confirmPassword) {
      setSubmitError('Passwords do not match.')
      return
    }

    try {
      setSubmitting(true)
      setSubmitError('')
      await apiPost('/auth/reset-password', {
        token,
        password,
      })
      navigate('/login', {
        state: {
          message: 'Your password has been successfully reset. Please sign in with your new credentials.',
        },
      })
    } catch (err) {
      setSubmitError(err.message || 'Failed to reset password. The link may have expired.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loadingVerify) {
    return (
      <div style={{ minHeight: 'calc(100vh - 250px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: '#f4f5f7' }}>
        <div style={{ textAlign: 'center' }}>
          <LoadingSpinner size="lg" />
          <p style={{ marginTop: '1rem', color: '#4b5563', fontWeight: 600 }}>Verifying password reset token...</p>
        </div>
      </div>
    )
  }

  if (verifyError || !userInfo) {
    return (
      <div style={{ minHeight: 'calc(100vh - 250px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: '#f4f5f7' }}>
        <div className="card" style={{ maxWidth: '480px', width: '100%', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', textAlign: 'center' }}>
          <Alert type="error" title="Reset Token Invalid">
            {verifyError || 'Invalid or expired password reset link.'}
          </Alert>
          <div style={{ marginTop: '1.5rem' }}>
            <Link to="/forgot-password" className="btn btn--primary" style={{ textDecoration: 'none' }}>
              Request New Reset Link
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 250px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: '#f4f5f7' }}>
      <div className="card" style={{ maxWidth: '480px', width: '100%', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-block', background: '#1a3a6b', color: '#ffffff', fontWeight: 700, padding: '0.35rem 0.75rem', borderRadius: '4px', fontSize: '0.8125rem', marginBottom: '0.75rem' }}>
            SECURITY VERIFIED
          </div>
          <h1 style={{ fontSize: '1.6rem', color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>Choose New Password</h1>
          <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
            Resetting password for <strong>{userInfo.full_name || userInfo.email}</strong>
          </p>
        </div>

        {submitError && <Alert type="error" title="Reset Error" className="mb-4">{submitError}</Alert>}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
              New Password (Min 8 Characters)
            </label>
            <PasswordInput
              required
              minLength={8}
              className="input"
              placeholder="Enter new secure password (min 8 characters)"
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
              Confirm New Password
            </label>
            <PasswordInput
              required
              minLength={8}
              className="input"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn btn--primary btn--full btn--lg"
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
          >
            {submitting ? <LoadingSpinner size="sm" /> : 'Update Password & Continue →'}
          </button>
        </form>
      </div>
    </div>
  )
}
