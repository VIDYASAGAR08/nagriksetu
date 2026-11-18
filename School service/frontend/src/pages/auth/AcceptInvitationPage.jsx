import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate, Link } from 'react-router-dom'
import { apiGet, apiPost } from '../../utils/api.js'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'

export default function AcceptInvitationPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  const schoolId = searchParams.get('school_id') || searchParams.get('institution_id')
  const navigate = useNavigate()

  // State
  const [isVerified, setIsVerified] = useState(false)
  const [sessionToken, setSessionToken] = useState(null)
  const [invitationInfo, setInvitationInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Verification step (when entering via institution card without token)
  const [institutionMeta, setInstitutionMeta] = useState(null)
  const [verifyEmail, setVerifyEmail] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [verifyError, setVerifyError] = useState('')

  // Password setup step
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [activatedSuccess, setActivatedSuccess] = useState(false)

  // 1. Initial check: If token is provided in URL, verify token directly
  useEffect(() => {
    async function verifyWithToken() {
      if (token) {
        try {
          setLoading(true)
          setError('')
          const info = await apiGet(`/auth/verify-invitation?token=${encodeURIComponent(token)}`)
          setInvitationInfo(info)
          setIsVerified(true)
        } catch (err) {
          setError(err.message || 'Invitation token is invalid, expired, or has already been accepted.')
        } finally {
          setLoading(false)
        }
      } else if (schoolId) {
        // Fetch institution metadata for context
        try {
          const statusRes = await apiGet(`/auth/institution/${schoolId}/admin-status`)
          setInstitutionMeta(statusRes)
        } catch {
          // If status fetch fails, continue with fallback
        }
      }
    }
    verifyWithToken()
  }, [token, schoolId])

  // 2. Handle Identity Verification (Email Match against Institution Invitation)
  async function handleVerifyIdentity(e) {
    e.preventDefault()
    if (!verifyEmail.trim()) {
      setVerifyError('Please enter your official administrator email address.')
      return
    }

    try {
      setVerifying(true)
      setVerifyError('')
      const res = await apiPost('/auth/invitations/verify-identity', {
        institution_id: schoolId,
        email: verifyEmail.trim()
      })

      setSessionToken(res.session_token)
      setInvitationInfo(res.administrator)
      setIsVerified(true)
    } catch (err) {
      setVerifyError(err.message || 'Identity verification failed. The provided email does not match the appointed administrator.')
    } finally {
      setVerifying(false)
    }
  }

  // 3. Handle Password Setup and Final Account Activation
  async function handlePasswordSubmit(e) {
    e.preventDefault()
    if (!password || !confirmPassword) {
      setSubmitError('Please enter and confirm your password.')
      return
    }

    if (password.length < 8) {
      setSubmitError('Password must contain at least 8 characters.')
      return
    }

    if (password !== confirmPassword) {
      setSubmitError('Passwords do not match. Please re-enter.')
      return
    }

    try {
      setSubmitting(true)
      setSubmitError('')

      const payload = {
        password: password,
        ...(sessionToken ? { session_token: sessionToken } : { token: token })
      }

      const res = await apiPost('/auth/accept-invitation', payload)
      setActivatedSuccess(true)
    } catch (err) {
      setSubmitError(err.message || 'Failed to activate administrator account. The session may have expired.')
    } finally {
      setSubmitting(false)
    }
  }

  // View: Loading Token Verification
  if (loading) {
    return (
      <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F5F7FA', padding: '2rem 1rem' }}>
        <div style={{ textAlign: 'center' }}>
          <LoadingSpinner size="lg" />
          <p style={{ marginTop: '1rem', color: '#475467', fontWeight: 600 }}>Verifying cryptographic invitation...</p>
        </div>
      </div>
    )
  }

  // View: Direct Token Error
  if (token && error) {
    return (
      <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F5F7FA', padding: '2rem 1rem' }}>
        <div style={{ maxWidth: '480px', width: '100%', background: '#FFFFFF', padding: '2rem', borderRadius: '12px', border: '1px solid #E2E8F0', textAlign: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>⚠️</div>
          <Alert type="error" title="Invitation Verification Failed" style={{ marginBottom: '1.25rem' }}>
            {error}
          </Alert>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
            <Link to="/select-institution" className="btn btn--secondary" style={{ textDecoration: 'none' }}>
              ← Return to Institution Selection
            </Link>
          </div>
        </div>
      </div>
    )
  }

  // View: Success Screen after Account Activation
  if (activatedSuccess) {
    const targetInstId = invitationInfo?.institution_id || schoolId
    return (
      <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F5F7FA', padding: '2rem 1rem' }}>
        <div style={{ maxWidth: '520px', width: '100%', background: '#FFFFFF', padding: '2.5rem', borderRadius: '12px', border: '1px solid #E2E8F0', textAlign: 'center', boxShadow: '0 8px 24px rgba(16,43,70,0.08)' }}>
          <div style={{ width: '64px', height: '64px', borderRadius: '50%', background: '#ECFDF3', color: '#027A48', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', margin: '0 auto 1.25rem auto' }}>
            ✓
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
            Account Successfully Activated!
          </h2>
          <p style={{ color: '#475467', fontSize: '0.95rem', margin: '0 0 1.5rem 0', lineHeight: 1.5 }}>
            Your administrator account for <strong>{invitationInfo?.school_name || targetInstId}</strong> is now fully active with your configured password.
          </p>

          <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', marginBottom: '1.75rem', textAlign: 'left', fontSize: '0.85rem' }}>
            <div style={{ marginBottom: '0.35rem', color: '#344054' }}>
              <strong>Administrator:</strong> {invitationInfo?.full_name}
            </div>
            <div style={{ marginBottom: '0.35rem', color: '#344054' }}>
              <strong>Official Email:</strong> {invitationInfo?.email}
            </div>
            <div style={{ color: '#344054' }}>
              <strong>Assigned Role:</strong> Academic Administrator
            </div>
          </div>

          <button
            onClick={() => navigate(`/select-institution?school_id=${encodeURIComponent(targetInstId)}`)}
            style={{
              width: '100%',
              background: '#155EEF',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '8px',
              padding: '0.75rem 1.25rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.5rem',
              boxShadow: '0 2px 6px rgba(21,94,239,0.25)'
            }}
          >
            Continue to Administrator Login →
          </button>
        </div>
      </div>
    )
  }

  // View: No Institution & No Token
  if (!token && !schoolId) {
    return (
      <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#F5F7FA', padding: '2rem 1rem' }}>
        <div style={{ maxWidth: '480px', width: '100%', background: '#FFFFFF', padding: '2rem', borderRadius: '12px', border: '1px solid #E2E8F0', textAlign: 'center' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🏛️</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#102B46' }}>Institution Required</h3>
          <p style={{ color: '#667085', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Please select your institution from the official directory to proceed with administrator account setup.
          </p>
          <Link to="/select-institution" className="btn btn--primary" style={{ textDecoration: 'none' }}>
            Browse Institutions Directory →
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="accept-invitation-page" style={{ minHeight: '85vh', background: '#F5F7FA', padding: '2rem 1rem 5rem 1rem' }}>
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Select Institution', href: '/select-institution' },
        { label: 'Administrator Account Setup' }
      ]} />

      <div style={{ maxWidth: '580px', margin: '1.5rem auto 0 auto' }}>
        {/* Back Link */}
        <Link
          to="/select-institution"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.35rem',
            color: '#155EEF',
            fontSize: '0.875rem',
            fontWeight: 600,
            textDecoration: 'none',
            marginBottom: '1rem'
          }}
        >
          ← Return to Institution Selection
        </Link>

        {/* Institution Context Header */}
        <div style={{
          background: '#102B46',
          color: '#FFFFFF',
          borderRadius: '12px',
          padding: '1.5rem',
          marginBottom: '1.5rem',
          boxShadow: '0 4px 12px rgba(16,43,70,0.12)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              background: '#EFF4FF',
              color: '#155EEF',
              padding: '0.2rem 0.5rem',
              borderRadius: '4px',
              fontFamily: 'monospace'
            }}>
              {schoolId || invitationInfo?.institution_id}
            </span>

            <span style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              background: isVerified ? '#027A48' : '#026AA2',
              color: '#FFFFFF',
              padding: '0.2rem 0.55rem',
              borderRadius: '4px'
            }}>
              {isVerified ? '● Identity Verified' : '● Invitation Pending'}
            </span>
          </div>

          <h1 style={{ fontSize: '1.45rem', fontWeight: 800, margin: '0 0 0.35rem 0', color: '#FFFFFF' }}>
            {invitationInfo?.school_name || institutionMeta?.institution_name || `Institution ${schoolId}`}
          </h1>
          <p style={{ color: '#D0D5DD', fontSize: '0.85rem', margin: 0 }}>
            Official Academic Administrator Onboarding
          </p>
        </div>

        {/* =================================================================
           STAGE 1: IDENTITY VERIFICATION (When accessed without token)
           ================================================================= */}
        {!isVerified ? (
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #D0D5DD',
            borderRadius: '12px',
            padding: '2rem',
            boxShadow: '0 4px 10px rgba(0,0,0,0.06)'
          }}>
            <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
              <div style={{ display: 'inline-block', background: '#F0F9FF', color: '#026AA2', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
                Step 1 of 2: Identity Verification
              </div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                Verify Appointed Administrator
              </h2>
              <p style={{ color: '#667085', fontSize: '0.875rem', margin: 0, lineHeight: 1.5 }}>
                To establish that you are the designated invitee appointed by the Platform Administration, please enter the official email address specified in your appointment.
              </p>
            </div>

            {/* Strict Access Control Notice */}
            <div style={{
              background: '#F8F9FA',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '0.85rem 1rem',
              marginBottom: '1.5rem',
              fontSize: '0.8rem',
              color: '#475467',
              lineHeight: 1.45
            }}>
              🔒 <strong>Multi-Tenant Access Control:</strong> Administrative desk access is restricted strictly to verified institutional appointees. Unauthorized claim attempts are prohibited and logged in the state audit ledger.
            </div>

            {verifyError && (
              <Alert type="error" title="Verification Failed" style={{ marginBottom: '1.25rem' }}>
                {verifyError}
              </Alert>
            )}

            <form onSubmit={handleVerifyIdentity}>
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.4rem' }}>
                  Invited Administrator Official Email Address *
                </label>
                <input
                  type="email"
                  required
                  placeholder="e.g. academic.head@institution.gov"
                  value={verifyEmail}
                  onChange={(e) => setVerifyEmail(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.9rem',
                    border: '1px solid #D0D5DD',
                    borderRadius: '8px',
                    fontSize: '0.95rem',
                    boxSizing: 'border-box'
                  }}
                />
                <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.35rem' }}>
                  Enter the exact email address registered by the Platform Admin during invitation dispatch.
                </div>
              </div>

              <button
                type="submit"
                disabled={verifying}
                style={{
                  width: '100%',
                  background: '#026AA2',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.75rem 1rem',
                  fontSize: '0.95rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 2px 6px rgba(2,106,162,0.25)'
                }}
              >
                {verifying ? <LoadingSpinner size="sm" /> : 'Verify Identity & Unlock Setup →'}
              </button>
            </form>
          </div>
        ) : (
          /* =================================================================
             STAGE 2: PREFILLED ACCOUNT SETUP FORM (Name, Email, Role Non-Editable)
             ================================================================= */
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #D0D5DD',
            borderRadius: '12px',
            padding: '2rem',
            boxShadow: '0 4px 10px rgba(0,0,0,0.06)'
          }}>
            <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
              <div style={{ display: 'inline-block', background: '#ECFDF3', color: '#027A48', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
                Step 2 of 2: Credential Configuration
              </div>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                Institution Administrator Account Setup
              </h2>
              <p style={{ color: '#667085', fontSize: '0.875rem', margin: 0 }}>
                Configure your secure password to activate administrative desk access.
              </p>
            </div>

            {submitError && (
              <Alert type="error" title="Setup Error" style={{ marginBottom: '1.25rem' }}>
                {submitError}
              </Alert>
            )}

            {/* Read-Only Prefilled Appointee Identity Box */}
            <div style={{
              background: '#F8F9FA',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              padding: '1.25rem',
              marginBottom: '1.5rem'
            }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748B', textTransform: 'uppercase', marginBottom: '0.75rem' }}>
                🔒 Official Appointment Details (Verified & Locked)
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>
                    ADMINISTRATOR FULL NAME
                  </label>
                  <input
                    type="text"
                    readOnly
                    disabled
                    value={invitationInfo?.full_name || ''}
                    style={{
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      background: '#F1F5F9',
                      border: '1px solid #CBD5E1',
                      borderRadius: '6px',
                      fontSize: '0.9rem',
                      fontWeight: 600,
                      color: '#0F172A',
                      cursor: 'not-allowed',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>
                    OFFICIAL EMAIL ADDRESS
                  </label>
                  <input
                    type="text"
                    readOnly
                    disabled
                    value={invitationInfo?.email || ''}
                    style={{
                      width: '100%',
                      padding: '0.55rem 0.75rem',
                      background: '#F1F5F9',
                      border: '1px solid #CBD5E1',
                      borderRadius: '6px',
                      fontSize: '0.9rem',
                      fontFamily: 'monospace',
                      color: '#0369A1',
                      cursor: 'not-allowed',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.25rem' }}>
                  <div style={{ fontSize: '0.825rem', color: '#475467' }}>
                    Assigned Institution: <strong style={{ color: '#102B46' }}>{invitationInfo?.school_name}</strong> ({invitationInfo?.institution_id})
                  </div>
                  <div style={{ background: '#EFF4FF', color: '#155EEF', border: '1px solid #B2DDFF', padding: '0.15rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                    Academic Administrator
                  </div>
                </div>
              </div>
            </div>

            {/* Password Configuration Form */}
            <form onSubmit={handlePasswordSubmit}>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                  Create Password (Minimum 8 Characters) *
                </label>
                <PasswordInput
                  required
                  minLength={8}
                  placeholder="Enter strong administrator password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.7rem 0.85rem',
                    border: '1px solid #D0D5DD',
                    borderRadius: '6px',
                    fontSize: '0.925rem',
                    boxSizing: 'border-box'
                  }}
                />
                <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.25rem' }}>
                  Must be at least 8 characters. Upper/lowercase letters, numbers & symbols recommended.
                </div>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                  Confirm Password *
                </label>
                <PasswordInput
                  required
                  minLength={8}
                  placeholder="Re-enter administrator password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.7rem 0.85rem',
                    border: '1px solid #D0D5DD',
                    borderRadius: '6px',
                    fontSize: '0.925rem',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <button
                type="submit"
                disabled={submitting}
                style={{
                  width: '100%',
                  background: '#155EEF',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.75rem 1rem',
                  fontSize: '0.95rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem',
                  boxShadow: '0 2px 6px rgba(21,94,239,0.25)'
                }}
              >
                {submitting ? <LoadingSpinner size="sm" /> : 'Activate Administrator Account →'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}
