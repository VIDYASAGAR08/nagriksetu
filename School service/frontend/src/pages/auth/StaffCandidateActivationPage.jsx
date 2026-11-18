import { useState } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { apiPost } from '../../utils/api.js'
import Alert from '../../components/ui/Alert.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'

export default function StaffCandidateActivationPage() {
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState(() => searchParams.get('token') || '')
  const navigate = useNavigate()

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function handleActivate(e) {
    e.preventDefault()
    if (!token.trim()) {
      setError('Please provide your single-use activation token.')
      return
    }

    if (!password || !confirmPassword) {
      setError('Please enter and confirm your password.')
      return
    }

    if (password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    try {
      setSubmitting(true)
      setError('')
      const res = await apiPost('/auth/staff-candidate/activate', {
        activation_token: token.trim(),
        password
      })
      setSuccess(res.message || 'Account activated successfully!')
      setTimeout(() => {
        navigate('/login', {
          state: { message: 'Your staff account is now activated! Sign in below with your credentials.' }
        })
      }, 2000)
    } catch (err) {
      setError(err.message || 'Failed to activate staff account. Your activation token may have expired.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div style={{ background: '#F5F7FA', minHeight: '85vh', paddingBottom: '4rem' }}>
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Staff Account Activation' }
      ]} />

      <div style={{ maxWidth: '520px', margin: '3rem auto 0 auto', padding: '0 1rem' }}>
        <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '2rem', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
          <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔐</div>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.35rem 0' }}>
              Staff Account Activation
            </h1>
            <p style={{ color: '#667085', fontSize: '0.85rem', margin: 0 }}>
              Set your personal access password to activate your authorized institutional staff account.
            </p>
          </div>

          {error && <Alert type="error" title="Activation Notice" style={{ marginBottom: '1.25rem' }}>{error}</Alert>}
          {success && <Alert type="success" title="Success" style={{ marginBottom: '1.25rem' }}>{success}</Alert>}

          <form onSubmit={handleActivate}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Activation Token *
              </label>
              <input
                type="text"
                required
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Paste your 72-hour single-use activation token"
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.825rem', fontFamily: 'monospace' }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Create Password * (Minimum 8 characters)
              </label>
              <PasswordInput
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter at least 8 characters"
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
              />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Confirm Password *
              </label>
              <PasswordInput
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Re-enter password"
                style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="btn btn--primary"
              style={{ width: '100%', padding: '0.75rem', fontSize: '0.95rem', fontWeight: 700 }}
            >
              {submitting ? 'Activating Account...' : 'Activate Staff Account & Sign In →'}
            </button>
          </form>

          <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.8rem', color: '#667085' }}>
            Already have an active account? <Link to="/login" style={{ color: '#155EEF', fontWeight: 600 }}>Sign in here</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
