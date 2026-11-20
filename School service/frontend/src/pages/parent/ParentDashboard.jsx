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

  // New Linking Request Form State
  const [formSchoolId, setFormSchoolId] = useState(() => searchParams.get('school_id') || '')
  const [formStudentRef, setFormStudentRef] = useState(() => searchParams.get('student_ref') || '')
  const [formRelationship, setFormRelationship] = useState('Father')
  const [formNotes, setFormNotes] = useState('')
  const [formDocId, setFormDocId] = useState('')
  const [submitting, setSubmitting] = useState(false)

  // Records Modal State
  const [selectedChild, setSelectedChild] = useState(null)
  const [childRecords, setChildRecords] = useState(null)
  const [loadingRecords, setLoadingRecords] = useState(false)
  const [recordsError, setRecordsError] = useState('')
  const [recordModalTab, setRecordModalTab] = useState('summary')

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

  // Direct Child Profile Edit State (Parent Student Account Management)
  const [editingChild, setEditingChild] = useState(null)
  const [editName, setEditName] = useState('')
  const [editDOB, setEditDOB] = useState('')
  const [editGender, setEditGender] = useState('Female')
  const [editLanguage, setEditLanguage] = useState('Kannada')
  const [editSaving, setEditSaving] = useState(false)
  const [editMsg, setEditMsg] = useState(null)

  function openEditModal(child) {
    setEditingChild(child)
    setEditName(child.student_name || '')
    setEditDOB(child.date_of_birth || '')
    setEditGender(child.gender || 'Female')
    setEditLanguage(child.first_language || 'Kannada')
    setEditMsg(null)
  }

  async function handleSaveChildProfile(e) {
    e.preventDefault()
    if (!editingChild) return
    setEditSaving(true)
    setEditMsg(null)
    try {
      await apiPost(
        `/parent/children/${editingChild.permanent_student_id}/profile`,
        {
          student_name: editName,
          date_of_birth: editDOB,
          gender: editGender,
          first_language: editLanguage,
        },
        token
      )
      setSuccess(`Profile for ${editName} successfully updated in official school records!`)
      setEditingChild(null)
      loadParentData()
    } catch (err) {
      setEditMsg({ type: 'error', text: err.message || 'Failed to update student profile.' })
    } finally {
      setEditSaving(false)
    }
  }

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

  // If school_id or student_ref passed via query param, pre-fill form
  useEffect(() => {
    const qSchool = searchParams.get('school_id')
    const qRef = searchParams.get('student_ref')
    if (qSchool) {
      setFormSchoolId(qSchool)
      setActiveTab('new-request')
    }
    if (qRef) {
      setFormStudentRef(qRef)
      setActiveTab('new-request')
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

  // Submit Linking Request
  async function handleRequestSubmit(e) {
    e.preventDefault()
    if (!formSchoolId) {
      setError('Please select a school.')
      return
    }
    if (!formStudentRef.trim()) {
      setError('Please provide a student reference (Permanent Student ID, Admission Number, or Student Name).')
      return
    }

    try {
      setSubmitting(true)
      setError('')
      setSuccess('')

      const payload = {
        school_id: formSchoolId,
        student_ref: formStudentRef.trim(),
        relationship_type: formRelationship,
        additional_notes: formNotes.trim() || undefined,
        verification_doc_id: formDocId.trim() || undefined,
      }

      await apiPost('/parent/linking-requests', payload, token)

      setSuccess('Your student-linking request has been submitted successfully to the school staff desk! Status is pending verification.')
      setFormStudentRef('')
      setFormNotes('')
      setFormDocId('')

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

  // View Child Academic Records
  async function viewRecords(child) {
    setSelectedChild(child)
    setLoadingRecords(true)
    setRecordsError('')
    setChildRecords(null)
    setRecordModalTab('summary')

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

          <button
            onClick={() => switchTab('new-request')}
            className="btn btn--accent"
          >
            + Link New Student
          </button>
        </div>

        {error && <Alert type="error" title="Error" className="mb-4">{error}</Alert>}
        {success && <Alert type="success" title="Success" className="mb-4">{success}</Alert>}

        {/* Tab Navigation */}
        <div style={{ display: 'flex', borderBottom: '2px solid #e8eaed', marginBottom: '1.5rem', gap: '0.5rem' }}>
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
            Submit Linking Request
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
            Request History ({requests.length})
          </button>
        </div>

        {/* Tab 1: Linked Children */}
        {activeTab === 'children' && (
          <div>
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
                  You have not linked any student records to your account yet. Submit a linking request with your child's school to view their official academic records.
                </p>
                <button onClick={() => switchTab('new-request')} className="btn btn--primary">
                  Submit Student-Linking Request Now →
                </button>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                {children.map(child => {
                  const isCentralEligible = child.enrollment_status === 'eligible_for_admission'
                  return (
                    <div key={child.permanent_student_id} className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', padding: '1.5rem', background: '#ffffff', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                          <span className={isCentralEligible ? "badge badge--warning" : "badge badge--success"}>
                            {isCentralEligible ? '🏛️ Central Citizen Registry' : 'Verified Linked Student'}
                          </span>
                          <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#6b7280' }}>
                            {child.citizen_code ? `Citizen: ${child.citizen_code}` : `PSID: ${child.permanent_student_id}`}
                          </span>
                        </div>

                        <h3 style={{ fontSize: '1.25rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
                          {child.student_name}
                        </h3>
                        <div style={{ color: '#4b5563', fontSize: '0.875rem', marginBottom: '0.75rem' }}>
                          🏫 {child.school_name || (child.school_id ? child.school_id : 'Central Household Dependent')}
                        </div>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', fontSize: '0.8125rem', marginBottom: '1rem' }}>
                          <div>Class: <strong>{child.standard ? `Class ${child.standard}` : 'Primary'}</strong></div>
                          <div>Section: <strong>{child.section || '-'}</strong></div>
                          <div>Language: <strong>{child.first_language || 'Kannada'}</strong></div>
                          <div>DOB: <strong>{child.date_of_birth || 'Registered'}</strong></div>
                          <div style={{ gridColumn: 'span 2' }}>
                            Status: <strong style={{ color: isCentralEligible ? '#b54708' : '#027a48' }}>
                              {isCentralEligible ? 'Eligible for School Admission' : (child.enrollment_status || 'Active Enrolled')}
                            </strong>
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {isCentralEligible ? (
                          <Link
                            to={`/schools?applicant_name=${encodeURIComponent(child.student_name)}&dob=${encodeURIComponent(child.date_of_birth || '')}`}
                            className="btn btn--primary btn--full btn--sm"
                            style={{ textAlign: 'center', textDecoration: 'none' }}
                          >
                            🏫 Apply for School Admission →
                          </Link>
                        ) : (
                          <>
                            <button
                              onClick={() => viewRecords(child)}
                              className="btn btn--secondary btn--full btn--sm"
                            >
                              📊 View Academic Results & Documents →
                            </button>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                              <button
                                onClick={() => openEditModal(child)}
                                className="btn btn--outline btn--sm"
                                style={{ flex: 1, fontSize: '0.75rem' }}
                              >
                                ✏️ Edit Profile Details
                              </button>
                              <button
                                onClick={() => {
                                  setFormStudentRef(child.student_id || child.permanent_student_id)
                                  setFormSchoolId(child.school_id || '')
                                  setActiveTab('update-request')
                                }}
                                className="btn btn--outline btn--sm"
                                style={{ flex: 1, fontSize: '0.75rem' }}
                              >
                                📝 Field Request
                              </button>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}

        {/* Tab 2: New Linking Request Form */}
        {activeTab === 'new-request' && (
          <div className="card" style={{ maxWidth: '680px', margin: '0 auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff' }}>
            <div style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.5rem', color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>
                Submit Student-Linking Request
              </h2>
              <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
                This request will be sent securely to the assigned school staff desk for identity matching and institutional authorization.
              </p>
            </div>

            <form onSubmit={handleRequestSubmit}>
              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                  Target School <span style={{ color: '#b91c1c' }}>*</span>
                </label>
                <select
                  required
                  className="input"
                  value={formSchoolId}
                  onChange={e => setFormSchoolId(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                >
                  <option value="">-- Select Enrolled School ({schools.length} Available) --</option>
                  {schools.map(s => (
                    <option key={s.school_id} value={s.school_id}>
                      {s.school_id} — {s.school_name} ({s.district || 'Karnataka'})
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                  Student Reference / Identifier <span style={{ color: '#b91c1c' }}>*</span>
                </label>
                <input
                  type="text"
                  required
                  className="input"
                  placeholder="e.g. Permanent Student ID, Student Name, or Admission Ref"
                  value={formStudentRef}
                  onChange={e => setFormStudentRef(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                />
                <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                  Enter your child's full name, roll number, or permanent student ID as recorded in school documents.
                </div>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                  Relationship to Student <span style={{ color: '#b91c1c' }}>*</span>
                </label>
                <select
                  required
                  className="input"
                  value={formRelationship}
                  onChange={e => setFormRelationship(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                >
                  <option value="Father">Father</option>
                  <option value="Mother">Mother</option>
                  <option value="Legal Guardian">Legal Guardian</option>
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                  Supporting Verification Document Reference <span style={{ color: '#6b7280', fontWeight: 400 }}>(Optional)</span>
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g. DOC-AADHAAR-2026 or Transfer Certificate Number"
                  value={formDocId}
                  onChange={e => setFormDocId(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                />
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                  Additional Notes for School Verification Staff <span style={{ color: '#6b7280', fontWeight: 400 }}>(Optional)</span>
                </label>
                <textarea
                  className="input"
                  rows={3}
                  placeholder="e.g. Standard 5 Section A, enrolled in academic year 2026"
                  value={formNotes}
                  onChange={e => setFormNotes(e.target.value)}
                  style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn--primary btn--lg"
                  style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                >
                  {submitting ? <LoadingSpinner size="sm" /> : 'Submit for School Staff Review →'}
                </button>
                <button
                  type="button"
                  onClick={() => switchTab('children')}
                  className="btn btn--ghost btn--lg"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Tab 3: Request History */}
        {activeTab === 'history' && (
          <div>
            {loading ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
              </div>
            ) : requests.length === 0 ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📂</div>
                <h3 style={{ color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>No Linking Requests Submitted</h3>
                <p style={{ color: '#4b5563', margin: '0 0 1rem 0' }}>You have not submitted any linking requests yet.</p>
                <button onClick={() => switchTab('new-request')} className="btn btn--primary">
                  Create First Linking Request
                </button>
              </div>
            ) : (
              <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc' }}>
                  <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1a3a6b' }}>Your Linking Request History</h3>
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#475569' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Request ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>School</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Student Reference</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Relationship</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Submitted At</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Staff Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {requests.map(r => (
                        <tr key={r.request_id} style={{ borderBottom: '1px solid #e8eaed' }}>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                            {r.request_id.slice(0, 8)}...
                          </td>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#1a3a6b' }}>
                            {r.school_name || r.school_id}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>{r.student_ref}</td>
                          <td style={{ padding: '0.75rem 1rem' }}>{r.relationship_type}</td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <StatusBadge status={r.request_status || r.status} />
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: '#6b7280' }}>
                            {r.submitted_at ? new Date(r.submitted_at).toLocaleDateString() : 'Recent'}
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: '#4b5563' }}>
                            {r.review_notes || '—'}
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

        {/* Modal: Direct Parent Student Profile Edit */}
        {editingChild && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000, backdropFilter: 'blur(2px)' }}>
            <div className="card" style={{ maxWidth: '520px', width: '100%', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '12px', background: '#ffffff', position: 'relative', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #e8eaed', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
                <h3 style={{ margin: 0, color: '#1a3a6b', fontSize: '1.25rem' }}>
                  ✏️ Edit Student Account Details
                </h3>
                <button
                  onClick={() => setEditingChild(null)}
                  style={{ background: '#f1f5f9', border: 'none', width: '32px', height: '32px', borderRadius: '16px', fontSize: '1rem', cursor: 'pointer', color: '#475467' }}
                >
                  ✕
                </button>
              </div>

              {editMsg && (
                <Alert type={editMsg.type} style={{ marginBottom: '1rem' }}>
                  {editMsg.text}
                </Alert>
              )}

              <p style={{ fontSize: '0.85rem', color: '#475467', marginBottom: '1rem' }}>
                As a verified parent, changes saved here update your child's student record directly across official education systems.
              </p>

              <form onSubmit={handleSaveChildProfile}>
                <div style={{ marginBottom: '1rem' }}>
                  <label className="form-label" style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                    Student Full Name *
                  </label>
                  <input
                    type="text"
                    className="form-input"
                    value={editName}
                    onChange={e => setEditName(e.target.value)}
                    required
                    style={{ width: '100%', padding: '0.5rem', border: '1px solid #d0d5dd', borderRadius: '6px' }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div>
                    <label className="form-label" style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                      Date of Birth
                    </label>
                    <input
                      type="date"
                      className="form-input"
                      value={editDOB}
                      onChange={e => setEditDOB(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', border: '1px solid #d0d5dd', borderRadius: '6px' }}
                    />
                  </div>
                  <div>
                    <label className="form-label" style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                      Gender
                    </label>
                    <select
                      className="form-input"
                      value={editGender}
                      onChange={e => setEditGender(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', border: '1px solid #d0d5dd', borderRadius: '6px' }}
                    >
                      <option value="Female">Female</option>
                      <option value="Male">Male</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>

                <div style={{ marginBottom: '1.5rem' }}>
                  <label className="form-label" style={{ display: 'block', fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                    First Language Preference
                  </label>
                  <select
                    className="form-input"
                    value={editLanguage}
                    onChange={e => setEditLanguage(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', border: '1px solid #d0d5dd', borderRadius: '6px' }}
                  >
                    <option value="Kannada">Kannada</option>
                    <option value="Hindi">Hindi</option>
                    <option value="Sanskrit">Sanskrit</option>
                    <option value="English">English</option>
                  </select>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <button
                    type="button"
                    onClick={() => setEditingChild(null)}
                    className="btn btn--secondary"
                    disabled={editSaving}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn--primary"
                    disabled={editSaving}
                  >
                    {editSaving ? 'Saving Changes...' : 'Save Student Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Modal: Child Academic Records & Student Performance */}
        {selectedChild && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(15, 23, 42, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000, backdropFilter: 'blur(2px)' }}>
            <div className="card" style={{ maxWidth: '900px', width: '100%', maxHeight: '92vh', overflowY: 'auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '12px', background: '#ffffff', position: 'relative', boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)' }}>
              {/* Header */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #e8eaed', paddingBottom: '1rem', marginBottom: '1.25rem' }}>
                <div>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.35rem' }}>
                    <span className="badge badge--success" style={{ fontWeight: 700 }}>OFFICIAL VERIFIED LEDGER</span>
                    <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>
                      PSID: <code style={{ color: '#0f172a', fontWeight: 700 }}>{selectedChild.permanent_student_id}</code>
                    </span>
                  </div>
                  <h2 style={{ fontSize: '1.65rem', color: '#1a3a6b', margin: '0.2rem 0', fontWeight: 800 }}>
                    {selectedChild.student_name}
                  </h2>
                  <p style={{ margin: 0, color: '#475467', fontSize: '0.875rem' }}>
                    🏫 <strong>{selectedChild.school_name || selectedChild.school_id}</strong> · Class <strong>{selectedChild.standard}-{selectedChild.section}</strong> · Status: <span style={{ color: '#027a48', fontWeight: 600 }}>Enrolled</span>
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
                  {/* Modal Navigation Sub-Tabs */}
                  <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '2px solid #f1f5f9', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
                    {[
                      { id: 'summary', label: '📊 Academic Summary' },
                      { id: 'attendance', label: `📅 Attendance (${childRecords?.attendance_summary?.attendance_percentage != null ? `${childRecords.attendance_summary.attendance_percentage}%` : 'Not available'})` },
                      { id: 'results', label: `📝 Examinations & Marks (${childRecords?.academic_results?.length || 0})` },
                      { id: 'announcements', label: `📢 Announcements (${childRecords?.announcements?.length || 0})` },
                      { id: 'documents', label: `📄 Documents (${childRecords?.documents?.length || 0})` }
                    ].map(tab => (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => setRecordModalTab(tab.id)}
                        style={{
                          padding: '0.6rem 1rem',
                          fontSize: '0.875rem',
                          fontWeight: recordModalTab === tab.id ? 700 : 500,
                          border: 'none',
                          background: 'none',
                          cursor: 'pointer',
                          color: recordModalTab === tab.id ? '#1a3a6b' : '#64748b',
                          borderBottom: recordModalTab === tab.id ? '3px solid #1a3a6b' : '3px solid transparent',
                          marginBottom: '-2px'
                        }}
                      >
                        {tab.label}
                      </button>
                    ))}
                  </div>

                  {/* SUB-TAB 1: ACADEMIC SUMMARY */}
                  {recordModalTab === 'summary' && (
                    <div>
                      {/* 4 KPI Cards */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.875rem', marginBottom: '1.5rem' }}>
                        <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Attendance Rate</div>
                          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: childRecords?.attendance_summary?.attendance_percentage != null ? (childRecords.attendance_summary.attendance_percentage >= 75 ? '#027a48' : '#b42318') : '#64748b', marginTop: '0.2rem' }}>
                            {childRecords?.attendance_summary?.attendance_percentage != null ? `${childRecords.attendance_summary.attendance_percentage}%` : 'Not available'}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                            {childRecords?.attendance_summary?.total_working_days ? `${childRecords.attendance_summary.present_days} of ${childRecords.attendance_summary.total_working_days} days attended` : 'No attendance recorded'}
                          </div>
                        </div>

                        <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Total Evaluations</div>
                          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#1a3a6b', marginTop: '0.2rem' }}>
                            {childRecords?.academic_results?.length || 0}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>Recorded in official gradebook</div>
                        </div>

                        <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Upcoming Exams</div>
                          <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0284c7', marginTop: '0.2rem' }}>
                            {childRecords?.upcoming_examinations?.length || 0}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>Scheduled assessments</div>
                        </div>

                        <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Parent Linking Status</div>
                          <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#027a48', marginTop: '0.4rem' }}>
                            ✓ Verified & Linked
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>Access: Academic, Attendance, Exams</div>
                        </div>
                      </div>

                      {/* Subject Performance Preview */}
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

                      {/* Upcoming Examinations Card */}
                      {childRecords?.upcoming_examinations && childRecords.upcoming_examinations.length > 0 && (
                        <div style={{ marginBottom: '1.5rem', background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '8px', padding: '1rem' }}>
                          <h4 style={{ margin: '0 0 0.5rem 0', color: '#0369a1', fontSize: '0.95rem', fontWeight: 700 }}>
                            📅 Upcoming Examinations
                          </h4>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                            {childRecords.upcoming_examinations.map((exam, i) => (
                              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#ffffff', padding: '0.6rem 0.85rem', borderRadius: '6px', border: '1px solid #e0f2fe' }}>
                                <div>
                                  <strong style={{ fontSize: '0.875rem', color: '#0369a1' }}>{exam.exam_name}</strong>
                                  <span style={{ marginLeft: '0.5rem', fontSize: '0.75rem', color: '#64748b' }}>({exam.academic_year})</span>
                                </div>
                                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0284c7', background: '#e0f2fe', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                                  {exam.exam_date || 'Date TBD'}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* SUB-TAB 2: ATTENDANCE LEDGER */}
                  {recordModalTab === 'attendance' && (
                    <div>
                      {childRecords?.attendance_summary?.total_working_days == null || childRecords?.attendance_summary?.total_working_days === 0 ? (
                        <div style={{ padding: '2rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📅</div>
                          <h4 style={{ color: '#1a3a6b', margin: '0 0 0.35rem 0' }}>Attendance: Not available</h4>
                          <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                            No daily attendance entries have been recorded yet by institution staff for this student.
                          </p>
                        </div>
                      ) : (
                        <div>
                          {/* Attendance Metrics Bar */}
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

                          {/* Monthly Breakdown */}
                          {childRecords.attendance_summary.monthly_breakdown && childRecords.attendance_summary.monthly_breakdown.length > 0 && (
                            <div style={{ marginBottom: '1.25rem' }}>
                              <h5 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.9rem' }}>Monthly Summary</h5>
                              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                                {childRecords.attendance_summary.monthly_breakdown.map((m, idx) => (
                                  <div key={idx} style={{ padding: '0.4rem 0.75rem', background: '#f1f5f9', borderRadius: '6px', fontSize: '0.8rem', border: '1px solid #e2e8f0' }}>
                                    <strong>{m.month}:</strong> {m.present}/{m.total_recorded} days ({m.attendance_percentage}%)
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Attendance Ledger Table */}
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
                                {childRecords?.attendance_records?.slice(0, 15).map((att, i) => (
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
                        </div>
                      )}
                    </div>
                  )}

                  {/* SUB-TAB 3: EXAMINATIONS & MARKS */}
                  {recordModalTab === 'results' && (
                    <div>
                      {childRecords?.academic_results?.length === 0 ? (
                        <div style={{ padding: '2rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</div>
                          <h4 style={{ color: '#1a3a6b', margin: '0 0 0.35rem 0' }}>Evaluations & Marks: Not available</h4>
                          <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                            No examination marks have been entered yet for the current academic session.
                          </p>
                        </div>
                      ) : (
                        <div style={{ overflowX: 'auto', marginBottom: '1.5rem', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                            <thead>
                              <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                <th style={{ padding: '0.6rem 0.75rem' }}>Academic Year</th>
                                <th style={{ padding: '0.6rem 0.75rem' }}>Exam Name</th>
                                <th style={{ padding: '0.6rem 0.75rem' }}>Subject</th>
                                <th style={{ padding: '0.6rem 0.75rem' }}>Score</th>
                                <th style={{ padding: '0.6rem 0.75rem' }}>Percentage</th>
                                <th style={{ padding: '0.6rem 0.75rem' }}>Grade</th>
                              </tr>
                            </thead>
                            <tbody>
                              {childRecords?.academic_results?.map((res, i) => (
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
                      )}
                    </div>
                  )}

                  {/* SUB-TAB 4: ANNOUNCEMENTS */}
                  {recordModalTab === 'announcements' && (
                    <div>
                      {childRecords?.announcements?.length === 0 ? (
                        <div style={{ padding: '2rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📢</div>
                          <h4 style={{ color: '#1a3a6b', margin: '0 0 0.35rem 0' }}>Announcements: Not available</h4>
                          <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                            No institutional announcements have been issued for students or parents.
                          </p>
                        </div>
                      ) : (
                        <div style={{ display: 'grid', gap: '0.75rem', marginBottom: '1rem' }}>
                          {childRecords.announcements.map((ann, i) => (
                            <div key={i} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                                <strong style={{ fontSize: '0.95rem', color: '#1a3a6b' }}>{ann.title}</strong>
                                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>📅 {ann.published_date}</span>
                              </div>
                              <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.875rem', color: '#334155' }}>
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

                  {/* SUB-TAB 5: DOCUMENTS */}
                  {recordModalTab === 'documents' && (
                    <div>
                      {childRecords?.documents?.length === 0 ? (
                        <div style={{ padding: '2rem', textAlign: 'center', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📄</div>
                          <h4 style={{ color: '#1a3a6b', margin: '0 0 0.35rem 0' }}>Verification Documents: Not available</h4>
                          <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                            No institutional verification documents archived yet.
                          </p>
                        </div>
                      ) : (
                        <div style={{ display: 'grid', gap: '0.5rem', marginBottom: '1.5rem' }}>
                          {childRecords?.documents?.map((doc, i) => (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem', background: '#f8fafc', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                              <div>
                                <div style={{ fontWeight: 600, color: '#1a3a6b' }}>📄 {doc.document_type}</div>
                                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{doc.file_name}</div>
                              </div>
                              <StatusBadge status={doc.verification_status} />
                            </div>
                          ))}
                        </div>
                      )}
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
