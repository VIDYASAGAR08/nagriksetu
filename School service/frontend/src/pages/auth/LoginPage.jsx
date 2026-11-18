import { useState, useEffect } from 'react'
import { Link, useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import { apiPost } from '../../utils/api.js'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [searchParams, setSearchParams] = useSearchParams()

  // Selected category: null (category selection screen), 'student', 'parent', 'admin'
  const initialCategory = searchParams.get('category')
  const [selectedCategory, setSelectedCategory] = useState(
    ['student', 'parent', 'admin'].includes(initialCategory) ? initialCategory : null
  )

  // Standard Login Form states
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(location.state?.message || '')

  // Student activation tab & fields
  const [studentTab, setStudentTab] = useState('login') // 'login' or 'activate'
  const [studentIdInput, setStudentIdInput] = useState('')
  const [studentNameInput, setStudentNameInput] = useState('')
  const [studentEmailInput, setStudentEmailInput] = useState('')
  const [studentPhoneInput, setStudentPhoneInput] = useState('')
  const [studentPasswordInput, setStudentPasswordInput] = useState('')
  const [studentConfirmPasswordInput, setStudentConfirmPasswordInput] = useState('')
  const [studentActLoading, setStudentActLoading] = useState(false)

  // Student Verified Identity Activation States
  const [studentLookupData, setStudentLookupData] = useState(null)
  const [studentLookupLoading, setStudentLookupLoading] = useState(false)
  const [studentDobInput, setStudentDobInput] = useState('')
  const [studentConfirmedRecord, setStudentConfirmedRecord] = useState(false)

  // Sync category & tab state with URL search param
  useEffect(() => {
    const cat = searchParams.get('category')
    if (['student', 'parent', 'admin'].includes(cat)) {
      setSelectedCategory(cat)
    } else if (!cat) {
      setSelectedCategory(null)
    }
    const tab = searchParams.get('tab')
    if (tab === 'activate') {
      setStudentTab('activate')
    }
    const sid = searchParams.get('student_id')
    if (sid) {
      setStudentIdInput(sid)
      if (searchParams.get('auto_lookup') === 'true') {
        apiPost('/auth/student/lookup', { student_identifier: sid })
          .then(res => {
            setStudentLookupData(res)
            setStudentNameInput(res.official_student_name)
            setStudentConfirmedRecord(true)
          })
          .catch(() => {})
      }
    }
  }, [searchParams])

  function selectCategory(cat) {
    setError('')
    setSuccess('')
    if (cat === 'public') {
      navigate('/schools')
      return
    }
    setSelectedCategory(cat)
    const redirectParam = searchParams.get('redirect')
    const newParams = cat ? { category: cat } : {}
    if (redirectParam) {
      newParams.redirect = redirectParam
    }
    setSearchParams(newParams)
  }

  function handleBackToCategories() {
    setError('')
    setSuccess('')
    setIdentifier('')
    setPassword('')
    setSelectedCategory(null)
    const redirectParam = searchParams.get('redirect')
    setSearchParams(redirectParam ? { redirect: redirectParam } : {})
  }

  // Handle standard login (Citizen/Parent, Student, Admin/Staff)
  async function handleLogin(e) {
    e.preventDefault()
    if (!identifier.trim() || !password) {
      setError('Please provide your registered credentials and password.')
      return
    }

    try {
      setLoading(true)
      setError('')
      const res = await login(identifier.trim(), password)

      if (res.requires_workspace_selection) {
        navigate('/select-workspace', {
          state: {
            temp_token: res.temp_token,
            workspaces: res.workspaces,
          },
        })
        return
      }

      // Role-based redirection
      const redirectUrl = searchParams.get('redirect') || location.state?.redirect
      if (res.role === 'parent' && redirectUrl) {
        navigate(redirectUrl)
        return
      }
      if (res.role === 'student') {
        navigate('/student')
      } else if (res.role === 'parent') {
        navigate('/parent')
      } else if (['school_admin', 'academic_admin', 'institution_admin'].includes(res.role)) {
        navigate('/institution-admin')
      } else if (['school_staff', 'admissions_officer', 'student_records_officer', 'general_staff'].includes(res.role)) {
        navigate('/staff')
      } else if (res.role === 'platform_admin') {
        navigate('/admin')
      } else {
        navigate('/')
      }
    } catch (err) {
      if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
        setError('Unable to connect to NagrikSetu authentication server. Please verify network connectivity and backend service status.')
      } else {
        setError(err.message || 'Login failed. Please check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Handle student account registration / activation
  async function handleStudentActivate(e) {
    e.preventDefault()
    if (!studentLookupData) {
      setError('Please look up and confirm your official enrolled student record first.')
      return
    }

    if (!studentDobInput.trim()) {
      setError('Please provide your official Date of Birth for identity verification.')
      return
    }

    if (!studentConfirmedRecord) {
      setError('Please confirm that the displayed institution record belongs to you.')
      return
    }

    if (studentPasswordInput.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    if (studentPasswordInput !== studentConfirmPasswordInput) {
      setError('Passwords do not match.')
      return
    }

    try {
      setStudentActLoading(true)
      setError('')
      const payload = {
        student_identifier: studentLookupData.permanent_student_id || studentLookupData.student_id || studentIdInput.trim(),
        date_of_birth: studentDobInput.trim(),
        email: studentEmailInput.trim() || null,
        phone: studentPhoneInput.trim() || null,
        password: studentPasswordInput,
        confirm_password: studentConfirmPasswordInput,
      }
      const res = await apiPost('/auth/student/register', payload)
      setSuccess(res.message || `Student account for ${studentLookupData.official_student_name} activated successfully! You can now sign in.`)
      setIdentifier(studentLookupData.permanent_student_id || studentLookupData.student_id || studentIdInput.trim())
      setPassword(studentPasswordInput)
      setStudentLookupData(null)
      setStudentDobInput('')
      setStudentConfirmedRecord(false)
      setStudentTab('login')
    } catch (err) {
      if (err.message && (err.message.includes('Failed to fetch') || err.message.includes('NetworkError'))) {
        setError('Unable to connect to NagrikSetu authentication server. Please verify network connectivity and backend service status.')
      } else {
        setError(err.message || 'Failed to activate student account. Please verify your details.')
      }
    } finally {
      setStudentActLoading(false)
    }
  }

  // Handle Initial Lookup by Student ID / Permanent SATS ID
  async function handleStudentLookup(e) {
    e.preventDefault()
    if (!studentIdInput.trim()) {
      setError('Please enter your Student ID or Permanent SATS ID.')
      return
    }

    try {
      setStudentLookupLoading(true)
      setError('')
      setSuccess('')
      const res = await apiPost('/auth/student/lookup', {
        student_identifier: studentIdInput.trim()
      })
      setStudentLookupData(res)
      setStudentNameInput(res.official_student_name || '')
      setStudentConfirmedRecord(false)
    } catch (err) {
      setStudentLookupData(null)
      setError(err.message || 'No enrolled student record found matching that identifier. Please verify with your school administration.')
    } finally {
      setStudentLookupLoading(false)
    }
  }

  // Demo autofill helpers
  function fillDemoStudent() {
    setIdentifier('SCH01125')
    setPassword('Password@2026!')
    setError('')
  }

  function fillDemoParent() {
    setIdentifier('6361168242')
    setPassword('ValidPassword@123')
    setError('')
  }

  function fillDemoPlatformAdmin() {
    setIdentifier('admin.central@nagriksetu.gov')
    setPassword('Central@NagrikSetu2026!')
    setError('')
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 200px)', padding: '2.5rem 1rem', background: '#F8FAFC' }}>
      <div style={{ maxWidth: selectedCategory ? '480px' : '1100px', margin: '0 auto' }}>

        {/* ========================================================= */}
        {/* VIEW 1: CATEGORY SELECTION SCREEN (when category is null) */}
        {/* ========================================================= */}
        {!selectedCategory && (
          <div>
            {/* Header Banner */}
            <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
              <div style={{
                display: 'inline-block',
                background: '#102B46',
                color: '#ffffff',
                fontWeight: 700,
                padding: '0.35rem 0.85rem',
                borderRadius: '4px',
                fontSize: '0.8125rem',
                letterSpacing: '0.5px',
                marginBottom: '0.75rem'
              }}>
                GOVERNMENT OF KARNATAKA · NAGRIKSETU PORTAL
              </div>
              <h1 style={{ fontSize: '2.1rem', color: '#102B46', fontWeight: 800, margin: '0 0 0.5rem 0' }}>
                Select Your User Category
              </h1>
              <p style={{ color: '#475467', fontSize: '1rem', maxWidth: '640px', margin: '0 auto', lineHeight: 1.5 }}>
                Please choose your user category to proceed to the relevant portal, dashboard, or authentication service.
              </p>
            </div>

            {/* 3 Main Category Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>

              {/* Card 1: Citizen / Parent / Guardian */}
              <div
                className="card category-card"
                style={{
                  background: '#ffffff',
                  border: '2px solid #155EEF',
                  borderRadius: '10px',
                  padding: '1.75rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 4px 10px rgba(21, 94, 239, 0.08)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>
                      👨‍👩‍👧‍👦
                    </div>
                    <span style={{ background: '#eff6ff', color: '#155EEF', fontSize: '0.75rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '12px' }}>
                      Citizen Portal
                    </span>
                  </div>

                  <h2 style={{ fontSize: '1.35rem', color: '#102B46', fontWeight: 700, margin: '0 0 0.5rem 0' }}>
                    Citizen / Parent / Guardian
                  </h2>
                  <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                    Public citizen gateway for school admissions, tracking application status, and managing verified student linkages.
                  </p>

                  <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.5rem 0', fontSize: '0.8125rem', color: '#334155' }}>
                    <li style={{ marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#155EEF', fontWeight: 700 }}>✓</span> Simple Password Authentication (Email / Mobile)
                    </li>
                    <li style={{ marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#155EEF', fontWeight: 700 }}>✓</span> Apply for Admission across Karnataka Institutions
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#155EEF', fontWeight: 700 }}>✓</span> Citizen Dashboard with verified records
                    </li>
                  </ul>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                  <button
                    type="button"
                    onClick={() => selectCategory('parent')}
                    className="btn btn--primary btn--full"
                    style={{ fontWeight: 700, background: '#102B46' }}
                  >
                    Citizen Sign In →
                  </button>
                  <Link
                    to={searchParams.get('redirect') ? `/register?redirect=${encodeURIComponent(searchParams.get('redirect'))}` : '/register'}
                    className="btn btn--secondary btn--full"
                    style={{ fontWeight: 700, borderColor: '#cbd5e1', color: '#102B46', textAlign: 'center', textDecoration: 'none' }}
                  >
                    New Citizen Registration
                  </Link>
                </div>
              </div>

              {/* Card 2: Student */}
              <div
                className="card category-card"
                style={{
                  background: '#ffffff',
                  border: '1px solid #d0d5dd',
                  borderRadius: '10px',
                  padding: '1.75rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.04)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#fef3c7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>
                      🎓
                    </div>
                    <span style={{ background: '#fef3c7', color: '#b45309', fontSize: '0.75rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '12px' }}>
                      Enrolled Students
                    </span>
                  </div>

                  <h2 style={{ fontSize: '1.35rem', color: '#102B46', fontWeight: 700, margin: '0 0 0.5rem 0' }}>
                    Student
                  </h2>
                  <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                    Self-service access for enrolled Karnataka school and PU students to view academic results and attendance.
                  </p>

                  <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.5rem 0', fontSize: '0.8125rem', color: '#334155' }}>
                    <li style={{ marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#b45309', fontWeight: 700 }}>✓</span> Instant Student Account Activation
                    </li>
                    <li style={{ marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#b45309', fontWeight: 700 }}>✓</span> View Academic Results & Attendance
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#b45309', fontWeight: 700 }}>✓</span> Download Verified Certificates
                    </li>
                  </ul>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                  <button
                    type="button"
                    onClick={() => selectCategory('student')}
                    className="btn btn--secondary btn--full"
                    style={{ fontWeight: 700, borderColor: '#d0d5dd', color: '#102B46' }}
                  >
                    Student Portal Sign In →
                  </button>
                  <button
                    type="button"
                    onClick={() => { selectCategory('student'); setStudentTab('activate'); }}
                    className="btn btn--secondary btn--full"
                    style={{ fontWeight: 600, borderColor: '#d0d5dd', color: '#475467' }}
                  >
                    Activate Enrolled Account
                  </button>
                </div>
              </div>

              {/* Card 3: Institution Administrator & Staff */}
              <div
                className="card category-card"
                style={{
                  background: '#ffffff',
                  border: '1px solid #d0d5dd',
                  borderRadius: '10px',
                  padding: '1.75rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.04)',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem' }}>
                      🏛️
                    </div>
                    <span style={{ background: '#f1f5f9', color: '#102B46', fontSize: '0.75rem', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '12px' }}>
                      Authorized Staff
                    </span>
                  </div>

                  <h2 style={{ fontSize: '1.35rem', color: '#102B46', fontWeight: 700, margin: '0 0 0.5rem 0' }}>
                    Institution Admin / Staff
                  </h2>
                  <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                    Secure administration portal for Karnataka school principals, admissions officers, and central platform administrators.
                  </p>

                  <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 1.5rem 0', fontSize: '0.8125rem', color: '#334155' }}>
                    <li style={{ marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#102B46', fontWeight: 700 }}>✓</span> School Admissions Review & Processing
                    </li>
                    <li style={{ marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#102B46', fontWeight: 700 }}>✓</span> Attendance & Academic Audit Log Management
                    </li>
                    <li style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: '#102B46', fontWeight: 700 }}>✓</span> 30 Institution Switchable Workspaces
                    </li>
                  </ul>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                  <button
                    type="button"
                    onClick={() => selectCategory('admin')}
                    className="btn btn--secondary btn--full"
                    style={{ fontWeight: 700, borderColor: '#d0d5dd', color: '#102B46' }}
                  >
                    Administrator Sign In →
                  </button>
                  <Link
                    to="/select-institution"
                    className="btn btn--secondary btn--full"
                    style={{ fontWeight: 600, borderColor: '#d0d5dd', color: '#475467', textAlign: 'center', textDecoration: 'none' }}
                  >
                    Select Institution (Direct Gateway)
                  </Link>
                </div>
              </div>

            </div>
          </div>
        )}

        {/* ========================================================= */}
        {/* VIEW 2: CATEGORY SPECIFIC SIGN IN CARDS                   */}
        {/* ========================================================= */}
        {selectedCategory && (
          <div
            className="card"
            style={{
              padding: '2.25rem',
              border: '1px solid #D0D5DD',
              borderRadius: '10px',
              background: '#FFFFFF',
              boxShadow: '0 4px 12px rgba(16, 43, 70, 0.06)',
            }}
          >
            {/* Top Navigation Row: Back Link & Role Badge */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <button
                type="button"
                onClick={handleBackToCategories}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#155EEF',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  padding: 0,
                }}
              >
                <span>←</span> Back to Categories
              </button>

              <span
                style={{
                  background: selectedCategory === 'student' ? '#eff6ff' : selectedCategory === 'parent' ? '#eff8ff' : '#f1f5f9',
                  color: selectedCategory === 'student' ? '#1d4ed8' : selectedCategory === 'parent' ? '#175cd3' : '#102B46',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  padding: '0.2rem 0.6rem',
                  borderRadius: '12px',
                  textTransform: 'capitalize',
                }}
              >
                {selectedCategory === 'admin' ? 'Administrator Portal' : selectedCategory === 'parent' ? 'Citizen Portal' : 'Student Portal'}
              </span>
            </div>

            {/* Category Header */}
            <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.4rem' }}>
                {selectedCategory === 'student' ? '🎓' : selectedCategory === 'parent' ? '🏛️' : '🏛️'}
              </div>
              <h1 style={{ fontSize: '1.65rem', color: '#102B46', fontWeight: 800, margin: '0 0 0.4rem 0' }}>
                {selectedCategory === 'student' && 'Student Portal Sign In'}
                {selectedCategory === 'parent' && 'Citizen Sign In'}
                {selectedCategory === 'admin' && 'Administrator & Staff Sign In'}
              </h1>
              <p style={{ color: '#475467', fontSize: '0.875rem', margin: 0 }}>
                {selectedCategory === 'student' && 'Sign in using your Student ID, SATS ID, or registered credentials.'}
                {selectedCategory === 'parent' && 'Sign in using your registered Email Address or Mobile Number and password.'}
                {selectedCategory === 'admin' && 'Central Platform Administrators, Institution Admins, and Staff.'}
              </p>
            </div>

            {/* Alerts */}
            {success && <Alert type="success" title="Success" className="mb-4">{success}</Alert>}
            {error && <Alert type="error" title="Notice" className="mb-4">{error}</Alert>}

            {/* ---------------------------------------------------- */}
            {/* CATEGORY 1: CITIZEN / PARENT / GUARDIAN (PASSWORD)   */}
            {/* ---------------------------------------------------- */}
            {selectedCategory === 'parent' && (
              <div>
                <form onSubmit={handleLogin} noValidate>
                  {/* Email Address or Mobile Number */}
                  <div style={{ marginBottom: '1.25rem' }}>
                    <label
                      htmlFor="citizen-identifier"
                      style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}
                    >
                      Email Address or Mobile Number <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <input
                      id="citizen-identifier"
                      name="username"
                      type="text"
                      required
                      autoComplete="username"
                      placeholder="e.g. 9876543210 or yourname@example.com"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        border: '1px solid #D0D5DD',
                        borderRadius: '6px',
                        fontSize: '0.9375rem',
                        color: '#101828',
                        backgroundColor: '#FFFFFF',
                        boxSizing: 'border-box',
                      }}
                    />
                    <span style={{ display: 'block', fontSize: '0.75rem', color: '#667085', marginTop: '0.3rem' }}>
                      Enter either your registered email address or 10-digit mobile number.
                    </span>
                  </div>

                  {/* Password */}
                  <div style={{ marginBottom: '0.75rem' }}>
                    <label
                      htmlFor="citizen-password"
                      style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}
                    >
                      Password <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <PasswordInput
                      id="citizen-password"
                      name="password"
                      autoComplete="current-password"
                      required
                      placeholder="Enter your password"
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

                  {/* Recovery & Setup links */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                    <Link
                      to="/setup-password"
                      style={{ fontSize: '0.8125rem', color: '#475467', textDecoration: 'none' }}
                    >
                      Set up password for existing account
                    </Link>
                    <Link
                      to="/forgot-password"
                      style={{ fontSize: '0.8125rem', color: '#155EEF', fontWeight: 600, textDecoration: 'none' }}
                    >
                      Forgot password?
                    </Link>
                  </div>

                  {/* Sign In Button */}
                  <button
                    type="submit"
                    disabled={loading || !identifier.trim() || !password}
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
                      cursor: (loading || !identifier.trim() || !password) ? 'not-allowed' : 'pointer',
                      marginBottom: '1.25rem',
                      boxShadow: '0 2px 4px rgba(16, 43, 70, 0.15)',
                    }}
                  >
                    {loading ? <LoadingSpinner size="sm" /> : 'Sign In →'}
                  </button>
                </form>

                {/* Footer Navigation */}
                <div style={{ borderTop: '1px solid #EAECF0', paddingTop: '1.25rem', textAlign: 'center' }}>
                  <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
                    Don&apos;t have an account?{' '}
                    <Link
                      to={searchParams.get('redirect') ? `/register?redirect=${encodeURIComponent(searchParams.get('redirect'))}` : '/register'}
                      style={{ color: '#155EEF', fontWeight: 700, textDecoration: 'none' }}
                    >
                      Register as Citizen / Guardian →
                    </Link>
                  </p>
                </div>
              </div>
            )}

            {/* ---------------------------------------------------- */}
            {/* CATEGORY 2: STUDENT PORTAL                           */}
            {/* ---------------------------------------------------- */}
            {selectedCategory === 'student' && (
              <div>
                {/* Tab Switcher */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', background: '#f1f5f9', padding: '0.25rem', borderRadius: '6px', marginBottom: '1.5rem' }}>
                  <button
                    type="button"
                    onClick={() => { setStudentTab('login'); setError(''); }}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '4px',
                      border: 'none',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      background: studentTab === 'login' ? '#ffffff' : 'transparent',
                      color: studentTab === 'login' ? '#102B46' : '#64748b',
                      boxShadow: studentTab === 'login' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                    }}
                  >
                    1. Enrolled Student Sign In
                  </button>
                  <button
                    type="button"
                    onClick={() => { setStudentTab('activate'); setError(''); }}
                    style={{
                      padding: '0.5rem',
                      borderRadius: '4px',
                      border: 'none',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      background: studentTab === 'activate' ? '#ffffff' : 'transparent',
                      color: studentTab === 'activate' ? '#102B46' : '#64748b',
                      boxShadow: studentTab === 'activate' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                    }}
                  >
                    2. First-Time Account Activation
                  </button>
                </div>

                {studentTab === 'login' ? (
                  /* Standard Student Sign In Form */
                  <form onSubmit={handleLogin}>
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                        Student ID or Permanent SATS ID
                      </label>
                      <input
                        type="text"
                        required
                        className="input"
                        placeholder="e.g. SCH01125 or NS-445851DF..."
                        value={identifier}
                        onChange={e => setIdentifier(e.target.value)}
                        style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
                      />
                    </div>

                    <div style={{ marginBottom: '0.75rem' }}>
                      <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                        Password
                      </label>
                      <PasswordInput
                        required
                        minLength={8}
                        className="input"
                        placeholder="Enter your student password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
                      />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.25rem' }}>
                      <Link to="/forgot-password" style={{ fontSize: '0.8125rem', color: '#155EEF', textDecoration: 'underline' }}>
                        Forgot password?
                      </Link>
                    </div>

                    <button
                      type="submit"
                      disabled={loading}
                      className="btn btn--primary btn--full btn--lg"
                      style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem', background: '#102B46' }}
                    >
                      {loading ? <LoadingSpinner size="sm" /> : 'Sign In as Student →'}
                    </button>
                  </form>
                ) : (
                  /* Verified Identity Student Activation Flow */
                  <div>
                    {!studentLookupData ? (
                      <form onSubmit={handleStudentLookup}>
                        <div style={{ marginBottom: '1rem' }}>
                          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 700, color: '#102B46', marginBottom: '0.35rem' }}>
                            Enter Student ID or Permanent SATS ID <span style={{ color: '#D92D20' }}>*</span>
                          </label>
                          <input
                            type="text"
                            required
                            placeholder="e.g. SCH01001, SCH01125, or NS-..."
                            value={studentIdInput}
                            onChange={e => setStudentIdInput(e.target.value)}
                            style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={studentLookupLoading || !studentIdInput.trim()}
                          className="btn btn--primary btn--full"
                          style={{ background: '#155EEF', fontWeight: 700, padding: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                        >
                          {studentLookupLoading ? <LoadingSpinner size="sm" /> : 'Find Official Enrolled Record →'}
                        </button>
                      </form>
                    ) : (
                      <form onSubmit={handleStudentActivate}>
                        <div style={{ marginBottom: '1rem', background: '#F8FAFC', padding: '1rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#102B46' }}>
                            {studentLookupData.official_student_name}
                          </div>
                          <div style={{ fontSize: '0.8125rem', color: '#64748B' }}>
                            {studentLookupData.school_name} · Standard {studentLookupData.standard}
                          </div>
                          <div style={{ marginTop: '0.5rem' }}>
                            <label style={{ fontSize: '0.8125rem', color: '#102B46', display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                              <input
                                type="checkbox"
                                required
                                checked={studentConfirmedRecord}
                                onChange={e => setStudentConfirmedRecord(e.target.checked)}
                              />
                              I confirm this is my official enrolled student profile
                            </label>
                          </div>
                        </div>

                        <div style={{ marginBottom: '1rem', background: '#FFFFFF', padding: '1rem', border: '1px solid #E2E8F0', borderRadius: '8px' }}>
                          <div style={{ marginBottom: '0.85rem' }}>
                            <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#102B46', marginBottom: '0.3rem' }}>
                              Official Date of Birth (DOB) <span style={{ color: '#D92D20' }}>*</span>
                            </label>
                            <input
                              type="date"
                              required
                              value={studentDobInput}
                              onChange={e => setStudentDobInput(e.target.value)}
                              style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                            />
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '0.25rem' }}>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#102B46', marginBottom: '0.25rem' }}>
                                Create Password <span style={{ color: '#D92D20' }}>*</span>
                              </label>
                              <PasswordInput
                                required
                                minLength={8}
                                placeholder="Min 8 characters"
                                value={studentPasswordInput}
                                onChange={e => setStudentPasswordInput(e.target.value)}
                                style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
                              />
                            </div>
                            <div>
                              <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#102B46', marginBottom: '0.25rem' }}>
                                Confirm Password <span style={{ color: '#D92D20' }}>*</span>
                              </label>
                              <PasswordInput
                                required
                                minLength={8}
                                placeholder="Min 8 characters"
                                value={studentConfirmPasswordInput}
                                onChange={e => setStudentConfirmPasswordInput(e.target.value)}
                                style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
                              />
                            </div>
                          </div>
                        </div>

                        <button
                          type="submit"
                          disabled={studentActLoading || !studentConfirmedRecord || !studentDobInput}
                          className="btn btn--primary btn--full"
                          style={{ background: '#12B76A', fontWeight: 700, padding: '0.65rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                        >
                          {studentActLoading ? <LoadingSpinner size="sm" /> : '✓ Verify Identity & Activate Student Account'}
                        </button>
                      </form>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* ---------------------------------------------------- */}
            {/* CATEGORY 3: ADMIN & STAFF                            */}
            {/* ---------------------------------------------------- */}
            {selectedCategory === 'admin' && (
              <div>
                {/* Institutional Administrator Selection Notice */}
                <div style={{ marginBottom: '1.5rem', padding: '1rem', background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '6px', textAlign: 'center' }}>
                  <div style={{ fontSize: '0.875rem', color: '#1e40af', fontWeight: 700, marginBottom: '0.35rem' }}>
                    🏛️ Institution Administrator?
                  </div>
                  <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.8125rem', color: '#1e3a8a' }}>
                    Access one of the 30 Karnataka institutions (Schools, PU Colleges, Degree Colleges, Universities).
                  </p>
                  <Link
                    to="/select-institution"
                    style={{
                      display: 'inline-block',
                      background: '#155EEF',
                      color: '#ffffff',
                      padding: '0.5rem 1rem',
                      borderRadius: '4px',
                      fontSize: '0.8125rem',
                      fontWeight: 700,
                      textDecoration: 'none',
                    }}
                  >
                    Select Your Institution to Log In →
                  </Link>
                </div>

                <form onSubmit={handleLogin}>
                  <div style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                      Official Email or Registered Mobile
                    </label>
                    <input
                      type="text"
                      required
                      className="input"
                      placeholder="e.g. admin.central@nagriksetu.gov or staff.sch001@example.com"
                      value={identifier}
                      onChange={e => setIdentifier(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
                    />
                  </div>

                  <div style={{ marginBottom: '0.75rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                      Password
                    </label>
                    <PasswordInput
                      required
                      minLength={8}
                      className="input"
                      placeholder="Enter administrator password"
                      value={password}
                      onChange={e => setPassword(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.9375rem' }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.25rem' }}>
                    <Link to="/forgot-password" style={{ fontSize: '0.8125rem', color: '#155EEF', textDecoration: 'underline' }}>
                      Forgot password?
                    </Link>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="btn btn--primary btn--full btn--lg"
                    style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', marginBottom: '1rem', background: '#102B46' }}
                  >
                    {loading ? <LoadingSpinner size="sm" /> : 'Sign In as Administrator / Staff →'}
                  </button>

                  {/* Quick Administrator Access Shortcuts */}
                  <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid #EAECF0', background: '#F8F9FC', padding: '1rem', borderRadius: '8px' }}>
                    <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#102B46', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>🔐</span>
                      <span>Authorized Administrator Gateways</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.6rem' }}>
                      <button
                        type="button"
                        className="btn btn--secondary btn--sm"
                        onClick={() => navigate('/select-institution')}
                        style={{ fontSize: '0.8rem', border: '1px solid #155EEF', color: '#155EEF', textAlign: 'center', fontWeight: 700, background: '#FFFFFF', padding: '8px 12px' }}
                      >
                        1. School Admin (30 Institutions) →
                      </button>
                      <button
                        type="button"
                        className="btn btn--secondary btn--sm"
                        onClick={fillDemoPlatformAdmin}
                        style={{ fontSize: '0.8rem', border: '1px solid #D0D5DD', color: '#102B46', textAlign: 'center', fontWeight: 600, background: '#FFFFFF', padding: '8px 12px' }}
                      >
                        2. Platform Central Admin
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  )
}
