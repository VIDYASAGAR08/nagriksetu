import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import StatusBadge from '../../components/ui/StatusBadge.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'
import Stage2AdmissionModal from '../../components/admissions/Stage2AdmissionModal.jsx'
import RequesterPortalView from '../../components/requests/RequesterPortalView.jsx'

export default function ParentDashboard() {
  const { user, token, isAuthenticated } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()

  const [activeTab, setActiveTab] = useState(() => searchParams.get('tab') || (searchParams.get('school_id') ? 'new-request' : 'children'))
  const [children, setChildren] = useState([])
  const [requests, setRequests] = useState([])
  const [schools, setSchools] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Centralised Student ID Child Linking State
  const [linkStudentIdInput, setLinkStudentIdInput] = useState('')
  const [isLookingUpId, setIsLookingUpId] = useState(false)
  const [lookupChildResult, setLookupChildResult] = useState(null)
  const [lookupChildError, setLookupChildError] = useState('')
  const [linkRelationship, setLinkRelationship] = useState('Father')
  const [isRequestingCode, setIsRequestingCode] = useState(false)
  const [linkingCodeIssued, setLinkingCodeIssued] = useState(false)
  const [verificationCodeInput, setVerificationCodeInput] = useState('')
  const [resendCooldown, setResendCooldown] = useState(0)

  // Resend cooldown timer
  useEffect(() => {
    if (resendCooldown <= 0) return
    const timer = setInterval(() => {
      setResendCooldown((prev) => Math.max(0, prev - 1))
    }, 1000)
    return () => clearInterval(timer)
  }, [resendCooldown])
  const [isSubmittingLink, setIsSubmittingLink] = useState(false)
  const [verificationError, setVerificationError] = useState('')
  const [submitLinkingSuccess, setSubmitLinkingSuccess] = useState(null)
  const [clarificationResponses, setClarificationResponses] = useState({})
  const [submittingClarificationId, setSubmittingClarificationId] = useState(null)
  const [clarificationFeedback, setClarificationFeedback] = useState({})

  // New Linking Request Form State
  const [formStudentRef, setFormStudentRef] = useState(() => searchParams.get('student_ref') || '')
  const [formRelationship, setFormRelationship] = useState('Father')
  const [formNotes, setFormNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Institution-Scoped Linking Request State
  const [selectedInstForLinking, setSelectedInstForLinking] = useState(null)
  const [instFilterTerm, setInstFilterTerm] = useState('')
  const [institutionStudents, setInstitutionStudents] = useState([])
  const [loadingInstStudents, setLoadingInstStudents] = useState(false)
  const [instEmptyMessage, setInstEmptyMessage] = useState('')
  const [studentSearchTerm, setStudentSearchTerm] = useState('')

  // Student Lookup & Autocomplete State
  const [detectedStudent, setDetectedStudent] = useState(null)
  const [studentSuggestions, setStudentSuggestions] = useState([])
  const [isSearchingStudent, setIsSearchingStudent] = useState(false)
  const [showStudentDropdown, setShowStudentDropdown] = useState(false)
  const [lookupError, setLookupError] = useState('')

  // Records Modal State
  const [selectedChild, setSelectedChild] = useState(null)
  const [childRecords, setChildRecords] = useState(null)
  const [loadingRecords, setLoadingRecords] = useState(false)
  const [recordsError, setRecordsError] = useState('')
  const [recordModalTab, setRecordModalTab] = useState('profile')

  // Phase 4 Stage 1 Admission Applications State
  const [admissionApps, setAdmissionApps] = useState([])
  const [loadingAdmissions, setLoadingAdmissions] = useState(false)
  const [claimIdInput, setClaimIdInput] = useState('')
  const [claimApplicantNameInput, setClaimApplicantNameInput] = useState('')
  const [claimPasswordInput, setClaimPasswordInput] = useState('')
  const [claimStatusMsg, setClaimStatusMsg] = useState(null)
  const [claiming, setClaiming] = useState(false)
  const [clarifyReplyMap, setClarifyReplyMap] = useState({})
  const [replySubmittingId, setReplySubmittingId] = useState(null)
  const [selectedStage2AppId, setSelectedStage2AppId] = useState(null)

  // Load parent data
  async function loadAdmissionApps() {
    if (!token) return
    try {
      setLoadingAdmissions(true)
      const res = await apiGet('/parent/admissions/applications', token)
      setAdmissionApps(Array.isArray(res) ? res : res?.applications || [])
    } catch (err) {
      console.error('Failed to load admission applications:', err)
    } finally {
      setLoadingAdmissions(false)
    }
  }

  async function handleClaimApplication(e) {
    e.preventDefault()
    if (!claimIdInput.trim() || !claimApplicantNameInput.trim()) {
      setClaimStatusMsg({ type: 'error', text: 'Please enter both the Application ID and Applicant Full Name.' })
      return
    }
    setClaiming(true)
    setClaimStatusMsg(null)
    try {
      const payload = {
        application_id: claimIdInput.trim(),
        applicant_name: claimApplicantNameInput.trim(),
      }
      if (claimPasswordInput) {
        payload.password = claimPasswordInput
      }
      const res = await apiPost('/parent/admissions/claim', payload, token)
      setClaimStatusMsg({ type: 'success', text: res.message || 'Application successfully claimed and linked!' })
      setClaimIdInput('')
      setClaimApplicantNameInput('')
      setClaimPasswordInput('')
      loadAdmissionApps()
    } catch (err) {
      setClaimStatusMsg({ type: 'error', text: err.message || 'Unable to claim application.' })
    } finally {
      setClaiming(false)
    }
  }

  async function handleSendClarificationReply(appId) {
    const text = clarifyReplyMap[appId]?.trim()
    if (!text || text.length < 3) {
      alert('Please enter your response (minimum 3 characters).')
      return
    }
    setReplySubmittingId(appId)
    try {
      await apiPost(`/parent/admissions/applications/${appId}/respond-clarification`, { response_text: text }, token)
      alert('Your response has been dispatched to the institution admission desk.')
      setClarifyReplyMap(prev => ({ ...prev, [appId]: '' }))
      loadAdmissionApps()
    } catch (err) {
      alert(err.message || 'Failed to submit response.')
    } finally {
      setReplySubmittingId(null)
    }
  }

  async function loadData() {
    if (!token) return
    try {
      setLoading(true)
      const [childData, reqData, schoolData] = await Promise.all([
        apiGet('/parent/children', token).catch(() => []),
        apiGet('/parent/linking-requests', token).catch(() => []),
        apiGet('/schools?limit=100').catch(() => [])
      ])
      setChildren(Array.isArray(childData) ? childData : [])
      setRequests(Array.isArray(reqData) ? reqData : [])
      setSchools(Array.isArray(schoolData) ? schoolData : [])
    } catch (err) {
      setError(err.message || 'Unable to load parent dashboard.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    if (activeTab === 'admissions') {
      loadAdmissionApps()
    }
  }, [token, activeTab])

  // If student_ref passed via query param, pre-fill form
  useEffect(() => {
    const qRef = searchParams.get('student_ref')
    if (qRef) {
      setFormStudentRef(qRef)
      setActiveTab('new-request')
      handleDirectLookup(qRef)
    }
  }, [searchParams])

  // Automatically open Child Academic Modal if child_psid is provided in URL
  useEffect(() => {
    const qPsid = searchParams.get('child_psid')
    if (qPsid && children.length > 0 && !selectedChild) {
      const match = children.find(c => c.permanent_student_id === qPsid) || children[0]
      if (match) viewRecords(match)
    }
  }, [searchParams, children])

  // Handle Tab Switch
  function switchTab(tab) {
    setActiveTab(tab)
    setSearchParams({ tab })
    setError('')
    setSuccess('')
  }

  // Select Institution and load its enrolled students
  async function handleSelectInstitution(inst) {
    setSelectedInstForLinking(inst)
    setDetectedStudent(null)
    setFormStudentRef('')
    setStudentSearchTerm('')
    setLookupError('')
    setError('')
    setInstEmptyMessage('')
    setInstitutionStudents([])

    if (!inst) return

    setLoadingInstStudents(true)
    try {
      const res = await apiGet(`/parent/lookup-student?institution_id=${encodeURIComponent(inst.school_id)}`, token)
      const matches = res?.matches || []
      setInstitutionStudents(matches)
      if (matches.length === 0) {
        setInstEmptyMessage(res?.message || 'No students are currently registered under this institution.')
      } else {
        setInstEmptyMessage('')
      }
    } catch (err) {
      setInstitutionStudents([])
      setInstEmptyMessage(err.message || 'Error loading students for this institution.')
    } finally {
      setLoadingInstStudents(false)
    }
  }

  // Search students strictly within the selected institution
  async function handleSearchStudentsInInst(q) {
    if (!selectedInstForLinking) return
    const query = (q !== undefined ? q : studentSearchTerm).trim()
    setLoadingInstStudents(true)
    setLookupError('')
    try {
      const url = query
        ? `/parent/lookup-student?institution_id=${encodeURIComponent(selectedInstForLinking.school_id)}&q=${encodeURIComponent(query)}`
        : `/parent/lookup-student?institution_id=${encodeURIComponent(selectedInstForLinking.school_id)}`
      const res = await apiGet(url, token)
      const matches = res?.matches || []
      setInstitutionStudents(matches)
      if (matches.length === 0) {
        setLookupError(res?.message || (query ? `No students matching '${query}' found in this institution.` : 'No students are currently registered under this institution.'))
      } else {
        setLookupError('')
      }
    } catch (err) {
      setInstitutionStudents([])
      setLookupError(err.message || 'Failed to search students.')
    } finally {
      setLoadingInstStudents(false)
    }
  }

  // Search / Lookup Student by query with debouncing
  async function searchStudent(query) {
    const q = (query || '').trim()
    if (!q || q.length < 2) {
      setStudentSuggestions([])
      setShowStudentDropdown(false)
      return
    }
    try {
      setIsSearchingStudent(true)
      const res = await apiGet(`/parent/lookup-student?q=${encodeURIComponent(q)}`, token)
      const matches = res?.matches || []
      setStudentSuggestions(matches)
      setShowStudentDropdown(matches.length > 0)
      if (matches.length === 0) {
        setLookupError('No matching student found. Please verify the Student ID or Permanent Student ID.')
      } else {
        setLookupError('')
      }
    } catch (err) {
      console.error('Student lookup failed:', err)
      setStudentSuggestions([])
      setLookupError(err.message || 'Error looking up student.')
    } finally {
      setIsSearchingStudent(false)
    }
  }

  // Handle direct lookup on Enter, blur, or Lookup button click
  async function handleDirectLookup(forceValue) {
    const target = (forceValue !== undefined ? forceValue : formStudentRef).trim()
    if (!target) return
    setIsSearchingStudent(true)
    setLookupError('')
    try {
      const res = await apiGet(`/parent/lookup-student?q=${encodeURIComponent(target)}`, token)
      const matches = res?.matches || []
      if (matches.length > 0) {
        const exactMatch = matches.find(m => 
          m.student_id?.toUpperCase() === target.toUpperCase() ||
          m.permanent_student_id?.toUpperCase() === target.toUpperCase()
        ) || matches[0]
        selectStudent(exactMatch)
      } else {
        setDetectedStudent(null)
        setLookupError('No matching student found. Please verify the Student ID or Permanent Student ID.')
      }
    } catch (err) {
      setDetectedStudent(null)
      setLookupError(err.message || 'Unable to lookup student.')
    } finally {
      setIsSearchingStudent(false)
      setShowStudentDropdown(false)
    }
  }

  function selectStudent(student) {
    setDetectedStudent(student)
    setFormStudentRef(student.student_id || student.permanent_student_id)
    setShowStudentDropdown(false)
    setStudentSuggestions([])
    setLookupError('')
    setError('')
  }

  // Submit Linking Request
  async function handleRequestSubmit(e) {
    e.preventDefault()
    if (!formStudentRef.trim()) {
      setError('Please provide a valid Student ID or Permanent Student ID.')
      return
    }
    if (!detectedStudent) {
      setError('Please verify a valid student from the system before submitting.')
      return
    }
    if (!detectedStudent.has_valid_enrollment && detectedStudent.enrollment_status !== 'active') {
      setError('Cannot submit linking request: student does not have an active enrollment at an accredited institution.')
      return
    }

    try {
      setSubmitting(true)
      setError('')
      setSuccess('')

      const payload = {
        school_id: selectedInstForLinking ? selectedInstForLinking.school_id : (detectedStudent ? detectedStudent.institution_id || detectedStudent.school_id : undefined),
        student_ref: formStudentRef.trim(),
        relationship_type: formRelationship,
        additional_notes: formNotes.trim() || undefined,
      }

      const res = await apiPost('/parent/linking-requests', payload, token)

      setSuccess(res.message || 'Your student-linking request has been submitted successfully to the school staff desk! Status is pending verification.')
      setFormStudentRef('')
      setDetectedStudent(null)
      setFormNotes('')

      // Reload requests & switch to history tab after short delay
      const reqData = await apiGet('/parent/linking-requests', token).catch(() => [])
      setRequests(Array.isArray(reqData) ? reqData : [])
      setActiveTab('history')
    } catch (err) {
      setError(err.message || 'Failed to submit linking request. Check for pending duplicates.')
    } finally {
      setSubmitting(false)
    }
  }

  // Centralised Student ID Child Lookup (Module 1 - Step 1)
  async function handleCentralisedStudentLookup(e) {
    if (e) e.preventDefault()
    const target = linkStudentIdInput.trim()
    if (!target) {
      setLookupChildError('Please enter a valid centralised Student ID.')
      return
    }
    setIsLookingUpId(true)
    setLookupChildError('')
    setLookupChildResult(null)
    setSubmitLinkingSuccess(null)

    try {
      const res = await apiGet(`/parent/lookup-by-student-id?student_id=${encodeURIComponent(target)}`, token)
      setLookupChildResult(res)
    } catch (err) {
      setLookupChildResult(null)
      setLookupChildError(err.message || `No student record found matching Student ID '${target}'.`)
    } finally {
      setIsLookingUpId(false)
    }
  }

  // Submit Linking Request for Institution Review (Module 1 - Step 2 & 3)
  async function handleSubmitLinkingRequest() {
    if (!lookupChildResult?.student_id) return
    setIsSubmittingLink(true)
    setSubmitLinkingSuccess(null)
    setLookupChildError('')
    try {
      const payload = {
        student_ref: lookupChildResult.student_id,
        student_id: lookupChildResult.student_id,
        school_id: lookupChildResult.institution_id,
        permanent_student_id: lookupChildResult.permanent_student_id,
        relationship_type: linkRelationship,
      }
      const res = await apiPost('/parent/linking-requests', payload, token)
      setSubmitLinkingSuccess(res.message || `Your request has been submitted successfully to ${lookupChildResult.institution_name}. The institution will review and notify you of its decision.`)
      // Refresh requests list
      const reqData = await apiGet('/parent/linking-requests', token).catch(() => [])
      setRequests(Array.isArray(reqData) ? reqData : [])
    } catch (err) {
      setLookupChildError(err.message || 'Failed to submit linking request. Check for pending duplicates.')
    } finally {
      setIsSubmittingLink(false)
    }
  }

  // Parent response to institution clarification (Module 3)
  async function handleRespondClarification(requestId) {
    const text = (clarificationResponses[requestId] || '').trim()
    if (!text) {
      setClarificationFeedback(prev => ({ ...prev, [requestId]: { type: 'error', message: 'Please enter your clarification response before submitting.' } }))
      return
    }
    setSubmittingClarificationId(requestId)
    setClarificationFeedback(prev => ({ ...prev, [requestId]: null }))
    try {
      const res = await apiPost(`/parent/linking-requests/${requestId}/respond-clarification`, {
        response_notes: text
      }, token)
      setClarificationFeedback(prev => ({ ...prev, [requestId]: { type: 'success', message: res.message || 'Clarification submitted. Waiting for institution review.' } }))
      // Refresh requests list
      const reqData = await apiGet('/parent/linking-requests', token).catch(() => [])
      setRequests(Array.isArray(reqData) ? reqData : [])
    } catch (err) {
      setClarificationFeedback(prev => ({ ...prev, [requestId]: { type: 'error', message: err.message || 'Failed to submit clarification.' } }))
    } finally {
      setSubmittingClarificationId(null)
    }
  }

  function handleResetLookup() {
    setLookupChildResult(null)
    setSubmitLinkingSuccess(null)
    setLookupChildError('')
  }

  // View Child Academic Records
  async function viewRecords(child) {
    setSelectedChild(child)
    setLoadingRecords(true)
    setRecordsError('')
    setChildRecords(null)
    setRecordModalTab('profile')

    try {
      const data = await apiGet(`/parent/children/${child.permanent_student_id}/records`, token)
      setChildRecords(data)
    } catch (err) {
      setRecordsError(err.message || 'Failed to load official child records.')
    } finally {
      setLoadingRecords(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="container" style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <Alert type="warning" title="Authentication Required">
          Please sign in with your parent credentials to access this dashboard.
        </Alert>
        <Link to="/login" className="btn btn--primary" style={{ marginTop: '1rem', textDecoration: 'none' }}>
          Go to Sign In
        </Link>
      </div>
    )
  }

  return (
    <div className="parent-dashboard-page">
      <Breadcrumbs crumbs={[{ label: 'Home', href: '/' }, { label: 'Parent Portal' }]} />

      <div className="container" style={{ maxWidth: '1100px', margin: '2rem auto', padding: '0 1rem' }}>
        {/* Welcome Header */}
        <div className="card" style={{ padding: '1.5rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'inline-block', background: '#dcfce7', color: '#15803d', fontWeight: 600, padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
              VERIFIED CITIZEN ACCOUNT (PARENT / GUARDIAN)
            </div>
            <h1 style={{ fontSize: '1.75rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
              Welcome, {user?.full_name || 'Parent Guardian'}
            </h1>
            <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
              Registered Mobile: <strong>{user?.phone || 'N/A'}</strong> · Email: <strong>{user?.email || 'Not provided'}</strong>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button
              onClick={() => switchTab('link-child')}
              className="btn btn--primary"
              style={{ fontWeight: 700 }}
            >
              + Link My Child
            </button>
            <button
              onClick={() => switchTab('new-request')}
              className="btn btn--secondary"
            >
              Desk Request
            </button>
          </div>
        </div>

        {error && <Alert type="error" title="Error" className="mb-4">{error}</Alert>}
        {success && <Alert type="success" title="Success" className="mb-4">{success}</Alert>}

        {/* Tab Navigation */}
        <div style={{ display: 'flex', borderBottom: '2px solid #e8eaed', marginBottom: '1.5rem', gap: '0.5rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => switchTab('children')}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 600,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: activeTab === 'children' ? '#1a3a6b' : '#6b7280',
              borderBottom: activeTab === 'children' ? '3px solid #1a3a6b' : '3px solid transparent',
              marginBottom: '-2px'
            }}
          >
            Linked Children ({children.length})
          </button>

          <button
            onClick={() => switchTab('link-child')}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 700,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: activeTab === 'link-child' ? '#155EEF' : '#6b7280',
              borderBottom: activeTab === 'link-child' ? '3px solid #155EEF' : '3px solid transparent',
              marginBottom: '-2px'
            }}
          >
            🔗 Link My Child
          </button>

          <button
            onClick={() => { switchTab('admissions'); loadAdmissionApps(); }}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 700,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: activeTab === 'admissions' ? '#155EEF' : '#6b7280',
              borderBottom: activeTab === 'admissions' ? '3px solid #155EEF' : '3px solid transparent',
              marginBottom: '-2px'
            }}
          >
            📋 Admission Applications ({admissionApps.length})
          </button>

          <button
            onClick={() => switchTab('new-request')}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 600,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: activeTab === 'new-request' ? '#1a3a6b' : '#6b7280',
              borderBottom: activeTab === 'new-request' ? '3px solid #1a3a6b' : '3px solid transparent',
              marginBottom: '-2px'
            }}
          >
            Institution Desk Request
          </button>

          <button
            onClick={() => switchTab('history')}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 600,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: activeTab === 'history' ? '#1a3a6b' : '#6b7280',
              borderBottom: activeTab === 'history' ? '3px solid #1a3a6b' : '3px solid transparent',
              marginBottom: '-2px'
            }}
          >
            My Child Linking Requests ({requests.length})
          </button>

          <button
            onClick={() => switchTab('requests')}
            style={{
              padding: '0.75rem 1.25rem',
              fontWeight: 700,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: activeTab === 'requests' ? '#155EEF' : '#6b7280',
              borderBottom: activeTab === 'requests' ? '3px solid #155EEF' : '3px solid transparent',
              marginBottom: '-2px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem'
            }}
          >
            <span>📋</span> My Requests & Complaints
          </button>
        </div>

        {/* Tab: Requests, Complaints & Record Corrections */}
        {activeTab === 'requests' && (
          <div style={{ marginTop: '0.5rem' }}>
            <RequesterPortalView token={token} userRole="parent" linkedStudents={children} />
          </div>
        )}

        {/* Tab 1: Linked Children */}
        {activeTab === 'children' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                  My Children
                </h2>
                <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
                  Verified children linked to your parent account across all educational institutions.
                </p>
              </div>
              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <span className="badge badge--primary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.85rem', fontWeight: 600 }}>
                  {children.length} {children.length === 1 ? 'Child' : 'Children'} Linked
                </span>
                <button
                  onClick={() => switchTab('link-child')}
                  className="btn btn--primary btn--sm"
                  style={{ fontWeight: 600 }}
                >
                  + Link Another Child
                </button>
              </div>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>Loading your verified children...</p>
              </div>
            ) : children.length === 0 ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>👶</div>
                <h3 style={{ color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>No Linked Students Found</h3>
                <p style={{ color: '#4b5563', maxWidth: '500px', margin: '0 auto 1.5rem auto', fontSize: '0.9375rem' }}>
                  You have not linked any student records to your account yet. Use the Student ID lookup to link your child using their centralised Student ID.
                </p>
                <button onClick={() => switchTab('link-child')} className="btn btn--primary">
                  Link Your Child Now →
                </button>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                {children
                  .filter(c => c.is_verified === 1 || c.is_verified === true || c.is_verified === undefined)
                  .map(child => {
                    const tier = child.institution_tier || (child.school_type === 'PU College' ? 'pu_college' : 'school')
                    let tierSummary = child.class_or_standard || `Standard ${child.standard}`
                    let tierLabel = 'Class / Standard'
                    if (tier === 'pu_college') {
                      tierLabel = 'PUC Programme & Stream'
                      tierSummary = `${child.puc_year || child.class_or_standard || 'PUC'} · ${child.stream || ''} ${child.subject_combination ? '(' + child.subject_combination + ')' : ''} · Sec ${child.section || 'A'}`.trim()
                    } else if (tier === 'engineering_college') {
                      tierLabel = 'Engineering Programme'
                      tierSummary = `${child.degree || 'B.E.'} in ${child.branch || child.programme || 'Engineering'} · Sem ${child.semester || 1} (Sec ${child.section || 'A'})`.trim()
                    } else if (tier === 'degree_college' || tier === 'university') {
                      tierLabel = 'Degree Programme'
                      tierSummary = `${child.degree || child.programme || child.program_or_stream} · Sem ${child.semester || 1} (Sec ${child.section || 'A'})`.trim()
                    } else {
                      tierLabel = 'School Standard & Section'
                      tierSummary = `${child.class_or_standard || `Standard ${child.standard}`} · Section ${child.section || 'A'}`
                    }
                    return (
                      <div key={child.permanent_student_id} className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', padding: '1.5rem', background: '#ffffff', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', boxShadow: '0 2px 4px rgba(0,0,0,0.04)' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                            <span className="badge badge--success" style={{ fontWeight: 600 }}>Verified Child</span>
                            <span style={{ fontSize: '0.8rem', fontWeight: 700, fontFamily: 'monospace', color: '#155EEF', background: '#EFF4FF', padding: '0.15rem 0.45rem', borderRadius: '4px' }}>
                              {child.student_id || 'N/A'}
                            </span>
                          </div>

                          <h3 style={{ fontSize: '1.25rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                            {child.student_name}
                          </h3>
                          <div style={{ color: '#4b5563', fontSize: '0.9rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                            <span>🏫</span>
                            <strong>{child.institution_name || child.school_name || child.school_id}</strong>
                          </div>

                          <div style={{ background: '#f8fafc', padding: '0.85rem', borderRadius: '6px', fontSize: '0.8125rem', marginBottom: '1.25rem', border: '1px solid #e2e8f0' }}>
                            <div style={{ marginBottom: '0.5rem' }}>
                              <span style={{ color: '#64748b', fontSize: '0.75rem', fontWeight: 600, display: 'block', textTransform: 'uppercase' }}>{tierLabel}:</span>
                              <strong style={{ color: '#0f172a', fontSize: '0.875rem' }}>{tierSummary}</strong>
                            </div>
                            <div style={{ borderTop: '1px solid #edf2f7', paddingTop: '0.5rem', display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.35rem' }}>
                              <div>Student ID: <strong style={{ fontFamily: 'monospace', color: '#155EEF' }}>{child.student_id}</strong></div>
                              <div>Type: <strong>{child.institution_type || child.school_type || 'Accredited'}</strong></div>
                              <div>Status: <strong style={{ color: '#027a48', textTransform: 'capitalize' }}>{child.enrollment_status || 'Active'}</strong></div>
                              <div>Academic Year: <strong>{child.academic_year || '2026-2027'}</strong></div>
                            </div>
                          </div>
                        </div>

                        <button
                          onClick={() => viewRecords(child)}
                          className="btn btn--primary btn--full btn--sm"
                          style={{ fontWeight: 600 }}
                        >
                          View Details →
                        </button>
                      </div>
                    )
                  })}
              </div>
            )}
          </div>
        )}

        {/* Tab: Link My Child Using Centralised Student ID */}
        {activeTab === 'link-child' && (
          <div className="card" style={{ maxWidth: '850px', margin: '0 auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', boxShadow: '0 2px 6px rgba(0,0,0,0.04)' }}>
            <div style={{ marginBottom: '1.75rem', borderBottom: '1px solid #e8eaed', paddingBottom: '1rem' }}>
              <div style={{ display: 'inline-block', background: '#EFF4FF', color: '#155EEF', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem', textTransform: 'uppercase' }}>
                Centralised Student Verification
              </div>
              <h2 style={{ fontSize: '1.45rem', color: '#1a3a6b', margin: '0 0 0.35rem 0', fontWeight: 700 }}>
                Link My Child
              </h2>
              <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0, lineHeight: 1.5 }}>
                Enter your child's exact centralised Student ID. The system retrieves official enrollment details directly from the live institution database. Upon your confirmation, a formal verification request is submitted to the educational institution for review and approval.
              </p>
            </div>

            {/* STEP 1: Enter Student ID */}
            <div style={{ marginBottom: '1.5rem', padding: '1.25rem', border: '1px solid #E2E8F0', borderRadius: '8px', background: '#F8FAFC' }}>
              <form onSubmit={handleCentralisedStudentLookup}>
                <label style={{ display: 'block', fontWeight: 600, color: '#1e293b', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  Student ID <span style={{ color: '#b91c1c' }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <input
                    type="text"
                    value={linkStudentIdInput}
                    onChange={(e) => {
                      setLinkStudentIdInput(e.target.value.toUpperCase())
                      setLookupChildError('')
                      setSubmitLinkingSuccess(null)
                    }}
                    placeholder="e.g. BSDS260001, PCMB260001, COL03001, 20260001"
                    style={{ flex: 1, minWidth: '240px', padding: '0.7rem 0.9rem', fontSize: '1rem', fontWeight: 600, fontFamily: 'monospace', border: '1px solid #cbd5e1', borderRadius: '6px', letterSpacing: '0.5px' }}
                    disabled={isLookingUpId}
                  />
                  <button
                    type="submit"
                    className="btn btn--primary"
                    disabled={isLookingUpId || !linkStudentIdInput.trim()}
                    style={{ minWidth: '150px', fontWeight: 600 }}
                  >
                    {isLookingUpId ? 'Searching...' : 'Search Student 🔍'}
                  </button>
                  {lookupChildResult && (
                    <button
                      type="button"
                      onClick={handleResetLookup}
                      className="btn btn--secondary"
                      style={{ fontSize: '0.85rem' }}
                    >
                      Reset
                    </button>
                  )}
                </div>
                <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#64748b' }}>
                  💡 Supported IDs across all institutions: Schools (<code>20260001</code>), PU Colleges (<code>PCMB260001</code>, <code>PCMC260001</code>, <code>HEBA260001</code>), Degree & Engineering (<code>BSDS260001</code>, <code>BCA260001</code>, <code>COL03001</code>).
                </div>
              </form>
            </div>

            {/* Error during lookup */}
            {lookupChildError && (
              <Alert type="error" title="Lookup Unsuccessful" className="mb-4">
                {lookupChildError}
              </Alert>
            )}

            {/* Success message on submission */}
            {submitLinkingSuccess && (
              <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: '#065F46', fontWeight: 700, fontSize: '1rem', marginBottom: '0.35rem' }}>
                  <span>✓</span> Request Submitted Successfully
                </div>
                <p style={{ color: '#047857', fontSize: '0.9rem', margin: '0 0 1rem 0', lineHeight: 1.5 }}>
                  {submitLinkingSuccess}
                </p>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    onClick={() => switchTab('history')}
                    className="btn btn--primary btn--sm"
                    style={{ fontWeight: 600 }}
                  >
                    Track in "My Child Linking Requests" →
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setLookupChildResult(null)
                      setSubmitLinkingSuccess(null)
                      setLinkStudentIdInput('')
                    }}
                    className="btn btn--secondary btn--sm"
                  >
                    Link Another Child
                  </button>
                </div>
              </div>
            )}

            {/* STEP 2: Display Student Details & Confirmation Card */}
            {lookupChildResult && !submitLinkingSuccess && (
              <div style={{ border: '1px solid #B9E6FE', borderRadius: '8px', background: '#F0F9FF', padding: '1.5rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem', borderBottom: '1px solid #BAE6FD', paddingBottom: '0.75rem' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0284C7', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Step 2: Review Official Student Details
                    </span>
                    <h3 style={{ fontSize: '1.25rem', color: '#0C4A6E', margin: '0.2rem 0 0 0', fontWeight: 700 }}>
                      {lookupChildResult.student_full_name}
                    </h3>
                  </div>
                  <span className="badge badge--primary" style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.9rem', padding: '0.3rem 0.6rem' }}>
                    {lookupChildResult.student_id}
                  </span>
                </div>

                <p style={{ color: '#0369A1', fontSize: '0.875rem', marginBottom: '1rem' }}>
                  The following details were retrieved directly from the live institution database:
                </p>

                {/* Database details grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', background: '#FFFFFF', padding: '1.25rem', borderRadius: '6px', border: '1px solid #E0F2FE', marginBottom: '1.25rem' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Student Full Name:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.95rem' }}>{lookupChildResult.student_full_name}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Student ID:</span>
                    <strong style={{ color: '#155EEF', fontFamily: 'monospace', fontSize: '0.95rem' }}>{lookupChildResult.student_id}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Permanent Student ID (PSID):</span>
                    <strong style={{ color: '#334155', fontFamily: 'monospace', fontSize: '0.9rem' }}>{lookupChildResult.permanent_student_id}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Institution Name:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.9rem' }}>{lookupChildResult.institution_name}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Institution ID:</span>
                    <strong style={{ color: '#475569', fontFamily: 'monospace', fontSize: '0.85rem' }}>{lookupChildResult.institution_id}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Institution Type:</span>
                    <span style={{ color: '#334155', fontWeight: 600, fontSize: '0.85rem' }}>
                      {(lookupChildResult.institution_type || lookupChildResult.category || 'Accredited Institution').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')}
                    </span>
                  </div>
                  {lookupChildResult.academic_division && (
                    <div>
                      <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Division:</span>
                      <span style={{ display: 'inline-block', padding: '0.2rem 0.6rem', background: '#E0F2FE', color: '#0369A1', borderRadius: '4px', fontWeight: 700, fontSize: '0.85rem', border: '1px solid #BAE6FD' }}>
                        {lookupChildResult.academic_division}
                      </span>
                    </div>
                  )}
                  {/* Tier-specific academic details */}
                  {(() => {
                    const effectiveTier = (
                      lookupChildResult.effective_tier ||
                      (lookupChildResult.academic_division === 'School Division' || (lookupChildResult.standard && lookupChildResult.standard <= 10 && !lookupChildResult.puc_year) ? 'School' : null) ||
                      (lookupChildResult.academic_division === 'PU Division' || lookupChildResult.puc_year || lookupChildResult.standard === 11 || lookupChildResult.standard === 12 ? 'PU College' : null) ||
                      lookupChildResult.institution_tier ||
                      ''
                    ).toLowerCase().replace(/[\s-]/g, '_')
                    if (effectiveTier === 'pu_college') {
                      return (
                        <>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>PUC Year:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.puc_year || lookupChildResult.class_or_standard}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Stream:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.stream || 'Science'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Subject Combination:</span>
                            <strong style={{ color: '#155EEF', fontSize: '0.875rem', fontWeight: 700 }}>{lookupChildResult.subject_combination || 'PCMB'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Section:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Section {lookupChildResult.section || 'A'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Pre-University Board:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.board || 'Dept of Pre-University Education (DPUE)'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Year:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.academic_year || '2026-2027'}</strong>
                          </div>
                        </>
                      )
                    } else if (effectiveTier === 'engineering_college') {
                      return (
                        <>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Degree Programme:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.degree || 'Bachelor of Engineering (B.E.)'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Engineering Branch:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.branch || lookupChildResult.programme || 'Civil Engineering'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Department:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.department || 'Department of Engineering'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Semester / Term:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Semester {lookupChildResult.semester || 1}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Section:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Section {lookupChildResult.section || 'A'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Year:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.academic_year || '2026-2027'}</strong>
                          </div>
                        </>
                      )
                    } else if (effectiveTier === 'degree_college') {
                      return (
                        <>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Degree / Programme:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.degree || lookupChildResult.programme || 'Undergraduate Degree'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Department:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.department || 'Academic Department'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Semester:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Semester {lookupChildResult.semester || 1}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Section:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Section {lookupChildResult.section || 'A'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Year:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.academic_year || '2026-2027'}</strong>
                          </div>
                        </>
                      )
                    } else if (effectiveTier === 'university') {
                      return (
                        <>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>University Programme:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.programme || lookupChildResult.program_or_stream}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Department:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.department || 'Postgraduate Department'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Current Year / Semester:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Year {lookupChildResult.current_year || 1} · Semester {lookupChildResult.semester || 1}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Section:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Section {lookupChildResult.section || 'A'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Year:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.academic_year || '2026-2027'}</strong>
                          </div>
                        </>
                      )
                    } else {
                      return (
                        <>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Class / Standard:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>
                              {lookupChildResult.class_or_standard || `Standard ${lookupChildResult.standard}`}
                            </strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Section:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Section {lookupChildResult.section || 'A'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Board / Curriculum:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.board || 'Karnataka State Board (KSEEB)'}</strong>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Year:</span>
                            <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.academic_year || '2026-2027'}</strong>
                          </div>
                          {lookupChildResult.stream && (
                            <div>
                              <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Stream:</span>
                              <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.stream}</strong>
                            </div>
                          )}
                          {lookupChildResult.subject_combination && (
                            <div>
                              <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Curriculum Program:</span>
                              <strong style={{ color: '#0F172A', fontSize: '0.85rem' }}>{lookupChildResult.subject_combination}</strong>
                            </div>
                          )}
                        </>
                      )
                    }
                  })()}
                </div>

                {lookupChildResult.review_flag && (
                  <div style={{ background: '#FFFBEB', border: '1px solid #FCD34D', borderRadius: '6px', padding: '0.75rem 1rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#92400E', fontSize: '0.85rem' }}>
                    <span>⚠️</span>
                    <span><strong>Administrative Classification Notice:</strong> This enrollment is marked with flag <code>{lookupChildResult.review_flag}</code> for administrative tier alignment review.</span>
                  </div>
                )}

                {/* Already linked check */}
                {lookupChildResult.is_already_linked ? (
                  <div style={{ background: '#FEF3C7', border: '1px solid #FCD34D', borderRadius: '6px', padding: '1rem', color: '#92400E', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <strong>✓ Already Verified:</strong> This child is already verified and linked to your parent account.
                    </div>
                    <button
                      type="button"
                      onClick={() => switchTab('children')}
                      className="btn btn--primary btn--sm"
                    >
                      View on Dashboard →
                    </button>
                  </div>
                ) : (
                  /* Relationship Selection & Actions */
                  <div style={{ borderTop: '1px solid #BAE6FD', paddingTop: '1.25rem' }}>
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontWeight: 600, color: '#0C4A6E', marginBottom: '0.4rem', fontSize: '0.875rem' }}>
                        Select Your Relationship to {lookupChildResult.student_full_name} <span style={{ color: '#b91c1c' }}>*</span>:
                      </label>
                      <select
                        value={linkRelationship}
                        onChange={(e) => setLinkRelationship(e.target.value)}
                        style={{ maxWidth: '280px', padding: '0.6rem 0.85rem', border: '1px solid #94A3B8', borderRadius: '6px', fontWeight: 600, fontSize: '0.9rem', background: '#FFFFFF' }}
                      >
                        <option value="Mother">Mother</option>
                        <option value="Father">Father</option>
                        <option value="Legal Guardian">Legal Guardian</option>
                        <option value="Other Guardian">Other Guardian</option>
                      </select>
                    </div>

                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                      <button
                        type="button"
                        onClick={handleSubmitLinkingRequest}
                        className="btn btn--primary"
                        disabled={isSubmittingLink}
                        style={{ fontWeight: 700 }}
                      >
                        {isSubmittingLink ? 'Submitting to Institution...' : 'Confirm & Submit for Verification →'}
                      </button>
                      <button
                        type="button"
                        onClick={handleResetLookup}
                        className="btn btn--secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        {/* Tab 2: New Linking Request Form — Institution-Wise Student Search */}
        {activeTab === 'new-request' && (
          <div className="card" style={{ maxWidth: '800px', margin: '0 auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', boxShadow: '0 2px 6px rgba(0,0,0,0.04)' }}>
            <div style={{ marginBottom: '1.5rem', borderBottom: '1px solid #e8eaed', paddingBottom: '1rem' }}>
              <div style={{ display: 'inline-block', background: '#EFF4FF', color: '#155EEF', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem', textTransform: 'uppercase' }}>
                Institution-Scoped Linking
              </div>
              <h2 style={{ fontSize: '1.45rem', color: '#1a3a6b', margin: '0 0 0.35rem 0', fontWeight: 700 }}>
                Submit Student-Linking Request
              </h2>
              <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0, lineHeight: 1.4 }}>
                Select your child's accredited educational institution first, then search and select the enrolled student to submit a linking request.
              </p>
            </div>

            {/* STEP 1: SELECT INSTITUTION */}
            <div style={{ marginBottom: '1.75rem', padding: '1.25rem', border: '1px solid #E2E8F0', borderRadius: '8px', background: selectedInstForLinking ? '#F0F9FF' : '#F8FAFC' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Step 1
                  </span>
                  <h3 style={{ fontSize: '1.1rem', color: '#102B46', margin: '0.15rem 0 0 0', fontWeight: 700 }}>
                    Select School / College / University <span style={{ color: '#b91c1c' }}>*</span>
                  </h3>
                </div>
                {selectedInstForLinking && (
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedInstForLinking(null)
                      setDetectedStudent(null)
                      setFormStudentRef('')
                      setInstitutionStudents([])
                      setInstEmptyMessage('')
                      setLookupError('')
                    }}
                    className="btn btn--secondary btn--sm"
                    style={{ fontSize: '0.8rem', fontWeight: 600 }}
                  >
                    Change Institution
                  </button>
                )}
              </div>

              {selectedInstForLinking ? (
                /* Selected Institution Summary Card */
                <div style={{ background: '#FFFFFF', border: '1px solid #B9E6FE', borderRadius: '6px', padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0C4A6E' }}>
                      {selectedInstForLinking.school_name}
                    </div>
                    <div style={{ fontSize: '0.85rem', color: '#0369A1', marginTop: '0.2rem', display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                      <span style={{ fontFamily: 'monospace', fontWeight: 700, background: '#EFF4FF', color: '#155EEF', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                        ID: {selectedInstForLinking.school_id}
                      </span>
                      <span>🏛️ {(selectedInstForLinking.category || selectedInstForLinking.school_type || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')}</span>
                      <span>📍 {selectedInstForLinking.district || 'Karnataka'}, {selectedInstForLinking.state || 'Karnataka'}</span>
                    </div>
                  </div>
                  <span className="badge badge--success" style={{ fontWeight: 700 }}>
                    ✓ Selected
                  </span>
                </div>
              ) : (
                /* Institution Selector Dropdown with Filter */
                <div>
                  <div style={{ marginBottom: '0.75rem' }}>
                    <input
                      type="text"
                      className="input"
                      placeholder="Filter institutions by name, ID (e.g. BMS, SCH001, Ballari)..."
                      value={instFilterTerm}
                      onChange={(e) => setInstFilterTerm(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #CBD5E1', borderRadius: '6px', fontSize: '0.875rem' }}
                    />
                  </div>

                  <select
                    className="input"
                    value=""
                    onChange={(e) => {
                      const found = schools.find(s => s.school_id === e.target.value)
                      if (found) handleSelectInstitution(found)
                    }}
                    style={{ width: '100%', padding: '0.65rem 0.75rem', border: '1px solid #155EEF', borderRadius: '6px', fontSize: '0.9rem', color: '#102B46', background: '#FFFFFF', fontWeight: 600 }}
                  >
                    <option value="">-- Choose School, PU College, Degree College or University ({schools.length} available) --</option>
                    {schools
                      .filter(s => {
                        if (!instFilterTerm.trim()) return true
                        const term = instFilterTerm.toLowerCase()
                        return (
                          s.school_name?.toLowerCase().includes(term) ||
                          s.school_id?.toLowerCase().includes(term) ||
                          s.district?.toLowerCase().includes(term) ||
                          s.school_type?.toLowerCase().includes(term)
                        )
                      })
                      .map(s => (
                        <option key={s.school_id} value={s.school_id}>
                          {s.school_name} [{s.school_id}] — {(s.category || s.school_type || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')} ({s.district || 'Karnataka'})
                        </option>
                      ))}
                  </select>
                  <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.35rem' }}>
                    Select the accredited educational institution where your child is currently enrolled.
                  </div>
                </div>
              )}
            </div>

            {/* STEP 2 & 3: INSTITUTION-SCOPED STUDENT SEARCH & SELECTION */}
            {selectedInstForLinking && (
              <div style={{ marginBottom: '1.75rem', padding: '1.25rem', border: '1px solid #E2E8F0', borderRadius: '8px', background: '#FFFFFF' }}>
                <div style={{ marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                    Step 2 & 3
                  </span>
                  <h3 style={{ fontSize: '1.1rem', color: '#102B46', margin: '0.15rem 0 0 0', fontWeight: 700 }}>
                    Search & Select Enrolled Student in {selectedInstForLinking.school_name}
                  </h3>
                  <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.825rem', color: '#64748B' }}>
                    Only students currently enrolled in <strong>{selectedInstForLinking.school_name}</strong> are displayed.
                  </p>
                </div>

                {/* Search Input within Selected Institution */}
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
                  <input
                    type="text"
                    className="input"
                    placeholder="Search by Student Name, Student ID, or Permanent Student ID (PSID)..."
                    value={studentSearchTerm}
                    onChange={(e) => {
                      const val = e.target.value
                      setStudentSearchTerm(val)
                      handleSearchStudentsInInst(val)
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleSearchStudentsInInst()
                      }
                    }}
                    style={{ flex: 1, padding: '0.625rem 0.75rem', border: '1px solid #CBD5E1', borderRadius: '6px', fontSize: '0.875rem' }}
                  />
                  <button
                    type="button"
                    onClick={() => handleSearchStudentsInInst()}
                    disabled={loadingInstStudents}
                    className="btn btn--secondary"
                    style={{ padding: '0.625rem 1rem', fontSize: '0.85rem', fontWeight: 600, whiteSpace: 'nowrap' }}
                  >
                    {loadingInstStudents ? 'Searching...' : '🔍 Filter'}
                  </button>
                </div>

                {/* Loading State */}
                {loadingInstStudents && (
                  <div style={{ textAlign: 'center', padding: '1.5rem', color: '#64748B' }}>
                    <LoadingSpinner size="sm" />
                    <span style={{ marginLeft: '0.5rem', fontSize: '0.875rem' }}>Retrieving enrolled students from official institution database...</span>
                  </div>
                )}

                {/* Empty State when Institution has 0 students */}
                {!loadingInstStudents && instEmptyMessage && (
                  <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '6px', padding: '1rem', color: '#92400E', fontSize: '0.875rem', textAlign: 'center' }}>
                    ℹ️ <strong>{instEmptyMessage}</strong>
                    <div style={{ fontSize: '0.8rem', color: '#B45309', marginTop: '0.25rem' }}>
                      No cross-institution student records are shown.
                    </div>
                  </div>
                )}

                {/* Lookup / Search Error Message */}
                {!loadingInstStudents && lookupError && !instEmptyMessage && (
                  <div style={{ background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: '6px', padding: '0.75rem 1rem', color: '#B91C1C', fontSize: '0.85rem' }}>
                    ⚠️ {lookupError}
                  </div>
                )}

                {/* Students Results Table */}
                {!loadingInstStudents && institutionStudents.length > 0 && (
                  <div style={{ border: '1px solid #E2E8F0', borderRadius: '6px', overflow: 'hidden', marginTop: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', position: 'sticky', top: 0, zIndex: 10 }}>
                        <tr style={{ textAlign: 'left' }}>
                          <th style={{ padding: '0.6rem 0.75rem' }}>Student ID</th>
                          <th style={{ padding: '0.6rem 0.75rem' }}>Student Name</th>
                          <th style={{ padding: '0.6rem 0.75rem' }}>Class / Programme</th>
                          <th style={{ padding: '0.6rem 0.75rem' }}>Permanent Student ID</th>
                          <th style={{ padding: '0.6rem 0.75rem', textAlign: 'center' }}>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {institutionStudents.map((s) => {
                          const isSelected = detectedStudent?.student_id === s.student_id || detectedStudent?.permanent_student_id === s.permanent_student_id
                          return (
                            <tr
                              key={s.student_id || s.permanent_student_id}
                              style={{
                                borderBottom: '1px solid #F1F5F9',
                                background: isSelected ? '#EFF4FF' : '#FFFFFF',
                                cursor: 'pointer'
                              }}
                              onClick={() => selectStudent(s)}
                            >
                              <td style={{ padding: '0.6rem 0.75rem', fontFamily: 'monospace', fontWeight: 700, color: '#155EEF' }}>
                                {s.student_id}
                              </td>
                              <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#0F172A' }}>
                                {s.student_name}
                              </td>
                              <td style={{ padding: '0.6rem 0.75rem', color: '#475569' }}>
                                {s.standard ? `Class ${s.standard}${s.section ? ' (' + s.section + ')' : ''}` : s.stream || 'Enrolled'}
                              </td>
                              <td style={{ padding: '0.6rem 0.75rem', fontFamily: 'monospace', fontSize: '0.75rem', color: '#64748B' }}>
                                {s.permanent_student_id?.slice(0, 16)}...
                              </td>
                              <td style={{ padding: '0.6rem 0.75rem', textAlign: 'center' }}>
                                <button
                                  type="button"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    selectStudent(s)
                                  }}
                                  className={`btn btn--xs ${isSelected ? 'btn--primary' : 'btn--outline'}`}
                                  style={{ fontWeight: 600 }}
                                >
                                  {isSelected ? '✓ Selected' : 'Select'}
                                </button>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* STEP 4: SELECTED STUDENT & SUBMIT LINKING REQUEST */}
            {detectedStudent && (
              <form onSubmit={handleRequestSubmit}>
                {/* Selected Student Read-Only Card */}
                <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid #DCFCE7', paddingBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#15803D', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <span>✓</span> Selected Enrolled Student Details (Read-Only)
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#166534', background: '#FFFFFF', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #BBF7D0', fontWeight: 600 }}>
                      Verified Active Enrollment
                    </span>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.85rem', fontSize: '0.85rem' }}>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Student Name</span>
                      <strong style={{ color: '#0F172A', fontSize: '1rem' }}>{detectedStudent.student_name}</strong>
                    </div>

                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Student ID</span>
                      <code style={{ color: '#155EEF', fontWeight: 700, fontSize: '0.95rem' }}>{detectedStudent.student_id}</code>
                    </div>

                    <div style={{ gridColumn: 'span 2' }}>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>School / College Name</span>
                      <strong style={{ color: '#102B46', fontSize: '0.95rem' }}>{detectedStudent.institution_name || detectedStudent.school_name}</strong>
                    </div>

                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Institution ID</span>
                      <code style={{ color: '#0F172A', fontWeight: 700 }}>{detectedStudent.institution_id || detectedStudent.school_id}</code>
                    </div>

                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Current Class / Standard</span>
                      <strong>Class {detectedStudent.standard}</strong>
                    </div>

                    {detectedStudent.section && (
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Section / Stream</span>
                        <strong>Section {detectedStudent.section}</strong>
                      </div>
                    )}

                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Enrollment Status</span>
                      <span style={{ color: '#15803D', fontWeight: 700, textTransform: 'capitalize' }}>
                        {detectedStudent.enrollment_status || 'Active'}
                      </span>
                    </div>

                    <div style={{ gridColumn: 'span 2' }}>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block', fontWeight: 500 }}>Permanent Student ID (PSID)</span>
                      <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#475569', wordBreak: 'break-all' }}>{detectedStudent.permanent_student_id}</span>
                    </div>
                  </div>
                </div>

                {/* Relationship to Student */}
                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                    Relationship to Student <span style={{ color: '#b91c1c' }}>*</span>
                  </label>
                  <select
                    required
                    className="input"
                    value={formRelationship}
                    onChange={e => setFormRelationship(e.target.value)}
                    style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.875rem' }}
                  >
                    <option value="Father">Father</option>
                    <option value="Mother">Mother</option>
                    <option value="Legal Guardian">Legal Guardian</option>
                  </select>
                </div>

                {/* Additional Notes */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                    Additional Notes for School Verification Staff <span style={{ color: '#64748B', fontWeight: 400 }}>(Optional)</span>
                  </label>
                  <textarea
                    className="input"
                    rows={3}
                    placeholder="e.g. Any relevant notes regarding admission roll, contact info, or verification details"
                    value={formNotes}
                    onChange={e => setFormNotes(e.target.value)}
                    style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #D0D5DD', borderRadius: '6px', resize: 'vertical', fontSize: '0.875rem' }}
                  />
                </div>

                {/* Action Buttons */}
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="btn btn--primary btn--lg"
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', background: '#155EEF', borderColor: '#155EEF' }}
                  >
                    {submitting ? <LoadingSpinner size="sm" /> : 'Submit for School Staff Review →'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setDetectedStudent(null)
                      setFormStudentRef('')
                    }}
                    className="btn btn--ghost btn--lg"
                  >
                    Clear Student
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        {/* Tab 3: Request History */}
        {activeTab === 'history' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#1a3a6b', fontWeight: 700 }}>
                  My Child Linking Requests
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', color: '#64748B', fontSize: '0.85rem' }}>
                  Track the verification status of student-linking requests submitted to educational institutions.
                </p>
              </div>
              <button onClick={() => switchTab('link-child')} className="btn btn--primary btn--sm" style={{ fontWeight: 600 }}>
                + Submit New Linking Request
              </button>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
              </div>
            ) : requests.length === 0 ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📂</div>
                <h3 style={{ color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>No Linking Requests Submitted</h3>
                <p style={{ color: '#4b5563', margin: '0 0 1rem 0' }}>You have not submitted any child linking requests yet.</p>
                <button onClick={() => switchTab('link-child')} className="btn btn--primary">
                  Link My Child Now →
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {requests.map(r => {
                  const status = (r.request_status || r.status || '').toLowerCase()
                  const isApproved = status === 'approved'
                  const isRejected = status === 'rejected'
                  const isClarify = status === 'clarification_required'
                  const isPendingReview = status === 'pending_review'
                  const isPending = status === 'pending'

                  return (
                    <div
                      key={r.request_id}
                      className="card"
                      style={{
                        padding: '1.25rem 1.5rem',
                        border: isApproved ? '1px solid #A7F3D0' : isRejected ? '1px solid #FCA5A5' : isClarify ? '1px solid #FCD34D' : isPendingReview ? '1px solid #BAE6FD' : '1px solid #E2E8F0',
                        borderRadius: '10px',
                        background: '#FFFFFF',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.85rem' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                            <h4 style={{ margin: 0, fontSize: '1.15rem', color: '#102B46', fontWeight: 700 }}>
                              {r.student_name || r.student_ref}
                            </h4>
                            <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.85rem', background: '#EFF8FF', color: '#175CD3', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                              ID: {r.student_id || r.student_ref}
                            </span>
                            {r.permanent_student_id && (
                              <span style={{ fontFamily: 'monospace', fontSize: '0.78rem', color: '#64748B' }}>
                                PSID: {r.permanent_student_id}
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#475467', marginTop: '0.25rem' }}>
                            🏛️ <strong>{r.institution_name || r.school_name || r.school_id}</strong> · {r.institution_type || 'Accredited Institution'}
                            {r.class_or_standard && ` · ${r.class_or_standard}`}
                            {r.program_or_stream && ` · ${r.program_or_stream}`}
                          </div>
                        </div>

                        <div>
                          {isApproved && (
                            <span style={{ background: '#ECFDF5', color: '#027A48', border: '1px solid #A7F3D0', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ✓ VERIFIED & APPROVED
                            </span>
                          )}
                          {isRejected && (
                            <span style={{ background: '#FEF2F2', color: '#B42318', border: '1px solid #FCA5A5', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ✕ REJECTED
                            </span>
                          )}
                          {isClarify && (
                            <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FCD34D', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ⚠️ CLARIFICATION REQUIRED
                            </span>
                          )}
                          {isPendingReview && (
                            <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ⏳ PENDING REVIEW
                            </span>
                          )}
                          {isPending && (
                            <span style={{ background: '#F2F4F7', color: '#344054', border: '1px solid #D0D5DD', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              🕒 PENDING APPROVAL
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Request details row */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', background: '#F8FAFC', padding: '0.75rem 1rem', borderRadius: '6px', fontSize: '0.825rem', marginBottom: '0.85rem' }}>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Relationship Claimed:</span>
                          <strong>{r.relationship || r.relationship_type || 'Parent'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Request Submitted:</span>
                          <strong>{r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recent'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Decision / Review Date:</span>
                          <strong>{r.decision_date || r.reviewed_at ? new Date(r.decision_date || r.reviewed_at).toLocaleDateString() : 'Awaiting Review'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Request Reference ID:</span>
                          <span style={{ fontFamily: 'monospace' }}>{r.request_id.slice(0, 8)}...</span>
                        </div>
                      </div>

                      {/* Status-specific banners and interactions */}
                      {isApproved && (
                        <div style={{ background: '#ECFDF5', border: '1px solid #D1FADF', borderRadius: '6px', padding: '0.85rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                          <div>
                            <span style={{ color: '#027A48', fontWeight: 600, fontSize: '0.85rem' }}>
                              ✓ Approved by Institution Administrator. Your child's academic dashboard and official records are verified and active.
                            </span>
                            {r.reviewer_comment && (
                              <div style={{ fontSize: '0.8rem', color: '#065F46', marginTop: '0.2rem' }}>
                                Remarks: "{r.reviewer_comment}"
                              </div>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => switchTab('children')}
                            className="btn btn--primary btn--sm"
                            style={{ fontWeight: 600 }}
                          >
                            Open Child Academic Dashboard →
                          </button>
                        </div>
                      )}

                      {isRejected && (
                        <div style={{ background: '#FEF2F2', border: '1px solid #FEE4E2', borderRadius: '6px', padding: '0.85rem 1rem' }}>
                          <div style={{ color: '#B42318', fontWeight: 700, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                            ✕ Linking Request Not Approved by {r.institution_name || r.school_name || 'Institution'}
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#991B1B', lineHeight: 1.5 }}>
                            <strong>Rejection Reason:</strong> {r.rejection_reason || 'Verification requirements not satisfied.'}
                          </div>
                          {r.reviewer_comment && r.reviewer_comment !== r.rejection_reason && (
                            <div style={{ fontSize: '0.825rem', color: '#7F1D1D', marginTop: '0.25rem' }}>
                              <strong>Administrator Remarks:</strong> {r.reviewer_comment}
                            </div>
                          )}
                          <div style={{ fontSize: '0.78rem', color: '#B42318', marginTop: '0.4rem' }}>
                            ⚠️ Access to this student's records remains restricted. If you believe this is an error, please contact the institution office directly.
                          </div>
                        </div>
                      )}

                      {isClarify && (
                        <div style={{ background: '#FFFAEB', border: '1px solid #FEF0C7', borderRadius: '6px', padding: '1rem' }}>
                          <div style={{ color: '#B54708', fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                            ⚠️ Institution Requests Clarification
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#7A2E0E', marginBottom: '0.85rem', background: '#FFFFFF', padding: '0.65rem 0.85rem', borderRadius: '6px', border: '1px solid #FEDF89' }}>
                            <strong>Institution Remarks / Instructions:</strong> {r.reviewer_comment || 'Please provide additional documentation confirming your relationship.'}
                          </div>

                          {clarificationFeedback[r.request_id] && (
                            <div style={{ marginBottom: '0.75rem', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.85rem', background: clarificationFeedback[r.request_id].type === 'success' ? '#ECFDF5' : '#FEF2F2', color: clarificationFeedback[r.request_id].type === 'success' ? '#027A48' : '#B42318' }}>
                              {clarificationFeedback[r.request_id].message}
                            </div>
                          )}

                          <div>
                            <label style={{ display: 'block', fontWeight: 600, color: '#475467', fontSize: '0.825rem', marginBottom: '0.35rem' }}>
                              Your Clarification Response / Documentation Details:
                            </label>
                            <textarea
                              rows={3}
                              value={clarificationResponses[r.request_id] || ''}
                              onChange={(e) => setClarificationResponses(prev => ({ ...prev, [r.request_id]: e.target.value }))}
                              placeholder="Enter your response, explanation, or document reference numbers requested by the institution..."
                              style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', fontFamily: 'inherit', resize: 'vertical', boxSizing: 'border-box' }}
                              disabled={submittingClarificationId === r.request_id}
                            />
                            <button
                              type="button"
                              onClick={() => handleRespondClarification(r.request_id)}
                              disabled={submittingClarificationId === r.request_id || !(clarificationResponses[r.request_id] || '').trim()}
                              className="btn btn--primary btn--sm"
                              style={{ marginTop: '0.5rem', fontWeight: 700 }}
                            >
                              {submittingClarificationId === r.request_id ? 'Submitting Clarification...' : 'Submit Response to Institution →'}
                            </button>
                          </div>
                        </div>
                      )}

                      {isPendingReview && (
                        <div style={{ background: '#EFF8FF', border: '1px solid #B2DDFF', borderRadius: '6px', padding: '0.85rem 1rem' }}>
                          <div style={{ color: '#175CD3', fontWeight: 700, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                            ⏳ Clarification Under Institution Review
                          </div>
                          {r.parent_response && (
                            <div style={{ fontSize: '0.85rem', color: '#1E40AF', marginTop: '0.25rem', background: '#FFFFFF', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #D1E9FF' }}>
                              <strong>Your Submitted Response:</strong> "{r.parent_response}"
                            </div>
                          )}
                          <div style={{ fontSize: '0.78rem', color: '#475467', marginTop: '0.35rem' }}>
                            The institution has received your response and is re-evaluating your linking request.
                          </div>
                        </div>
                      )}

                      {isPending && (
                        <div style={{ background: '#F8FAFC', border: '1px solid #EAECF0', borderRadius: '6px', padding: '0.75rem 1rem', color: '#475467', fontSize: '0.85rem' }}>
                          🕒 <strong>Awaiting Institution Review:</strong> Your request is queued for administrative verification at {r.institution_name || r.school_name || 'the institution'}. You will receive a notification once decided.
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* TAB 4: Admission Applications */}
        {activeTab === 'admissions' && (
          <div>
            {/* Claim Application Card */}
            <div className="card" style={{ padding: '1.25rem 1.5rem', border: '1px solid #d0d5dd', borderRadius: '10px', marginBottom: '1.5rem', background: '#f8fafc' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ margin: '0 0 0.25rem 0', fontSize: '1rem', color: '#102B46', fontWeight: 700 }}>
                    🔗 Claim / Link an External Application
                  </h3>
                  <p style={{ margin: 0, fontSize: '0.825rem', color: '#64748B' }}>
                    Submitted a Stage 1 application without logging in? Enter your Application ID to track it here.
                  </p>
                </div>
                <form onSubmit={handleClaimApplication} style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Application ID (APP-...)"
                    value={claimIdInput}
                    onChange={(e) => setClaimIdInput(e.target.value)}
                    style={{ padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', minWidth: '180px', fontFamily: 'monospace' }}
                  />
                  <input
                    type="text"
                    placeholder="Applicant Full Name"
                    value={claimApplicantNameInput}
                    onChange={(e) => setClaimApplicantNameInput(e.target.value)}
                    style={{ padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', minWidth: '160px' }}
                  />
                  <PasswordInput
                    placeholder="Parent Account Password"
                    value={claimPasswordInput}
                    onChange={(e) => setClaimPasswordInput(e.target.value)}
                    containerStyle={{ width: 'auto', display: 'inline-block' }}
                    style={{ padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', minWidth: '160px' }}
                  />
                  <button
                    type="submit"
                    disabled={claiming}
                    style={{ background: '#102B46', color: '#ffffff', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}
                  >
                    {claiming ? 'Verifying & Linking...' : 'Verify & Link'}
                  </button>
                </form>
              </div>
              {claimStatusMsg && (
                <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: claimStatusMsg.type === 'success' ? '#027A48' : '#B42318' }}>
                  {claimStatusMsg.type === 'success' ? '✓ ' : '⚠️ '} {claimStatusMsg.text}
                </div>
              )}
            </div>

            {/* Applications List */}
            {loadingAdmissions ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.75rem', color: '#64748B' }}>Retrieving admission applications...</p>
              </div>
            ) : admissionApps.length === 0 ? (
              <div className="card" style={{ padding: '3rem 1.5rem', textAlign: 'center', border: '1px dashed #CBD5E1', borderRadius: '10px', background: '#ffffff', color: '#64748B' }}>
                <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: '0.5rem' }}>📋</span>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#102B46' }}>No Admission Applications Found</h3>
                <p style={{ margin: '0 0 1.25rem 0', fontSize: '0.9rem' }}>
                  You have not submitted any Stage 1 preliminary admission applications yet.
                </p>
                <Link to="/schools" style={{ display: 'inline-block', background: '#155EEF', color: '#ffffff', padding: '0.6rem 1.25rem', borderRadius: '8px', fontWeight: 600, textDecoration: 'none', fontSize: '0.9rem' }}>
                  Browse Institutions to Apply →
                </Link>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {admissionApps.map(app => (
                  <div key={app.application_id} className="card" style={{
                    padding: '1.5rem',
                    border: '1px solid #d0d5dd',
                    borderRadius: '12px',
                    background: '#ffffff',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.03)'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid #F1F5F9', paddingBottom: '1rem', marginBottom: '1rem' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                          <span style={{ background: '#F1F5F9', color: '#475569', fontSize: '0.75rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', textTransform: 'uppercase' }}>
                            {app.education_level?.replace('_', ' ')}
                          </span>
                          <span style={{ fontFamily: 'monospace', fontSize: '0.85rem', fontWeight: 700, color: '#102B46' }}>
                            {app.application_id}
                          </span>
                        </div>
                        <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#102B46', fontWeight: 800 }}>
                          {app.institution_name || app.institution_id}
                        </h3>
                        <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.825rem', color: '#64748B' }}>
                          Submitted on {app.created_at ? new Date(app.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Recent'} • Academic Cycle {app.academic_year || '2026-2027'}
                        </p>
                      </div>

                      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                        {app.status === 'submitted' && <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>Submitted (Pending Review)</span>}
                        {app.status === 'under_review' && <span style={{ background: '#F8F9FC', color: '#3E4784', border: '1px solid #D5D9EB', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>Under Review</span>}
                        {app.status === 'action_required' && <span style={{ background: '#FFFAEB', color: '#B54708', border: '1px solid #FEDF89', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>⚠️ Clarification Needed</span>}
                        {app.status === 'approved' && <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✓ Stage 1 Approved</span>}
                        {app.status === 'stage2_submitted' && <span style={{ background: '#F0F9FF', color: '#026AA2', border: '1px solid #B9E6FE', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>📋 Stage 2 Submitted</span>}
                        {app.status === 'documents_uploaded' && <span style={{ background: '#EEF4FF', color: '#3538CD', border: '1px solid #C7D7FE', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>📁 Documents Uploaded</span>}
                        {(app.status === 'detailed_review_completed' || app.status === 'documents_verified') && <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✓ Stage 2 Verified</span>}
                        {(app.status === 'final_admission_confirmed' || app.status === 'enrolled') && <span style={{ background: '#FDF4FF', color: '#C11574', border: '1px solid #FCCEEE', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>🎓 Enrolled</span>}
                        {app.status === 'rejected' && <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✕ Not Approved</span>}
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', fontSize: '0.875rem', marginBottom: '1rem' }}>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Applicant</span>
                        <strong>{app.applicant_name}</strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Standard / Offering</span>
                        <strong>
                          {app.education_level === 'school' && `Standard ${app.requested_standard} (Lang: ${app.first_language_preference || 'Kannada'})`}
                          {app.education_level === 'higher_secondary' && `PU: ${app.combination_code || app.stream_preference}`}
                          {(app.education_level === 'diploma' || app.education_level === 'undergraduate') && (app.requested_program_id || 'Degree Programme')}
                        </strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Registered Phone</span>
                        <strong>{app.parent_phone}</strong>
                      </div>
                    </div>

                    {/* Action Required Box */}
                    {app.status === 'action_required' && (
                      <div style={{ background: '#FFFAEB', border: '1px solid #FEDF89', borderRadius: '8px', padding: '1rem', marginTop: '1rem' }}>
                        <div style={{ fontWeight: 700, color: '#B54708', marginBottom: '0.35rem', fontSize: '0.9rem' }}>
                          💬 Institution Review Desk Request:
                        </div>
                        <p style={{ margin: '0 0 0.75rem 0', color: '#78350F', fontSize: '0.875rem' }}>
                          "{app.clarification_request || app.clarification_message || 'The school review desk has requested additional information regarding your preliminary submission.'}"
                        </p>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                          <input
                            type="text"
                            placeholder="Type your response to the school..."
                            value={clarifyReplyMap[app.application_id] || ''}
                            onChange={(e) => setClarifyReplyMap(prev => ({ ...prev, [app.application_id]: e.target.value }))}
                            style={{ flex: 1, minWidth: '240px', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #FEDF89', fontSize: '0.85rem' }}
                          />
                          <button
                            onClick={() => handleSendClarificationReply(app.application_id)}
                            disabled={replySubmittingId === app.application_id}
                            style={{ background: '#B54708', color: '#ffffff', border: 'none', padding: '0.5rem 1rem', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}
                          >
                            {replySubmittingId === app.application_id ? 'Sending...' : 'Send Response'}
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Approved Banner - Actionable for Stage 2 */}
                    {app.status === 'approved' && (
                      <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#027A48', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                              🎉 Preliminary Eligibility Confirmed: Stage 1 Approved!
                            </div>
                            <p style={{ margin: 0, color: '#05603A', fontSize: '0.85rem' }}>
                              Your Stage 1 preliminary application has been approved. Please complete Stage 2 to provide student demographics, previous schooling history, and upload required certificates for verification.
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setSelectedStage2AppId(app.application_id)}
                            style={{ background: '#027A48', color: '#ffffff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', fontSize: '0.875rem', whiteSpace: 'nowrap' }}
                          >
                            Complete Stage 2 Dossier & Uploads →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Stage 2 Submitted / Documents Uploaded Banner */}
                    {(app.status === 'stage2_submitted' || app.status === 'documents_uploaded') && (
                      <div style={{ background: '#F0F9FF', border: '1px solid #B9E6FE', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#026AA2', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                              📋 Stage 2 Dossier & Documents Under Review
                            </div>
                            <p style={{ margin: 0, color: '#026AA2', fontSize: '0.85rem' }}>
                              Your detailed demographics and uploaded documents are currently being verified by the admissions desk staff. You can view or add more certificates if requested.
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setSelectedStage2AppId(app.application_id)}
                            style={{ background: '#026AA2', color: '#ffffff', border: 'none', padding: '0.55rem 1.1rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem', whiteSpace: 'nowrap' }}
                          >
                            Manage Documents & Dossier →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Stage 2 Verified Banner */}
                    {(app.status === 'detailed_review_completed' || app.status === 'documents_verified') && (
                      <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#027A48', fontSize: '0.875rem' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                          ✓ Documents & Stage 2 Dossier Verified
                        </div>
                        <p style={{ margin: 0, color: '#05603A', fontSize: '0.85rem' }}>
                          All required institutional certificates have been verified by the admissions desk. Awaiting final seat allotment and student enrolment.
                        </p>
                      </div>
                    )}

                    {/* Final Admission Confirmed & Enrolled Banner */}
                    {(app.status === 'final_admission_confirmed' || app.status === 'enrolled') && (
                      <div style={{ background: '#FDF4FF', border: '1px solid #FCCEEE', borderRadius: '10px', padding: '1.25rem', marginTop: '1rem', color: '#701A75', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '1.1rem' }}>🎓</span>
                              <strong style={{ fontSize: '1rem', color: '#4A044E' }}>
                                Official Admission Confirmed & Student Enrolled!
                              </strong>
                            </div>
                            <p style={{ margin: '0 0 0.5rem 0', color: '#86198F', fontSize: '0.85rem' }}>
                              Your child has been allotted a permanent institutional seat. The official student ledger and academic enrollment record are live.
                            </p>
                            {app.enrolled_student_id && (
                              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: '#ffffff', padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid #F5D0FE' }}>
                                <span style={{ fontSize: '0.75rem', color: '#701A75', fontWeight: 600 }}>PERMANENT STUDENT ID:</span>
                                <code style={{ fontSize: '0.85rem', fontWeight: 800, color: '#4A044E' }}>{app.enrolled_student_id}</code>
                              </div>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => switchTab('children')}
                            style={{ background: '#701A75', color: '#ffffff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
                          >
                            View Child in Student Portal →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Rejected Banner */}
                    {app.status === 'rejected' && (
                      <div style={{ background: '#FEF3F2', border: '1px solid #FECDCA', borderRadius: '8px', padding: '1rem', marginTop: '1rem', color: '#B42318', fontSize: '0.875rem' }}>
                        <div><strong>Official Reason:</strong> {app.rejection_reason || 'Seat quota full or catchment criteria not satisfied.'}</div>
                        {app.rejection_explanation && <div style={{ marginTop: '0.25rem', fontSize: '0.825rem', color: '#7A271A' }}>{app.rejection_explanation}</div>}
                        {app.institution_contact_phone && <div style={{ marginTop: '0.25rem', fontSize: '0.825rem' }}>For inquiries: 📞 <strong>{app.institution_contact_phone}</strong></div>}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Modal: Child Academic Records & Student Performance */}
        {selectedChild && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000, backdropFilter: 'blur(2px)' }}>
            <div className="card" style={{ maxWidth: '960px', width: '100%', maxHeight: '92vh', overflowY: 'auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '12px', background: '#ffffff', position: 'relative', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #e8eaed', paddingBottom: '1rem', marginBottom: '1.25rem' }}>
                <div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                    <span className="badge badge--success" style={{ fontWeight: 700 }}>OFFICIAL VERIFIED LEDGER</span>
                    <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>
                      PSID: <code style={{ color: '#0f172a', fontWeight: 700 }}>{selectedChild.permanent_student_id}</code>
                    </span>
                    {selectedChild.student_id && (
                      <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>
                        Student ID: <code style={{ color: '#0f172a', fontWeight: 700 }}>{selectedChild.student_id}</code>
                      </span>
                    )}
                  </div>
                  <h2 style={{ fontSize: '1.65rem', color: '#1a3a6b', margin: '0.2rem 0', fontWeight: 800 }}>
                    {selectedChild.student_name}
                  </h2>
                  <p style={{ margin: 0, color: '#475467', fontSize: '0.875rem' }}>
                    🏫 <strong>{selectedChild.school_name || selectedChild.school_id}</strong> · Class <strong>{selectedChild.standard}-{selectedChild.section}</strong> · Status: <span style={{ color: '#027a48', fontWeight: 600 }}>{selectedChild.enrollment_status || 'Active'}</span>
                  </p>
                </div>
                <button
                  onClick={() => setSelectedChild(null)}
                  style={{ background: '#f1f5f9', border: 'none', width: '36px', height: '36px', borderRadius: '18px', fontSize: '1.1rem', cursor: 'pointer', color: '#475467', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  title="Close Record Viewer"
                >
                  ✕
                </button>
              </div>

              {loadingRecords ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}>
                  <LoadingSpinner />
                  <p style={{ marginTop: '0.75rem', color: '#6b7280', fontSize: '0.9rem' }}>Fetching authenticated academic & attendance records from institution ledger...</p>
                </div>
              ) : recordsError ? (
                <Alert type="error" title="Access Error">{recordsError}</Alert>
              ) : (
                <div>
                  {/* Modal Navigation: 8 Required Sections */}
                  <div style={{ display: 'flex', gap: '0.35rem', borderBottom: '2px solid #f1f5f9', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                    {[
                      { id: 'profile', label: '1. Student Profile' },
                      { id: 'school', label: '2. School Information' },
                      { id: 'attendance', label: '3. Attendance' },
                      { id: 'examinations', label: '4. Examination Details' },
                      { id: 'results', label: '5. Academic Results & Marks' },
                      { id: 'fees', label: '6. Fees & Payments' },
                      { id: 'announcements', label: '7. Announcements' },
                      { id: 'other', label: '8. Other Information' },
                    ].map(tab => (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => setRecordModalTab(tab.id)}
                        style={{
                          padding: '0.55rem 0.85rem',
                          fontSize: '0.825rem',
                          fontWeight: recordModalTab === tab.id ? 700 : 500,
                          border: 'none',
                          background: recordModalTab === tab.id ? '#eff6ff' : 'none',
                          borderRadius: '4px 4px 0 0',
                          cursor: 'pointer',
                          color: recordModalTab === tab.id ? '#1a3a6b' : '#64748b',
                          borderBottom: recordModalTab === tab.id ? '3px solid #1a3a6b' : '3px solid transparent',
                          marginBottom: '-2px',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>

                  {/* TAB 1: STUDENT PROFILE */}
                  {recordModalTab === 'profile' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          Official Student Profile
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Verified student demographic and institutional enrollment record from Department of School Education.
                        </p>
                      </div>

                      <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', background: '#ffffff', marginBottom: '1.25rem' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                          <tbody>
                            <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                              <td style={{ padding: '0.75rem 1rem', width: '35%', color: '#475467', fontWeight: 600 }}>Full Name of Student</td>
                              <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#0f172a' }}>{childRecords?.student?.student_name || selectedChild.student_name}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Student ID</td>
                              <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#1a3a6b' }}>{childRecords?.student?.student_id || selectedChild.student_id || 'N/A'}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Permanent Student ID (PSID)</td>
                              <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#0f172a' }}>{childRecords?.student?.permanent_student_id || selectedChild.permanent_student_id}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Enrolled Institution</td>
                              <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{childRecords?.student?.school_name || childRecords?.school?.school_name || selectedChild.school_name || selectedChild.school_id}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>School Code / Institution ID</td>
                              <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 600 }}>{childRecords?.student?.school_id || selectedChild.school_id}</td>
                            </tr>
                            {/* Tier-specific academic parameters */}
                            {((childRecords?.student?.institution_tier || selectedChild.institution_tier || (selectedChild.school_type === 'PU College' ? 'pu_college' : 'school')) === 'pu_college') ? (
                              <>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>PUC Academic Year</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#102B46' }}>{childRecords?.student?.puc_year || selectedChild.puc_year || selectedChild.class_or_standard || '1st PUC'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Academic Stream</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>{childRecords?.student?.stream || selectedChild.stream || 'Science'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Subject Combination</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#155EEF', fontFamily: 'monospace' }}>{childRecords?.student?.subject_combination || selectedChild.subject_combination || 'PCMB'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Section / Division</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Section {childRecords?.student?.section || selectedChild.section || 'A'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Pre-University Board</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{childRecords?.student?.board || selectedChild.board || 'Dept of Pre-University Education (DPUE)'}</td>
                                </tr>
                              </>
                            ) : ((childRecords?.student?.institution_tier || selectedChild.institution_tier) === 'engineering_college') ? (
                              <>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Degree Programme</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#102B46' }}>{childRecords?.student?.degree || selectedChild.degree || 'Bachelor of Engineering (B.E.)'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Engineering Branch</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>{childRecords?.student?.branch || selectedChild.branch || childRecords?.student?.programme || selectedChild.programme || 'Civil Engineering'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Department</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{childRecords?.student?.department || selectedChild.department || 'Department of Engineering'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Semester / Section</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Semester {childRecords?.student?.semester || selectedChild.semester || 1} · Section {childRecords?.student?.section || selectedChild.section || 'A'}</td>
                                </tr>
                              </>
                            ) : ((childRecords?.student?.institution_tier || selectedChild.institution_tier) === 'degree_college' || (childRecords?.student?.institution_tier || selectedChild.institution_tier) === 'university') ? (
                              <>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Degree / Programme</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#102B46' }}>{childRecords?.student?.degree || childRecords?.student?.programme || selectedChild.degree || selectedChild.programme || 'Degree Programme'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Department</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{childRecords?.student?.department || selectedChild.department || 'Academic Department'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Semester / Section</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Semester {childRecords?.student?.semester || selectedChild.semester || 1} · Section {childRecords?.student?.section || selectedChild.section || 'A'}</td>
                                </tr>
                              </>
                            ) : (
                              <>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Current Standard / Class</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>{childRecords?.student?.class_or_standard || selectedChild.class_or_standard || `Standard ${childRecords?.student?.standard || selectedChild.standard}`}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Section</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>Section {childRecords?.student?.section || selectedChild.section || 'A'}</td>
                                </tr>
                                <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Board / Curriculum</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{childRecords?.student?.board || childRecords?.student?.curriculum_or_board || selectedChild.board || 'Karnataka State Board (KSEEB)'}</td>
                                </tr>
                              </>
                            )}
                            <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>First Language / Medium</td>
                              <td style={{ padding: '0.75rem 1rem' }}>{childRecords?.student?.first_language || selectedChild.first_language || 'Kannada'}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Date of Birth</td>
                              <td style={{ padding: '0.75rem 1rem' }}>{childRecords?.student?.date_of_birth || 'Not specified'}</td>
                            </tr>
                            <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Gender</td>
                              <td style={{ padding: '0.75rem 1rem', textTransform: 'capitalize' }}>{childRecords?.student?.gender || 'Not specified'}</td>
                            </tr>
                            <tr>
                              <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Enrollment Status</td>
                              <td style={{ padding: '0.75rem 1rem' }}>
                                <span className="badge badge--success" style={{ textTransform: 'capitalize', fontWeight: 700 }}>
                                  {childRecords?.student?.enrollment_status || selectedChild.enrollment_status || 'Active'}
                                </span>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {/* TAB 2: SCHOOL INFORMATION */}
                  {recordModalTab === 'school' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          School & Institution Information
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Official school affiliation, address, administrative jurisdiction, and contact records.
                        </p>
                      </div>

                      {!childRecords?.school ? (
                        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '1rem 0' }}>
                          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>ℹ️</div>
                          <p style={{ color: '#475467', fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                            Information is currently unavailable because records have not yet been added.
                          </p>
                        </div>
                      ) : (
                        <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden', background: '#ffffff', marginBottom: '1.25rem' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                            <tbody>
                              <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                <td style={{ padding: '0.75rem 1rem', width: '35%', color: '#475467', fontWeight: 600 }}>School Name</td>
                                <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#1a3a6b' }}>{childRecords.school.school_name}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>School ID / Institution Code</td>
                                <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700 }}>{childRecords.school.school_id}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>District & State</td>
                                <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{childRecords.school.district || 'Karnataka'}, {childRecords.school.state || 'Karnataka'}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>School Type</td>
                                <td style={{ padding: '0.75rem 1rem', textTransform: 'capitalize' }}>{childRecords.school.school_type || 'Government School'}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Affiliation Board</td>
                                <td style={{ padding: '0.75rem 1rem' }}>{childRecords.school.affiliation || childRecords.school.affiliation_board || 'Karnataka State Examination and Assessment Board (KSEAB)'}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Recognition Status</td>
                                <td style={{ padding: '0.75rem 1rem' }}>{childRecords.school.recognition || childRecords.school.recognition_status || 'Recognized by Department of School Education'}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7', background: '#f8fafc' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Address</td>
                                <td style={{ padding: '0.75rem 1rem' }}>{childRecords.school.address || 'Karnataka, India'} {childRecords.school.pincode ? `— PIN: ${childRecords.school.pincode}` : ''}</td>
                              </tr>
                              <tr style={{ borderBottom: '1px solid #edf2f7' }}>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Public Phone</td>
                                <td style={{ padding: '0.75rem 1rem' }}>{childRecords.school.public_phone || childRecords.school.phone || 'N/A'}</td>
                              </tr>
                              <tr>
                                <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>Official Website</td>
                                <td style={{ padding: '0.75rem 1rem' }}>
                                  {childRecords.school.website ? (
                                    <a href={childRecords.school.website} target="_blank" rel="noopener noreferrer" style={{ color: '#155eef', textDecoration: 'underline' }}>
                                      {childRecords.school.website}
                                    </a>
                                  ) : 'N/A'}
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 3: ATTENDANCE */}
                  {recordModalTab === 'attendance' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          Student Attendance Ledger
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Daily attendance records recorded by classroom teachers and verified by institution administration.
                        </p>
                      </div>

                      {(!childRecords?.attendance_summary || childRecords.attendance_summary.total_working_days == null || childRecords.attendance_summary.total_working_days === 0) ? (
                        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '1rem 0' }}>
                          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>ℹ️</div>
                          <p style={{ color: '#475467', fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                            Information is currently unavailable because records have not yet been added.
                          </p>
                        </div>
                      ) : (
                        <div>
                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
                            <div style={{ background: '#ecfdf5', border: '1px solid #a7f3d0', padding: '0.75rem', borderRadius: '6px', textAlign: 'center' }}>
                              <div style={{ fontSize: '0.75rem', color: '#047857', fontWeight: 600 }}>ATTENDANCE RATE</div>
                              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#065f46' }}>{childRecords.attendance_summary.attendance_percentage}%</div>
                            </div>
                            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', padding: '0.75rem', borderRadius: '6px', textAlign: 'center' }}>
                              <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>WORKING DAYS</div>
                              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e293b' }}>{childRecords.attendance_summary.total_working_days}</div>
                            </div>
                            <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '0.75rem', borderRadius: '6px', textAlign: 'center' }}>
                              <div style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: 600 }}>PRESENT</div>
                              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#15803d' }}>{childRecords.attendance_summary.present_days}</div>
                            </div>
                            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '0.75rem', borderRadius: '6px', textAlign: 'center' }}>
                              <div style={{ fontSize: '0.75rem', color: '#dc2626', fontWeight: 600 }}>ABSENT</div>
                              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#b91c1c' }}>{childRecords.attendance_summary.absent_days}</div>
                            </div>
                            <div style={{ background: '#fffbeb', border: '1px solid #fde68a', padding: '0.75rem', borderRadius: '6px', textAlign: 'center' }}>
                              <div style={{ fontSize: '0.75rem', color: '#d97706', fontWeight: 600 }}>APPROVED LEAVE</div>
                              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#b45309' }}>{childRecords.attendance_summary.leave_days}</div>
                            </div>
                          </div>

                          {childRecords.attendance_summary.monthly_breakdown && childRecords.attendance_summary.monthly_breakdown.length > 0 && (
                            <div style={{ marginBottom: '1.25rem' }}>
                              <h5 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.9rem', fontWeight: 700 }}>Monthly Attendance Breakdown</h5>
                              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                {childRecords.attendance_summary.monthly_breakdown.map((m, idx) => (
                                  <div key={idx} style={{ padding: '0.4rem 0.75rem', background: '#f1f5f9', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid #e2e8f0' }}>
                                    <strong>{m.month}:</strong> {m.present}/{m.total_recorded} days ({m.attendance_percentage}%)
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {childRecords?.attendance && childRecords.attendance.length > 0 && (
                            <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
                              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                                <thead>
                                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                    <th style={{ padding: '0.5rem 0.75rem' }}>Date</th>
                                    <th style={{ padding: '0.5rem 0.75rem' }}>Subject / Session</th>
                                    <th style={{ padding: '0.5rem 0.75rem' }}>Status</th>
                                    <th style={{ padding: '0.5rem 0.75rem' }}>Remarks</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {childRecords.attendance.slice(0, 15).map((att, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                      <td style={{ padding: '0.5rem 0.75rem', fontWeight: 600 }}>{att.attendance_date}</td>
                                      <td style={{ padding: '0.5rem 0.75rem' }}>{att.subject_name || 'Daily Attendance'}</td>
                                      <td style={{ padding: '0.5rem 0.75rem' }}>
                                        <span style={{
                                          display: 'inline-block',
                                          padding: '0.15rem 0.5rem',
                                          borderRadius: '4px',
                                          fontSize: '0.75rem',
                                          fontWeight: 700,
                                          textTransform: 'uppercase',
                                          background: att.status === 'present' ? '#dcfce7' : (att.status === 'absent' ? '#fee2e2' : '#fef3c7'),
                                          color: att.status === 'present' ? '#15803d' : (att.status === 'absent' ? '#b91c1c' : '#b45309')
                                        }}>
                                          {att.status}
                                        </span>
                                      </td>
                                      <td style={{ padding: '0.5rem 0.75rem', color: '#64748b' }}>{att.remarks || '—'}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 4: EXAMINATION DETAILS */}
                  {recordModalTab === 'examinations' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          Examination Details & Schedules
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Scheduled assessments, mid-term examinations, and board evaluations announced by the institution.
                        </p>
                      </div>

                      {(!childRecords?.examinations || childRecords.examinations.length === 0) ? (
                        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '1rem 0' }}>
                          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>ℹ️</div>
                          <p style={{ color: '#475467', fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                            Information is currently unavailable because records have not yet been added.
                          </p>
                        </div>
                      ) : (
                        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                            <thead>
                              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475467' }}>
                                <th style={{ padding: '0.75rem 1rem' }}>Exam Name</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Academic Year</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Standard / Level</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Start Date</th>
                                <th style={{ padding: '0.75rem 1rem' }}>End Date</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Description</th>
                              </tr>
                            </thead>
                            <tbody>
                              {childRecords.examinations.map((exam, i) => (
                                <tr key={i} style={{ borderBottom: '1px solid #edf2f7' }}>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#1a3a6b' }}>{exam.exam_name}</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{exam.academic_year || '2025-26'}</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{exam.standard_or_level || `Standard ${childRecords?.student?.standard}`}</td>
                                  <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{exam.start_date || 'TBD'}</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>{exam.end_date || '—'}</td>
                                  <td style={{ padding: '0.75rem 1rem' }}>
                                    <span className="badge badge--primary" style={{ textTransform: 'capitalize' }}>
                                      {exam.status || 'Scheduled'}
                                    </span>
                                  </td>
                                  <td style={{ padding: '0.75rem 1rem', color: '#64748b' }}>{exam.description || '—'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 5: ACADEMIC RESULTS AND MARKS */}
                  {recordModalTab === 'results' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          Academic Results and Marks
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Official evaluation records, subject marks, percentages, and performance grades awarded by teachers.
                        </p>
                      </div>

                      {(!childRecords?.academic_results || childRecords.academic_results.length === 0) ? (
                        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '1rem 0' }}>
                          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>ℹ️</div>
                          <p style={{ color: '#475467', fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                            Information is currently unavailable because records have not yet been added.
                          </p>
                        </div>
                      ) : (
                        <div>
                          {childRecords?.subject_performance && childRecords.subject_performance.length > 0 && (
                            <div style={{ marginBottom: '1.5rem', background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                              <h4 style={{ margin: '0 0 1rem 0', color: '#1a3a6b', fontSize: '1rem', fontWeight: 700 }}>
                                Subject-wise Academic Standing
                              </h4>
                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem' }}>
                                {childRecords.subject_performance.map((sub, idx) => (
                                  <div key={idx} style={{ padding: '0.75rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #edf2f7' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                                      <strong style={{ fontSize: '0.875rem', color: '#0f172a' }}>{sub.subject_name}</strong>
                                      <span style={{ fontSize: '0.8rem', fontWeight: 700, padding: '0.1rem 0.4rem', borderRadius: '4px', background: sub.average_percentage >= 75 ? '#dcfce7' : '#fef3c7', color: sub.average_percentage >= 75 ? '#15803d' : '#b45309' }}>
                                        {sub.overall_grade} ({sub.average_percentage}%)
                                      </span>
                                    </div>
                                    <div style={{ background: '#e2e8f0', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                                      <div style={{ width: `${Math.min(100, Math.max(0, sub.average_percentage))}%`, height: '100%', background: sub.average_percentage >= 75 ? '#10b981' : '#f59e0b' }} />
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                              <thead>
                                <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475467' }}>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Academic Year</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Exam Name</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Subject</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Score</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Percentage</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Grade</th>
                                </tr>
                              </thead>
                              <tbody>
                                {childRecords.academic_results.map((res, i) => (
                                  <tr key={i} style={{ borderBottom: '1px solid #e8eaed' }}>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>{res.academic_year || '2025-26'}</td>
                                    <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#1e293b' }}>{res.exam_name}</td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>{res.subject_name}</td>
                                    <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700, color: '#0f172a' }}>
                                      {res.marks_obtained} <span style={{ color: '#64748b', fontWeight: 400 }}>/ {res.maximum_marks}</span>
                                    </td>
                                    <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>
                                      {res.percentage != null ? `${res.percentage}%` : `${Math.round((res.marks_obtained / (res.maximum_marks || 100)) * 100)}%`}
                                    </td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>
                                      <span style={{
                                        display: 'inline-block',
                                        padding: '0.15rem 0.5rem',
                                        borderRadius: '4px',
                                        fontSize: '0.75rem',
                                        fontWeight: 800,
                                        background: ['A+', 'A'].includes(res.grade) ? '#dcfce7' : (['B+', 'B'].includes(res.grade) ? '#dbeafe' : (res.grade === 'F' ? '#fee2e2' : '#fef3c7')),
                                        color: ['A+', 'A'].includes(res.grade) ? '#15803d' : (['B+', 'B'].includes(res.grade) ? '#1d4ed8' : (res.grade === 'F' ? '#b91c1c' : '#b45309'))
                                      }}>
                                        {res.grade || 'PASS'}
                                      </span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 6: FEES AND PAYMENT DETAILS */}
                  {recordModalTab === 'fees' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          Fees and Payment Details
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Institutional fee structure, dues, payment transactions, and receipt status.
                        </p>
                      </div>

                      {(!childRecords?.fees || childRecords.fees.length === 0) ? (
                        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '1rem 0' }}>
                          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>ℹ️</div>
                          <p style={{ color: '#475467', fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                            Information is currently unavailable because records have not yet been added.
                          </p>
                        </div>
                      ) : (
                        <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                            <thead>
                              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475467' }}>
                                <th style={{ padding: '0.75rem 1rem' }}>Fee Category</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Academic Year</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Amount Due</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Amount Paid</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Balance</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Due Date</th>
                                <th style={{ padding: '0.75rem 1rem' }}>Payment Status</th>
                              </tr>
                            </thead>
                            <tbody>
                              {childRecords.fees.map((fee, i) => {
                                const balance = Math.max(0, (fee.amount_due || 0) - (fee.amount_paid || 0))
                                return (
                                  <tr key={i} style={{ borderBottom: '1px solid #edf2f7' }}>
                                    <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#1a3a6b' }}>{fee.fee_type}</td>
                                    <td style={{ padding: '0.75rem 1rem' }}>{fee.academic_year || '2025-26'}</td>
                                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>₹{Number(fee.amount_due || 0).toLocaleString('en-IN')}</td>
                                    <td style={{ padding: '0.75rem 1rem', color: '#15803d', fontWeight: 600 }}>₹{Number(fee.amount_paid || 0).toLocaleString('en-IN')}</td>
                                    <td style={{ padding: '0.75rem 1rem', color: balance > 0 ? '#b91c1c' : '#15803d', fontWeight: 700 }}>₹{balance.toLocaleString('en-IN')}</td>
                                    <td style={{ padding: '0.75rem 1rem' }}>{fee.due_date || '—'}</td>
                                    <td style={{ padding: '0.75rem 1rem' }}>
                                      <span style={{
                                        display: 'inline-block',
                                        padding: '0.2rem 0.5rem',
                                        borderRadius: '4px',
                                        fontSize: '0.75rem',
                                        fontWeight: 700,
                                        textTransform: 'uppercase',
                                        background: fee.payment_status === 'paid' ? '#dcfce7' : (fee.payment_status === 'partial' ? '#fef3c7' : '#fee2e2'),
                                        color: fee.payment_status === 'paid' ? '#15803d' : (fee.payment_status === 'partial' ? '#b45309' : '#b91c1c')
                                      }}>
                                        {fee.payment_status || 'Pending'}
                                      </span>
                                    </td>
                                  </tr>
                                )
                              })}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 7: ANNOUNCEMENTS */}
                  {recordModalTab === 'announcements' && (
                    <div>
                      <div style={{ marginBottom: '1rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          School Announcements and Circulars
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Official notices, circulars, parent-teacher meeting notifications, and holiday advisories.
                        </p>
                      </div>

                      {(!childRecords?.announcements || childRecords.announcements.length === 0) ? (
                        <div style={{ padding: '2.5rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '1rem 0' }}>
                          <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>ℹ️</div>
                          <p style={{ color: '#475467', fontSize: '0.95rem', fontWeight: 600, margin: 0 }}>
                            Information is currently unavailable because records have not yet been added.
                          </p>
                        </div>
                      ) : (
                        <div style={{ display: 'grid', gap: '0.75rem', marginBottom: '1rem' }}>
                          {childRecords.announcements.map((ann, i) => (
                            <div key={i} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                                <strong style={{ fontSize: '0.95rem', color: '#1a3a6b' }}>{ann.title}</strong>
                                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>📅 {ann.published_date}</span>
                              </div>
                              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: '#334155', lineHeight: 1.5 }}>
                                {ann.content}
                              </p>
                              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                                Target Audience: <span style={{ textTransform: 'capitalize', fontWeight: 600 }}>{ann.target_audience || 'All'}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 8: OTHER STUDENT INFORMATION */}
                  {recordModalTab === 'other' && (
                    <div>
                      <div style={{ marginBottom: '1.25rem' }}>
                        <h3 style={{ fontSize: '1.15rem', color: '#1a3a6b', margin: '0 0 0.25rem 0', fontWeight: 700 }}>
                          Other Available Student Information
                        </h3>
                        <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                          Verified historical enrollment transitions, transfer logs, and archived government documents.
                        </p>
                      </div>

                      {/* Section A: Enrollment History */}
                      <div style={{ marginBottom: '1.5rem' }}>
                        <h4 style={{ fontSize: '1rem', color: '#1a3a6b', margin: '0 0 0.5rem 0', fontWeight: 700 }}>
                          Historical Enrollment & Admission Records
                        </h4>
                        {(!childRecords?.enrollment_history || childRecords.enrollment_history.length === 0) ? (
                          <div style={{ padding: '2rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '0.5rem 0 1rem 0' }}>
                            <p style={{ color: '#475467', fontSize: '0.9rem', fontWeight: 600, margin: 0 }}>
                              Information is currently unavailable because records have not yet been added.
                            </p>
                          </div>
                        ) : (
                          <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#ffffff' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                              <thead>
                                <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475467' }}>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>School</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Academic Year</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Class & Section</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>First Language</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Admission Date</th>
                                  <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                                </tr>
                              </thead>
                              <tbody>
                                {childRecords.enrollment_history.map((h, idx) => (
                                  <tr key={idx} style={{ borderBottom: '1px solid #edf2f7' }}>
                                    <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#1a3a6b' }}>{h.school_name || h.school_id}</td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>{h.academic_year}</td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>Class {h.standard}-{h.section}</td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>{h.first_language || 'Kannada'}</td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>{h.admission_date || '—'}</td>
                                    <td style={{ padding: '0.6rem 0.75rem' }}>
                                      <span className="badge badge--success" style={{ textTransform: 'capitalize' }}>
                                        {h.enrollment_status || 'Active'}
                                      </span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>

                      {/* Section B: Official Verification Documents */}
                      <div>
                        <h4 style={{ fontSize: '1rem', color: '#1a3a6b', margin: '0 0 0.5rem 0', fontWeight: 700 }}>
                          Archived Verification Documents
                        </h4>
                        {(!childRecords?.documents || childRecords.documents.length === 0) ? (
                          <div style={{ padding: '2rem 1.5rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', margin: '0.5rem 0 1rem 0' }}>
                            <p style={{ color: '#475467', fontSize: '0.9rem', fontWeight: 600, margin: 0 }}>
                              Information is currently unavailable because records have not yet been added.
                            </p>
                          </div>
                        ) : (
                          <div style={{ display: 'grid', gap: '0.5rem' }}>
                            {childRecords.documents.map((doc, i) => (
                              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 1rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                                <div>
                                  <div style={{ fontWeight: 600, color: '#1a3a6b' }}>📄 {doc.document_type}</div>
                                  <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.file_name} {doc.created_at ? `• Uploaded ${new Date(doc.created_at).toLocaleDateString()}` : ''}</div>
                                </div>
                                <StatusBadge status={doc.verification_status} />
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1.5rem', borderTop: '1px solid #f1f5f9', paddingTop: '1rem' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      🔒 Data Integrity & Privacy: Access strictly limited to verified parent account.
                    </div>
                    <button onClick={() => setSelectedChild(null)} className="btn btn--secondary">
                      Close Record Viewer
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
        {/* Modal: Stage 2 Admission Dossier & Document Upload */}
        <Stage2AdmissionModal
          applicationId={selectedStage2AppId}
          isOpen={Boolean(selectedStage2AppId)}
          onClose={() => setSelectedStage2AppId(null)}
          onSuccess={() => {
            setSelectedStage2AppId(null)
            loadAdmissionApps()
          }}
        />
      </div>
    </div>
  )
}
