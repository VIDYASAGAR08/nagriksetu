import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { apiGet, apiPut, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'
import StatusBadge from '../ui/StatusBadge.jsx'
import StudentDossierModal from '../academic/StudentDossierModal.jsx'

export default function InstitutionStudentManagementDesk({
  token,
  institutionId,
  institutionName,
  institutionCategory = 'Schools',
}) {
  // ---------------------------------------------------------------------------
  // 1. DASHBOARD METRICS & STATS STATE
  // ---------------------------------------------------------------------------
  const [stats, setStats] = useState(null)
  const [loadingStats, setLoadingStats] = useState(true)
  const [statsError, setStatsError] = useState('')
  const [showRecentUpdatesModal, setShowRecentUpdatesModal] = useState(false)
  const [showPendingRequestsModal, setShowPendingRequestsModal] = useState(false)

  // ---------------------------------------------------------------------------
  // 2. ACADEMIC STRUCTURE STATE
  // ---------------------------------------------------------------------------
  const [structure, setStructure] = useState(null)
  const [loadingStructure, setLoadingStructure] = useState(true)
  const [structureError, setStructureError] = useState('')

  // ---------------------------------------------------------------------------
  // 3. SEARCH & FILTER STATE
  // ---------------------------------------------------------------------------
  const [searchQuery, setSearchQuery] = useState('')
  const [divisionFilter, setDivisionFilter] = useState('all') // 'all' | 'school' | 'pu' | 'degree'
  const [selectedStandard, setSelectedStandard] = useState('')
  const [selectedSection, setSelectedSection] = useState('')
  const [academicYearFilter, setAcademicYearFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all') // 'all' | 'active' | 'inactive'
  const [selectedStream, setSelectedStream] = useState('')
  const [selectedCombination, setSelectedCombination] = useState('')
  const [selectedProgram, setSelectedProgram] = useState('')

  // Sorting & Pagination
  const [sortBy, setSortBy] = useState('student_name')
  const [sortOrder, setSortOrder] = useState('asc')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  // ---------------------------------------------------------------------------
  // 4. STUDENT QUERY RESULTS STATE
  // ---------------------------------------------------------------------------
  const [students, setStudents] = useState([])
  const [totalCount, setTotalCount] = useState(0)
  const [loadingStudents, setLoadingStudents] = useState(false)
  const [studentsError, setStudentsError] = useState('')
  const [feedbackMessage, setFeedbackMessage] = useState(null) // { type: 'success' | 'error', text: '' }

  // ---------------------------------------------------------------------------
  // 5. STUDENT PROFILE MODAL STATE
  // ---------------------------------------------------------------------------
  const [selectedStudentId, setSelectedStudentId] = useState(null)
  const [dossierModalOpen, setDossierModalOpen] = useState(false)
  const [reportStudentId, setReportStudentId] = useState(null)
  const [studentProfile, setStudentProfile] = useState(null)
  const [loadingProfile, setLoadingProfile] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [profileTab, setProfileTab] = useState('personal') // 'personal' | 'guardian' | 'academic' | 'attendance' | 'results' | 'documents' | 'history'

  // ---------------------------------------------------------------------------
  // 6. RECORD EDITING MODAL STATE
  // ---------------------------------------------------------------------------
  const [editingStudent, setEditingStudent] = useState(null)
  const [editFormData, setEditFormData] = useState({})
  const [editReason, setEditReason] = useState('')
  const [editValidationErrors, setEditValidationErrors] = useState({})
  const [showEditConfirmModal, setShowEditConfirmModal] = useState(false)
  const [savingEdit, setSavingEdit] = useState(false)
  const [confirmError, setConfirmError] = useState('')

  // ---------------------------------------------------------------------------
  // 7. ATTENDANCE CORRECTION MODAL STATE
  // ---------------------------------------------------------------------------
  const [correctingAttendance, setCorrectingAttendance] = useState(null) // attendance record
  const [attNewStatus, setAttNewStatus] = useState('present')
  const [attRemarks, setAttRemarks] = useState('')
  const [attReason, setAttReason] = useState('')
  const [savingAttendance, setSavingAttendance] = useState(false)

  // ---------------------------------------------------------------------------
  // 8. EXAMINATION RESULT CORRECTION MODAL STATE
  // ---------------------------------------------------------------------------
  const [correctingResult, setCorrectingResult] = useState(null) // exam result record
  const [examNewMarks, setExamNewMarks] = useState('')
  const [examNewMaxMarks, setExamNewMaxMarks] = useState('')
  const [examNewGrade, setExamNewGrade] = useState('')
  const [examReason, setExamReason] = useState('')
  const [savingResult, setSavingResult] = useState(false)

  // ---------------------------------------------------------------------------
  // 9. ADD / REPLACE DOCUMENT MODAL STATE
  // ---------------------------------------------------------------------------
  const [showAddDocModal, setShowAddDocModal] = useState(false)
  const [docName, setDocName] = useState('')
  const [docType, setDocType] = useState('Birth Certificate')
  const [docFileName, setDocFileName] = useState('')
  const [docReason, setDocReason] = useState('')
  const [savingDoc, setSavingDoc] = useState(false)

  // Category & Tier detection
  const isSchool = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('school') && !cat.includes('pu')
  }, [structure, institutionCategory])

  const isPU = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('pre-university') || cat.includes('pu')
  }, [structure, institutionCategory])

  const isComposite = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('composite')
  }, [structure, institutionCategory])

  // ---------------------------------------------------------------------------
  // FETCH STATS
  // ---------------------------------------------------------------------------
  const fetchStats = useCallback(async () => {
    if (!token || !institutionId) return
    try {
      setLoadingStats(true)
      setStatsError('')
      const data = await apiGet(`/institution/${institutionId}/student-management/stats`, token)
      setStats(data)
    } catch (err) {
      setStatsError(err.message || 'Failed to load student statistics.')
    } finally {
      setLoadingStats(false)
    }
  }, [token, institutionId])

  useEffect(() => {
    fetchStats()
  }, [fetchStats])

  // ---------------------------------------------------------------------------
  // FETCH ACADEMIC STRUCTURE
  // ---------------------------------------------------------------------------
  useEffect(() => {
    async function loadStructure() {
      if (!token || !institutionId) return
      try {
        setLoadingStructure(true)
        setStructureError('')
        const data = await apiGet(`/institution/${institutionId}/academic-structure`, token)
        setStructure(data)
      } catch (err) {
        setStructureError(err.message || 'Failed to load academic structure.')
      } finally {
        setLoadingStructure(false)
      }
    }
    loadStructure()
  }, [token, institutionId])

  // ---------------------------------------------------------------------------
  // FETCH STUDENTS (DIRECTORY QUERY)
  // ---------------------------------------------------------------------------
  const fetchStudents = useCallback(async (targetPage = 1) => {
    if (!token || !institutionId) return
    try {
      setLoadingStudents(true)
      setStudentsError('')

      const params = new URLSearchParams()
      params.set('limit', String(pageSize))
      params.set('offset', String((targetPage - 1) * pageSize))
      params.set('sort_by', sortBy)
      params.set('sort_order', sortOrder)

      if (searchQuery.trim()) {
        params.set('search', searchQuery.trim())
      }
      if (statusFilter !== 'all') {
        params.set('status', statusFilter)
      }
      if (divisionFilter !== 'all') {
        params.set('division_id', divisionFilter)
      }
      if (selectedStandard) {
        params.set('standard', selectedStandard)
      }
      if (selectedSection) {
        params.set('section', selectedSection)
      }
      if (academicYearFilter !== 'all') {
        params.set('academic_year', academicYearFilter)
      }
      if (selectedStream) {
        params.set('stream', selectedStream)
      }
      if (selectedCombination) {
        params.set('combination', selectedCombination)
      }
      if (selectedProgram) {
        params.set('program_id', selectedProgram)
      }

      const res = await apiGet(`/institution/${institutionId}/students?${params.toString()}`, token)
      setStudents(res.students || [])
      setTotalCount(res.total || 0)
      setPage(targetPage)
    } catch (err) {
      setStudentsError(err.message || 'Failed to retrieve students.')
    } finally {
      setLoadingStudents(false)
    }
  }, [token, institutionId, pageSize, sortBy, sortOrder, searchQuery, statusFilter, divisionFilter, selectedStandard, selectedSection, academicYearFilter, selectedStream, selectedCombination, selectedProgram])

  // Initial student directory fetch on mount
  useEffect(() => {
    fetchStudents(1)
  }, [fetchStudents])

  // ---------------------------------------------------------------------------
  // VIEW STUDENT PROFILE
  // ---------------------------------------------------------------------------
  async function openStudentProfile(studentId, defaultTab = 'personal') {
    setSelectedStudentId(studentId)
    setProfileTab(defaultTab)
    try {
      setLoadingProfile(true)
      setProfileError('')
      const profile = await apiGet(`/institution/${institutionId}/students/${studentId}`, token)
      setStudentProfile(profile)
    } catch (err) {
      setProfileError(err.message || 'Failed to load student profile.')
    } finally {
      setLoadingProfile(false)
    }
  }

  function closeStudentProfile() {
    setSelectedStudentId(null)
    setStudentProfile(null)
    setProfileError('')
  }

  // ---------------------------------------------------------------------------
  // OPEN RECORD EDITOR
  // ---------------------------------------------------------------------------
  function openRecordEditor(student) {
    setEditingStudent(student)
    setEditReason('')
    setEditValidationErrors({})
    setShowEditConfirmModal(false)

    // Pre-fill editable form with existing student values
    setEditFormData({
      student_name: student.student_name || '',
      date_of_birth: student.date_of_birth || '',
      gender: student.gender || 'Male',
      blood_group: student.blood_group || 'O+',
      first_language: student.first_language || 'Kannada',
      medium_of_instruction: student.medium_of_instruction || 'Kannada',
      contact_number: student.contact_number || student.phone || '',
      student_email: student.student_email || student.email || '',
      address: student.address || '',
      district: student.district || 'Bengaluru Urban',
      taluk: student.taluk || 'Bengaluru North',
      village_city: student.village_city || student.district || 'Bengaluru',
      pincode: student.pincode || '560001',
      enrollment_status: (student.enrollment_status || 'active').toLowerCase(),
      admission_number: student.admission_number || student.student_id || '',
      admission_date: student.admission_date || '',
      // Academic
      standard: student.standard !== undefined && student.standard !== null ? Number(student.standard) : '',
      section: student.section || 'A',
      puc_year: student.puc_year || '',
      stream: student.stream || '',
      subject_combination: student.subject_combination || '',
      curriculum_or_board: student.curriculum_or_board || student.board || 'Karnataka State Board (KSEEB)'
    })
  }

  function handleEditFieldChange(field, value) {
    setEditFormData(prev => ({ ...prev, [field]: value }))
    if (editValidationErrors[field]) {
      setEditValidationErrors(prev => {
        const next = { ...prev }
        delete next[field]
        return next
      })
    }
  }

  // Calculate Modified Fields (Diff)
  const modifiedFieldsDiff = useMemo(() => {
    if (!editingStudent) return []
    const diff = []
    const checkFields = [
      { key: 'student_name', label: 'Full Name' },
      { key: 'date_of_birth', label: 'Date of Birth' },
      { key: 'gender', label: 'Gender' },
      { key: 'blood_group', label: 'Blood Group' },
      { key: 'contact_number', label: 'Contact Number' },
      { key: 'student_email', label: 'Student Email' },
      { key: 'address', label: 'Residential Address' },
      { key: 'district', label: 'District' },
      { key: 'taluk', label: 'Taluk' },
      { key: 'village_city', label: 'Village / City' },
      { key: 'pincode', label: 'Pincode' },
      { key: 'enrollment_status', label: 'Enrollment Status' },
      { key: 'admission_number', label: 'Admission Number' },
      { key: 'admission_date', label: 'Admission Date' },
      { key: 'standard', label: 'Standard / Class' },
      { key: 'section', label: 'Section' },
      { key: 'puc_year', label: 'PUC Level' },
      { key: 'stream', label: 'Stream' },
      { key: 'subject_combination', label: 'Subject Combination' },
      { key: 'first_language', label: 'First Language' },
      { key: 'medium_of_instruction', label: 'Medium of Instruction' }
    ]

    for (const f of checkFields) {
      const origVal = String(editingStudent[f.key] ?? '').trim()
      const newVal = String(editFormData[f.key] ?? '').trim()
      if (newVal !== origVal && (newVal !== '' || origVal !== '')) {
        diff.push({
          key: f.key,
          label: f.label,
          oldValue: origVal || '(empty)',
          newValue: newVal || '(empty)'
        })
      }
    }
    return diff
  }, [editingStudent, editFormData])

  // Validate and Open Confirm Modal
  function handleInitiateSaveEdit(e) {
    e.preventDefault()
    const errors = {}

    if (!editFormData.student_name?.trim()) {
      errors.student_name = 'Student full name is required.'
    }
    if (editFormData.date_of_birth && !/^\d{4}-\d{2}-\d{2}$/.test(editFormData.date_of_birth)) {
      errors.date_of_birth = 'Date of birth must follow YYYY-MM-DD format.'
    }

    if (Object.keys(errors).length > 0) {
      setEditValidationErrors(errors)
      return
    }

    if (modifiedFieldsDiff.length === 0) {
      setFeedbackMessage({ type: 'error', text: 'No modifications detected. Please change at least one field.' })
      return
    }

    setConfirmError('')
    setShowEditConfirmModal(true)
  }

  // Execute Save Record Edit
  async function handleConfirmSaveEdit() {
    try {
      setSavingEdit(true)
      setConfirmError('')
      const finalReason = editReason.trim() || 'Administrative record update'
      const payload = {
        ...editFormData,
        reason: finalReason,
        source: 'Direct Admin Edit'
      }

      const res = await apiPut(`/institution/${institutionId}/students/${editingStudent.student_id}`, payload, token)

      setFeedbackMessage({
        type: 'success',
        text: res.message || `Successfully updated ${res.modified_fields?.length || 1} field(s) for ${editingStudent.student_name}.`
      })

      setShowEditConfirmModal(false)
      setEditingStudent(null)

      // Refresh list, stats, and profile if open
      fetchStudents(page)
      fetchStats()
      if (selectedStudentId === editingStudent.student_id) {
        openStudentProfile(editingStudent.student_id, profileTab)
      }
    } catch (err) {
      setConfirmError(err.message || 'Failed to save student record changes.')
      setFeedbackMessage({ type: 'error', text: err.message || 'Failed to save student record changes.' })
    } finally {
      setSavingEdit(false)
    }
  }

  // ---------------------------------------------------------------------------
  // ATTENDANCE CORRECTION HANDLER
  // ---------------------------------------------------------------------------
  function openAttendanceCorrection(rec) {
    setCorrectingAttendance(rec)
    setAttNewStatus(rec.status || 'present')
    setAttRemarks(rec.remarks || '')
    setAttReason('')
  }

  async function handleSaveAttendanceCorrection(e) {
    e.preventDefault()
    if (!attReason.trim() || attReason.trim().length < 5) {
      alert('Please enter a valid reason for correction (at least 5 characters).')
      return
    }

    try {
      setSavingAttendance(true)
      const res = await apiPut(
        `/institution/${institutionId}/students/${studentProfile.personal_info.student_id}/attendance/${correctingAttendance.attendance_id}`,
        {
          new_status: attNewStatus,
          remarks: attRemarks.trim(),
          reason: attReason.trim()
        },
        token
      )

      setFeedbackMessage({ type: 'success', text: res.message || 'Attendance corrected successfully.' })
      setCorrectingAttendance(null)
      // Refresh profile to show updated attendance & audit history
      openStudentProfile(studentProfile.personal_info.student_id, 'attendance')
      fetchStats()
    } catch (err) {
      alert(err.message || 'Failed to correct attendance.')
    } finally {
      setSavingAttendance(false)
    }
  }

  // ---------------------------------------------------------------------------
  // EXAMINATION RESULT CORRECTION HANDLER
  // ---------------------------------------------------------------------------
  function openResultCorrection(res) {
    setCorrectingResult(res)
    setExamNewMarks(String(res.marks_obtained ?? ''))
    setExamNewMaxMarks(String(res.maximum_marks || res.max_marks || 100))
    setExamNewGrade(res.grade || '')
    setExamReason('')
  }

  async function handleSaveResultCorrection(e) {
    e.preventDefault()
    const marksNum = parseFloat(examNewMarks)
    const maxMarksNum = parseFloat(examNewMaxMarks)

    if (isNaN(marksNum) || marksNum < 0) {
      alert('Please enter valid marks obtained.')
      return
    }
    if (isNaN(maxMarksNum) || maxMarksNum <= 0) {
      alert('Please enter valid maximum marks.')
      return
    }
    if (marksNum > maxMarksNum) {
      alert(`Marks obtained (${marksNum}) cannot exceed maximum marks (${maxMarksNum}).`)
      return
    }
    if (!examReason.trim() || examReason.trim().length < 5) {
      alert('Please enter a valid reason for correction (at least 5 characters).')
      return
    }

    try {
      setSavingResult(true)
      const res = await apiPut(
        `/institution/${institutionId}/students/${studentProfile.personal_info.student_id}/results/${correctingResult.result_id}`,
        {
          marks_obtained: marksNum,
          maximum_marks: maxMarksNum,
          grade: examNewGrade.trim() || undefined,
          reason: examReason.trim()
        },
        token
      )

      setFeedbackMessage({ type: 'success', text: res.message || 'Examination result corrected successfully.' })
      setCorrectingResult(null)
      openStudentProfile(studentProfile.personal_info.student_id, 'results')
      fetchStats()
    } catch (err) {
      alert(err.message || 'Failed to correct examination result.')
    } finally {
      setSavingResult(false)
    }
  }

  // ---------------------------------------------------------------------------
  // ADD / REPLACE DOCUMENT HANDLER
  // ---------------------------------------------------------------------------
  async function handleSaveDocument(e) {
    e.preventDefault()
    if (!docName.trim() || !docFileName.trim() || !docReason.trim() || docReason.trim().length < 5) {
      alert('Please fill out all document fields and enter a valid reason.')
      return
    }

    try {
      setSavingDoc(true)
      const res = await apiPost(
        `/institution/${institutionId}/students/${studentProfile.personal_info.student_id}/documents`,
        {
          document_name: docName.trim(),
          document_type: docType,
          file_name: docFileName.trim(),
          verification_status: 'verified',
          reason: docReason.trim()
        },
        token
      )

      setFeedbackMessage({ type: 'success', text: res.message || 'Document added successfully.' })
      setShowAddDocModal(false)
      setDocName('')
      setDocFileName('')
      setDocReason('')
      openStudentProfile(studentProfile.personal_info.student_id, 'documents')
    } catch (err) {
      alert(err.message || 'Failed to upload document.')
    } finally {
      setSavingDoc(false)
    }
  }

  return (
    <div className="student-records-management-module" style={{ padding: '0.5rem 0' }}>
      {/* =====================================================================
          HEADER SECTION & TITLE
          ===================================================================== */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.5rem',
        background: '#FFFFFF',
        padding: '1.25rem 1.5rem',
        borderRadius: '12px',
        border: '1px solid #E4E7EC',
        boxShadow: '0 1px 3px rgba(16, 24, 40, 0.05)'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
            <span style={{ fontSize: '1.5rem' }}>👨‍🎓</span>
            <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Student Records Management
            </h1>
            <span style={{
              background: '#E0F2FE',
              color: '#0369A1',
              padding: '0.2rem 0.6rem',
              borderRadius: '12px',
              fontSize: '0.75rem',
              fontWeight: 700,
              letterSpacing: '0.04em'
            }}>
              OFFICIAL REGISTRY
            </span>
          </div>
          <p style={{ color: '#475467', margin: 0, fontSize: '0.9rem' }}>
            Comprehensive institutional registry for viewing, searching, correcting, and managing verified student dossiers for <strong>{institutionName}</strong> ({institutionId}).
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <button
            onClick={() => { fetchStats(); fetchStudents(page); }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              background: '#F8FAFC',
              color: '#344054',
              border: '1px solid #D0D5DD',
              padding: '0.55rem 0.95rem',
              borderRadius: '8px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <span>🔄</span> Refresh Data
          </button>
        </div>
      </div>

      {/* Global Feedback Alert */}
      {feedbackMessage && (
        <div style={{ marginBottom: '1.25rem' }}>
          <Alert
            type={feedbackMessage.type}
            message={feedbackMessage.text}
            onClose={() => setFeedbackMessage(null)}
          />
        </div>
      )}

      {/* =====================================================================
          SECTION 1: DASHBOARD METRICS CARDS
          ===================================================================== */}
      {loadingStats ? (
        <div style={{ textAlign: 'center', padding: '1.5rem', background: '#FFFFFF', borderRadius: '12px', marginBottom: '1.5rem' }}>
          <LoadingSpinner size="sm" text="Loading real-time institutional metrics..." />
        </div>
      ) : stats ? (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '1rem',
          marginBottom: '1.5rem'
        }}>
          {/* Card 1: Total Registered */}
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E4E7EC',
            borderRadius: '12px',
            padding: '1.2rem',
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475467' }}>Total Registered Students</span>
              <span style={{ background: '#EFF8FF', padding: '0.3rem', borderRadius: '6px' }}>👥</span>
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#102B46' }}>
              {stats.total_students?.toLocaleString() || 0}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.25rem' }}>
              Permanent enrolled institutional records
            </div>
          </div>

          {/* Card 2: Active Students */}
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E4E7EC',
            borderRadius: '12px',
            padding: '1.2rem',
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475467' }}>Active Enrolled</span>
              <span style={{ background: '#ECFDF3', padding: '0.3rem', borderRadius: '6px' }}>🟢</span>
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#027A48' }}>
              {stats.active_students?.toLocaleString() || 0}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#027A48', marginTop: '0.25rem' }}>
              Active academic standing (2026-2027)
            </div>
          </div>

          {/* Card 3: Inactive / Transferred */}
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E4E7EC',
            borderRadius: '12px',
            padding: '1.2rem',
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475467' }}>Inactive / Transferred</span>
              <span style={{ background: '#F8FAFC', padding: '0.3rem', borderRadius: '6px' }}>⚪</span>
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#64748B' }}>
              {stats.inactive_students?.toLocaleString() || 0}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '0.25rem' }}>
              Graduated or archived entries
            </div>
          </div>

          {/* Card 4: Recently Updated Records */}
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E4E7EC',
            borderRadius: '12px',
            padding: '1.2rem',
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)',
            cursor: 'pointer'
          }}
          onClick={() => setShowRecentUpdatesModal(true)}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#475467' }}>Recently Updated</span>
              <span style={{ background: '#FDF2FA', padding: '0.3rem', borderRadius: '6px' }}>📝</span>
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#C11574' }}>
              {stats.recently_updated?.length || 0}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#C11574', marginTop: '0.25rem', fontWeight: 600 }}>
              View Recent Audit History →
            </div>
          </div>

          {/* Card 5: Pending Correction Requests */}
          <div style={{
            background: stats.pending_correction_requests_count > 0 ? '#FFFBEB' : '#FFFFFF',
            border: stats.pending_correction_requests_count > 0 ? '1px solid #FCD34D' : '1px solid #E4E7EC',
            borderRadius: '12px',
            padding: '1.2rem',
            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)',
            cursor: 'pointer'
          }}
          onClick={() => setShowPendingRequestsModal(true)}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#B45309' }}>Pending Correction Requests</span>
              <span style={{ background: '#FEF3C7', padding: '0.3rem', borderRadius: '6px' }}>⏳</span>
            </div>
            <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#B45309' }}>
              {stats.pending_correction_requests_count || 0}
            </div>
            <div style={{ fontSize: '0.78rem', color: '#B45309', marginTop: '0.25rem', fontWeight: 600 }}>
              Review Citizen & Parent Requests →
            </div>
          </div>
        </div>
      ) : null}

      {/* =====================================================================
          SECTION 2: SEARCH & FILTER CONTROLS
          ===================================================================== */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid #E4E7EC',
        borderRadius: '12px',
        padding: '1.25rem',
        marginBottom: '1.5rem',
        boxShadow: '0 1px 3px rgba(16, 24, 40, 0.04)'
      }}>
        {/* Search Input Bar */}
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#344054', marginBottom: '0.4rem' }}>
            Search Verified Student Directory
          </label>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: 1, minWidth: '280px' }}>
              <span style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#98A2B3' }}>🔍</span>
              <input
                type="text"
                placeholder="Search by Student ID, PSID, Student Name, or Verified Parent Name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') fetchStudents(1); }}
                style={{
                  width: '100%',
                  padding: '0.65rem 0.85rem 0.65rem 2.5rem',
                  borderRadius: '8px',
                  border: '1px solid #D0D5DD',
                  fontSize: '0.9rem',
                  outline: 'none'
                }}
              />
            </div>
            <button
              onClick={() => fetchStudents(1)}
              style={{
                background: '#155EEF',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: '8px',
                padding: '0.65rem 1.25rem',
                fontSize: '0.9rem',
                fontWeight: 700,
                cursor: 'pointer'
              }}
            >
              Search
            </button>
            {(searchQuery || divisionFilter !== 'all' || selectedStandard || selectedSection || statusFilter !== 'all' || academicYearFilter !== 'all') && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setDivisionFilter('all')
                  setSelectedStandard('')
                  setSelectedSection('')
                  setStatusFilter('all')
                  setAcademicYearFilter('all')
                  setSelectedStream('')
                  setSelectedCombination('')
                }}
                style={{
                  background: '#F2F4F7',
                  color: '#475467',
                  border: '1px solid #D0D5DD',
                  borderRadius: '8px',
                  padding: '0.65rem 1rem',
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Clear Filters
              </button>
            )}
          </div>
        </div>

        {/* Filter Dropdowns Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '0.75rem',
          paddingTop: '0.75rem',
          borderTop: '1px solid #F2F4F7'
        }}>
          {/* Filter 1: Academic Division */}
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#475467', marginBottom: '0.3rem' }}>
              Academic Division
            </label>
            <select
              value={divisionFilter}
              onChange={(e) => { setDivisionFilter(e.target.value); setSelectedStandard(''); }}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: '#FFFFFF' }}
            >
              <option value="all">All Academic Divisions</option>
              <option value="school">School Division (Std 1–10)</option>
              <option value="pu">PU Division (1st & 2nd PUC)</option>
              <option value="degree">Degree / College Division</option>
            </select>
          </div>

          {/* Filter 2: Standard / Class */}
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#475467', marginBottom: '0.3rem' }}>
              Standard / Class
            </label>
            <select
              value={selectedStandard}
              onChange={(e) => setSelectedStandard(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: '#FFFFFF' }}
            >
              <option value="">All Standards</option>
              {divisionFilter === 'pu' ? (
                <>
                  <option value="11">1st PUC (Std 11)</option>
                  <option value="12">2nd PUC (Std 12)</option>
                </>
              ) : divisionFilter === 'school' ? (
                [1,2,3,4,5,6,7,8,9,10].map(s => <option key={s} value={String(s)}>Standard {s}</option>)
              ) : (
                [1,2,3,4,5,6,7,8,9,10,11,12].map(s => (
                  <option key={s} value={String(s)}>
                    {s <= 10 ? `Standard ${s}` : (s === 11 ? '1st PUC (Std 11)' : '2nd PUC (Std 12)')}
                  </option>
                ))
              )}
            </select>
          </div>

          {/* Filter 3: Section */}
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#475467', marginBottom: '0.3rem' }}>
              Section
            </label>
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: '#FFFFFF' }}
            >
              <option value="">All Sections</option>
              <option value="A">Section A</option>
              <option value="B">Section B</option>
              <option value="C">Section C</option>
              <option value="D">Section D</option>
            </select>
          </div>

          {/* Filter 4: Academic Year */}
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#475467', marginBottom: '0.3rem' }}>
              Academic Year
            </label>
            <select
              value={academicYearFilter}
              onChange={(e) => setAcademicYearFilter(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: '#FFFFFF' }}
            >
              <option value="all">All Academic Years</option>
              <option value="2026-2027">2026-2027 (Current)</option>
              <option value="2025-2026">2025-2026</option>
              <option value="2024-2025">2024-2025</option>
            </select>
          </div>

          {/* Filter 5: Student Status */}
          <div>
            <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#475467', marginBottom: '0.3rem' }}>
              Enrollment Status
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', background: '#FFFFFF' }}
            >
              <option value="all">All Statuses</option>
              <option value="active">Active Enrolled</option>
              <option value="inactive">Inactive / Withdrawn</option>
              <option value="transferred">Transferred</option>
              <option value="graduated">Graduated</option>
            </select>
          </div>
        </div>
      </div>

      {/* =====================================================================
          SECTION 3: STUDENT DIRECTORY TABLE
          ===================================================================== */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid #E4E7EC',
        borderRadius: '12px',
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(16, 24, 40, 0.04)'
      }}>
        {/* Table Header Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem 1.25rem',
          borderBottom: '1px solid #E4E7EC',
          background: '#FAFAFA'
        }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#102B46', margin: 0 }}>
              Institutional Student Registry
            </h3>
            <span style={{ fontSize: '0.8rem', color: '#667085' }}>
              Showing {students.length} of {totalCount} matching student records
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.82rem', color: '#475467' }}>Page Size:</span>
            <select
              value={pageSize}
              onChange={(e) => setPageSize(Number(e.target.value))}
              style={{ padding: '0.35rem 0.6rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.82rem' }}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
            </select>
          </div>
        </div>

        {/* Table Data */}
        {loadingStudents ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <LoadingSpinner size="md" text="Loading student records from database..." />
          </div>
        ) : studentsError ? (
          <div style={{ padding: '1.5rem' }}>
            <Alert type="error" message={studentsError} />
          </div>
        ) : students.length === 0 ? (
          <div style={{ padding: '3.5rem 1.5rem', textAlign: 'center', color: '#667085' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🔍</div>
            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
              No Student Records Found
            </h4>
            <p style={{ margin: 0, fontSize: '0.88rem' }}>
              No students matched your search query or selected academic filters.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467', fontWeight: 700 }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Student ID / PSID</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Student Name</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Academic Division</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Class / Standard</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Section</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Contact Info</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Last Updated</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s, idx) => (
                  <tr
                    key={s.student_id || idx}
                    style={{
                      borderBottom: '1px solid #F1F5F9',
                      background: idx % 2 === 0 ? '#FFFFFF' : '#FAFCFE',
                      transition: 'background 0.15s ease'
                    }}
                  >
                    {/* Student ID & PSID */}
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 700, color: '#102B46', fontFamily: 'monospace', fontSize: '0.88rem' }}>
                        {s.student_id}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: '#64748B', fontFamily: 'monospace' }}>
                        {s.permanent_student_id ? `${s.permanent_student_id.slice(0, 16)}...` : '—'}
                      </div>
                    </td>

                    {/* Student Name */}
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 700, color: '#0F172A' }}>
                        {s.student_name}
                      </div>
                      <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                        DOB: {s.date_of_birth || '—'} • {s.gender || '—'}
                      </div>
                    </td>

                    {/* Academic Division */}
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '0.2rem 0.55rem',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        background: s.academic_division === 'PU Division' ? '#F3E8FF' : '#E0F2FE',
                        color: s.academic_division === 'PU Division' ? '#7E22CE' : '#0369A1'
                      }}>
                        {s.academic_division || 'School Division'}
                      </span>
                    </td>

                    {/* Class / Standard */}
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#1E293B' }}>
                      {s.class_or_standard_display || `Standard ${s.standard}`}
                      {s.stream && (
                        <div style={{ fontSize: '0.72rem', color: '#7E22CE', fontWeight: 500 }}>
                          {s.stream} ({s.subject_combination || '—'})
                        </div>
                      )}
                    </td>

                    {/* Section */}
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#334155' }}>
                      Sec {s.section || 'A'}
                    </td>

                    {/* Contact Info */}
                    <td style={{ padding: '0.75rem 1rem', color: '#475467', fontSize: '0.8rem' }}>
                      <div>📞 {s.contact_number || '—'}</div>
                      <div style={{ fontSize: '0.74rem', color: '#64748B' }}>{s.student_email || ''}</div>
                    </td>

                    {/* Status */}
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <StatusBadge status={(s.enrollment_status || 'active').toLowerCase()} />
                    </td>

                    {/* Last Updated */}
                    <td style={{ padding: '0.75rem 1rem', color: '#64748B', fontSize: '0.78rem' }}>
                      {s.updated_at ? s.updated_at.slice(0, 10) : (s.admission_date || '2024-06-01')}
                    </td>

                    {/* Action Buttons */}
                    <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                        <button
                          onClick={() => openStudentProfile(s.student_id, 'personal')}
                          title="View Complete Official Profile"
                          style={{
                            background: '#155EEF',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.35rem 0.65rem',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                        >
                          View
                        </button>

                        <button
                          onClick={() => {
                            setReportStudentId(s.student_id)
                            setDossierModalOpen(true)
                          }}
                          title="Generate Official Certified Academic Dossier"
                          style={{
                            background: '#1E40AF',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.35rem 0.65rem',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.2rem'
                          }}
                          id={`btn-desk-report-${s.student_id}`}
                        >
                          📜 Report
                        </button>

                        <button
                          onClick={() => openRecordEditor(s)}
                          title="Edit Student Record"
                          style={{
                            background: '#ECFDF3',
                            color: '#027A48',
                            border: '1px solid #A6F4C5',
                            borderRadius: '6px',
                            padding: '0.35rem 0.65rem',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                        >
                          ✏️ Edit
                        </button>

                        {/* Quick Jump Action Dropdown */}
                        <select
                          onChange={(e) => {
                            if (e.target.value) {
                              openStudentProfile(s.student_id, e.target.value)
                              e.target.value = ''
                            }
                          }}
                          defaultValue=""
                          style={{
                            padding: '0.35rem 0.5rem',
                            borderRadius: '6px',
                            border: '1px solid #CBD5E1',
                            fontSize: '0.78rem',
                            background: '#FFFFFF',
                            color: '#475467',
                            cursor: 'pointer'
                          }}
                        >
                          <option value="" disabled>More...</option>
                          <option value="academic">Academic Details</option>
                          <option value="attendance">Attendance</option>
                          <option value="results">Examination Results</option>
                          <option value="documents">Documents</option>
                          <option value="history">Correction History</option>
                        </select>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Table Pagination Footer */}
        {totalCount > 0 && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.85rem 1.25rem',
            borderTop: '1px solid #E2E8F0',
            background: '#F8FAFC'
          }}>
            <div style={{ fontSize: '0.82rem', color: '#475467' }}>
              Page <strong>{page}</strong> of <strong>{Math.ceil(totalCount / pageSize)}</strong> ({totalCount} total students)
            </div>

            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button
                disabled={page <= 1 || loadingStudents}
                onClick={() => fetchStudents(page - 1)}
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #D0D5DD',
                  background: page <= 1 ? '#F1F5F9' : '#FFFFFF',
                  color: page <= 1 ? '#94A3B8' : '#334155',
                  cursor: page <= 1 ? 'not-allowed' : 'pointer',
                  fontSize: '0.82rem',
                  fontWeight: 600
                }}
              >
                ← Previous
              </button>

              <button
                disabled={page >= Math.ceil(totalCount / pageSize) || loadingStudents}
                onClick={() => fetchStudents(page + 1)}
                style={{
                  padding: '0.35rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #D0D5DD',
                  background: page >= Math.ceil(totalCount / pageSize) ? '#F1F5F9' : '#FFFFFF',
                  color: page >= Math.ceil(totalCount / pageSize) ? '#94A3B8' : '#334155',
                  cursor: page >= Math.ceil(totalCount / pageSize) ? 'not-allowed' : 'pointer',
                  fontSize: '0.82rem',
                  fontWeight: 600
                }}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>

      {/* =====================================================================
          MODAL 1: COMPLETE STUDENT PROFILE VIEW (7 TABS)
          ===================================================================== */}
      {selectedStudentId && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          backdropFilter: 'blur(3px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1.5rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            width: '100%',
            maxWidth: '1000px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)'
          }}>
            {/* Modal Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '1.25rem 1.75rem',
              borderBottom: '1px solid #E2E8F0',
              background: '#0F172A',
              color: '#FFFFFF'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800, margin: 0 }}>
                    {studentProfile?.personal_info?.student_name || 'Student Dossier'}
                  </h3>
                  <span style={{
                    background: '#1E293B',
                    color: '#93C5FD',
                    fontFamily: 'monospace',
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.78rem'
                  }}>
                    {selectedStudentId}
                  </span>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.2rem' }}>
                  PSID: {studentProfile?.personal_info?.permanent_student_id || '—'} • {institutionName}
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <button
                  onClick={() => {
                    setReportStudentId(selectedStudentId)
                    setDossierModalOpen(true)
                  }}
                  title="Generate Official Certified Academic Dossier"
                  style={{
                    background: '#1D4ED8',
                    color: '#FFFFFF',
                    border: 'none',
                    padding: '0.45rem 0.9rem',
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                >
                  📜 Official Report
                </button>
                {studentProfile && (
                  <button
                    onClick={() => {
                      const studentObj = {
                        ...studentProfile.personal_info,
                        ...studentProfile.academic_info
                      }
                      openRecordEditor(studentObj)
                    }}
                    style={{
                      background: '#10B981',
                      color: '#FFFFFF',
                      border: 'none',
                      padding: '0.45rem 0.9rem',
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    ✏️ Edit Record
                  </button>
                )}
                <button
                  onClick={closeStudentProfile}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#94A3B8',
                    fontSize: '1.5rem',
                    cursor: 'pointer'
                  }}
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Profile Tabs Navigation */}
            <div style={{
              display: 'flex',
              overflowX: 'auto',
              background: '#F8FAFC',
              borderBottom: '1px solid #E2E8F0',
              padding: '0 1rem'
            }}>
              {[
                { id: 'personal', label: '1. Personal Information', icon: '👤' },
                { id: 'guardian', label: '2. Parent & Guardians', icon: '👨‍👩‍👧' },
                { id: 'academic', label: '3. Academic Details', icon: '📚' },
                { id: 'attendance', label: '4. Attendance', icon: '📅' },
                { id: 'results', label: '5. Examinations', icon: '📊' },
                { id: 'documents', label: '6. Documents', icon: '📁' },
                { id: 'history', label: '7. Correction History', icon: '⏱️' }
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setProfileTab(t.id)}
                  style={{
                    padding: '0.85rem 1rem',
                    border: 'none',
                    background: 'transparent',
                    borderBottom: profileTab === t.id ? '3px solid #155EEF' : '3px solid transparent',
                    color: profileTab === t.id ? '#155EEF' : '#64748B',
                    fontWeight: profileTab === t.id ? 700 : 500,
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    whiteSpace: 'nowrap',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  <span>{t.icon}</span>
                  <span>{t.label}</span>
                  {t.id === 'history' && (studentProfile?.record_history?.length > 0) && (
                    <span style={{ background: '#E0E7FF', color: '#4338CA', borderRadius: '10px', padding: '0.1rem 0.4rem', fontSize: '0.7rem' }}>
                      {studentProfile.record_history.length}
                    </span>
                  )}
                </button>
              ))}
            </div>

            {/* Modal Body / Tab Content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
              {loadingProfile ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}>
                  <LoadingSpinner size="md" text="Loading complete student dossier..." />
                </div>
              ) : profileError ? (
                <Alert type="error" message={profileError} />
              ) : studentProfile ? (
                <>
                  {/* TAB 1: PERSONAL INFORMATION */}
                  {profileTab === 'personal' && (
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', marginBottom: '1.5rem', background: '#F8FAFC', padding: '1.2rem', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
                        <div style={{
                          width: '72px',
                          height: '72px',
                          borderRadius: '50%',
                          background: '#E2E8F0',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '2rem'
                        }}>
                          {studentProfile.personal_info.gender === 'Female' ? '👧' : '👦'}
                        </div>
                        <div>
                          <h4 style={{ margin: '0 0 0.25rem 0', fontSize: '1.2rem', fontWeight: 800, color: '#0F172A' }}>
                            {studentProfile.personal_info.student_name}
                          </h4>
                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            <StatusBadge status={(studentProfile.personal_info.enrollment_status || 'active').toLowerCase()} />
                            <span style={{ background: '#F1F5F9', color: '#475467', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                              Blood Group: {studentProfile.personal_info.blood_group || 'O+'}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
                        {[
                          { label: 'Student ID', value: studentProfile.personal_info.student_id, isMono: true },
                          { label: 'Permanent Student ID (PSID)', value: studentProfile.personal_info.permanent_student_id, isMono: true },
                          { label: 'Admission Number', value: studentProfile.personal_info.admission_number || studentProfile.personal_info.student_id },
                          { label: 'Date of Birth', value: studentProfile.personal_info.date_of_birth },
                          { label: 'Gender', value: studentProfile.personal_info.gender },
                          { label: 'First Language', value: studentProfile.personal_info.first_language },
                          { label: 'Medium of Instruction', value: studentProfile.personal_info.medium_of_instruction },
                          { label: 'Contact Number', value: studentProfile.personal_info.contact_number || '—' },
                          { label: 'Student Email', value: studentProfile.personal_info.student_email || '—' },
                          { label: 'Admission Date', value: studentProfile.personal_info.admission_date || '—' },
                          { label: 'District', value: studentProfile.personal_info.district },
                          { label: 'Taluk', value: studentProfile.personal_info.taluk || '—' },
                          { label: 'Village / City', value: studentProfile.personal_info.village_city || '—' },
                          { label: 'Pincode', value: studentProfile.personal_info.pincode || '—' },
                          { label: 'Residential Address', value: studentProfile.personal_info.address || '—', full: true }
                        ].map((item, idx) => (
                          <div
                            key={idx}
                            style={{
                              background: '#FFFFFF',
                              border: '1px solid #E2E8F0',
                              borderRadius: '8px',
                              padding: '0.75rem 1rem',
                              gridColumn: item.full ? '1 / -1' : 'auto'
                            }}
                          >
                            <span style={{ display: 'block', fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>
                              {item.label}
                            </span>
                            <span style={{
                              display: 'block',
                              fontSize: '0.9rem',
                              fontWeight: 700,
                              color: '#0F172A',
                              marginTop: '0.15rem',
                              fontFamily: item.isMono ? 'monospace' : 'inherit'
                            }}>
                              {item.value || '—'}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 2: PARENT AND GUARDIAN INFORMATION */}
                  {profileTab === 'guardian' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1E293B', marginBottom: '1rem' }}>
                        Verified Parents & Legal Guardians
                      </h4>
                      {studentProfile.parent_info && studentProfile.parent_info.length > 0 ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                          {studentProfile.parent_info.map((g, idx) => (
                            <div key={idx} style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '1.25rem' }}>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                                <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#0F172A' }}>
                                  {g.full_name}
                                </div>
                                <span style={{ background: '#ECFDF3', color: '#027A48', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                  ✓ Institution Verified
                                </span>
                              </div>
                              <div style={{ fontSize: '0.85rem', color: '#334155', lineHeight: '1.6' }}>
                                <div><strong>Relationship:</strong> {g.relationship || 'Guardian'}</div>
                                <div><strong>Contact:</strong> 📞 {g.phone || '—'}</div>
                                <div><strong>Email:</strong> ✉️ {g.email || '—'}</div>
                                <div><strong>Address:</strong> {g.address || '—'}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{ padding: '2rem', textAlign: 'center', background: '#F8FAFC', borderRadius: '12px', color: '#64748B' }}>
                          No verified parent/guardian linking relationships currently on file for this student.
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 3: ACADEMIC INFORMATION */}
                  {profileTab === 'academic' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1E293B', marginBottom: '1rem' }}>
                        Current Academic Enrolment & Curricular Mapping
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
                        {[
                          { label: 'Institution Name', value: studentProfile.academic_info.school_name },
                          { label: 'Institution ID', value: studentProfile.academic_info.school_id, isMono: true },
                          { label: 'Academic Standing / Level', value: studentProfile.academic_info.class_or_standard },
                          { label: 'Section', value: `Section ${studentProfile.academic_info.section}` },
                          { label: 'Academic Year', value: studentProfile.academic_info.academic_year || '2026-2027' },
                          { label: 'Curriculum / Board', value: studentProfile.academic_info.board || studentProfile.academic_info.curriculum_or_board || 'Karnataka State Board (KSEEB)' },
                          // PU specific
                          ...(studentProfile.academic_info.puc_year ? [
                            { label: 'PUC Level', value: studentProfile.academic_info.puc_year },
                            { label: 'Stream', value: studentProfile.academic_info.stream },
                            { label: 'Subject Combination', value: studentProfile.academic_info.subject_combination }
                          ] : []),
                          // Degree specific
                          ...(studentProfile.academic_info.degree ? [
                            { label: 'Programme / Degree', value: studentProfile.academic_info.degree },
                            { label: 'Branch / Specialization', value: studentProfile.academic_info.branch },
                            { label: 'Semester', value: `Semester ${studentProfile.academic_info.semester}` }
                          ] : [])
                        ].map((item, idx) => (
                          <div key={idx} style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '0.75rem 1rem' }}>
                            <span style={{ display: 'block', fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>{item.label}</span>
                            <span style={{ display: 'block', fontSize: '0.9rem', fontWeight: 700, color: '#0F172A', marginTop: '0.15rem' }}>{item.value || '—'}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* TAB 4: ATTENDANCE */}
                  {profileTab === 'attendance' && (
                    <div>
                      {/* Attendance Summary Banner */}
                      {studentProfile.attendance?.summary && (
                        <div style={{
                          display: 'grid',
                          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                          gap: '1rem',
                          marginBottom: '1.5rem',
                          background: '#F0FDF4',
                          border: '1px solid #BBF7D0',
                          borderRadius: '12px',
                          padding: '1.25rem'
                        }}>
                          <div>
                            <span style={{ fontSize: '0.78rem', color: '#166534', fontWeight: 600 }}>Attendance Percentage</span>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#166534' }}>
                              {studentProfile.attendance.summary.percentage}%
                            </div>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.78rem', color: '#166534', fontWeight: 600 }}>Total Working Days</span>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#166534' }}>
                              {studentProfile.attendance.summary.total_days}
                            </div>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.78rem', color: '#166534', fontWeight: 600 }}>Present Days</span>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#15803D' }}>
                              {studentProfile.attendance.summary.present_days}
                            </div>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.78rem', color: '#991B1B', fontWeight: 600 }}>Absent Days</span>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#DC2626' }}>
                              {studentProfile.attendance.summary.absent_days}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Attendance Table */}
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.75rem' }}>
                        Date-wise Attendance History (Last 50 Scheduled Days)
                      </h4>
                      {studentProfile.attendance?.records?.length > 0 ? (
                        <div style={{ border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                            <thead>
                              <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467' }}>
                                <th style={{ padding: '0.65rem 1rem' }}>Date</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Subject / Session</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Status</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Remarks</th>
                                <th style={{ padding: '0.65rem 1rem', textAlign: 'center' }}>Admin Action</th>
                              </tr>
                            </thead>
                            <tbody>
                              {studentProfile.attendance.records.map((a, idx) => (
                                <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                                  <td style={{ padding: '0.65rem 1rem', fontWeight: 600 }}>{a.attendance_date}</td>
                                  <td style={{ padding: '0.65rem 1rem' }}>{a.subject_name || 'General Academic Day'}</td>
                                  <td style={{ padding: '0.65rem 1rem' }}>
                                    <span style={{
                                      display: 'inline-block',
                                      padding: '0.15rem 0.5rem',
                                      borderRadius: '4px',
                                      fontSize: '0.75rem',
                                      fontWeight: 700,
                                      background: a.status === 'present' ? '#DCFCE7' : '#FEE2E2',
                                      color: a.status === 'present' ? '#15803D' : '#B91C1C'
                                    }}>
                                      {a.status.toUpperCase()}
                                    </span>
                                  </td>
                                  <td style={{ padding: '0.65rem 1rem', color: '#64748B' }}>{a.remarks || '—'}</td>
                                  <td style={{ padding: '0.65rem 1rem', textAlign: 'center' }}>
                                    <button
                                      onClick={() => openAttendanceCorrection(a)}
                                      style={{
                                        background: '#F1F5F9',
                                        color: '#334155',
                                        border: '1px solid #CBD5E1',
                                        padding: '0.25rem 0.55rem',
                                        borderRadius: '4px',
                                        fontSize: '0.75rem',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                      }}
                                    >
                                      Correct Status
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p style={{ color: '#64748B' }}>No attendance records recorded.</p>
                      )}
                    </div>
                  )}

                  {/* TAB 5: EXAMINATION AND RESULTS */}
                  {profileTab === 'results' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.75rem' }}>
                        Official Examination Performance & Gradebook
                      </h4>
                      {studentProfile.examinations?.results?.length > 0 ? (
                        <div style={{ border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                            <thead>
                              <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467' }}>
                                <th style={{ padding: '0.65rem 1rem' }}>Subject</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Examination Name</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Marks Obtained</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Max Marks</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Percentage</th>
                                <th style={{ padding: '0.65rem 1rem' }}>Grade</th>
                                <th style={{ padding: '0.65rem 1rem', textAlign: 'center' }}>Admin Action</th>
                              </tr>
                            </thead>
                            <tbody>
                              {studentProfile.examinations.results.map((r, idx) => (
                                <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                                  <td style={{ padding: '0.65rem 1rem', fontWeight: 700, color: '#0F172A' }}>{r.subject_name}</td>
                                  <td style={{ padding: '0.65rem 1rem', color: '#475467' }}>{r.exam_name || 'Annual Evaluation'}</td>
                                  <td style={{ padding: '0.65rem 1rem', fontWeight: 700 }}>{r.marks_obtained}</td>
                                  <td style={{ padding: '0.65rem 1rem', color: '#64748B' }}>{r.maximum_marks || r.max_marks || 100}</td>
                                  <td style={{ padding: '0.65rem 1rem', fontWeight: 600 }}>{r.percentage}%</td>
                                  <td style={{ padding: '0.65rem 1rem' }}>
                                    <span style={{ background: '#E0E7FF', color: '#3730A3', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 700 }}>
                                      {r.grade || 'A'}
                                    </span>
                                  </td>
                                  <td style={{ padding: '0.65rem 1rem', textAlign: 'center' }}>
                                    <button
                                      onClick={() => openResultCorrection(r)}
                                      style={{
                                        background: '#F1F5F9',
                                        color: '#334155',
                                        border: '1px solid #CBD5E1',
                                        padding: '0.25rem 0.55rem',
                                        borderRadius: '4px',
                                        fontSize: '0.75rem',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                      }}
                                    >
                                      Correct Marks
                                    </button>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p style={{ color: '#64748B' }}>No examination results found.</p>
                      )}
                    </div>
                  )}

                  {/* TAB 6: DOCUMENTS */}
                  {profileTab === 'documents' && (
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1E293B', margin: 0 }}>
                          Verified Institutional Dossier Documents
                        </h4>
                        <button
                          onClick={() => setShowAddDocModal(true)}
                          style={{
                            background: '#155EEF',
                            color: '#FFFFFF',
                            border: 'none',
                            padding: '0.45rem 0.85rem',
                            borderRadius: '6px',
                            fontSize: '0.82rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                        >
                          + Add / Replace Document
                        </button>
                      </div>

                      <div style={{ background: '#FEF3C7', color: '#92400E', padding: '0.75rem 1rem', borderRadius: '8px', fontSize: '0.78rem', marginBottom: '1rem' }}>
                        ⚠️ <strong>Demonstration Dataset Notice:</strong> Synthetic demo document keys are maintained for illustrative verification purposes.
                      </div>

                      {studentProfile.documents?.length > 0 ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                          {studentProfile.documents.map((d, idx) => (
                            <div key={idx} style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem' }}>
                              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <span style={{ fontWeight: 700, color: '#0F172A', fontSize: '0.9rem' }}>
                                  📄 {d.document_type || d.document_name}
                                </span>
                                <span style={{ background: '#DCFCE7', color: '#15803D', fontSize: '0.7rem', padding: '0.15rem 0.4rem', borderRadius: '4px', fontWeight: 700 }}>
                                  ✓ {d.verification_status || 'Verified'}
                                </span>
                              </div>
                              <div style={{ fontSize: '0.78rem', color: '#64748B', fontFamily: 'monospace', marginBottom: '0.5rem' }}>
                                {d.file_name}
                              </div>
                              <div style={{ fontSize: '0.74rem', color: '#94A3B8' }}>
                                Uploaded: {d.uploaded_at ? d.uploaded_at.slice(0, 10) : '2024-06-01'}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p style={{ color: '#64748B' }}>No documents uploaded.</p>
                      )}
                    </div>
                  )}

                  {/* TAB 7: CORRECTION HISTORY */}
                  {profileTab === 'history' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.75rem' }}>
                        Immutable Record Modification Audit Trail
                      </h4>
                      {studentProfile.record_history?.length > 0 ? (
                        <div style={{ border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden' }}>
                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                            <thead>
                              <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467' }}>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Audit ID</th>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Field Modified</th>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Previous Value</th>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Updated Value</th>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Reason for Modification</th>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Source</th>
                                <th style={{ padding: '0.65rem 0.85rem' }}>Timestamp</th>
                              </tr>
                            </thead>
                            <tbody>
                              {studentProfile.record_history.map((h, idx) => (
                                <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                                  <td style={{ padding: '0.65rem 0.85rem', fontFamily: 'monospace', color: '#64748B' }}>{h.audit_id}</td>
                                  <td style={{ padding: '0.65rem 0.85rem', fontWeight: 700, color: '#0F172A' }}>{h.field_modified}</td>
                                  <td style={{ padding: '0.65rem 0.85rem', color: '#DC2626' }}>{h.previous_value}</td>
                                  <td style={{ padding: '0.65rem 0.85rem', color: '#16A34A', fontWeight: 600 }}>{h.updated_value}</td>
                                  <td style={{ padding: '0.65rem 0.85rem', color: '#334155' }}>{h.reason}</td>
                                  <td style={{ padding: '0.65rem 0.85rem' }}>
                                    <span style={{
                                      background: h.source?.includes('Approved') ? '#FEF3C7' : '#F1F5F9',
                                      color: h.source?.includes('Approved') ? '#B45309' : '#334155',
                                      padding: '0.15rem 0.45rem',
                                      borderRadius: '4px',
                                      fontSize: '0.72rem',
                                      fontWeight: 600
                                    }}>
                                      {h.source}
                                    </span>
                                  </td>
                                  <td style={{ padding: '0.65rem 0.85rem', color: '#64748B', whiteSpace: 'nowrap' }}>
                                    {h.created_at ? h.created_at.slice(0, 19).replace('T', ' ') : '—'}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div style={{ padding: '2rem', textAlign: 'center', background: '#F8FAFC', borderRadius: '12px', color: '#64748B' }}>
                          No administrative modifications or corrections have been recorded for this student yet. Record is in original state.
                        </div>
                      )}
                    </div>
                  )}
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 2: STUDENT RECORD EDITING MODAL (MAIN FORM)
          ===================================================================== */}
      {editingStudent && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10000,
          padding: '1.5rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            width: '100%',
            maxWidth: '900px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            {/* Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '1.25rem 1.75rem',
              borderBottom: '1px solid #E2E8F0',
              background: '#0F172A',
              color: '#FFFFFF'
            }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, margin: 0 }}>
                  ✏️ Edit Student Record — {editingStudent.student_name}
                </h3>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.2rem' }}>
                  Student ID: {editingStudent.student_id} • PSID: {editingStudent.permanent_student_id}
                </div>
              </div>
              <button
                onClick={() => setEditingStudent(null)}
                style={{ background: 'transparent', border: 'none', color: '#94A3B8', fontSize: '1.5rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            {/* Form Body */}
            <form onSubmit={handleInitiateSaveEdit} style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
              {/* SECTION A: PROTECTED IDENTIFIERS */}
              <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '1rem', marginBottom: '1.25rem' }}>
                <span style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.5rem' }}>
                  🔒 PROTECTED SYSTEM IDENTIFIERS (NON-EDITABLE)
                </span>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
                  <div>
                    <label style={{ fontSize: '0.72rem', color: '#64748B' }}>Student ID</label>
                    <input type="text" disabled value={editingStudent.student_id} style={{ width: '100%', padding: '0.45rem', background: '#E2E8F0', border: '1px solid #CBD5E1', borderRadius: '6px', fontSize: '0.85rem', fontFamily: 'monospace' }} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.72rem', color: '#64748B' }}>Permanent Student ID (PSID)</label>
                    <input type="text" disabled value={editingStudent.permanent_student_id} style={{ width: '100%', padding: '0.45rem', background: '#E2E8F0', border: '1px solid #CBD5E1', borderRadius: '6px', fontSize: '0.85rem', fontFamily: 'monospace' }} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.72rem', color: '#64748B' }}>Institution ID</label>
                    <input type="text" disabled value={editingStudent.school_id || institutionId} style={{ width: '100%', padding: '0.45rem', background: '#E2E8F0', border: '1px solid #CBD5E1', borderRadius: '6px', fontSize: '0.85rem', fontFamily: 'monospace' }} />
                  </div>
                </div>
              </div>

              {/* SECTION B: PERSONAL INFORMATION */}
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.75rem' }}>
                1. Personal Information
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.85rem', marginBottom: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Full Name *</label>
                  <input
                    type="text"
                    value={editFormData.student_name}
                    onChange={(e) => handleEditFieldChange('student_name', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: editValidationErrors.student_name ? '1px solid #EF4444' : '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                  {editValidationErrors.student_name && <span style={{ color: '#EF4444', fontSize: '0.72rem' }}>{editValidationErrors.student_name}</span>}
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Date of Birth (YYYY-MM-DD)</label>
                  <input
                    type="date"
                    value={editFormData.date_of_birth}
                    onChange={(e) => handleEditFieldChange('date_of_birth', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: editValidationErrors.date_of_birth ? '1px solid #EF4444' : '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                  {editValidationErrors.date_of_birth && <span style={{ color: '#EF4444', fontSize: '0.72rem' }}>{editValidationErrors.date_of_birth}</span>}
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Gender</label>
                  <select
                    value={editFormData.gender}
                    onChange={(e) => handleEditFieldChange('gender', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF' }}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Blood Group</label>
                  <select
                    value={editFormData.blood_group}
                    onChange={(e) => handleEditFieldChange('blood_group', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF' }}
                  >
                    {['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'].map(b => (
                      <option key={b} value={b}>{b}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Contact Number</label>
                  <input
                    type="text"
                    value={editFormData.contact_number}
                    onChange={(e) => handleEditFieldChange('contact_number', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: editValidationErrors.contact_number ? '1px solid #EF4444' : '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                  {editValidationErrors.contact_number && <span style={{ color: '#EF4444', fontSize: '0.72rem' }}>{editValidationErrors.contact_number}</span>}
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Student Email</label>
                  <input
                    type="email"
                    value={editFormData.student_email}
                    onChange={(e) => handleEditFieldChange('student_email', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: editValidationErrors.student_email ? '1px solid #EF4444' : '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                  {editValidationErrors.student_email && <span style={{ color: '#EF4444', fontSize: '0.72rem' }}>{editValidationErrors.student_email}</span>}
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>District</label>
                  <input
                    type="text"
                    value={editFormData.district}
                    onChange={(e) => handleEditFieldChange('district', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Taluk</label>
                  <input
                    type="text"
                    value={editFormData.taluk}
                    onChange={(e) => handleEditFieldChange('taluk', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Village / City</label>
                  <input
                    type="text"
                    value={editFormData.village_city}
                    onChange={(e) => handleEditFieldChange('village_city', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Pincode</label>
                  <input
                    type="text"
                    value={editFormData.pincode}
                    onChange={(e) => handleEditFieldChange('pincode', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Enrollment Status</label>
                  <select
                    value={editFormData.enrollment_status}
                    onChange={(e) => handleEditFieldChange('enrollment_status', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF' }}
                  >
                    <option value="active">Active Enrolled</option>
                    <option value="inactive">Inactive / Withdrawn</option>
                    <option value="transferred">Transferred</option>
                    <option value="graduated">Graduated</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Admission Number</label>
                  <input
                    type="text"
                    value={editFormData.admission_number}
                    onChange={(e) => handleEditFieldChange('admission_number', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>Residential Address</label>
                  <textarea
                    rows={2}
                    value={editFormData.address}
                    onChange={(e) => handleEditFieldChange('address', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>
              </div>

              {/* SECTION C: ACADEMIC INFORMATION */}
              <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.75rem' }}>
                2. Academic Information
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.85rem', marginBottom: '1.25rem' }}>
                {/* Standard / Class */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                    Standard / Class Level
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="12"
                    value={editFormData.standard}
                    onChange={(e) => handleEditFieldChange('standard', Number(e.target.value))}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                {/* Section */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                    Section
                  </label>
                  <select
                    value={editFormData.section}
                    onChange={(e) => handleEditFieldChange('section', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF' }}
                  >
                    <option value="A">Section A</option>
                    <option value="B">Section B</option>
                    <option value="C">Section C</option>
                    <option value="D">Section D</option>
                  </select>
                </div>

                {/* First Language */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                    First Language
                  </label>
                  <input
                    type="text"
                    value={editFormData.first_language}
                    onChange={(e) => handleEditFieldChange('first_language', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                {/* Medium of Instruction */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                    Medium of Instruction
                  </label>
                  <input
                    type="text"
                    value={editFormData.medium_of_instruction}
                    onChange={(e) => handleEditFieldChange('medium_of_instruction', e.target.value)}
                    style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                  />
                </div>

                {/* PU specific fields */}
                {(isPU || isComposite || editFormData.standard >= 11) && (
                  <>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                        PUC Level
                      </label>
                      <select
                        value={editFormData.puc_year}
                        onChange={(e) => handleEditFieldChange('puc_year', e.target.value)}
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF' }}
                      >
                        <option value="">Not Applicable</option>
                        <option value="1st PUC">1st PUC</option>
                        <option value="2nd PUC">2nd PUC</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                        PU Stream
                      </label>
                      <select
                        value={editFormData.stream}
                        onChange={(e) => handleEditFieldChange('stream', e.target.value)}
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF' }}
                      >
                        <option value="">Select Stream</option>
                        <option value="Science">Science</option>
                        <option value="Commerce">Commerce</option>
                        <option value="Arts / Humanities">Arts / Humanities</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.25rem' }}>
                        Subject Combination Code
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. PCMB, PCMC, CEBA, HEPS"
                        value={editFormData.subject_combination}
                        onChange={(e) => handleEditFieldChange('subject_combination', e.target.value.toUpperCase())}
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                      />
                    </div>
                  </>
                )}
              </div>

              {/* SECTION D: MANDATORY REASON FOR RECORD MODIFICATION */}
              <div style={{ background: '#FFFBEB', border: '1px solid #FCD34D', borderRadius: '10px', padding: '1rem', marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 800, color: '#92400E', marginBottom: '0.4rem' }}>
                  Mandatory Reason for Record Modification *
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="Provide an official administrative justification for modifying this student record (e.g., Parent submitted updated birth certificate, verified correction per register review)..."
                  value={editReason}
                  onChange={(e) => {
                    setEditReason(e.target.value)
                    if (editValidationErrors.reason) {
                      setEditValidationErrors(prev => { const n = { ...prev }; delete n.reason; return n; })
                    }
                  }}
                  style={{
                    width: '100%',
                    padding: '0.6rem',
                    borderRadius: '6px',
                    border: editValidationErrors.reason ? '1px solid #EF4444' : '1px solid #F59E0B',
                    fontSize: '0.85rem'
                  }}
                />
                {editValidationErrors.reason && (
                  <span style={{ color: '#DC2626', fontSize: '0.75rem', fontWeight: 600, display: 'block', marginTop: '0.2rem' }}>
                    {editValidationErrors.reason}
                  </span>
                )}
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setEditingStudent(null)}
                  style={{
                    background: '#F1F5F9',
                    color: '#475467',
                    border: '1px solid #CBD5E1',
                    borderRadius: '8px',
                    padding: '0.65rem 1.25rem',
                    fontSize: '0.88rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{
                    background: '#155EEF',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.65rem 1.35rem',
                    fontSize: '0.88rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  Review Changes & Save →
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 3: CONFIRMATION SCREEN BEFORE SAVING DIFF
          ===================================================================== */}
      {showEditConfirmModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.8)',
          backdropFilter: 'blur(5px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10001,
          padding: '1.5rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '16px',
            width: '100%',
            maxWidth: '650px',
            overflow: 'hidden',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.3)'
          }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.25rem 1.5rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: '0 0 0.25rem 0' }}>
                Confirm Official Record Modification
              </h3>
              <p style={{ margin: 0, fontSize: '0.8rem', color: '#94A3B8' }}>
                The following {modifiedFieldsDiff.length} field(s) will be updated in the official database and an immutable audit entry will be created.
              </p>
            </div>

            <div style={{ padding: '1.5rem', maxHeight: '60vh', overflowY: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467' }}>
                    <th style={{ padding: '0.6rem 0.75rem', textAlign: 'left' }}>Field</th>
                    <th style={{ padding: '0.6rem 0.75rem', textAlign: 'left' }}>Previous Value</th>
                    <th style={{ padding: '0.6rem 0.75rem', textAlign: 'left' }}>Proposed New Value</th>
                  </tr>
                </thead>
                <tbody>
                  {modifiedFieldsDiff.map((diff, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700, color: '#0F172A' }}>{diff.label}</td>
                      <td style={{ padding: '0.6rem 0.75rem', color: '#DC2626', background: '#FEF2F2' }}>{diff.oldValue}</td>
                      <td style={{ padding: '0.6rem 0.75rem', color: '#16A34A', background: '#F0FDF4', fontWeight: 700 }}>{diff.newValue}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <div style={{ marginTop: '1rem', background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                <span style={{ fontSize: '0.78rem', color: '#64748B', fontWeight: 600 }}>Stated Reason for Change:</span>
                <div style={{ fontSize: '0.85rem', color: '#1E293B', fontWeight: 600, marginTop: '0.2rem' }}>
                  "{editReason}"
                </div>
              </div>

              {confirmError && (
                <div style={{ marginTop: '1rem' }}>
                  <Alert type="error" message={confirmError} />
                </div>
              )}
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'flex-end',
              gap: '0.75rem',
              padding: '1.25rem 1.5rem',
              borderTop: '1px solid #E2E8F0',
              background: '#FAFAFA'
            }}>
              <button
                type="button"
                disabled={savingEdit}
                onClick={() => setShowEditConfirmModal(false)}
                style={{
                  background: '#FFFFFF',
                  color: '#475467',
                  border: '1px solid #CBD5E1',
                  borderRadius: '8px',
                  padding: '0.55rem 1.15rem',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Back to Editing
              </button>
              <button
                type="button"
                disabled={savingEdit}
                onClick={handleConfirmSaveEdit}
                style={{
                  background: '#027A48',
                  color: '#FFFFFF',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '0.55rem 1.35rem',
                  fontSize: '0.85rem',
                  fontWeight: 700,
                  cursor: savingEdit ? 'not-allowed' : 'pointer'
                }}
              >
                {savingEdit ? 'Writing to Database...' : '✓ Confirm & Save to Official Registry'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 4: ATTENDANCE RECORD CORRECTION MODAL
          ===================================================================== */}
      {correctingAttendance && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10001,
          padding: '1.5rem'
        }}>
          <div style={{ background: '#FFFFFF', borderRadius: '14px', width: '100%', maxWidth: '500px', overflow: 'hidden' }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.2rem 1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0 }}>
                Correct Attendance Record
              </h3>
              <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.2rem' }}>
                Date: {correctingAttendance.attendance_date} • {correctingAttendance.subject_name || 'General Session'}
              </div>
            </div>

            <form onSubmit={handleSaveAttendanceCorrection} style={{ padding: '1.5rem' }}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                  Corrected Attendance Status
                </label>
                <select
                  value={attNewStatus}
                  onChange={(e) => setAttNewStatus(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem', background: '#FFFFFF' }}
                >
                  <option value="present">Present</option>
                  <option value="absent">Absent</option>
                  <option value="leave">Official Leave</option>
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                  Register Remarks (Optional)
                </label>
                <input
                  type="text"
                  value={attRemarks}
                  onChange={(e) => setAttRemarks(e.target.value)}
                  placeholder="e.g. Verified manual attendance register"
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#B45309', marginBottom: '0.3rem' }}>
                  Mandatory Reason for Attendance Correction *
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Student marked absent due to biometric scanner malfunction; manual register confirms presence..."
                  value={attReason}
                  onChange={(e) => setAttReason(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #F59E0B', fontSize: '0.85rem' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setCorrectingAttendance(null)}
                  style={{ background: '#F1F5F9', color: '#475467', border: '1px solid #CBD5E1', borderRadius: '6px', padding: '0.5rem 1rem', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingAttendance}
                  style={{ background: '#155EEF', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.5rem 1.15rem', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}
                >
                  {savingAttendance ? 'Saving...' : 'Save Correction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 5: EXAMINATION RESULT CORRECTION MODAL
          ===================================================================== */}
      {correctingResult && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10001,
          padding: '1.5rem'
        }}>
          <div style={{ background: '#FFFFFF', borderRadius: '14px', width: '100%', maxWidth: '500px', overflow: 'hidden' }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.2rem 1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0 }}>
                Correct Examination Result
              </h3>
              <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.2rem' }}>
                Subject: {correctingResult.subject_name} • Exam: {correctingResult.exam_name || 'Evaluation'}
              </div>
            </div>

            <form onSubmit={handleSaveResultCorrection} style={{ padding: '1.5rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                    Marks Obtained *
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    required
                    value={examNewMarks}
                    onChange={(e) => setExamNewMarks(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                    Maximum Marks *
                  </label>
                  <input
                    type="number"
                    step="1"
                    min="1"
                    required
                    value={examNewMaxMarks}
                    onChange={(e) => setExamNewMaxMarks(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                  Grade (Leave blank to auto-calculate)
                </label>
                <input
                  type="text"
                  placeholder="e.g. A+, A, B+, B, C, F"
                  value={examNewGrade}
                  onChange={(e) => setExamNewGrade(e.target.value.toUpperCase())}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#B45309', marginBottom: '0.3rem' }}>
                  Mandatory Reason for Examination Correction *
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Re-totalling adjustment after answer script verification per subject teacher..."
                  value={examReason}
                  onChange={(e) => setExamReason(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #F59E0B', fontSize: '0.85rem' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setCorrectingResult(null)}
                  style={{ background: '#F1F5F9', color: '#475467', border: '1px solid #CBD5E1', borderRadius: '6px', padding: '0.5rem 1rem', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingResult}
                  style={{ background: '#155EEF', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.5rem 1.15rem', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}
                >
                  {savingResult ? 'Saving...' : 'Save Correction'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 6: ADD / REPLACE DOCUMENT MODAL
          ===================================================================== */}
      {showAddDocModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10001,
          padding: '1.5rem'
        }}>
          <div style={{ background: '#FFFFFF', borderRadius: '14px', width: '100%', maxWidth: '500px', overflow: 'hidden' }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.2rem 1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, margin: 0 }}>
                Add Verified Student Document
              </h3>
              <div style={{ fontSize: '0.8rem', color: '#94A3B8', marginTop: '0.2rem' }}>
                Student ID: {studentProfile.personal_info.student_id}
              </div>
            </div>

            <form onSubmit={handleSaveDocument} style={{ padding: '1.5rem' }}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                  Document Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Birth Certificate, Transfer Certificate"
                  value={docName}
                  onChange={(e) => setDocName(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                  Document Type *
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem', background: '#FFFFFF' }}
                >
                  <option value="Birth Certificate">Birth Certificate</option>
                  <option value="Transfer Certificate">Transfer Certificate</option>
                  <option value="Previous Marksheet">Previous Marksheet</option>
                  <option value="Aadhaar Card Copy">Aadhaar Card Copy</option>
                  <option value="Caste & Income Certificate">Caste & Income Certificate</option>
                  <option value="Medical Certificate">Medical Certificate</option>
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#334155', marginBottom: '0.3rem' }}>
                  File Reference / Storage Key *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. doc_verified_upload_2026.pdf"
                  value={docFileName}
                  onChange={(e) => setDocFileName(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.88rem' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#B45309', marginBottom: '0.3rem' }}>
                  Reason for Upload / Verification *
                </label>
                <textarea
                  rows={2}
                  required
                  placeholder="e.g. Physical document verified during in-person admission verification..."
                  value={docReason}
                  onChange={(e) => setDocReason(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #F59E0B', fontSize: '0.85rem' }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => setShowAddDocModal(false)}
                  style={{ background: '#F1F5F9', color: '#475467', border: '1px solid #CBD5E1', borderRadius: '6px', padding: '0.5rem 1rem', fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingDoc}
                  style={{ background: '#155EEF', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.5rem 1.15rem', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}
                >
                  {savingDoc ? 'Adding...' : 'Add Document'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 7: RECENTLY UPDATED RECORDS AUDIT PREVIEW MODAL
          ===================================================================== */}
      {showRecentUpdatesModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10001,
          padding: '1.5rem'
        }}>
          <div style={{ background: '#FFFFFF', borderRadius: '16px', width: '100%', maxWidth: '750px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0 }}>Recently Updated Student Records</h3>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Audit trail of recent modifications in {institutionName}</div>
              </div>
              <button onClick={() => setShowRecentUpdatesModal(false)} style={{ background: 'transparent', border: 'none', color: '#94A3B8', fontSize: '1.5rem', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem' }}>
              {stats?.recently_updated?.length > 0 ? (
                <div style={{ border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                    <thead>
                      <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467' }}>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Student</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Field</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Change</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Reason</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.recently_updated.map((rec, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                          <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700 }}>
                            {rec.student_name}
                            <div style={{ fontSize: '0.72rem', color: '#64748B', fontFamily: 'monospace' }}>{rec.student_id}</div>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>{rec.field_modified}</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <span style={{ color: '#DC2626' }}>{rec.previous_value}</span> → <span style={{ color: '#16A34A', fontWeight: 700 }}>{rec.updated_value}</span>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', color: '#334155' }}>{rec.reason}</td>
                          <td style={{ padding: '0.6rem 0.75rem', color: '#64748B', whiteSpace: 'nowrap' }}>
                            {rec.created_at ? rec.created_at.slice(0, 16).replace('T', ' ') : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ textAlign: 'center', color: '#64748B', padding: '2rem' }}>No recent student updates recorded yet.</p>
              )}
            </div>

            <div style={{ padding: '1rem 1.5rem', background: '#FAFAFA', borderTop: '1px solid #E2E8F0', textAlign: 'right' }}>
              <button onClick={() => setShowRecentUpdatesModal(false)} style={{ background: '#0F172A', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.5rem 1rem', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* =====================================================================
          MODAL 8: PENDING CORRECTION REQUESTS MODAL
          ===================================================================== */}
      {showPendingRequestsModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(15, 23, 42, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 10001,
          padding: '1.5rem'
        }}>
          <div style={{ background: '#FFFFFF', borderRadius: '16px', width: '100%', maxWidth: '850px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0 }}>Pending Student Correction Requests</h3>
                <div style={{ fontSize: '0.8rem', color: '#94A3B8' }}>Requests submitted by verified students and parents requiring institutional review</div>
              </div>
              <button onClick={() => setShowPendingRequestsModal(false)} style={{ background: 'transparent', border: 'none', color: '#94A3B8', fontSize: '1.5rem', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '1.25rem' }}>
              {stats?.pending_correction_requests?.length > 0 ? (
                <div style={{ border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                    <thead>
                      <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467' }}>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Tracking #</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Category & Title</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Student Name</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Field & Request</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Priority</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Submitted</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.pending_correction_requests.map((req, idx) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                          <td style={{ padding: '0.6rem 0.75rem', fontFamily: 'monospace', fontWeight: 700, color: '#155EEF' }}>{req.tracking_number}</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <div style={{ fontWeight: 700, color: '#0F172A' }}>{req.title}</div>
                            <div style={{ fontSize: '0.72rem', color: '#64748B' }}>{req.category}</div>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>
                            {req.affected_person_name}
                            <div style={{ fontSize: '0.72rem', color: '#64748B', fontFamily: 'monospace' }}>{req.affected_student_id}</div>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <div style={{ fontWeight: 600, color: '#334155' }}>{req.field_name || 'Record'}</div>
                            <div style={{ fontSize: '0.72rem' }}>
                              <span style={{ color: '#DC2626' }}>{req.current_value || '—'}</span> → <span style={{ color: '#16A34A', fontWeight: 700 }}>{req.requested_value || '—'}</span>
                            </div>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <span style={{
                              padding: '0.15rem 0.45rem',
                              borderRadius: '4px',
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              background: req.priority === 'urgent' ? '#FEE2E2' : '#FEF3C7',
                              color: req.priority === 'urgent' ? '#B91C1C' : '#B45309'
                            }}>
                              {req.priority?.toUpperCase()}
                            </span>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', color: '#64748B', whiteSpace: 'nowrap' }}>
                            {req.submitted_at ? req.submitted_at.slice(0, 10) : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p style={{ textAlign: 'center', color: '#64748B', padding: '2rem' }}>No pending correction requests currently awaiting review.</p>
              )}
            </div>

            <div style={{ padding: '1rem 1.5rem', background: '#FAFAFA', borderTop: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem', color: '#64748B' }}>
                Use the <strong>Citizen & Stakeholder Requests</strong> tab in the main sidebar to execute authorized record corrections.
              </span>
              <button onClick={() => setShowPendingRequestsModal(false)} style={{ background: '#0F172A', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.5rem 1rem', fontSize: '0.85rem', fontWeight: 700, cursor: 'pointer' }}>Close</button>
            </div>
          </div>
        </div>
      )}
      {/* Certified Academic Dossier Modal */}
      <StudentDossierModal
        isOpen={dossierModalOpen}
        onClose={() => setDossierModalOpen(false)}
        studentId={reportStudentId}
        studentName={students.find(s => s.student_id === reportStudentId)?.student_name}
      />
    </div>
  )
}
