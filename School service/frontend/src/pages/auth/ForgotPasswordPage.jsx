import { useState } from 'react'
import { Link } from 'react-router-dom'
import { apiPost } from '../../utils/api.js'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'

export default function ForgotPasswordPage() {
  const [identifier, setIdentifier] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [devResetToken, setDevResetToken] = useState('')
  const [error, setError] = useState('')

  const [isMobileOnly, setIsMobileOnly] = useState(false)
  const [mobileOnlyMsg, setMobileOnlyMsg] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!identifier.trim()) {
      setError('Please provide your registered mobile number or email.')
      return
    }

    try {
      setLoading(true)
      setError('')
      setIsMobileOnly(false)
      const res = await apiPost('/auth/forgot-password', { identifier: identifier.trim() })
      setSubmitted(true)
      if (res?.status === 'mobile_only') {
        setIsMobileOnly(true)
        setMobileOnlyMsg(res.message)
      } else if (res?.reset_token) {
        setDevResetToken(res.reset_token)
      }
    } catch (err) {
      setError(err.message || 'Unable to process password reset request.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 250px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: '#f4f5f7' }}>
      <div className="card" style={{ maxWidth: '480px', width: '100%', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-block', background: '#1a3a6b', color: '#ffffff', fontWeight: 700, padding: '0.35rem 0.75rem', borderRadius: '4px', fontSize: '0.8125rem', marginBottom: '0.75rem' }}>
            ACCOUNT RECOVERY
          </div>
          <h1 style={{ fontSize: '1.6rem', color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>Forgot Password</h1>
          <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
            Enter your registered email address or mobile number to receive a secure password reset link.
          </p>
        </div>

        {error && <Alert type="error" title="Error" className="mb-4">{error}</Alert>}

        {submitted ? (
          <div>
            {isMobileOnly ? (
              <Alert type="warning" title="Mobile-Only Account Notice">
                {mobileOnlyMsg || 'This account is registered with a mobile number only. Online automated password reset is available for email accounts. For security, please contact your School Administrator or the NagrikSetu Institution Helpdesk to verify your identity and reset your password.'}
              </Alert>
            ) : (
              <Alert type="success" title="Request Dispatched">
                If an account with those details exists in NagrikSetu, password reset instructions have been issued. The reset link is valid for 1 hour.
              </Alert>
            )}

            {devResetToken && (
              <div style={{ marginTop: '1.25rem', padding: '1rem', background: '#f8fafc', border: '1px dashed #0284c7', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0284c7', marginBottom: '0.4rem', textTransform: 'uppercase' }}>
                  Demo / Development Direct Reset Link
                </div>
                <div style={{ fontSize: '0.8125rem', color: '#334155', wordBreak: 'break-all' }}>
                  <Link to={`/reset-password?token=${devResetToken}`} style={{ color: '#0284c7', fontWeight: 600 }}>
                    Click here to reset password directly →
                  </Link>
                </div>
              </div>
            )}

            <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
              <Link to="/login" className="btn btn--primary" style={{ textDecoration: 'none' }}>
                Return to Sign In
              </Link>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                Mobile Number or Email
              </label>
              <input
                type="text"
                required
                className="input"
                placeholder="e.g. 9876543210 or admin@example.com"
                value={identifier}
                onChange={e => setIdentifier(e.target.value)}
                style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn--primary btn--full btn--lg"
              style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem' }}
            >
              {loading ? <LoadingSpinner size="sm" /> : 'Request Password Reset →'}
            </button>

            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <Link to="/login" style={{ fontSize: '0.875rem', color: '#64748b', textDecoration: 'none' }}>
                ← Remember your password? Sign In
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
