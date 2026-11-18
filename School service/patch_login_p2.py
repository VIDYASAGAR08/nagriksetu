import re

login_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\LoginPage.jsx"

with open(login_path, "r", encoding="utf-8") as f:
    content = f.read()

# Locate the citizen section
parent_section_start = "{selectedCategory === 'parent' && ("
admin_section_start = "{/* ---------------------------------------------------- */}\n            {/* CATEGORY: ADMIN & STAFF                              */}"

assert parent_section_start in content, "parent_section_start not found"
assert admin_section_start in content, "admin_section_start not found"

# Find positions
start_idx = content.find(parent_section_start)
end_idx = content.find(admin_section_start)

# Define GoogleIcon component at the top of file or right before LoginPage
google_icon_def = """// Google 'G' Icon Component
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
"""

if "function GoogleIcon()" not in content:
    content = google_icon_def + "\n" + content

# Handler functions to insert before return statement
handlers_code = """
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

# Insert handlers before the return statement of LoginPage
return_stmt = "  return ("
assert return_stmt in content, "return statement not found"
content = content.replace(return_stmt, handlers_code + "\n" + return_stmt, 1)

# Now rebuild the Citizen section inside JSX
new_parent_jsx = """{selectedCategory === 'parent' && (
              <div>
                {/* Top Back to Methods Button (when inside a method) */}
                {citizenMethod && (
                  <div style={{ marginBottom: '1.25rem' }}>
                    <button
                      type="button"
                      onClick={handleResetCitizenState}
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
                      <span>←</span> Choose another sign-in method
                    </button>
                  </div>
                )}

                {/* ==================================================== */}
                {/* VIEW 1: TWO MAIN METHOD SELECTION BUTTONS            */}
                {/* ==================================================== */}
                {!citizenMethod && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {/* Method 1: Continue with Google */}
                    <button
                      type="button"
                      onClick={() => {
                        setError('')
                        setSuccess('')
                        setCitizenMethod('google')
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
                        setSuccess('')
                        setCitizenMethod('mobile')
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

                {/* ==================================================== */}
                {/* VIEW 2: GOOGLE EMAIL OTP FLOW                        */}
                {/* ==================================================== */}
                {citizenMethod === 'google' && (
                  <div>
                    {!googleOtpSent ? (
                      <div>
                        {/* If Google OAuth is configured, show GIS prompt button */}
                        {oauthConfig.is_google_configured ? (
                          <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                            <div style={{ fontSize: '0.875rem', color: '#475467', marginBottom: '1rem' }}>
                              Select your Google account. We will dispatch a 6-digit verification code to your verified Gmail address.
                            </div>
                            <div id="googleSignInBtn" style={{ display: 'flex', justifyContent: 'center' }}></div>
                          </div>
                        ) : (
                          /* If Google OAuth Client ID is unconfigured, display clear development notice */
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
                              Google OAuth client ID is not configured. Add <code>GOOGLE_CLIENT_ID</code> in <code>backend/.env</code> and configure <code>http://localhost:5173</code> in Google Cloud Console authorized origins.
                            </p>
                            <div style={{
                              background: '#ffffff',
                              border: '1px solid #FDE68A',
                              borderRadius: '6px',
                              padding: '0.75rem',
                              marginTop: '0.75rem'
                            }}>
                              <div style={{ fontWeight: 700, color: '#102B46', marginBottom: '0.4rem' }}>
                                Test Google Email Sign-In (SMTP OTP Delivery):
                              </div>
                              <form onSubmit={handleDevGoogleSendOtp}>
                                <input
                                  type="email"
                                  required
                                  placeholder="e.g. chandhan123@gmail.com"
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
                                  disabled={googleSending || !devGoogleEmail.trim()}
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
                      /* OTP Entry Form for Google Email */
                      <form onSubmit={handleVerifyGoogleOtp}>
                        <div style={{
                          marginBottom: '1.25rem',
                          padding: '1.15rem',
                          background: '#f8fafc',
                          borderRadius: '8px',
                          border: '1px solid #e2e8f0'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.825rem', color: '#475467' }}>
                              Verification code sent to Google email: <strong style={{ color: '#102B46' }}>{googleEmailMasked}</strong>
                            </span>
                            <button
                              type="button"
                              onClick={() => {
                                setGoogleOtpSent(false)
                                setGoogleOtp('')
                                setError('')
                                setSuccess('')
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
                          {googleVerifying ? <LoadingSpinner size="sm" /> : '✓ Verify OTP & Sign In'}
                        </button>
                      </form>
                    )}
                  </div>
                )}

                {/* ==================================================== */}
                {/* VIEW 3: MOBILE NUMBER SMS OTP FLOW                   */}
                {/* ==================================================== */}
                {citizenMethod === 'mobile' && (
                  <div>
                    {!mobileOtpSent ? (
                      <form onSubmit={handleSendMobileOtp}>
                        <div style={{ marginBottom: '1.25rem' }}>
                          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
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
                          <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.3rem' }}>
                            Enter your registered 10-digit Indian mobile number.
                          </div>
                        </div>

                        <button
                          type="submit"
                          disabled={mobileSending || mobileNumber.replace(/\\D/g, '').length !== 10}
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
                      /* OTP Entry Form for Mobile */
                      <form onSubmit={handleVerifyMobileOtp}>
                        <div style={{
                          marginBottom: '1.25rem',
                          padding: '1.15rem',
                          background: '#f8fafc',
                          borderRadius: '8px',
                          border: '1px solid #e2e8f0'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.825rem', color: '#475467' }}>
                              OTP sent to: <strong style={{ color: '#102B46' }}>{mobileMasked}</strong>
                            </span>
                            <button
                              type="button"
                              onClick={() => {
                                setMobileOtpSent(false)
                                setMobileOtp('')
                                setMobileDevInfo(null)
                                setError('')
                                setSuccess('')
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
                          {mobileVerifying ? <LoadingSpinner size="sm" /> : '✓ Verify OTP & Sign In'}
                        </button>
                      </form>
                    )}
                  </div>
                )}

                {/* Footer Link */}
                <div style={{ borderTop: '1px solid #E4E7EC', paddingTop: '1.25rem', marginTop: '1.5rem', textAlign: 'center' }}>
                  <span style={{ fontSize: '0.875rem', color: '#475467' }}>
                    First time visiting NagrikSetu?{' '}
                  </span>
                  <Link
                    to={searchParams.get('redirect') ? `/register?redirect=${encodeURIComponent(searchParams.get('redirect'))}` : '/register'}
                    style={{ color: '#155EEF', fontWeight: 700, textDecoration: 'none' }}
                  >
                    Register as a New Citizen →
                  </Link>
                </div>
              </div>
            )}"""

# Replace the parent section
# Let's locate exactly the old parent section in content
old_parent_full = content[content.find(parent_section_start):content.find(admin_section_start)]
content = content.replace(old_parent_full, new_parent_jsx + "\n\n            ")

with open(login_path, "w", encoding="utf-8") as f:
    f.write(content)

print("LoginPage.jsx completely updated!")
