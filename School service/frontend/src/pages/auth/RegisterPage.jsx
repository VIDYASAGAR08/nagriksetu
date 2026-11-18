import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import { apiPost } from '../../utils/api.js'
import { saveToken, saveUser } from '../../utils/auth.js'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const redirectUrl = searchParams.get('redirect')

  // Form states
  const [fullName, setFullName] = useState('')
  const [contact, setContact] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  // UI state
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Validation logic
  function validate() {
    const trimmedName = fullName.trim()
    if (!trimmedName || trimmedName.length < 2) {
      return 'Please enter your full name (minimum 2 characters).'
    }

    const trimmedContact = contact.trim()
    if (!trimmedContact) {
      return 'Please enter an email address or mobile number.'
    }

    if (trimmedContact.includes('@')) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(trimmedContact)) {
        return 'Please enter a valid email address.'
      }
    } else {
      let digits = trimmedContact.replace(/\D/g, '')
      if (digits.length === 12 && digits.startsWith('91')) {
        digits = digits.slice(2)
      } else if (digits.length === 11 && digits.startsWith('0')) {
        digits = digits.slice(1)
      }
      if (!/^[6-9]\d{9}$/.test(digits)) {
        return 'Please enter a valid 10-digit Indian mobile number or email address.'
      }
    }

    if (!password || password.length < 8) {
      return 'Password must contain at least 8 characters.'
    }

    const hasLetter = /[a-zA-Z]/.test(password)
    const hasNumOrSymbol = /[^a-zA-Z]/.test(password)
    if (!hasLetter || !hasNumOrSymbol) {
      return 'Password must include at least one letter and at least one number or symbol.'
    }

    if (password !== confirmPassword) {
      return 'Passwords do not match.'
    }

    return null
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    const validationError = validate()
    if (validationError) {
      setError(validationError)
      return
    }

    const trimmedContact = contact.trim()
    let emailVal = null
    let phoneVal = null

    if (trimmedContact.includes('@')) {
      emailVal = trimmedContact.toLowerCase()
    } else {
      let digits = trimmedContact.replace(/\D/g, '')
      if (digits.length === 12 && digits.startsWith('91')) {
        digits = digits.slice(2)
      } else if (digits.length === 11 && digits.startsWith('0')) {
        digits = digits.slice(1)
      }
      phoneVal = digits
    }

    const payload = {
      full_name: fullName.trim(),
      email: emailVal,
      phone: phoneVal,
      password: password,
      confirm_password: confirmPassword,
    }

    try {
      setLoading(true)
      const data = await apiPost('/auth/register', payload)

      if (data?.access_token) {
        saveToken(data.access_token)
        saveUser({
          user_id: data.user_id,
          full_name: data.full_name,
          role: data.role || 'parent',
          email: emailVal,
          phone: phoneVal,
        })

        if (redirectUrl) {
          navigate(redirectUrl, { replace: true })
        } else {
          navigate('/parent', {
            replace: true,
            state: {
              welcome: true,
              message: 'Account created successfully. Welcome to NagrikSetu.',
            },
          })
        }
      } else {
        navigate('/login?category=parent', {
          replace: true,
          state: {
            message: 'Registration successful. Please sign in with your credentials.',
          },
        })
      }
    } catch (err) {
      setError(err.message || 'Registration failed. Please check your information and try again.')
    } finally {
      setLoading(false)
    }
  }

  const loginDestination = redirectUrl
    ? `/login?category=parent&redirect=${encodeURIComponent(redirectUrl)}`
    : '/login?category=parent'

  return (
    <div
      style={{
        minHeight: 'calc(100vh - 180px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
        background: '#FFFFFF',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '440px',
          background: '#FFFFFF',
          border: '1px solid #D0D5DD',
          borderRadius: '8px',
          padding: '2rem',
          boxShadow: '0 2px 8px rgba(16, 43, 70, 0.05)',
          boxSizing: 'border-box',
        }}
      >
        {/* Compact Header: NS Logo, NagrikSetu, Education Information Platform, Login Navigation */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingBottom: '1.25rem',
            marginBottom: '1.25rem',
            borderBottom: '1px solid #EAECF0',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '6px',
                background: '#102B46',
                color: '#FFFFFF',
                fontWeight: 800,
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                letterSpacing: '0.5px',
              }}
            >
              NS
            </div>
            <div>
              <div
                style={{
                  fontSize: '1.1rem',
                  fontWeight: 800,
                  color: '#102B46',
                  lineHeight: 1.2,
                  letterSpacing: '-0.01em',
                }}
              >
                NagrikSetu
              </div>
              <div
                style={{
                  fontSize: '0.75rem',
                  color: '#475467',
                  fontWeight: 500,
                  lineHeight: 1.2,
                }}
              >
                Education Information Platform
              </div>
            </div>
          </div>

          <Link
            to={loginDestination}
            style={{
              fontSize: '0.8125rem',
              fontWeight: 600,
              color: '#155EEF',
              textDecoration: 'none',
            }}
          >
            Sign In
          </Link>
        </div>

        {/* Section Heading & Subtitle */}
        <div style={{ marginBottom: '1.25rem' }}>
          <h1
            style={{
              fontSize: '1.4rem',
              fontWeight: 700,
              color: '#102B46',
              margin: '0 0 0.35rem 0',
              letterSpacing: '-0.01em',
            }}
          >
            Citizen Registration
          </h1>
          <p
            style={{
              fontSize: '0.875rem',
              color: '#475467',
              margin: 0,
              lineHeight: 1.45,
            }}
          >
            Create your account to access NagrikSetu services.
          </p>
        </div>

        {error && (
          <Alert type="error" title="Registration Error" className="mb-4">
            {error}
          </Alert>
        )}

        {/* Registration Form */}
        <form onSubmit={handleSubmit} noValidate>
          {/* Field 1: Full Name */}
          <div style={{ marginBottom: '1rem' }}>
            <label
              htmlFor="full-name"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#102B46',
                marginBottom: '0.35rem',
              }}
            >
              Full Name
            </label>
            <input
              id="full-name"
              name="name"
              type="text"
              required
              autoComplete="name"
              placeholder="Enter your full name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              style={{
                width: '100%',
                height: '42px',
                padding: '0.55rem 0.75rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#101828',
                backgroundColor: '#FFFFFF',
                boxSizing: 'border-box',
                outline: 'none',
              }}
            />
          </div>

          {/* Field 2: Email Address / Mobile Number */}
          <div style={{ marginBottom: '1rem' }}>
            <label
              htmlFor="contact-identifier"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#102B46',
                marginBottom: '0.35rem',
              }}
            >
              Email Address / Mobile Number
            </label>
            <input
              id="contact-identifier"
              name="username"
              type="text"
              required
              autoComplete="username"
              placeholder="name@example.com or 10-digit mobile number"
              value={contact}
              onChange={(e) => setContact(e.target.value)}
              style={{
                width: '100%',
                height: '42px',
                padding: '0.55rem 0.75rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.875rem',
                color: '#101828',
                backgroundColor: '#FFFFFF',
                boxSizing: 'border-box',
                outline: 'none',
              }}
            />
          </div>

          {/* Field 3: Password */}
          <div style={{ marginBottom: '1rem' }}>
            <label
              htmlFor="password"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#102B46',
                marginBottom: '0.35rem',
              }}
            >
              Password
            </label>
            <PasswordInput
              id="password"
              name="new-password"
              autoComplete="new-password"
              required
              minLength={8}
              placeholder="Minimum 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                height: '42px',
                padding: '0.55rem 0.75rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.875rem',
              }}
            />
          </div>

          {/* Field 4: Confirm Password */}
          <div style={{ marginBottom: '1.35rem' }}>
            <label
              htmlFor="confirm-password"
              style={{
                display: 'block',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#102B46',
                marginBottom: '0.35rem',
              }}
            >
              Confirm Password
            </label>
            <PasswordInput
              id="confirm-password"
              name="confirm-password"
              autoComplete="new-password"
              required
              minLength={8}
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              style={{
                width: '100%',
                height: '42px',
                padding: '0.55rem 0.75rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                fontSize: '0.875rem',
              }}
            />
          </div>

          {/* Button: Create Account */}
          <button
            type="submit"
            disabled={loading}
            className="btn btn--primary btn--full"
            style={{
              width: '100%',
              height: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              background: '#102B46',
              color: '#FFFFFF',
              fontWeight: 700,
              fontSize: '0.9375rem',
              borderRadius: '6px',
              border: 'none',
              cursor: loading ? 'not-allowed' : 'pointer',
              boxShadow: '0 1px 2px rgba(16, 43, 70, 0.1)',
              marginBottom: '1.25rem',
            }}
          >
            {loading ? <LoadingSpinner size="sm" /> : 'Create Account'}
          </button>
        </form>

        {/* Existing Account Navigation */}
        <div
          style={{
            textAlign: 'center',
            paddingTop: '1rem',
            borderTop: '1px solid #EAECF0',
          }}
        >
          <span style={{ fontSize: '0.875rem', color: '#475467' }}>
            Already have an account?{' '}
          </span>
          <Link
            to={loginDestination}
            style={{
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#155EEF',
              textDecoration: 'none',
            }}
          >
            Sign In
          </Link>
        </div>
      </div>
    </div>
  )
}
