register_jsx = '''import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'

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

export default function RegisterPage() {
  const { sendOtp, registerWithOtp, getOAuthConfig, sendGoogleOtp, googleRegister } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const redirectUrl = searchParams.get('redirect')

  // Auth Method Selection: null (main screen with 2 buttons), 'google', 'mobile'
  const [method, setMethod] = useState(null)
  const [oauthConfig, setOauthConfig] = useState({ google_client_id: '', is_google_configured: false, is_sms_development: false })

  // Common Fields
  const [fullName, setFullName] = useState('')
  const [error, setError] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  // Google OTP Flow
  const [googleIdToken, setGoogleIdToken] = useState('')
  const [googleEmailMasked, setGoogleEmailMasked] = useState('')
  const [googleOtp, setGoogleOtp] = useState('')
  const [googleOtpSent, setGoogleOtpSent] = useState(false)
  const [googleSending, setGoogleSending] = useState(false)
  const [googleVerifying, setGoogleVerifying] = useState(false)
  const [googleCooldown, setGoogleCooldown] = useState(0)
  const [devGoogleEmail, setDevGoogleEmail] = useState('')

  // Mobile SMS OTP Flow
  const [mobileNumber, setMobileNumber] = useState('')
  const [mobileOtp, setMobileOtp] = useState('')
  const [mobileOtpSent, setMobileOtpSent] = useState(false)
  const [mobileSending, setMobileSending] = useState(false)
  const [mobileVerifying, setMobileVerifying] = useState(false)
  const [mobileCooldown, setMobileCooldown] = useState(0)
  const [mobileMasked, setMobileMasked] = useState('')
  const [mobileDevInfo, setMobileDevInfo] = useState(null)

  // Load OAuth Config
  useEffect(() => {
    if (getOAuthConfig) {
      getOAuthConfig()
        .then(cfg => {
          if (cfg) setOauthConfig(cfg)
        })
        .catch(() => {})
    }
  }, [getOAuthConfig])

  // Cooldown countdowns
  useEffect(() => {
    if (googleCooldown <= 0) return
    const timer = setInterval(() => setGoogleCooldown(c => Math.max(0, c - 1)), 1000)
    return () => clearInterval(timer)
  }, [googleCooldown])

  useEffect(() => {
    if (mobileCooldown <= 0) return
    const timer = setInterval(() => setMobileCooldown(c => Math.max(0, c - 1)), 1000)
    return () => clearInterval(timer)
  }, [mobileCooldown])

  // Reset to method chooser
  function handleResetState() {
    setMethod(null)
    setFullName('')
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
    setSuccessMsg('')
  }

  // Google Handlers
  async function handleGoogleCredentialResponse(idToken) {
    if (!idToken) return
    if (!fullName.trim() || fullName.trim().length < 2) {
      setError('Please enter your full name as per Aadhaar (minimum 2 characters).')
      return
    }
    setGoogleIdToken(idToken)
    setGoogleSending(true)
    setError('')
    setSuccessMsg('')
    try {
      const res = await sendGoogleOtp(idToken, 'register', fullName.trim())
      setGoogleEmailMasked(res.masked_email || 'your Google email')
      setGoogleOtpSent(true)
      setGoogleCooldown(res.resend_cooldown_seconds || 60)
      setSuccessMsg(`Verification code sent to ${res.masked_email || 'your Google email'}.`)
    } catch (err) {
      setError(err.message || 'Failed to dispatch email verification code.')
    } finally {
      setGoogleSending(false)
    }
  }

  async function handleDevGoogleSendOtp(e) {
    if (e) e.preventDefault()
    if (!fullName.trim() || fullName.trim().length < 2) {
      setError('Please enter your full name as per Aadhaar (minimum 2 characters).')
      return
    }
    const email = devGoogleEmail.trim().toLowerCase()
    if (!email || !email.includes('@')) {
      setError('Please enter a valid Google email address.')
      return
    }
    const simulatedToken = `dev_test_token:${email}:${fullName.trim()}`
    await handleGoogleCredentialResponse(simulatedToken)
  }

  async function handleVerifyGoogleRegister(e) {
    if (e) e.preventDefault()
    const trimmed = googleOtp.trim()
    if (trimmed.length !== 6 || !/^\\d{6}$/.test(trimmed)) {
      setError('Please enter the complete 6-digit verification code.')
      return
    }
    setGoogleVerifying(true)
    setError('')
    try {
      const user = await googleRegister(googleIdToken, trimmed, fullName.trim())
      setSuccessMsg(`Welcome, ${user.full_name || fullName}! Your account has been registered. Redirecting...`)
      setTimeout(() => {
        if (redirectUrl) navigate(redirectUrl, { replace: true })
        else navigate('/parent', { replace: true })
      }, 700)
    } catch (err) {
      setError(err.message || 'OTP verification failed. Please try again.')
    } finally {
      setGoogleVerifying(false)
    }
  }

  // Mobile Handlers
  async function handleSendMobileOtp(e) {
    if (e) e.preventDefault()
    if (!fullName.trim() || fullName.trim().length < 2) {
      setError('Please enter your full name as per Aadhaar (minimum 2 characters).')
      return
    }
    let digits = mobileNumber.replace(/\\D/g, '')
    if (digits.length === 12 && digits.startsWith('91')) digits = digits.slice(2)
    if (digits.length === 11 && digits.startsWith('0')) digits = digits.slice(1)
    if (!/^[6-9]\\d{9}$/.test(digits)) {
      setError('Please enter a valid 10-digit Indian mobile number (e.g. 9876543210).')
      return
    }
    setMobileSending(true)
    setError('')
    setSuccessMsg('')
    try {
      const res = await sendOtp(digits, 'register')
      setMobileOtpSent(true)
      setMobileMasked(res.masked_phone || `+91 ******${digits.slice(-4)}`)
      setMobileCooldown(res.resend_cooldown_seconds || 60)
      if (res.dev_mode && res.dev_otp) {
        setMobileDevInfo(res)
      } else {
        setMobileDevInfo(null)
      }
      setSuccessMsg(res.message || 'SMS OTP dispatched successfully.')
    } catch (err) {
      setError(err.message || 'Failed to dispatch SMS OTP. Mobile number may already be registered.')
    } finally {
      setMobileSending(false)
    }
  }

  async function handleVerifyMobileRegister(e) {
    if (e) e.preventDefault()
    const trimmed = mobileOtp.trim()
    if (trimmed.length !== 6 || !/^\\d{6}$/.test(trimmed)) {
      setError('Please enter the complete 6-digit numeric verification code.')
      return
    }
    let digits = mobileNumber.replace(/\\D/g, '')
    if (digits.length === 12 && digits.startsWith('91')) digits = digits.slice(2)
    if (digits.length === 11 && digits.startsWith('0')) digits = digits.slice(1)
    setMobileVerifying(true)
    setError('')
    try {
      const user = await registerWithOtp({ phone: digits, otp: trimmed, full_name: fullName.trim() })
      setSuccessMsg(`Welcome, ${user.full_name || fullName}! Your account has been registered. Redirecting...`)
      setTimeout(() => {
        if (redirectUrl) navigate(redirectUrl, { replace: true })
        else navigate('/parent', { replace: true })
      }, 700)
    } catch (err) {
      setError(err.message || 'OTP verification failed. Please try again.')
    } finally {
      setMobileVerifying(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '85vh',
        background: '#F8F9FC',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1rem',
      }}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '480px',
          padding: '2.25rem 2rem',
          borderRadius: '12px',
          boxShadow: '0 8px 24px rgba(16, 43, 70, 0.08)',
          background: '#ffffff',
          border: '1px solid #E2E8F0',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <h1 style={{ fontSize: '1.75rem', color: '#102B46', fontWeight: 800, margin: '0 0 0.5rem 0' }}>
            Register
          </h1>
          <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0, lineHeight: 1.5 }}>
            Create a NagrikSetu citizen account using your Google email or mobile number.
          </p>
        </div>

        {/* Feedback Alerts */}
        {error && (
          <Alert type="error" title="Notice" className="mb-4">
            {error}
          </Alert>
        )}
        {successMsg && (
          <Alert type="success" title="Success" className="mb-4">
            {successMsg}
          </Alert>
        )}

        {/* Top Back Button when a method is active */}
        {method && (
          <div style={{ marginBottom: '1.25rem' }}>
            <button
              type="button"
              onClick={handleResetState}
              style={{
                background: 'none',
                border: 'none',
                color: '#155EEF',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: 0
              }}
            >
              <span>←</span> Choose another registration method
            </button>
          </div>
        )}

        {/* ====================================================== */}
        {/* VIEW 1: TWO REGISTRATION BUTTONS (GOOGLE & MOBILE)     */}
        {/* ====================================================== */}
        {!method && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {/* Method 1: Continue with Google */}
            <button
              type="button"
              onClick={() => {
                setError('')
                setSuccessMsg('')
                setMethod('google')
              }}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                padding: '0.875rem 1.25rem',
                backgroundColor: '#ffffff',
                border: '1.5px solid #d0d5dd',
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: 600,
                color: '#1f2937',
                cursor: 'pointer',
                boxShadow: '0 1px 2px rgba(16, 24, 40, 0.05)',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#f9fafb'; e.currentTarget.style.borderColor = '#98a2b3' }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#ffffff'; e.currentTarget.style.borderColor = '#d0d5dd' }}
            >
              <GoogleIcon />
              <span>Continue with Google</span>
            </button>

            {/* Horizontal OR Divider */}
            <div style={{ display: 'flex', alignItems: 'center', margin: '0.5rem 0' }}>
              <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />
              <span style={{ padding: '0 0.85rem', fontSize: '0.8rem', fontWeight: 700, color: '#667085', letterSpacing: '0.05em' }}>
                OR
              </span>
              <div style={{ flex: 1, height: '1px', backgroundColor: '#e4e7ec' }} />
            </div>

            {/* Method 2: Continue with Mobile Number */}
            <button
              type="button"
              onClick={() => {
                setError('')
                setSuccessMsg('')
                setMethod('mobile')
              }}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                padding: '0.875rem 1.25rem',
                backgroundColor: '#ffffff',
                border: '1.5px solid #d0d5dd',
                borderRadius: '8px',
                fontSize: '0.95rem',
                fontWeight: 600,
                color: '#1f2937',
                cursor: 'pointer',
                boxShadow: '0 1px 2px rgba(16, 24, 40, 0.05)',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#f9fafb'; e.currentTarget.style.borderColor = '#98a2b3' }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#ffffff'; e.currentTarget.style.borderColor = '#d0d5dd' }}
            >
              <span style={{ fontSize: '1.2rem' }}>📱</span>
              <span>Continue with Mobile Number</span>
            </button>
          </div>
        )}

        {/* ====================================================== */}
        {/* VIEW 2: GOOGLE REGISTRATION (NAME + GOOGLE + OTP)      */}
        {/* ====================================================== */}
        {method === 'google' && (
          <div>
            {/* Step 1: Input Name & Select Google Account */}
            {!googleOtpSent ? (
              <div>
                <div style={{ marginBottom: '1.15rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
                    Full Name (as per Aadhaar) <span style={{ color: '#D92D20' }}>*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Enter full name as per Aadhaar"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.65rem 0.85rem',
                      border: '1px solid #CBD5E1',
                      borderRadius: '8px',
                      fontSize: '0.925rem',
                      color: '#102B46',
                      boxSizing: 'border-box'
                    }}
                  />
                  <small style={{ color: '#64748B', fontSize: '0.75rem', marginTop: '0.3rem', display: 'block' }}>
                    Official name used for student admissions and guardian verification.
                  </small>
                </div>

                {oauthConfig.is_google_configured ? (
                  <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                    <div style={{ fontSize: '0.875rem', color: '#475467', marginBottom: '1rem' }}>
                      Click below to choose your Google account:
                    </div>
                    <div id="googleRegisterBtn" style={{ display: 'flex', justifyContent: 'center' }}></div>
                  </div>
                ) : (
                  <div style={{
                    background: '#FFFBEB',
                    border: '1px solid #FCD34D',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1rem',
                    color: '#92400E',
                    fontSize: '0.825rem',
                    lineHeight: 1.45
                  }}>
                    <div style={{ fontWeight: 800, fontSize: '0.875rem', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#B45309' }}>
                      <span>ℹ️</span>
                      <span>GOOGLE IDENTITY SERVICES NOTICE</span>
                    </div>
                    <p style={{ margin: '0 0 0.5rem 0' }}>
                      Google OAuth client ID is not configured. Add <code>GOOGLE_CLIENT_ID</code> in <code>backend/.env</code> and configure <code>http://localhost:5173</code> in Google Cloud Console.
                    </p>
                    <div style={{
                      background: '#ffffff',
                      border: '1px solid #FDE68A',
                      borderRadius: '6px',
                      padding: '0.75rem',
                      marginTop: '0.75rem'
                    }}>
                      <div style={{ fontWeight: 700, color: '#102B46', marginBottom: '0.4rem' }}>
                        Test Google Email Registration (SMTP OTP Delivery):
                      </div>
                      <form onSubmit={handleDevGoogleSendOtp}>
                        <input
                          type="email"
                          required
                          placeholder="e.g. yourname@gmail.com"
                          value={devGoogleEmail}
                          onChange={(e) => setDevGoogleEmail(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '0.55rem 0.75rem',
                            border: '1px solid #D1D5DB',
                            borderRadius: '6px',
                            fontSize: '0.875rem',
                            marginBottom: '0.6rem',
                            boxSizing: 'border-box'
                          }}
                        />
                        <button
                          type="submit"
                          disabled={googleSending || !fullName.trim() || !devGoogleEmail.trim()}
                          className="btn btn--primary btn--full"
                          style={{
                            background: '#155EEF',
                            fontWeight: 700,
                            fontSize: '0.875rem',
                            padding: '0.55rem',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '0.5rem'
                          }}
                        >
                          {googleSending ? <LoadingSpinner size="sm" /> : 'Send OTP to Google Email →'}
                        </button>
                      </form>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              /* Step 2: Google Email OTP Verification */
              <form onSubmit={handleVerifyGoogleRegister}>
                <div style={{
                  marginBottom: '1.25rem',
                  padding: '1.15rem',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.825rem', color: '#475467' }}>
                      Verification code sent to: <strong style={{ color: '#102B46' }}>{googleEmailMasked}</strong>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setGoogleOtpSent(false)
                        setGoogleOtp('')
                        setError('')
                        setSuccessMsg('')
                      }}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#155eef',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        textDecoration: 'underline'
                      }}
                    >
                      Change
                    </button>
                  </div>

                  <div style={{ marginBottom: '0.75rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.4rem' }}>
                      Enter 6-Digit Email OTP <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      pattern="\\d{6}"
                      placeholder="• • • • • •"
                      value={googleOtp}
                      onChange={(e) => setGoogleOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        textAlign: 'center',
                        letterSpacing: '0.35em',
                        backgroundColor: '#ffffff',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                    <span style={{ color: '#667085' }}>Valid for 5 minutes</span>
                    {googleCooldown > 0 ? (
                      <span style={{ color: '#98a2b3', fontWeight: 600 }}>
                        Resend in {googleCooldown}s
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={() => handleGoogleCredentialResponse(googleIdToken)}
                        disabled={googleSending}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#155eef',
                          fontWeight: 700,
                          cursor: 'pointer',
                          padding: 0
                        }}
                      >
                        Resend OTP
                      </button>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={googleVerifying || googleOtp.trim().length !== 6}
                  className="btn btn--primary btn--full btn--lg"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem',
                    background: '#12B76A',
                    fontWeight: 700
                  }}
                >
                  {googleVerifying ? <LoadingSpinner size="sm" /> : '✓ Verify OTP and Complete Registration →'}
                </button>
              </form>
            )}
          </div>
        )}

        {/* ====================================================== */}
        {/* VIEW 3: MOBILE NUMBER REGISTRATION (NAME + SMS + OTP)   */}
        {/* ====================================================== */}
        {method === 'mobile' && (
          <div>
            {!mobileOtpSent ? (
              <form onSubmit={handleSendMobileOtp}>
                <div style={{ marginBottom: '1.15rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
                    Full Name (as per Aadhaar) <span style={{ color: '#D92D20' }}>*</span>
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="Enter full name as per Aadhaar"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.65rem 0.85rem',
                      border: '1px solid #CBD5E1',
                      borderRadius: '8px',
                      fontSize: '0.925rem',
                      color: '#102B46',
                      boxSizing: 'border-box'
                    }}
                  />
                  <small style={{ color: '#64748B', fontSize: '0.75rem', marginTop: '0.3rem', display: 'block' }}>
                    Official name used for student admissions and guardian verification.
                  </small>
                </div>

                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
                    Mobile Number <span style={{ color: '#D92D20' }}>*</span>
                  </label>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      padding: '0.625rem 0.75rem',
                      background: '#F1F5F9',
                      border: '1px solid #D0D5DD',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.875rem',
                      color: '#344054'
                    }}>
                      +91
                    </span>
                    <input
                      type="tel"
                      required
                      maxLength={10}
                      placeholder="10-digit mobile number"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value.replace(/\\D/g, '').slice(0, 10))}
                      style={{
                        flex: 1,
                        padding: '0.625rem 0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '0.9375rem',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>
                  <small style={{ color: '#64748B', fontSize: '0.75rem', marginTop: '0.3rem', display: 'block' }}>
                    We will send a 6-digit verification code to this mobile number.
                  </small>
                </div>

                <button
                  type="submit"
                  disabled={mobileSending || !fullName.trim() || mobileNumber.replace(/\\D/g, '').length !== 10}
                  className="btn btn--primary btn--full btn--lg"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem',
                    background: '#155EEF',
                    fontWeight: 700
                  }}
                >
                  {mobileSending ? <LoadingSpinner size="sm" /> : 'Send SMS OTP →'}
                </button>
              </form>
            ) : (
              /* OTP Verification for Mobile Registration */
              <form onSubmit={handleVerifyMobileRegister}>
                <div style={{
                  marginBottom: '1.25rem',
                  padding: '1.15rem',
                  background: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontSize: '0.825rem', color: '#475467' }}>
                      Code sent to: <strong style={{ color: '#102B46' }}>{mobileMasked}</strong>
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setMobileOtpSent(false)
                        setMobileOtp('')
                        setMobileDevInfo(null)
                        setError('')
                        setSuccessMsg('')
                      }}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#155eef',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        textDecoration: 'underline'
                      }}
                    >
                      Change
                    </button>
                  </div>

                  {/* Development SMS Simulation Notice Banner */}
                  {mobileDevInfo && mobileDevInfo.dev_otp && (
                    <div style={{
                      background: '#FEF08A',
                      border: '1px solid #EAB308',
                      borderRadius: '8px',
                      padding: '0.85rem 1rem',
                      marginBottom: '1rem',
                      color: '#713F12',
                      fontSize: '0.825rem',
                      lineHeight: 1.45,
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
                    }}>
                      <div style={{ fontWeight: 800, fontSize: '0.875rem', marginBottom: '0.3rem', display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#854D0E' }}>
                        <span>⚠️</span>
                        <span>DEVELOPMENT SMS GATEWAY NOTICE</span>
                      </div>
                      <p style={{ margin: '0 0 0.5rem 0' }}>
                        {mobileDevInfo.dev_notice || 'Real SMS delivery is disabled for student project testing. Use the simulated OTP code below to verify your account.'}
                      </p>
                      <div style={{
                        background: 'rgba(255, 255, 255, 0.9)',
                        padding: '0.4rem 0.75rem',
                        borderRadius: '6px',
                        border: '1px dashed #CA8A04',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        fontWeight: 700
                      }}>
                        <span>Development OTP:</span>
                        <span style={{ fontFamily: 'monospace', fontSize: '1.15rem', color: '#B45309', letterSpacing: '0.2em' }}>
                          {mobileDevInfo.dev_otp}
                        </span>
                      </div>
                    </div>
                  )}

                  <div style={{ marginBottom: '0.75rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.4rem' }}>
                      Enter 6-Digit SMS OTP <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <input
                      type="text"
                      required
                      maxLength={6}
                      pattern="\\d{6}"
                      placeholder="• • • • • •"
                      value={mobileOtp}
                      onChange={(e) => setMobileOtp(e.target.value.replace(/\\D/g, '').slice(0, 6))}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        border: '1px solid #d0d5dd',
                        borderRadius: '6px',
                        fontSize: '1.25rem',
                        fontWeight: 700,
                        textAlign: 'center',
                        letterSpacing: '0.35em',
                        backgroundColor: '#ffffff',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem' }}>
                    <span style={{ color: '#667085' }}>Valid for 5 minutes</span>
                    {mobileCooldown > 0 ? (
                      <span style={{ color: '#98a2b3', fontWeight: 600 }}>
                        Resend in {mobileCooldown}s
                      </span>
                    ) : (
                      <button
                        type="button"
                        onClick={handleSendMobileOtp}
                        disabled={mobileSending}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: '#155eef',
                          fontWeight: 700,
                          cursor: 'pointer',
                          padding: 0
                        }}
                      >
                        Resend OTP
                      </button>
                    )}
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={mobileVerifying || mobileOtp.trim().length !== 6}
                  className="btn btn--primary btn--full btn--lg"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem',
                    marginBottom: '1rem',
                    background: '#12B76A',
                    fontWeight: 700
                  }}
                >
                  {mobileVerifying ? <LoadingSpinner size="sm" /> : '✓ Verify OTP and Complete Registration →'}
                </button>
              </form>
            )}
          </div>
        )}

        {/* Footer Navigation */}
        <div style={{ textAlign: 'center', marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid #E2E8F0' }}>
          <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
            Already have a NagrikSetu account?{' '}
            <Link
              to={redirectUrl ? `/login?redirect=${encodeURIComponent(redirectUrl)}` : '/login'}
              style={{ color: '#155EEF', fontWeight: 700, textDecoration: 'none' }}
            >
              Sign In
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
'''

with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\auth\RegisterPage.jsx', 'w', encoding='utf-8') as f:
    f.write(register_jsx)

print('RegisterPage.jsx updated successfully!')
