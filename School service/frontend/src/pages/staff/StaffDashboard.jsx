import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import StatusBadge from '../../components/ui/StatusBadge.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'
import AdmissionDeskTab from '../../components/admissions/AdmissionDeskTab.jsx'
import StaffAcademicDesk from '../../components/academic/StaffAcademicDesk.jsx'

export default function StaffDashboard() {
  const { user, token, isAuthenticated } = useAuth()

  const isSchoolAdmin = user?.role === 'school_admin'
  const [effectiveRole, setEffectiveRole] = useState(user?.role || 'school_staff')
  const [permissions, setPermissions] = useState({
    can_view_applications: isSchoolAdmin,
    can_review_details: isSchoolAdmin,
    can_request_clarification: isSchoolAdmin,
    can_recommend_decision: isSchoolAdmin,
    can_approve_stage1: isSchoolAdmin,
    can_view_history: isSchoolAdmin,
    can_manage_academics: isSchoolAdmin,
    can_manage_students: isSchoolAdmin,
  })
  const [activeTab, setActiveTab] = useState(() => {
    if (window.location.search.includes('tab=admissions') || window.location.hash.includes('tab=admissions')) return 'admissions'
    if (window.location.search.includes('tab=academics') || window.location.hash.includes('tab=academics')) return 'academics'
    if (isSchoolAdmin) return 'admin-overview'
    return 'queue'
  })
  const [adminOverview, setAdminOverview] = useState(null)
  const [loadingAdminOverview, setLoadingAdminOverview] = useState(false)
  const [requests, setRequests] = useState([])
  const [loadingRequests, setLoadingRequests] = useState(true)
  const [requestFilter, setRequestFilter] = useState('pending')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [issuedCodeData, setIssuedCodeData] = useState(null)
  const [issuingCode, setIssuingCode] = useState(false)

  async function handleStaffIssueCode(req) {
    if (!req) return
    try {
      setIssuingCode(true)
      const res = await apiPost(`/school/linking-requests/${req.request_id}/issue-code`, {}, token)
      setIssuedCodeData({ ...res, request: req })
    } catch (err) {
      setError(err.message || 'Failed to generate verification code.')
    } finally {
      setIssuingCode(false)
    }
  }

  // Student directory state (Standard & Section filtered)
  const [students, setStudents] = useState([])
  const [loadingStudents, setLoadingStudents] = useState(false)
  const [selectedStandard, setSelectedStandard] = useState('1')
  const [selectedSection, setSelectedSection] = useState('A')
  const [hasQueriedStudents, setHasQueriedStudents] = useState(false)
  const [availableStandards, setAvailableStandards] = useState([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
  const [availableSections, setAvailableSections] = useState(['A', 'B', 'C'])
  const [schoolSectionsData, setSchoolSectionsData] = useState([])

  // Programme Distribution state (Level 1-4, Stream, Combination, Section strength)
  const [progSections, setProgSections] = useState([])
  const [loadingProgSections, setLoadingProgSections] = useState(false)
  const [filterLevel, setFilterLevel] = useState('all')
  const [filterInst, setFilterInst] = useState('all')
  const [filterStream, setFilterStream] = useState('all')
  const [filterCombination, setFilterCombination] = useState('all')
  const [filterAcademicYear, setFilterAcademicYear] = useState('2025-26')
  const [filterTermYear, setFilterTermYear] = useState('all')
  const [filterSemester, setFilterSemester] = useState('all')
  const [filterSection, setFilterSection] = useState('all')
  const [institutionsList, setInstitutionsList] = useState([])

  // Review Modal State
  const [activeReviewRequest, setActiveReviewRequest] = useState(null)
  const [candidateStudents, setCandidateStudents] = useState([])
  const [selectedCandidate, setSelectedCandidate] = useState(null)
  const [decision, setDecision] = useState('approved')
  const [reviewComment, setReviewComment] = useState('')
  const [confirmMatch, setConfirmMatch] = useState(false)
  const [submittingReview, setSubmittingReview] = useState(false)
  const [reviewError, setReviewError] = useState('')

  // Staff Management state (for school_admin)
  const [staffList, setStaffList] = useState([])
  const [loadingStaff, setLoadingStaff] = useState(false)
  const [showInviteStaffModal, setShowInviteStaffModal] = useState(false)
  const [staffFullName, setStaffFullName] = useState('')
  const [staffEmail, setStaffEmail] = useState('')
  const [staffPhone, setStaffPhone] = useState('')
  const [staffRole, setStaffRole] = useState('school_staff')
  const [submittingStaffInvite, setSubmittingStaffInvite] = useState(false)
  const [staffInviteResult, setStaffInviteResult] = useState(null)
  const [staffInviteError, setStaffInviteError] = useState('')

  const assignedSchoolId = user?.school_id || 'SCH001'

  async function loadStaffList() {
    if (!token || !isSchoolAdmin) return
    try {
      setLoadingStaff(true)
      const data = await apiGet('/school/admin/staff', token)
      setStaffList(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to load school staff roster.')
    } finally {
      setLoadingStaff(false)
    }
  }

  async function handleStaffInviteSubmit(e) {
    e.preventDefault()
    if (!staffFullName.trim() || !staffEmail.trim()) {
      setStaffInviteError('Please fill in required fields.')
      return
    }

    try {
      setSubmittingStaffInvite(true)
      setStaffInviteError('')
      const payload = {
        full_name: staffFullName.trim(),
        email: staffEmail.trim(),
        phone: staffPhone.trim() || undefined,
        institution_id: assignedSchoolId,
        role_id: staffRole
      }
      const res = await apiPost('/school/admin/staff/invite', payload, token)
      setStaffInviteResult(res)
      setSuccess(`Staff invitation issued for ${res.email}!`)
      loadStaffList()
    } catch (err) {
      setStaffInviteError(err.message || 'Failed to issue staff invitation.')
    } finally {
      setSubmittingStaffInvite(false)
    }
  }

  // Fetch linking requests for assigned school
  async function loadRequests() {
    if (!token) return
    try {
      setLoadingRequests(true)
      const data = await apiGet(`/school/linking-requests?status_filter=${requestFilter}`, token)
      setRequests(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Unable to load school linking requests.')
    } finally {
      setLoadingRequests(false)
    }
  }

  // Phase 11B: Fetch staff permissions and effective role
  useEffect(() => {
    async function fetchPermissions() {
      if (!token) return
      try {
        const data = await apiGet('/school/staff/me/permissions', token)
        if (data) {
          const r = data.role_id || user?.role || 'school_staff'
          setEffectiveRole(r)
          if (data.permissions) {
            setPermissions(data.permissions)
            // Auto switch to appropriate default tab based on role
            if (r === 'admissions_officer') {
              setActiveTab('admissions')
            } else if (r === 'student_records_officer') {
              setActiveTab('students')
            } else if (r === 'academic_admin') {
              setActiveTab('program-distribution')
            }
          }
        }
      } catch (err) {
        // Fallback gracefully
      }
    }
    fetchPermissions()
  }, [token, user])

  // Fetch school admin metrics if school admin
  useEffect(() => {
    async function loadSchoolAdminData() {
      if (!token || !isSchoolAdmin) return
      try {
        setLoadingAdminOverview(true)
        const data = await apiGet('/school/admin/overview', token)
        setAdminOverview(data)
      } catch {
        // Fallback gracefully
      } finally {
        setLoadingAdminOverview(false)
      }
    }
    loadSchoolAdminData()
  }, [token, isSchoolAdmin])

  useEffect(() => {
    loadRequests()
  }, [token, requestFilter])

  // Fetch school configuration for standards and sections dynamically
  useEffect(() => {
    async function loadSchoolSections() {
      if (!token || !assignedSchoolId) return
      try {
        const data = await apiGet(`/schools/${assignedSchoolId}/sections`, token)
        if (Array.isArray(data) && data.length > 0) {
          setSchoolSectionsData(data)
          const stds = [...new Set(data.map(d => d.standard))].sort((a, b) => a - b)
          setAvailableStandards(stds)
        }
      } catch {
        // Fallback gracefully to default 1-12
      }
    }
    loadSchoolSections()
  }, [token, assignedSchoolId])

  // Dynamically update available sections when selectedStandard changes
  useEffect(() => {
    if (schoolSectionsData.length > 0) {
      const currentStd = parseInt(selectedStandard, 10)
      const matchingSecs = schoolSectionsData
        .filter(d => d.standard === currentStd)
        .map(d => d.section)
      if (matchingSecs.length > 0) {
        setAvailableSections(matchingSecs)
        if (!matchingSecs.includes(selectedSection)) {
          setSelectedSection(matchingSecs[0])
        }
      } else {
        setAvailableSections(['A', 'B', 'C'])
      }
    }
  }, [selectedStandard, schoolSectionsData])

  // Fetch institutions for filter dropdown
  useEffect(() => {
    async function fetchInstitutions() {
      try {
        const data = await apiGet('/schools')
        if (Array.isArray(data)) {
          setInstitutionsList(data)
        }
      } catch {
        // Fallback silently
      }
    }
    fetchInstitutions()
  }, [])

  // Fetch programme sections based on selected multi-tier filters
  async function loadProgramSections() {
    if (!token) return
    try {
      setLoadingProgSections(true)
      const query = new URLSearchParams()
      if (filterInst && filterInst !== 'all') query.append('institution_id', filterInst)
      if (filterLevel && filterLevel !== 'all') query.append('education_level', filterLevel)
      if (filterStream && filterStream !== 'all') query.append('discipline_or_stream', filterStream)
      if (filterCombination && filterCombination !== 'all') query.append('combination_code', filterCombination)
      if (filterAcademicYear && filterAcademicYear !== 'all') query.append('academic_year', filterAcademicYear)
      if (filterTermYear && filterTermYear !== 'all') query.append('term_or_year', filterTermYear)
      if (filterSemester && filterSemester !== 'all') query.append('semester', filterSemester)
      if (filterSection && filterSection !== 'all') query.append('section_name', filterSection)

      const data = await apiGet(`/education/program-sections?${query.toString()}`, token)
      setProgSections(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Unable to load programme sections.')
    } finally {
      setLoadingProgSections(false)
    }
  }

  // Reload program sections when filters change or when switching to program-distribution tab
  useEffect(() => {
    if (activeTab === 'program-distribution') {
      loadProgramSections()
    }
  }, [
    activeTab,
    token,
    filterInst,
    filterLevel,
    filterStream,
    filterCombination,
    filterAcademicYear,
    filterTermYear,
    filterSemester,
    filterSection,
  ])

  // Fetch student roster on explicit filter action
  async function fetchRoster(e) {
    if (e) e.preventDefault()
    if (!token) return

    try {
      setLoadingStudents(true)
      setError('')
      const data = await apiGet(
        `/schools/${assignedSchoolId}/students?standard=${selectedStandard}&section=${selectedSection}&limit=100`,
        token
      )
      setStudents(Array.isArray(data) ? data : data.value ?? [])
      setHasQueriedStudents(true)
    } catch (err) {
      setError(err.message || 'Failed to fetch student roster for this standard/section.')
    } finally {
      setLoadingStudents(false)
    }
  }

  // Open Review Modal
  async function openReviewModal(req) {
    setActiveReviewRequest(req)
    setDecision('approved')
    setReviewComment('Verified against official institutional records.')
    setConfirmMatch(false)
    setReviewError('')
    setSelectedCandidate(null)

    // Pre-fetch candidate students in this school to match against
    try {
      const data = await apiGet(`/schools/${assignedSchoolId}/students?limit=50`, token)
      const list = Array.isArray(data) ? data : data.value ?? []
      setCandidateStudents(list)

      // Try automatic match
      const ref = (req.student_ref || '').trim().toLowerCase()
      const match = list.find(s => 
        (s.permanent_student_id && s.permanent_student_id.toLowerCase() === ref) ||
        (s.student_id && s.student_id.toLowerCase() === ref) ||
        (s.student_name && s.student_name.toLowerCase().includes(ref))
      )
      if (match) {
        setSelectedCandidate(match)
      } else if (list.length > 0) {
        setSelectedCandidate(list[0])
      }
    } catch {
      // Ignore background candidate fetch failure
    }
  }

  // Check if reference matches candidate verbatim
  function isDirectMatch(req, candidate) {
    if (!req || !candidate) return false
    const ref = (req.student_ref || '').trim().toLowerCase()
    const psid = (candidate.permanent_student_id || '').trim().toLowerCase()
    const sid = (candidate.student_id || '').trim().toLowerCase()
    const name = (candidate.student_name || '').trim().toLowerCase()
    return ref === psid || ref === sid || ref === name
  }

  // Submit Review
  async function handleReviewSubmit(e) {
    e.preventDefault()
    if (!reviewComment.trim() || reviewComment.trim().length < 3) {
      setReviewError('Review comment must be at least 3 characters.')
      return
    }

    if (decision === 'approved' && !selectedCandidate) {
      setReviewError('Please select a student record to link.')
      return
    }

    const directMatch = isDirectMatch(activeReviewRequest, selectedCandidate)
    if (decision === 'approved' && !directMatch && !confirmMatch) {
      setReviewError('Student reference does not match directly. You must check "Confirm manual verification of student match" to approve.')
      return
    }

    try {
      setSubmittingReview(true)
      setReviewError('')

      const payload = {
        decision,
        review_comment: reviewComment.trim(),
        permanent_student_id: decision === 'approved' ? (selectedCandidate.permanent_student_id || selectedCandidate.student_id) : undefined,
        confirm_student_match: confirmMatch,
      }

      await apiPost(`/school/linking-requests/${activeReviewRequest.request_id}/review`, payload, token)

      setSuccess(`Request ${activeReviewRequest.request_id.slice(0, 8)}... was successfully ${decision}!`)
      setActiveReviewRequest(null)
      loadRequests()
    } catch (err) {
      setReviewError(err.message || 'Review submission failed.')
    } finally {
      setSubmittingReview(false)
    }
  }

  if (!isAuthenticated || (!['school_staff', 'school_admin', 'academic_admin', 'institution_admin', 'platform_admin', 'admissions_officer'].includes(user?.role))) {
    return (
      <div className="container" style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <Alert type="warning" title="Institutional Authorization Required">
          Access to the School Staff Review Desk is restricted to authenticated school personnel and administrators.
        </Alert>
        <Link to="/login" className="btn btn--primary" style={{ marginTop: '1rem', textDecoration: 'none' }}>
          Sign In with Staff Account
        </Link>
      </div>
    )
  }

  return (
    <div className="staff-dashboard-page">
      <Breadcrumbs crumbs={[{ label: 'Home', href: '/' }, { label: 'School Staff Desk' }]} />

      <div className="container" style={{ maxWidth: '1100px', margin: '2rem auto', padding: '0 1rem' }}>
        {/* Staff Header */}
        <div className="card" style={{ padding: '1.5rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'inline-block', background: isSchoolAdmin ? '#fef3c7' : effectiveRole === 'admissions_officer' ? '#dbeafe' : effectiveRole === 'academic_admin' ? '#fce7f3' : effectiveRole === 'student_records_officer' ? '#dcfce7' : '#f1f5f9', color: isSchoolAdmin ? '#b45309' : effectiveRole === 'admissions_officer' ? '#1d4ed8' : effectiveRole === 'academic_admin' ? '#9d174d' : effectiveRole === 'student_records_officer' ? '#15803d' : '#334155', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
              {isSchoolAdmin ? 'INSTITUTION ADMINISTRATOR' :
               effectiveRole === 'admissions_officer' ? 'INSTITUTION ADMISSIONS OFFICER' :
               effectiveRole === 'academic_admin' ? 'ACADEMIC ADMINISTRATOR' :
               effectiveRole === 'student_records_officer' ? 'STUDENT RECORDS OFFICER' :
               'GENERAL STAFF MEMBER'}
            </div>
            <h1 style={{ fontSize: '1.75rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
              {isSchoolAdmin ? 'Institution Administrator Desk' :
               effectiveRole === 'admissions_officer' ? 'Admissions Management Desk' :
               effectiveRole === 'academic_admin' ? 'Academic Administration Desk' :
               effectiveRole === 'student_records_officer' ? 'Student Records Desk' :
               'Staff Verification Desk'}
            </h1>
            <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
              User: <strong>{user?.full_name || user?.email}</strong> · Assigned Institution ID: <strong style={{ color: '#1a3a6b' }}>{assignedSchoolId}</strong> · Role: <strong style={{ textTransform: 'capitalize' }}>{effectiveRole.replace('_', ' ')}</strong>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {isSchoolAdmin && (
              <button
                onClick={() => setActiveTab('admin-overview')}
                className={`btn btn--sm ${activeTab === 'admin-overview' ? 'btn--accent' : 'btn--ghost'}`}
              >
                School Overview
              </button>
            )}
            {(isSchoolAdmin || permissions.can_manage_students || effectiveRole === 'school_staff') && (
              <button
                onClick={() => { setActiveTab('queue'); loadRequests(); }}
                className={`btn btn--sm ${activeTab === 'queue' ? 'btn--primary' : 'btn--ghost'}`}
              >
                Linking Requests ({requests.length})
              </button>
            )}
            {(isSchoolAdmin || permissions.can_manage_students) && (
              <button
                onClick={() => setActiveTab('students')}
                className={`btn btn--sm ${activeTab === 'students' ? 'btn--primary' : 'btn--ghost'}`}
              >
                Student Roster (Filtered)
              </button>
            )}
            {isSchoolAdmin && (
              <button
                onClick={() => { setActiveTab('staff-mgmt'); loadStaffList(); }}
                className={`btn btn--sm ${activeTab === 'staff-mgmt' ? 'btn--accent' : 'btn--ghost'}`}
              >
                👥 Staff Management
              </button>
            )}
            {(isSchoolAdmin || permissions.can_view_applications) && (
              <button
                onClick={() => setActiveTab('admissions')}
                className={`btn btn--sm ${activeTab === 'admissions' ? 'btn--primary' : 'btn--ghost'}`}
              >
                📋 Admission Desk
              </button>
            )}
            {(isSchoolAdmin || permissions.can_manage_academics) && (
              <button
                onClick={() => setActiveTab('program-distribution')}
                className={`btn btn--sm ${activeTab === 'program-distribution' ? 'btn--accent' : 'btn--ghost'}`}
                style={{ fontWeight: 600 }}
              >
                📊 Programme Distribution
              </button>
            )}
            <button
              onClick={() => setActiveTab('academics')}
              className={`btn btn--sm ${activeTab === 'academics' ? 'btn--accent' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              📝 Academic & Attendance Desk
            </button>
          </div>
        </div>

        {error && <Alert type="error" title="Notice" className="mb-4">{error}</Alert>}
        {success && <Alert type="success" title="Success" className="mb-4">{success}</Alert>}

        {/* Tab 0: School Admin Overview (Only for school_admin) */}
        {activeTab === 'admin-overview' && isSchoolAdmin && (
          <div style={{ marginBottom: '1.5rem' }}>
            {loadingAdminOverview ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>Loading school administration metrics...</p>
              </div>
            ) : (
              <div>
                {/* 3 Metric Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div className="card" style={{ padding: '1.25rem', border: '1px solid #d0d5dd', borderRadius: '8px', textAlign: 'center', background: '#ffffff' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: '#1a3a6b' }}>
                      {adminOverview?.enrolled_students ?? 1500}
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#4b5563' }}>Enrolled Students</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Class 1 to 10 in this school</div>
                  </div>

                  <div className="card" style={{ padding: '1.25rem', border: '1px solid #d0d5dd', borderRadius: '8px', textAlign: 'center', background: '#ffffff' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d' }}>
                      {adminOverview?.authorized_staff_count ?? 2}
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#4b5563' }}>Authorized Staff</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Educators with review access</div>
                  </div>

                  <div className="card" style={{ padding: '1.25rem', border: '1px solid #d0d5dd', borderRadius: '8px', textAlign: 'center', background: '#ffffff' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: '#e07b00' }}>
                      {adminOverview?.pending_linking_requests ?? requests.filter(r => (r.request_status || r.status) === 'pending').length}
                    </div>
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, color: '#4b5563' }}>Pending Requests</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Awaiting guardian verification</div>
                  </div>
                </div>

                {/* Institution Profile Summary */}
                <div className="card" style={{ padding: '1.5rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff' }}>
                  <h3 style={{ fontSize: '1.2rem', color: '#1a3a6b', margin: '0 0 1rem 0' }}>
                    Institution Configuration & Data Governance
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', fontSize: '0.875rem' }}>
                    <div>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>School Name</div>
                      <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{adminOverview?.school?.school_name || 'Government Model School'}</div>
                    </div>
                    <div>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>District / State</div>
                      <div style={{ fontWeight: 600 }}>{adminOverview?.school?.district || 'Karnataka'}, {adminOverview?.school?.state || 'Karnataka'}</div>
                    </div>
                    <div>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>School Type</div>
                      <div style={{ fontWeight: 600 }}>{adminOverview?.school?.school_type || 'Government'}</div>
                    </div>
                    <div>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', textTransform: 'uppercase' }}>Review Oversight</div>
                      <div style={{ fontWeight: 600, color: '#15803d' }}>Stage 3 Multi-Verification Active</div>
                    </div>
                  </div>

                  <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid #e8eaed', display: 'flex', gap: '0.75rem' }}>
                    <button onClick={() => { setActiveTab('queue'); loadRequests(); }} className="btn btn--primary btn--sm">
                      Go to Linking Requests Queue →
                    </button>
                    <button onClick={() => setActiveTab('students')} className="btn btn--secondary btn--sm">
                      Inspect Student Roster →
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab: Staff Management (School Admin only) */}
        {activeTab === 'staff-mgmt' && isSchoolAdmin && (
          <div>
            <div className="card" style={{ padding: '1.25rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
                  Institutional Staff Directory & Invitations
                </h2>
                <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
                  Manage authorized educators, verification officers and staff assigned to school <strong>{assignedSchoolId}</strong>.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setStaffFullName('');
                  setStaffEmail('');
                  setStaffPhone('');
                  setStaffRole('school_staff');
                  setStaffInviteResult(null);
                  setStaffInviteError('');
                  setShowInviteStaffModal(true);
                }}
                className="btn btn--primary"
                style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                + Invite Staff Member
              </button>
            </div>

            {loadingStaff ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>Loading school staff roster...</p>
              </div>
            ) : (
              <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#475569' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Staff Member</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Assigned School</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Role</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Last Login</th>
                      </tr>
                    </thead>
                    <tbody>
                      {staffList.length === 0 ? (
                        <tr>
                          <td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                            No staff records found for this school.
                          </td>
                        </tr>
                      ) : (
                        staffList.map((st) => (
                          <tr key={st.user_id} style={{ borderBottom: '1px solid #e8eaed' }}>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{st.full_name}</div>
                              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{st.email}</div>
                              {st.phone && <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Tel: {st.phone}</div>}
                            </td>
                            <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#1a3a6b' }}>
                              {assignedSchoolId}
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span className="badge badge--info" style={{ fontSize: '0.75rem' }}>
                                {st.role_name || st.role_id || st.role}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span className={`badge ${st.status === 'active' ? 'badge--success' : 'badge--warning'}`} style={{ fontSize: '0.75rem' }}>
                                {(st.status || 'active').toUpperCase()}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem', fontSize: '0.8125rem', color: '#64748b' }}>
                              {st.last_login ? new Date(st.last_login).toLocaleString() : 'Never'}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Invite Staff Modal */}
        {showInviteStaffModal && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: '1rem',
            }}
          >
            <div
              className="card"
              style={{
                maxWidth: '520px',
                width: '100%',
                background: '#ffffff',
                borderRadius: '8px',
                padding: '2rem',
                maxHeight: '90vh',
                overflowY: 'auto',
                boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.35rem', color: '#1a3a6b', margin: 0 }}>
                  {staffInviteResult ? 'Staff Invitation Issued' : 'Invite Staff Member'}
                </h3>
                <button
                  type="button"
                  onClick={() => setShowInviteStaffModal(false)}
                  style={{ background: 'none', border: 'none', fontSize: '1.25rem', cursor: 'pointer', color: '#6b7280' }}
                >
                  ✕
                </button>
              </div>

              {staffInviteResult ? (
                <div>
                  <Alert type="success" title="Invitation Created" className="mb-4">
                    Invitation link generated for <strong>{staffInviteResult.email}</strong> at school <strong>{assignedSchoolId}</strong>.
                  </Alert>

                  <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '6px', border: '1px solid #cbd5e1', marginBottom: '1.5rem' }}>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.4rem' }}>
                      Activation Link:
                    </div>
                    <input
                      type="text"
                      readOnly
                      value={staffInviteResult.invitation_link || `http://localhost:5173/#/accept-invitation?token=${staffInviteResult.invitation_token}`}
                      style={{ width: '100%', padding: '0.5rem', fontSize: '0.8125rem', fontFamily: 'monospace', background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '4px', marginBottom: '0.75rem' }}
                      onClick={e => e.target.select()}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard?.writeText(staffInviteResult.invitation_link || `http://localhost:5173/#/accept-invitation?token=${staffInviteResult.invitation_token}`)
                        setSuccess('Staff invitation link copied to clipboard!')
                      }}
                      className="btn btn--accent"
                    >
                      Copy Link
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowInviteStaffModal(false)}
                      className="btn btn--primary"
                    >
                      Done
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleStaffInviteSubmit}>
                  {staffInviteError && <Alert type="error" title="Error" className="mb-4">{staffInviteError}</Alert>}

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Staff Member Name *
                    </label>
                    <input
                      type="text"
                      required
                      className="input"
                      placeholder="e.g. Anand Murthy"
                      value={staffFullName}
                      onChange={e => setStaffFullName(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      className="input"
                      placeholder="e.g. anand@school.edu.in"
                      value={staffEmail}
                      onChange={e => setStaffEmail(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Contact Mobile (Optional)
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="e.g. 9845098765"
                      value={staffPhone}
                      onChange={e => setStaffPhone(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Target Institution
                    </label>
                    <input
                      type="text"
                      disabled
                      value={`${assignedSchoolId} (Locked to your school)`}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', background: '#f1f5f9', color: '#64748b' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Role within School *
                    </label>
                    <select
                      className="input"
                      value={staffRole}
                      onChange={e => setStaffRole(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    >
                      <option value="school_staff">School Staff / Teacher</option>
                      <option value="admissions_officer">Admissions Desk Officer</option>
                      <option value="academic_admin">Academic Coordinator</option>
                      <option value="student_records_officer">Student Records Officer</option>
                    </select>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <button
                      type="button"
                      onClick={() => setShowInviteStaffModal(false)}
                      className="btn btn--ghost"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={submittingStaffInvite}
                      className="btn btn--primary"
                      style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                      {submittingStaffInvite ? <LoadingSpinner size="sm" /> : 'Send Staff Invitation →'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Tab 1: Linking Requests Queue */}
        {activeTab === 'queue' && (
          <div>
            {/* Filter Bar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {['pending', 'approved', 'rejected', 'all'].map(status => (
                  <button
                    key={status}
                    onClick={() => setRequestFilter(status)}
                    className={`btn btn--sm ${requestFilter === status ? 'btn--secondary' : 'btn--ghost'}`}
                    style={{ textTransform: 'capitalize' }}
                  >
                    {status}
                  </button>
                ))}
              </div>
              <button onClick={loadRequests} className="btn btn--ghost btn--sm">
                🔄 Refresh Queue
              </button>
            </div>

            {loadingRequests ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>Fetching incoming parent applications...</p>
              </div>
            ) : requests.length === 0 ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>✅</div>
                <h3 style={{ color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>No {requestFilter} Requests</h3>
                <p style={{ color: '#4b5563', margin: 0 }}>
                  There are currently no linking requests with status "{requestFilter}" for school {assignedSchoolId}.
                </p>
              </div>
            ) : (
              <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#475569' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Request ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Parent Guardian</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Relationship</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Student Reference</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Submitted</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {requests.map(r => (
                        <tr key={r.request_id} style={{ borderBottom: '1px solid #e8eaed' }}>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                            {r.request_id.slice(0, 8)}...
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{r.parent_name || 'Parent Guardian'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>ID: <code style={{ fontSize: '0.72rem' }}>{r.parent_user_id}</code></div>
                            {r.parent_email && <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{r.parent_email}</div>}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>{r.relationship_type}</td>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>
                            <span style={{ background: '#f8fafc', padding: '0.2rem 0.5rem', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
                              {r.student_ref}
                            </span>
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: '#6b7280' }}>
                            {(r.created_at || r.submitted_at) ? new Date(r.created_at || r.submitted_at).toLocaleDateString() : 'Recent'}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <StatusBadge status={r.request_status || r.status} />
                          </td>
                          <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                            {(r.request_status === 'pending' || r.status === 'pending') ? (
                              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                                <button
                                  onClick={() => openReviewModal(r)}
                                  className="btn btn--primary btn--sm"
                                >
                                  Review →
                                </button>
                                <button
                                  onClick={() => handleStaffIssueCode(r)}
                                  disabled={issuingCode}
                                  className="btn btn--sm"
                                  style={{ background: '#155EEF', color: '#fff', border: 'none', fontWeight: 600, borderRadius: '4px', padding: '0.35rem 0.65rem' }}
                                  title="Issue official 6-digit verification code"
                                >
                                  🔑 Issue Code
                                </button>
                              </div>
                            ) : (
                              <span style={{ fontSize: '0.8125rem', color: '#6b7280' }}>Reviewed</span>
                            )}
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

        {/* Tab 2: Enrolled Student Directory (Standard & Section Filtered) */}
        {activeTab === 'students' && (
          <div>
            <div className="card" style={{ padding: '1.5rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff' }}>
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.2rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
                  School Roster Query Engine
                </h3>
                <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
                  Per system performance and privacy regulations, full student tables are never queried automatically. Specify Standard and Section below.
                </p>
              </div>

              <form onSubmit={fetchRoster} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                <div style={{ flex: '1', minWidth: '150px' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.25rem' }}>
                    Select Standard <span style={{ color: '#b91c1c' }}>*</span>
                  </label>
                  <select
                    className="input"
                    value={selectedStandard}
                    onChange={e => setSelectedStandard(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                  >
                    {availableStandards.map(std => (
                      <option key={std} value={std}>
                        {std <= 10 ? `Standard ${std}` : `Standard ${std} (PUC-${std === 11 ? 'I' : 'II'})`}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ flex: '1', minWidth: '150px' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.25rem' }}>
                    Select Section <span style={{ color: '#b91c1c' }}>*</span>
                  </label>
                  <select
                    className="input"
                    value={selectedSection}
                    onChange={e => setSelectedSection(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                  >
                    {availableSections.map(sec => (
                      <option key={sec} value={sec}>Section {sec}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <button
                    type="submit"
                    disabled={loadingStudents}
                    className="btn btn--primary"
                    style={{ height: '38px', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                  >
                    {loadingStudents ? <LoadingSpinner size="sm" /> : 'Fetch Enrolled Students 🔍'}
                  </button>
                </div>
              </form>
            </div>

            {loadingStudents ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>Fetching Class {selectedStandard}-{selectedSection} student records...</p>
              </div>
            ) : !hasQueriedStudents ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px dashed #d0d5dd', borderRadius: '8px', color: '#6b7280' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📚</div>
                <p style={{ margin: 0 }}>Select Standard & Section above and click "Fetch Enrolled Students" to view records.</p>
              </div>
            ) : students.length === 0 ? (
              <div className="card" style={{ padding: '2rem', textAlign: 'center', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                No students enrolled in Standard {selectedStandard} Section {selectedSection}.
              </div>
            ) : (
              <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: '#1a3a6b' }}>
                    Standard {selectedStandard} — Section {selectedSection} ({students.length} Enrolled)
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>Max limit 50 per query</span>
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#475569' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Student ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Permanent Student ID</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Student Name</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Age</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Class</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map((st, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid #e8eaed' }}>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem' }}>{st.student_id}</td>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem', color: '#1a3a6b', fontWeight: 600 }}>
                            {st.permanent_student_id || st.student_id}
                          </td>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{st.student_name}</td>
                          <td style={{ padding: '0.75rem 1rem' }}>{st.age || '—'}</td>
                          <td style={{ padding: '0.75rem 1rem' }}>Class {st.standard}-{st.section}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Programme-Based Sections & Distribution */}
        {/* Tab 4: Admission Management Desk */}
        {activeTab === 'admissions' && (
          <AdmissionDeskTab
            schoolId={assignedSchoolId}
            permissions={permissions}
            effectiveRole={effectiveRole}
          />
        )}

        {activeTab === 'program-distribution' && (
          <div>
            {/* Header & Quick Filter Presets */}
            <div className="card" style={{ padding: '1.5rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
                <div>
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', background: '#eff6ff', color: '#1d4ed8', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
                    <span>🏫</span> FOUR-TIER EDUCATION STRUCTURE & SECTION STRENGTH ENGINE
                  </div>
                  <h2 style={{ fontSize: '1.35rem', color: '#1a3a6b', margin: '0 0 0.35rem 0' }}>
                    Programme-Based Student Distribution
                  </h2>
                  <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0, maxWidth: '800px' }}>
                    Independently configurable student strength and capacity limits across streams, combinations, degree specialisations, and sections. Student counts vary per programme according to institutional sanctions.
                  </p>
                </div>

                <button
                  onClick={loadProgramSections}
                  disabled={loadingProgSections}
                  className="btn btn--secondary btn--sm"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  🔄 {loadingProgSections ? 'Updating...' : 'Refresh Records'}
                </button>
              </div>

              {/* Quick Presets */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', paddingTop: '0.75rem', borderTop: '1px solid #f1f5f9' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#64748b' }}>Quick Filter Presets:</span>
                <button
                  type="button"
                  onClick={() => {
                    setFilterLevel('higher_secondary');
                    setFilterInst('SCH011');
                    setFilterStream('all');
                    setFilterCombination('all');
                    setFilterTermYear('11');
                    setFilterSection('all');
                  }}
                  className="btn btn--ghost btn--sm"
                  style={{ fontSize: '0.75rem', background: filterLevel === 'higher_secondary' ? '#e0f2fe' : '#f8fafc', border: '1px solid #cbd5e1' }}
                >
                  🔬 PU Combinations (PCMB, PCMC, SEBA, HEBA, MEBA)
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setFilterLevel('diploma');
                    setFilterInst('COL001');
                    setFilterStream('all');
                    setFilterCombination('all');
                    setFilterTermYear('all');
                    setFilterSection('all');
                  }}
                  className="btn btn--ghost btn--sm"
                  style={{ fontSize: '0.75rem', background: filterLevel === 'diploma' ? '#e0f2fe' : '#f8fafc', border: '1px solid #cbd5e1' }}
                >
                  ⚙️ Polytechnic Diplomas (CS, Automobile, Mech, Civil)
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setFilterLevel('undergraduate');
                    setFilterInst('COL006');
                    setFilterStream('all');
                    setFilterCombination('all');
                    setFilterTermYear('all');
                    setFilterSection('all');
                  }}
                  className="btn btn--ghost btn--sm"
                  style={{ fontSize: '0.75rem', background: filterLevel === 'undergraduate' ? '#e0f2fe' : '#f8fafc', border: '1px solid #cbd5e1' }}
                >
                  📜 BA Specialisations (History, Econ, PolSci, Soc, Psych)
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setFilterLevel('all');
                    setFilterInst('all');
                    setFilterStream('all');
                    setFilterCombination('all');
                    setFilterTermYear('all');
                    setFilterSemester('all');
                    setFilterSection('all');
                  }}
                  className="btn btn--ghost btn--sm"
                  style={{ fontSize: '0.75rem', color: '#64748b' }}
                >
                  Reset All Filters
                </button>
              </div>
            </div>

            {/* Filter Selection Panel */}
            <div className="card" style={{ padding: '1.25rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff' }}>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#1a3a6b', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <span>🎯</span> Multi-Tier Filter Controls
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                {/* 1. Education Level */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    1. Education Level
                  </label>
                  <select
                    className="input"
                    value={filterLevel}
                    onChange={e => { setFilterLevel(e.target.value); setFilterCombination('all'); }}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Education Levels</option>
                    <option value="school">Level 1: School Education (Std 1–10)</option>
                    <option value="higher_secondary">Level 2: Higher Secondary / PU</option>
                    <option value="diploma">Level 3: Diploma / Polytechnic</option>
                    <option value="undergraduate">Level 4: Undergraduate Degrees</option>
                  </select>
                </div>

                {/* 2. Institution */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    2. Institution
                  </label>
                  <select
                    className="input"
                    value={filterInst}
                    onChange={e => setFilterInst(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Institutions (Global)</option>
                    <optgroup label="Higher Secondary / PU Schools">
                      <option value="SCH011">SCH011 - Bangalore South Composite PU</option>
                      <option value="SCH012">SCH012 - Mysore Central Model PU</option>
                      <option value="SCH013">SCH013 - Hubli-Dharwad Composite School</option>
                    </optgroup>
                    <optgroup label="Colleges & Universities">
                      <option value="COL001">COL001 - Ramaiah Institute of Technology</option>
                      <option value="COL002">COL002 - RV College of Engineering</option>
                      <option value="COL004">COL004 - PES University</option>
                      <option value="COL006">COL006 - St. Joseph's University (BA / Degree)</option>
                      <option value="COL007">COL007 - Mount Carmel College</option>
                      <option value="COL008">COL008 - KLE Technological University</option>
                      <option value="COL009">COL009 - University of Mysore</option>
                    </optgroup>
                    <optgroup label="Primary / High Schools">
                      <option value="SCH001">SCH001 - Government Model Primary School</option>
                      <option value="SCH002">SCH002 - Government High School</option>
                    </optgroup>
                  </select>
                </div>

                {/* 3. Stream / Discipline */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    3. Stream / Discipline
                  </label>
                  <select
                    className="input"
                    value={filterStream}
                    onChange={e => setFilterStream(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Streams</option>
                    <option value="Science">Science (PCMB, PCMC, etc.)</option>
                    <option value="Commerce">Commerce (SEBA, HEBA, MEBA, CEBA)</option>
                    <option value="Arts / Humanities">Arts / Humanities (HEPS, BA)</option>
                    <option value="Engineering">Engineering & Technology</option>
                    <option value="Management">Management (BBA)</option>
                    <option value="Computer Applications">Computer Applications (BCA)</option>
                    <option value="Pharmacy">Pharmacy (B.Pharm)</option>
                    <option value="General">General / Core Schooling</option>
                  </select>
                </div>

                {/* 4. Combination / Specialisation */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    4. Combination / Specialisation
                  </label>
                  <select
                    className="input"
                    value={filterCombination}
                    onChange={e => setFilterCombination(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Combinations</option>
                    <optgroup label="PU Combinations">
                      <option value="PCMB">PCMB (Physics, Chem, Math, Bio)</option>
                      <option value="PCMC">PCMC (Physics, Chem, Math, CompSci)</option>
                      <option value="PCME">PCME (Physics, Chem, Math, Electronics)</option>
                      <option value="SEBA">SEBA (Stats, Econ, Business, Accts)</option>
                      <option value="HEBA">HEBA (History, Econ, Business, Accts)</option>
                      <option value="MEBA">MEBA (Math, Econ, Business, Accts)</option>
                      <option value="CEBA">CEBA (CompSci, Econ, Business, Accts)</option>
                      <option value="HEPS">HEPS (History, Econ, PolSci, Soc)</option>
                    </optgroup>
                    <optgroup label="Diploma Engineering Streams">
                      <option value="CS-DIP">Diploma in Computer Science</option>
                      <option value="AUTO-DIP">Diploma in Automobile Engineering</option>
                      <option value="ME-DIP">Diploma in Mechanical Engineering</option>
                      <option value="CE-DIP">Diploma in Civil Engineering</option>
                      <option value="EC-DIP">Diploma in Electronics & Comm</option>
                    </optgroup>
                    <optgroup label="Undergraduate BA Specialisations">
                      <option value="BA-HIST">BA - History & Archaeology</option>
                      <option value="BA-ECON">BA - Economics & Public Policy</option>
                      <option value="BA-POLS">BA - Political Science & Governance</option>
                      <option value="BA-SOC">BA - Sociology & Social Work</option>
                      <option value="BA-PSYC">BA - Applied Psychology</option>
                    </optgroup>
                    <optgroup label="Undergraduate Professional Degrees">
                      <option value="BCA">BCA - Computer Applications</option>
                      <option value="BBA">BBA - Business Administration</option>
                      <option value="B.Com">B.Com - International Finance / Hons</option>
                      <option value="B.Sc">B.Sc - Physical / Life Sciences</option>
                      <option value="B.E. / B.Tech">B.E. / B.Tech Engineering</option>
                      <option value="B.Pharm">B.Pharm - Pharmacy</option>
                    </optgroup>
                  </select>
                </div>

                {/* 5. Academic Year */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    5. Academic Year
                  </label>
                  <select
                    className="input"
                    value={filterAcademicYear}
                    onChange={e => setFilterAcademicYear(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="2025-26">2025-26 (Current Academic Term)</option>
                    <option value="all">All Academic Years</option>
                  </select>
                </div>

                {/* 6. Year of Study / Term */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    6. Year / Standard
                  </label>
                  <select
                    className="input"
                    value={filterTermYear}
                    onChange={e => setFilterTermYear(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Years / Terms</option>
                    <option value="11">Standard 11 (PUC-I)</option>
                    <option value="12">Standard 12 (PUC-II)</option>
                    <option value="1">1st Year (Degree / Diploma / Std 1)</option>
                    <option value="2">2nd Year (Degree / Diploma / Std 2)</option>
                    <option value="3">3rd Year (Degree / Diploma / Std 3)</option>
                    <option value="4">4th Year (Engineering / Pharmacy)</option>
                  </select>
                </div>

                {/* 7. Semester */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    7. Semester
                  </label>
                  <select
                    className="input"
                    value={filterSemester}
                    onChange={e => setFilterSemester(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Semesters</option>
                    <option value="1">Semester 1</option>
                    <option value="2">Semester 2</option>
                    <option value="3">Semester 3</option>
                    <option value="4">Semester 4</option>
                    <option value="5">Semester 5</option>
                    <option value="6">Semester 6</option>
                    <option value="7">Semester 7</option>
                    <option value="8">Semester 8</option>
                  </select>
                </div>

                {/* 8. Section */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475569', marginBottom: '0.25rem', textTransform: 'uppercase' }}>
                    8. Section
                  </label>
                  <select
                    className="input"
                    value={filterSection}
                    onChange={e => setFilterSection(e.target.value)}
                    style={{ width: '100%', padding: '0.45rem 0.6rem', fontSize: '0.85rem', border: '1px solid #cbd5e1', borderRadius: '4px' }}
                  >
                    <option value="all">All Sections (A, B, C)</option>
                    <option value="A">Section A</option>
                    <option value="B">Section B</option>
                    <option value="C">Section C</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Metrics Bar */}
            {(() => {
              const totalStrength = progSections.reduce((acc, s) => acc + (s.current_strength || 0), 0);
              const totalCapacity = progSections.reduce((acc, s) => acc + (s.capacity || 0), 0);
              const utilization = totalCapacity > 0 ? Math.round((totalStrength / totalCapacity) * 100) : 0;
              const avgStrength = progSections.length > 0 ? Math.round(totalStrength / progSections.length) : 0;

              return (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div className="card" style={{ padding: '1.15rem', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#ffffff', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Filtered Sections</div>
                    <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#1a3a6b', margin: '0.25rem 0' }}>
                      {progSections.length}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Configured division cohorts</div>
                  </div>

                  <div className="card" style={{ padding: '1.15rem', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#ffffff', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Total Enrolled Strength</div>
                    <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#15803d', margin: '0.25rem 0' }}>
                      {totalStrength.toLocaleString()}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Actual students across sections</div>
                  </div>

                  <div className="card" style={{ padding: '1.15rem', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#ffffff', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Sanctioned Capacity</div>
                    <div style={{ fontSize: '1.85rem', fontWeight: 700, color: '#3b82f6', margin: '0.25rem 0' }}>
                      {totalCapacity.toLocaleString()}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Max permissible seats</div>
                  </div>

                  <div className="card" style={{ padding: '1.15rem', border: '1px solid #e2e8f0', borderRadius: '8px', background: '#ffffff', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase' }}>Overall Utilization</div>
                    <div style={{ fontSize: '1.85rem', fontWeight: 700, color: utilization > 90 ? '#ea580c' : '#059669', margin: '0.25rem 0' }}>
                      {utilization}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Avg {avgStrength} students / section</div>
                  </div>
                </div>
              );
            })()}

            {/* Results Table */}
            {loadingProgSections ? (
              <div style={{ textAlign: 'center', padding: '3.5rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #d0d5dd' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.75rem', color: '#64748b' }}>Querying programme sections and strengths...</p>
              </div>
            ) : progSections.length === 0 ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px dashed #cbd5e1', borderRadius: '8px', background: '#ffffff' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🔍</div>
                <h3 style={{ color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>No Programme Sections Match This Filter</h3>
                <p style={{ color: '#64748b', margin: 0 }}>
                  Adjust education level, stream, combination, or institution filters to display matching section records.
                </p>
              </div>
            ) : (
              <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                <div style={{ padding: '0.85rem 1.25rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: '#1a3a6b', fontSize: '0.9rem' }}>
                    Showing {progSections.length} Programme Section Distributions
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    Academic Year 2025-26 · Live Configured Strengths
                  </span>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#475569' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Institution</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Education Level</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Programme & Discipline</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Combination / Specialisation</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Term / Semester</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Section</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Enrolled Strength</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Capacity</th>
                        <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Seat Utilization</th>
                      </tr>
                    </thead>
                    <tbody>
                      {progSections.map((sec, idx) => {
                        const pct = sec.capacity > 0 ? Math.round((sec.current_strength / sec.capacity) * 100) : 0;
                        const isPuHighlight = ['PCMB', 'PCMC', 'PCME', 'SEBA', 'HEBA', 'MEBA', 'CEBA', 'HEPS'].includes(sec.combination_code);

                        return (
                          <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9', background: idx % 2 === 0 ? '#ffffff' : '#fafafa' }}>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{sec.institution_id}</div>
                              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{sec.institution_name || sec.institution_id}</div>
                            </td>

                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span style={{
                                display: 'inline-block',
                                padding: '0.2rem 0.5rem',
                                borderRadius: '4px',
                                fontSize: '0.75rem',
                                fontWeight: 600,
                                background:
                                  sec.education_level === 'higher_secondary' ? '#eff6ff' :
                                  sec.education_level === 'diploma' ? '#fef3c7' :
                                  sec.education_level === 'undergraduate' ? '#ecfdf5' : '#f1f5f9',
                                color:
                                  sec.education_level === 'higher_secondary' ? '#1d4ed8' :
                                  sec.education_level === 'diploma' ? '#b45309' :
                                  sec.education_level === 'undergraduate' ? '#047857' : '#475569',
                              }}>
                                {sec.education_level === 'higher_secondary' ? 'Higher Secondary' :
                                 sec.education_level === 'diploma' ? 'Polytechnic Diploma' :
                                 sec.education_level === 'undergraduate' ? 'Undergraduate Degree' : 'School (1–10)'}
                              </span>
                            </td>

                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 600, color: '#0f172a' }}>{sec.program_name}</div>
                              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                                Stream: {sec.discipline_or_stream} {sec.degree_type && sec.degree_type !== 'None' ? `· Degree: ${sec.degree_type}` : ''}
                              </div>
                            </td>

                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span style={{
                                display: 'inline-block',
                                padding: '0.2rem 0.5rem',
                                borderRadius: '4px',
                                fontFamily: 'monospace',
                                fontWeight: 700,
                                fontSize: '0.8rem',
                                background: isPuHighlight ? '#dbeafe' : '#f1f5f9',
                                color: isPuHighlight ? '#1e40af' : '#334155',
                                border: isPuHighlight ? '1px solid #bfdbfe' : '1px solid #e2e8f0',
                              }}>
                                {sec.combination_code}
                              </span>
                            </td>

                            <td style={{ padding: '0.75rem 1rem', color: '#334155' }}>
                              <div style={{ fontWeight: 600 }}>
                                {sec.term_or_year >= 11 ? `Std ${sec.term_or_year} (PUC-${sec.term_or_year === 11 ? 'I' : 'II'})` :
                                 sec.term_or_year <= 10 && sec.education_level === 'school' ? `Standard ${sec.term_or_year}` :
                                 `Year ${sec.term_or_year}`}
                              </div>
                              {sec.semester && (
                                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Semester {sec.semester}</div>
                              )}
                            </td>

                            <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>
                              <span style={{
                                display: 'inline-flex',
                                width: '28px',
                                height: '28px',
                                borderRadius: '50%',
                                background: '#f8fafc',
                                border: '1px solid #cbd5e1',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontWeight: 700,
                                color: '#0f172a',
                              }}>
                                {sec.section_name}
                              </span>
                            </td>

                            <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                              <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#15803d' }}>
                                {sec.current_strength}
                              </div>
                              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>students</div>
                            </td>

                            <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                              <div style={{ fontSize: '0.95rem', fontWeight: 600, color: '#334155' }}>
                                {sec.capacity}
                              </div>
                              <div style={{ fontSize: '0.7rem', color: '#94a3b8' }}>max capacity</div>
                            </td>

                            <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>
                              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem' }}>
                                <div style={{ width: '80px', height: '6px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden' }}>
                                  <div style={{
                                    width: `${Math.min(pct, 100)}%`,
                                    height: '100%',
                                    background: pct >= 90 ? '#ea580c' : pct >= 70 ? '#15803d' : '#3b82f6',
                                  }} />
                                </div>
                                <span style={{
                                  fontSize: '0.7rem',
                                  fontWeight: 600,
                                  color: pct >= 90 ? '#c2410c' : pct >= 70 ? '#15803d' : '#2563eb',
                                }}>
                                  {pct}% filled
                                </span>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab: Academic & Attendance Desk */}
        {activeTab === 'academics' && (
          <StaffAcademicDesk
            token={token}
            schoolId={assignedSchoolId}
            institutionName={user?.school_name || assignedSchoolId}
          />
        )}

        {/* Official 6-Digit Code Modal for Staff Dispatch */}
        {issuedCodeData && (
          <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(15, 23, 42, 0.75)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, padding: '1rem'
          }}>
            <div style={{
              background: '#FFFFFF', borderRadius: '12px',
              maxWidth: '500px', width: '100%', overflow: 'hidden',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
            }}>
              <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#FFFFFF' }}>
                  🔑 Institution Verification Code Issued
                </h3>
                <button
                  onClick={() => setIssuedCodeData(null)}
                  style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '1.4rem', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>
              <div style={{ padding: '1.5rem' }}>
                <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
                  <div style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '0.5rem' }}>
                    Official 6-Digit Authorization Code:
                  </div>
                  <div style={{
                    background: '#F0FDF4', border: '2px dashed #16A34A', borderRadius: '8px',
                    padding: '1rem', display: 'inline-block', minWidth: '200px'
                  }}>
                    <span style={{ fontSize: '2.2rem', fontWeight: 900, fontFamily: 'monospace', letterSpacing: '8px', color: '#15803D' }}>
                      {issuedCodeData.verification_code}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.775rem', color: '#16A34A', marginTop: '0.4rem', fontWeight: 600 }}>
                    ⏱️ Valid for 15 minutes · Single-use authorization
                  </div>
                </div>

                <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem', fontSize: '0.84rem', color: '#334155' }}>
                  <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600 }}>
                    Provide this code to parent <strong>{issuedCodeData.request?.parent_name}</strong> (Parent Account: <code>{issuedCodeData.request?.parent_user_id}</code>).
                  </p>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748B' }}>
                    The parent will enter this code on the Parent Portal to complete the child verification.
                  </p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(issuedCodeData.verification_code)
                      alert('Code copied to clipboard!')
                    }}
                    className="btn btn--secondary btn--sm"
                  >
                    📋 Copy Code
                  </button>
                  <button
                    onClick={() => setIssuedCodeData(null)}
                    className="btn btn--primary btn--sm"
                  >
                    Done
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Review & Approval Modal */}
        {activeReviewRequest && (
          <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000 }}>
            <div className="card" style={{ maxWidth: '680px', width: '100%', maxHeight: '90vh', overflowY: 'auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', position: 'relative' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid #e8eaed', paddingBottom: '1rem', marginBottom: '1.25rem' }}>
                <div>
                  <span className="badge badge--pending" style={{ marginBottom: '0.25rem' }}>STAGE 3 VERIFICATION WORKFLOW</span>
                  <h2 style={{ fontSize: '1.4rem', color: '#1a3a6b', margin: '0.25rem 0' }}>
                    Review Student-Linking Request
                  </h2>
                  <p style={{ margin: 0, color: '#6b7280', fontSize: '0.8125rem' }}>
                    Request ID: <code>{activeReviewRequest.request_id}</code>
                  </p>
                </div>
                <button
                  onClick={() => setActiveReviewRequest(null)}
                  style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#6b7280' }}
                >
                  ✕
                </button>
              </div>

              {reviewError && <Alert type="error" title="Review Error" className="mb-4">{reviewError}</Alert>}

              {/* Request Details */}
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '1rem', marginBottom: '1.25rem', fontSize: '0.875rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem' }}>
                  <div>Parent Name: <strong>{activeReviewRequest.parent_name || 'Parent Guardian'}</strong></div>
                  <div>Relationship: <strong>{activeReviewRequest.relationship_type}</strong></div>
                  <div>Parent Student Ref: <strong style={{ color: '#e07b00', fontFamily: 'monospace' }}>{activeReviewRequest.student_ref}</strong></div>
                  <div>Submitted: <strong>{activeReviewRequest.submitted_at ? new Date(activeReviewRequest.submitted_at).toLocaleDateString() : 'Recent'}</strong></div>
                </div>
                {activeReviewRequest.additional_notes && (
                  <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px dashed #cbd5e1' }}>
                    Parent Notes: <em>"{activeReviewRequest.additional_notes}"</em>
                  </div>
                )}
              </div>

              <form onSubmit={handleReviewSubmit}>
                {/* Decision Radio */}
                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.5rem' }}>
                    Verification Decision <span style={{ color: '#b91c1c' }}>*</span>
                  </label>
                  <div style={{ display: 'flex', gap: '1.5rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name="decision"
                        value="approved"
                        checked={decision === 'approved'}
                        onChange={() => setDecision('approved')}
                      />
                      <span style={{ fontWeight: 600, color: '#15803d' }}>Approve Link</span>
                    </label>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                      <input
                        type="radio"
                        name="decision"
                        value="rejected"
                        checked={decision === 'rejected'}
                        onChange={() => setDecision('rejected')}
                      />
                      <span style={{ fontWeight: 600, color: '#b91c1c' }}>Reject Request</span>
                    </label>
                  </div>
                </div>

                {/* Candidate Selection (Only on approve) */}
                {decision === 'approved' && (
                  <div style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Matched Student in School Ledger <span style={{ color: '#b91c1c' }}>*</span>
                    </label>
                    <select
                      required
                      className="input"
                      value={selectedCandidate?.permanent_student_id || selectedCandidate?.student_id || ''}
                      onChange={e => {
                        const cand = candidateStudents.find(s => (s.permanent_student_id || s.student_id) === e.target.value)
                        setSelectedCandidate(cand)
                      }}
                      style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    >
                      <option value="">-- Select Candidate Student --</option>
                      {candidateStudents.map((s, idx) => (
                        <option key={idx} value={s.permanent_student_id || s.student_id}>
                          {s.student_name} (Class {s.standard}-{s.section}) — {s.permanent_student_id || s.student_id}
                        </option>
                      ))}
                    </select>

                    {/* Mismatch Warning & confirm_student_match toggle */}
                    {selectedCandidate && !isDirectMatch(activeReviewRequest, selectedCandidate) && (
                      <div style={{ marginTop: '0.75rem', background: '#fef3c7', border: '1px solid #f59c2a', borderRadius: '6px', padding: '0.75rem' }}>
                        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                          <span style={{ color: '#b45309', fontSize: '1.1rem' }}>⚠️</span>
                          <div>
                            <div style={{ fontWeight: 600, color: '#b45309', fontSize: '0.875rem' }}>
                              Student Reference Mismatch Detected
                            </div>
                            <div style={{ fontSize: '0.8125rem', color: '#78350f', marginTop: '0.2rem' }}>
                              The parent requested: <strong>"{activeReviewRequest.student_ref}"</strong>, which differs from selected student <strong>"{selectedCandidate.student_name}" ({selectedCandidate.permanent_student_id || selectedCandidate.student_id})</strong>.
                            </div>
                            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem', cursor: 'pointer', fontSize: '0.8125rem', fontWeight: 600, color: '#78350f' }}>
                              <input
                                type="checkbox"
                                checked={confirmMatch}
                                onChange={e => setConfirmMatch(e.target.checked)}
                              />
                              I explicitly confirm manual verification of this student match (confirm_student_match)
                            </label>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Review Comment */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                    Staff Audit Comment <span style={{ color: '#b91c1c' }}>*</span> (Minimum 3 characters)
                  </label>
                  <textarea
                    required
                    minLength={3}
                    className="input"
                    rows={3}
                    placeholder="Enter reason or verification notes (logged to audit_logs ledger)"
                    value={reviewComment}
                    onChange={e => setReviewComment(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', resize: 'vertical' }}
                  />
                </div>

                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button
                    type="submit"
                    disabled={submittingReview}
                    className={`btn btn--lg ${decision === 'approved' ? 'btn--primary' : 'btn--danger'}`}
                    style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}
                  >
                    {submittingReview ? <LoadingSpinner size="sm" /> : `Confirm & ${decision === 'approved' ? 'Approve Link' : 'Reject Request'}`}
                  </button>
                  <button
                    type="button"
                    onClick={() => setActiveReviewRequest(null)}
                    className="btn btn--ghost btn--lg"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
