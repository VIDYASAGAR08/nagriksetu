import { useState, useEffect } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'

const CATEGORIES = [
  { id: 'attendance_correction', label: 'Attendance Correction', module: 'student_attendance', field: 'status' },
  { id: 'student_personal_info', label: 'Student Personal Info Correction', module: 'students', field: 'student_name' },
  { id: 'parent_guardian_info', label: 'Parent / Guardian Info Correction', module: 'guardians', field: 'full_name' },
  { id: 'mobile_number_update', label: 'Mobile Number Update', module: 'guardians', field: 'phone' },
  { id: 'email_address_update', label: 'Email Address Update', module: 'guardians', field: 'email' },
  { id: 'address_update', label: 'Residential Address Update', module: 'guardians', field: 'address' },
  { id: 'dob_correction', label: 'Date of Birth Correction', module: 'students', field: 'date_of_birth' },
  { id: 'name_correction', label: 'Student Name Correction', module: 'students', field: 'student_name' },
  { id: 'marks_correction', label: 'Examination Marks Correction', module: 'academic_results', field: 'marks_obtained' },
  { id: 'result_correction', label: 'Examination Result Correction', module: 'academic_results', field: 'percentage' },
  { id: 'academic_record', label: 'Academic Record Correction', module: 'students', field: 'standard' },
  { id: 'fee_clarification', label: 'Fee Record Clarification', module: 'general', field: 'fee' },
  { id: 'admission_info', label: 'Admission Info Correction', module: 'students', field: 'student_id' },
  { id: 'linking_issue', label: 'Parent-Student Linking Issue', module: 'general', field: 'linking' },
  { id: 'institution_complaint', label: 'Institution Complaint', module: 'general', field: 'complaint' },
  { id: 'staff_complaint', label: 'Staff / Faculty Complaint', module: 'general', field: 'faculty' },
  { id: 'general_clarification', label: 'General Clarification', module: 'general', field: 'general' },
  { id: 'other', label: 'Other Requests', module: 'general', field: 'other' }
]

const STATUS_CONFIG = {
  SUBMITTED: { label: 'Submitted', color: '#155EEF', bg: '#EFF4FF', icon: '📝' },
  UNDER_REVIEW: { label: 'Under Review', color: '#B54708', bg: '#FEF0C7', icon: '🔍' },
  CLARIFICATION_REQUIRED: { label: 'Clarification Required', color: '#C01048', bg: '#FFE4E8', icon: '⚠️' },
  RESUBMITTED: { label: 'Resubmitted', color: '#7A5AF8', bg: '#F4F3FF', icon: '🔄' },
  ACCEPTED: { label: 'Accepted', color: '#027A48', bg: '#ECFDF3', icon: '✅' },
  CORRECTION_PENDING: { label: 'Correction Pending', color: '#E31B23', bg: '#FEF3F2', icon: '⏳' },
  CORRECTED: { label: 'Record Corrected', color: '#039855', bg: '#D1FADF', icon: '🎉' },
  VERIFICATION_PENDING: { label: 'Verification Pending', color: '#0E7090', bg: '#ECFEFF', icon: '📋' },
  VERIFIED: { label: 'Verified', color: '#027A48', bg: '#ECFDF3', icon: '🛡️' },
  REJECTED: { label: 'Rejected', color: '#B42318', bg: '#FEF3F2', icon: '❌' },
  CLOSED: { label: 'Closed', color: '#475467', bg: '#F2F4F7', icon: '🔒' }
}

