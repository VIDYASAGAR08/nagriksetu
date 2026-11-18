import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import { apiPost } from '../../utils/api.js'

export default function SetupPasswordPage() {
  const navigate = useNavigate()
  const [identifier, setIdentifier] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')

    if (!identifier.trim()) {
      setError('Please enter your registered email address or mobile number.')
      return
    }

    if (!fullName.trim() || fullName.trim().length < 2) {
      setError('Please enter your full name as registered on the account.')
      return
    }

    if (password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    const hasLetter = /[a-zA-Z]/.test(password)
    const hasNumOrSymbol = /[^a-zA-Z]/.test(password)
    if (!hasLetter || !hasNumOrSymbol) {
      setError('Password must include at least one letter and at least one number or symbol.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    try {
      setLoading(true)
      const res = await apiPost('/auth/setup-password', {
        identifier: identifier.trim(),
        full_name: fullName.trim(),
        password: password,
        confirm_password: confirmPassword,
      })

      setSuccess(res.message || 'Password configured successfully!')
      setTimeout(() => {
        navigate('/login?category=parent', {
          state: {
            message: 'Password set successfully! You can now sign in with your credentials.',
          },
        })
      }, 1500)
    } catch (err) {
      setError(err.message || 'Unable to set password. Please verify your details or contact your administrator.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 200px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2.5rem 1rem', background: '#F8FAFC' }}>
      <div
        className="card"
        style={{
          maxWidth: '500px',
          width: '100%',
          padding: '2.25rem',
          border: '1px solid #D0D5DD',
          borderRadius: '10px',
          background: '#FFFFFF',
          boxShadow: '0 4px 12px rgba(16, 43, 70, 0.06)',
          boxSizing: 'border-box',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: '#F1F5F9',
              border: '1px solid #CBD5E1',
              color: '#102B46',
              fontWeight: 700,
              padding: '0.3rem 0.75rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              marginBottom: '0.75rem',
            }}
          >
            ACCOUNT ACTIVATION
          </div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.4rem 0' }}>
            Set Up Password
          </h1>
          <p style={{ color: '#475467', fontSize: '0.875rem', margin: 0 }}>
            Configure your password for an existing account that does not have a password set.
          </p>
        </div>

        {error && (
          <Alert type="error" title="Setup Error" className="mb-4">
            {error}
          </Alert>
        )}

        {success && (
          <Alert type="success" title="Success" className="mb-4">
            {success}
          </Alert>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
              Registered Email or Mobile Number <span style={{ color: '#D92D20' }}>*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. 9876543210 or yourname@example.com"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.9375rem',
                boxSizing: 'border-box',
              }}
            />
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
              Full Name (as registered) <span style={{ color: '#D92D20' }}>*</span>
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Chandhan Kumar"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.9375rem',
                boxSizing: 'border-box',
              }}
            />
            <span style={{ display: 'block', fontSize: '0.75rem', color: '#667085', marginTop: '0.25rem' }}>
              Used to securely verify your identity without OTP.
            </span>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
              New Password <span style={{ color: '#D92D20' }}>*</span>
            </label>
            <PasswordInput
              required
              minLength={8}
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.9375rem',
              }}
            />
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
              Confirm Password <span style={{ color: '#D92D20' }}>*</span>
            </label>
            <PasswordInput
              required
              minLength={8}
              placeholder="Re-enter new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '0.65rem 0.85rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.9375rem',
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn--primary btn--full btn--lg"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              background: '#102B46',
              color: '#FFFFFF',
              fontWeight: 700,
              fontSize: '1rem',
              padding: '0.85rem',
              borderRadius: '6px',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              marginBottom: '1rem',
            }}
          >
            {loading ? <LoadingSpinner size="sm" /> : 'Configure Password →'}
          </button>
        </form>

        <div style={{ textAlign: 'center', paddingTop: '1rem', borderTop: '1px solid #EAECF0' }}>
          <Link to="/login?category=parent" style={{ color: '#64748B', fontSize: '0.875rem', textDecoration: 'none' }}>
            ← Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  )
}