export default function RequesterPortalView({ token, userRole, linkedStudents = [], studentSelf = null }) {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [feedback, setFeedback] = useState(null)

  // Raise Request Modal State
  const [showRaiseModal, setShowRaiseModal] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formCategory, setFormCategory] = useState('attendance_correction')
  const [formSubject, setFormSubject] = useState('')
  const [formDescription, setFormDescription] = useState('')
  const [formPriority, setFormPriority] = useState('MEDIUM')
  const [formSelectedStudent, setFormSelectedStudent] = useState('')
  const [formFieldName, setFormFieldName] = useState('')
  const [formCurrentVal, setFormCurrentVal] = useState('')
  const [formRequestedVal, setFormRequestedVal] = useState('')
  const [formAttendanceDate, setFormAttendanceDate] = useState('')
  const [formTestId, setFormTestId] = useState('')
  const [formAttachmentName, setFormAttachmentName] = useState('')
  const [formAttachmentBase64, setFormAttachmentBase64] = useState('')

  // View Details Modal State
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [loadingDetails, setLoadingDetails] = useState(false)
  const [detailsData, setDetailsData] = useState(null)

  // Clarification Response State
  const [clarificationResponseText, setClarificationResponseText] = useState('')
  const [submittingClarification, setSubmittingClarification] = useState(false)

  // Load user requests
  const loadRequests = async () => {
    try {
      setLoading(true)
      const data = await apiGet('/requests/my-requests', token)
      setRequests(data)
    } catch (err) {
      console.error('Failed to load requests:', err)
      setFeedback({ type: 'error', message: err.message || 'Failed to load requests' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [])

  // Auto-fill student options
  useEffect(() => {
    if (studentSelf) {
      setFormSelectedStudent(studentSelf.permanent_student_id || studentSelf.student_id || '')
    } else if (linkedStudents.length > 0 && !formSelectedStudent) {
      setFormSelectedStudent(linkedStudents[0].permanent_student_id || linkedStudents[0].student_id || '')
    }
  }, [linkedStudents, studentSelf])

  // Open Details Modal
  const openDetails = async (reqId) => {
    try {
      setSelectedRequest(reqId)
      setLoadingDetails(true)
      setDetailsData(null)
      const data = await apiGet(`/requests/${reqId}`, token)
      setDetailsData(data)
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to fetch request details' })
    } finally {
      setLoadingDetails(false)
    }
  }

  // Handle Clarification Response
  const handleClarificationSubmit = async (e) => {
    e.preventDefault()
    if (!clarificationResponseText.trim()) return
    try {
      setSubmittingClarification(true)
      await apiPost(`/requests/${selectedRequest}/respond-clarification`, {
        response_message: clarificationResponseText.trim(),
        additional_document_url: null
      }, token)
      setClarificationResponseText('')
      setFeedback({ type: 'success', message: 'Clarification submitted successfully. Status updated to Under Review.' })
      await openDetails(selectedRequest)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to submit clarification' })
    } finally {
      setSubmittingClarification(false)
    }
  }

  // Handle Raise Request
  const handleRaiseSubmit = async (e) => {
    e.preventDefault()
    if (!formSubject.trim() || !formDescription.trim()) {
      setFeedback({ type: 'error', message: 'Subject and detailed description are required.' })
      return
    }

    try {
      setSubmitting(true)
      setFeedback(null)

      const categoryObj = CATEGORIES.find(c => c.id === formCategory)
      const targetModule = categoryObj ? categoryObj.module : 'general'

      let fieldName = formFieldName || (categoryObj ? categoryObj.field : null)
      let currentVal = formCurrentVal
      let requestedVal = formRequestedVal

      let targetRecordId = null
      let targetStudentId = null

      if (studentSelf) {
        targetStudentId = studentSelf.permanent_student_id || studentSelf.student_id
        targetRecordId = targetStudentId
      } else if (formSelectedStudent) {
        targetStudentId = formSelectedStudent
        targetRecordId = formSelectedStudent
      }

      if (formCategory === 'attendance_correction') {
        fieldName = 'status'
        targetRecordId = `${targetStudentId}__${formAttendanceDate || 'today'}`
        if (formAttendanceDate) {
          currentVal = currentVal ? `${formAttendanceDate}: ${currentVal}` : formAttendanceDate
        }
      } else if (formCategory === 'marks_correction') {
        fieldName = 'marks_obtained'
        if (formTestId) {
          targetRecordId = formTestId
        }
      }

      const attachments = []
      if (formAttachmentBase64 && formAttachmentName) {
        attachments.push({
          file_name: formAttachmentName,
          file_type: 'application/pdf',
          file_url: formAttachmentBase64,
          file_size_bytes: 1024
        })
      }

      const payload = {
        title: formSubject.trim(),
        category: categoryObj ? categoryObj.label : formCategory,
        description: formDescription.trim(),
        priority: (formPriority || 'medium').toLowerCase(),
        affected_person_type: studentSelf ? 'self' : 'linked_child',
        affected_student_id: targetStudentId,
        target_module: targetModule,
        target_record_id: targetRecordId,
        field_name: fieldName,
        current_value: currentVal ? String(currentVal) : null,
        requested_value: requestedVal ? String(requestedVal) : null,
        supporting_document_url: formAttachmentBase64 || null,
        supporting_document_name: formAttachmentName || null
      }

      const res = await apiPost('/requests/raise', payload, token)
      setFeedback({
        type: 'success',
        message: `Request submitted successfully! Tracking Number: ${res.tracking_number} (Status: ${res.status})`
      })

      // Reset form
      setShowRaiseModal(false)
      setFormSubject('')
      setFormDescription('')
      setFormFieldName('')
      setFormCurrentVal('')
      setFormRequestedVal('')
      setFormAttendanceDate('')
      setFormTestId('')
      setFormAttachmentName('')
      setFormAttachmentBase64('')

      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to submit request.' })
    } finally {
      setSubmitting(false)
    }
  }

  // Filter requests
  const filteredRequests = requests.filter(r => {
    if (statusFilter !== 'ALL') {
      if (statusFilter === 'OPEN' && !['SUBMITTED', 'UNDER_REVIEW', 'RESUBMITTED', 'CORRECTION_PENDING'].includes(r.status)) return false
      if (statusFilter === 'CLARIFICATION' && r.status !== 'CLARIFICATION_REQUIRED') return false
      if (statusFilter === 'CORRECTED' && r.status !== 'CORRECTED') return false
      if (statusFilter === 'REJECTED' && r.status !== 'REJECTED') return false
      if (statusFilter === 'CLOSED' && r.status !== 'CLOSED') return false
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchTrack = r.tracking_number?.toLowerCase().includes(q)
      const matchSub = r.subject?.toLowerCase().includes(q)
      const matchCat = r.category?.toLowerCase().includes(q)
      const matchTarget = r.target_student_name?.toLowerCase().includes(q) || r.target_student_id?.toLowerCase().includes(q)
      if (!matchTrack && !matchSub && !matchCat && !matchTarget) return false
    }
    return true
  })

  return (
    <div style={{ padding: '0.5rem 0' }}>
      {/* Header and Actions */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.5rem',
        background: '#ffffff',
        padding: '1.25rem 1.5rem',
        borderRadius: '10px',
        border: '1px solid #E2E8F0',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.35rem', color: '#102B46', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>📋</span> My Requests, Complaints & Record Corrections
          </h2>
          <p style={{ margin: '0.25rem 0 0 0', color: '#64748B', fontSize: '0.875rem' }}>
            Submit grievances, clarify records, or request verified corrections to attendance, personal details, and academic marks.
          </p>
        </div>
        <button
          onClick={() => { setFeedback(null); setShowRaiseModal(true); }}
          className="btn btn--primary"
          style={{
            background: 'linear-gradient(135deg, #155EEF 0%, #102B46 100%)',
            color: '#ffffff',
            fontWeight: 600,
            padding: '0.65rem 1.25rem',
            borderRadius: '8px',
            border: 'none',
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            cursor: 'pointer'
          }}
        >
          <span style={{ fontSize: '1.1rem' }}>+</span> Raise New Request
        </button>
      </div>

      {feedback && (
        <div style={{ marginBottom: '1.25rem' }}>
          <Alert type={feedback.type}>{feedback.message}</Alert>
        </div>
      )}

      {/* Status Filter Tabs & Search */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          {[
            { id: 'ALL', label: 'All Requests' },
            { id: 'OPEN', label: 'Open / In-Progress' },
            { id: 'CLARIFICATION', label: 'Needs Clarification' },
            { id: 'CORRECTED', label: 'Corrected' },
            { id: 'REJECTED', label: 'Rejected' },
            { id: 'CLOSED', label: 'Closed' }
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setStatusFilter(f.id)}
              style={{
                padding: '0.4rem 0.85rem',
                borderRadius: '20px',
                fontSize: '0.825rem',
                fontWeight: statusFilter === f.id ? 700 : 500,
                border: '1px solid',
                borderColor: statusFilter === f.id ? '#155EEF' : '#D0D5DD',
                background: statusFilter === f.id ? '#EFF4FF' : '#FFFFFF',
                color: statusFilter === f.id ? '#155EEF' : '#475467',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        <input
          type="text"
          placeholder="Search by ID, subject, student..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            padding: '0.45rem 0.85rem',
            borderRadius: '6px',
            border: '1px solid #D0D5DD',
            fontSize: '0.85rem',
            width: '260px'
          }}
        />
      </div>

      {/* Requests List */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <LoadingSpinner />
          <p style={{ marginTop: '0.5rem', color: '#64748B' }}>Loading your submitted requests...</p>
        </div>
      ) : filteredRequests.length === 0 ? (
        <div style={{
          textAlign: 'center',
          padding: '3rem',
          background: '#FFFFFF',
          borderRadius: '10px',
          border: '1px solid #E2E8F0',
          boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
        }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📭</div>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#102B46' }}>No Requests Found</h3>
          <p style={{ color: '#64748B', margin: '0 0 1rem 0', fontSize: '0.9rem' }}>
            {statusFilter !== 'ALL' ? 'No requests match the selected filter.' : 'You have not submitted any requests or complaints yet.'}
          </p>
          <button
            onClick={() => setShowRaiseModal(true)}
            className="btn btn--outline"
            style={{ fontWeight: 600 }}
          >
            + Submit Your First Request
          </button>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: '0.85rem' }}>
          {filteredRequests.map(req => {
            const statusMeta = STATUS_CONFIG[req.status] || { label: req.status, color: '#475467', bg: '#F2F4F7', icon: '📄' }
            const isClarification = req.status === 'CLARIFICATION_REQUIRED'
            const isCorrected = req.status === 'CORRECTED'

            return (
              <div
                key={req.request_id}
                style={{
                  background: isClarification ? '#FFFDF5' : '#FFFFFF',
                  borderRadius: '10px',
                  border: isClarification ? '2px solid #F79009' : (isCorrected ? '1px solid #A6F4C5' : '1px solid #E2E8F0'),
                  padding: '1.25rem 1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  flexWrap: 'wrap',
                  gap: '1rem',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
                }}
              >
                <div style={{ flex: '1 1 500px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap', marginBottom: '0.4rem' }}>
                    <span style={{
                      fontFamily: 'monospace',
                      fontWeight: 700,
                      background: '#F1F5F9',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px',
                      color: '#0F172A',
                      fontSize: '0.85rem'
                    }}>
                      {req.tracking_number}
                    </span>
                    <span style={{
                      padding: '0.2rem 0.6rem',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      background: statusMeta.bg,
                      color: statusMeta.color,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem'
                    }}>
                      {statusMeta.icon} {statusMeta.label}
                    </span>
                    {req.priority === 'URGENT' && (
                      <span style={{ background: '#FEE4E2', color: '#D92D20', padding: '0.15rem 0.5rem', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700 }}>
                        URGENT
                      </span>
                    )}
                    <span style={{ fontSize: '0.78rem', color: '#94A3B8' }}>
                      Routing: {req.assigned_institution_name || (req.routing_tier === 'PLATFORM' ? 'State Authority' : req.assigned_institution_id)}
                    </span>
                  </div>

                  <h3 style={{ margin: '0.25rem 0 0.35rem 0', fontSize: '1.05rem', color: '#102B46', fontWeight: 700 }}>
                    {req.subject}
                  </h3>

                  <p style={{ margin: 0, color: '#475467', fontSize: '0.875rem', lineHeight: 1.4 }}>
                    {req.description?.length > 140 ? `${req.description.slice(0, 140)}...` : req.description}
                  </p>

                  <div style={{ display: 'flex', gap: '1.25rem', marginTop: '0.65rem', fontSize: '0.78rem', color: '#64748B', flexWrap: 'wrap' }}>
                    <span>Category: <strong>{req.category?.replace(/_/g, ' ')}</strong></span>
                    {req.target_student_name && (
                      <span>Student: <strong>{req.target_student_name} ({req.target_student_id})</strong></span>
                    )}
                    <span>Submitted: {new Date(req.created_at).toLocaleDateString()}</span>
                  </div>

                  {/* Clarification Alert inside Card */}
                  {isClarification && (
                    <div style={{
                      marginTop: '0.75rem',
                      background: '#FFF4ED',
                      border: '1px solid #FD853A',
                      padding: '0.6rem 0.85rem',
                      borderRadius: '6px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.6rem',
                      color: '#B54708',
                      fontSize: '0.85rem'
                    }}>
                      <span>⚠️</span>
                      <span><strong>Clarification requested by institution:</strong> {req.clarification_prompt || 'Please provide additional clarification.'}</span>
                    </div>
                  )}

                  {/* Corrected Badge inside Card */}
                  {isCorrected && (
                    <div style={{
                      marginTop: '0.75rem',
                      background: '#ECFDF3',
                      border: '1px solid #6CE9A6',
                      padding: '0.5rem 0.85rem',
                      borderRadius: '6px',
                      color: '#027A48',
                      fontSize: '0.825rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '0.5rem'
                    }}>
                      <span>✅</span>
                      <span>Record successfully corrected in live database! Click View Details to inspect previous vs corrected values.</span>
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', alignItems: 'flex-end' }}>
                  <button
                    onClick={() => openDetails(req.request_id)}
                    className="btn btn--sm"
                    style={{
                      background: isClarification ? '#B54708' : '#155EEF',
                      color: '#FFFFFF',
                      fontWeight: 600,
                      padding: '0.45rem 0.95rem',
                      borderRadius: '6px',
                      border: 'none',
                      cursor: 'pointer'
                    }}
                  >
                    {isClarification ? 'Respond to Clarification →' : 'View Details & Track →'}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* MODAL: RAISE NEW REQUEST */}
      {showRaiseModal && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(16, 24, 40, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            maxWidth: '680px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#102B46', fontWeight: 700 }}>
                  Raise Request, Complaint or Correction
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', color: '#64748B', fontSize: '0.825rem' }}>
                  Submissions are automatically routed to the accredited institution or State Authority.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setShowRaiseModal(false)}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#94A3B8' }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleRaiseSubmit}>
              {/* Category */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Request Category <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <select
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.9rem' }}
                >
                  {CATEGORIES.map(c => (
                    <option key={c.id} value={c.id}>{c.label}</option>
                  ))}
                </select>
              </div>

              {/* Student Selector if parent */}
              {userRole !== 'student' && linkedStudents.length > 0 && (
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                    Select Linked Child / Student <span style={{ color: '#D92D20' }}>*</span>
                  </label>
                  <select
                    value={formSelectedStudent}
                    onChange={(e) => setFormSelectedStudent(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.9rem' }}
                  >
                    {linkedStudents.map(s => (
                      <option key={s.permanent_student_id || s.student_id} value={s.permanent_student_id || s.student_id}>
                        {s.student_name} (ID: {s.student_id} | {s.school_name || s.institution_name || 'Enrolled Institution'})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Subject */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Subject / Summary <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Attendance marked absent on 2026-11-18 despite presence"
                  value={formSubject}
                  onChange={(e) => setFormSubject(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.9rem' }}
                />
              </div>

              {/* Field specific inputs */}
              {formCategory === 'attendance_correction' && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                      Date of Attendance <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <input
                      type="date"
                      required
                      value={formAttendanceDate}
                      onChange={(e) => setFormAttendanceDate(e.target.value)}
                      style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                      Requested Status <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <select
                      value={formRequestedVal}
                      onChange={(e) => setFormRequestedVal(e.target.value)}
                      style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                    >
                      <option value="">Select Status</option>
                      <option value="PRESENT">PRESENT</option>
                      <option value="EXCUSED">EXCUSED / LEAVE</option>
                      <option value="HALF_DAY">HALF DAY</option>
                    </select>
                  </div>
                </div>
              )}

              {/* Current Value & Requested Value for Record Corrections */}
              {['student_personal_info', 'parent_guardian_info', 'mobile_number_update', 'email_address_update', 'address_update', 'dob_correction', 'name_correction', 'marks_correction', 'academic_record'].includes(formCategory) && (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                      Current Recorded Value
                    </label>
                    <input
                      type="text"
                      placeholder="Current value on record"
                      value={formCurrentVal}
                      onChange={(e) => setFormCurrentVal(e.target.value)}
                      style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                      Requested Corrected Value <span style={{ color: '#D92D20' }}>*</span>
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="Requested correction"
                      value={formRequestedVal}
                      onChange={(e) => setFormRequestedVal(e.target.value)}
                      style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                    />
                  </div>
                </div>
              )}

              {/* Description */}
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Detailed Explanation & Justification <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <textarea
                  required
                  rows={4}
                  placeholder="Explain why this correction or grievance is being submitted..."
                  value={formDescription}
                  onChange={(e) => setFormDescription(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                />
              </div>

              {/* Priority & Supporting Document */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                    Priority Level
                  </label>
                  <select
                    value={formPriority}
                    onChange={(e) => setFormPriority(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium (Standard)</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent (Immediate attention)</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                    Attach Supporting Document (Optional)
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.png,.jpg,.jpeg"
                    onChange={(e) => {
                      const file = e.target.files[0]
                      if (file) {
                        setFormAttachmentName(file.name)
                        const reader = new FileReader()
                        reader.onloadend = () => {
                          setFormAttachmentBase64(reader.result)
                        }
                        reader.readAsDataURL(file)
                      }
                    }}
                    style={{ width: '100%', fontSize: '0.8rem' }}
                  />
                </div>
              </div>

              {/* Submit Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', borderTop: '1px solid #E2E8F0', paddingTop: '1rem' }}>
                <button
                  type="button"
                  onClick={() => setShowRaiseModal(false)}
                  className="btn btn--secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn--primary"
                  style={{ background: '#155EEF', color: '#FFFFFF', fontWeight: 600 }}
                >
                  {submitting ? 'Submitting to Authority...' : 'Submit Request Now'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: VIEW DETAILS & TRACKING */}
      {selectedRequest && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(16, 24, 40, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            maxWidth: '750px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase' }}>
                  Request Lifecycle Tracking
                </span>
                <h3 style={{ margin: '0.15rem 0 0 0', fontSize: '1.3rem', color: '#102B46', fontWeight: 700 }}>
                  {detailsData?.request?.tracking_number || selectedRequest}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => setSelectedRequest(null)}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#94A3B8' }}
              >
                ✕
              </button>
            </div>

            {loadingDetails || !detailsData ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#64748B' }}>Fetching timeline and audit status...</p>
              </div>
            ) : (
              <div>
                {/* Status & Priority Banner */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: STATUS_CONFIG[detailsData.request.status]?.bg || '#F8FAFC',
                  border: `1px solid ${STATUS_CONFIG[detailsData.request.status]?.color || '#CBD5E1'}`,
                  borderRadius: '8px',
                  padding: '1rem 1.25rem',
                  marginBottom: '1.25rem'
                }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', color: '#475467', fontWeight: 600 }}>CURRENT STATUS</div>
                    <div style={{ fontSize: '1.15rem', fontWeight: 800, color: STATUS_CONFIG[detailsData.request.status]?.color || '#102B46' }}>
                      {STATUS_CONFIG[detailsData.request.status]?.icon} {STATUS_CONFIG[detailsData.request.status]?.label}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.75rem', color: '#475467', fontWeight: 600 }}>ROUTED TO</div>
                    <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46' }}>
                      {detailsData.request.assigned_institution_name || (detailsData.request.routing_tier === 'PLATFORM' ? 'Platform Authority' : detailsData.request.assigned_institution_id)}
                    </div>
                  </div>
                </div>

                {/* VERIFIED CORRECTION CARD (If Corrected) */}
                {detailsData.request.status === 'CORRECTED' && detailsData.corrections && detailsData.corrections.length > 0 && (
                  <div style={{
                    background: '#ECFDF3',
                    border: '2px solid #32D583',
                    borderRadius: '8px',
                    padding: '1.25rem',
                    marginBottom: '1.5rem'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#027A48', fontWeight: 800, fontSize: '1rem', marginBottom: '0.5rem' }}>
                      <span>🛡️</span> AUTHENTICATED DATABASE RECORD CORRECTION VERIFIED
                    </div>
                    {detailsData.corrections.map((corr, idx) => (
                      <div key={idx} style={{ background: '#FFFFFF', padding: '0.85rem', borderRadius: '6px', border: '1px solid #A6F4C5', marginTop: '0.5rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.85rem' }}>
                          <div>
                            <span style={{ color: '#64748B', display: 'block', fontSize: '0.75rem', fontWeight: 600 }}>PREVIOUS VALUE</span>
                            <span style={{ color: '#B42318', textDecoration: 'line-through', fontWeight: 600 }}>{corr.previous_value || 'None'}</span>
                          </div>
                          <div>
                            <span style={{ color: '#64748B', display: 'block', fontSize: '0.75rem', fontWeight: 600 }}>CORRECTED VALUE (IN DATABASE)</span>
                            <span style={{ color: '#027A48', fontWeight: 700 }}>{corr.corrected_value}</span>
                          </div>
                        </div>
                        <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#475467' }}>
                          Target Table: <code>{corr.target_table}</code> ({corr.field_name}) | Corrected by: <strong>{corr.corrected_by}</strong> on {new Date(corr.corrected_at).toLocaleString()}
                        </div>
                        {corr.correction_notes && (
                          <div style={{ marginTop: '0.35rem', fontSize: '0.75rem', color: '#1E293B', fontStyle: 'italic' }}>
                            Remarks: "{corr.correction_notes}"
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* REJECTION CARD (If Rejected) */}
                {detailsData.request.status === 'REJECTED' && (
                  <div style={{
                    background: '#FEF3F2',
                    border: '2px solid #F97066',
                    borderRadius: '8px',
                    padding: '1.25rem',
                    marginBottom: '1.5rem',
                    color: '#B42318'
                  }}>
                    <div style={{ fontWeight: 800, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span>❌</span> REQUEST REJECTED BY AUTHORITY
                    </div>
                    <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', background: '#FFFFFF', padding: '0.75rem', borderRadius: '6px', border: '1px solid #FDA29B' }}>
                      <strong>Mandatory Official Rejection Reason:</strong>
                      <p style={{ margin: '0.25rem 0 0 0', color: '#344054' }}>
                        {detailsData.request.rejection_reason || 'No specific explanation provided.'}
                      </p>
                    </div>
                  </div>
                )}

                {/* CLARIFICATION RESPONSE FORM (If Clarification Required) */}
                {detailsData.request.status === 'CLARIFICATION_REQUIRED' && (
                  <div style={{
                    background: '#FFF8F0',
                    border: '2px solid #FD853A',
                    borderRadius: '8px',
                    padding: '1.25rem',
                    marginBottom: '1.5rem'
                  }}>
                    <div style={{ color: '#B54708', fontWeight: 800, fontSize: '0.95rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span>⚠️</span> ACTION REQUIRED: CLARIFICATION REQUESTED BY INSTITUTION
                    </div>
                    <div style={{ marginTop: '0.5rem', fontSize: '0.875rem', background: '#FFFFFF', padding: '0.75rem', borderRadius: '6px', border: '1px solid #FEDF89', color: '#344054' }}>
                      <strong>Institution Prompt:</strong>
                      <p style={{ margin: '0.25rem 0 0 0' }}>
                        {detailsData.request.clarification_prompt || 'Please provide additional clarification.'}
                      </p>
                    </div>

                    <form onSubmit={handleClarificationSubmit} style={{ marginTop: '1rem' }}>
                      <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                        Your Clarification / Counter Explanation <span style={{ color: '#D92D20' }}>*</span>
                      </label>
                      <textarea
                        required
                        rows={3}
                        value={clarificationResponseText}
                        onChange={(e) => setClarificationResponseText(e.target.value)}
                        placeholder="Type your response to the institution administrator..."
                        style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                      />
                      <div style={{ marginTop: '0.75rem', textAlign: 'right' }}>
                        <button
                          type="submit"
                          disabled={submittingClarification}
                          className="btn btn--primary"
                          style={{ background: '#B54708', color: '#FFFFFF', fontWeight: 600, border: 'none' }}
                        >
                          {submittingClarification ? 'Submitting...' : 'Submit Clarification to Authority'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Request Overview */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: '#102B46', fontSize: '0.95rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.35rem' }}>
                    Request Details
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                    <div><strong>Category:</strong> {detailsData.request.category?.replace(/_/g, ' ')}</div>
                    <div><strong>Priority:</strong> {detailsData.request.priority}</div>
                    <div><strong>Target Person/Student:</strong> {detailsData.request.target_student_name || detailsData.request.target_student_id || 'Self'}</div>
                    <div><strong>Submission Date:</strong> {new Date(detailsData.request.created_at).toLocaleString()}</div>
                    {detailsData.request.field_name && (
                      <div style={{ gridColumn: 'span 2' }}>
                        <strong>Target Field & Requested Change:</strong> <code>{detailsData.request.field_name}</code>: {detailsData.request.current_value || 'None'} → <strong>{detailsData.request.requested_value}</strong>
                      </div>
                    )}
                  </div>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#344054', background: '#F8FAFC', padding: '0.75rem', borderRadius: '6px' }}>
                    <strong>Original Statement:</strong>
                    <p style={{ margin: '0.25rem 0 0 0', lineHeight: 1.4 }}>{detailsData.request.description}</p>
                  </div>
                </div>

                {/* Remarks Thread (Visible to Requester Only) */}
                {detailsData.remarks && detailsData.remarks.length > 0 && (
                  <div style={{ marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#102B46', fontSize: '0.95rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.35rem' }}>
                      Official Communications & Remarks
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                      {detailsData.remarks.map((rem, idx) => (
                        <div key={idx} style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '6px', padding: '0.75rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748B', marginBottom: '0.25rem' }}>
                            <strong>{rem.author_name} ({rem.author_role?.replace(/_/g, ' ')})</strong>
                            <span>{new Date(rem.created_at).toLocaleString()}</span>
                          </div>
                          <p style={{ margin: 0, fontSize: '0.85rem', color: '#1E293B' }}>{rem.message || rem.remark_text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Lifecycle Status History */}
                {detailsData.status_history && detailsData.status_history.length > 0 && (
                  <div>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#102B46', fontSize: '0.95rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.35rem' }}>
                      Lifecycle Status History
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {detailsData.status_history.map((sh, idx) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.8rem', color: '#475467' }}>
                          <span style={{ fontFamily: 'monospace', color: '#94A3B8' }}>{new Date(sh.changed_at).toLocaleTimeString()}</span>
                          <span style={{ fontWeight: 600, color: '#0F172A' }}>{sh.old_status || 'INIT'} → {sh.new_status}</span>
                          <span style={{ color: '#64748B' }}>by {sh.changed_by}</span>
                          {sh.change_reason && <span style={{ fontStyle: 'italic', color: '#334155' }}>({sh.change_reason})</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
                  <button onClick={() => setSelectedRequest(null)} className="btn btn--secondary">
                    Close Details
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
