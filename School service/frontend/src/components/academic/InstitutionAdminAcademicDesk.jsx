import React, { useState, useEffect } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'

export default function InstitutionAdminAcademicDesk({ token, institutionId, institutionName }) {
  const [subTab, setSubTab] = useState('overview') // 'overview' | 'examinations' | 'attendance' | 'results' | 'announcements' | 'audits'

  // Data states
  const [examinations, setExaminations] = useState([])
  const [attendanceRecords, setAttendanceRecords] = useState([])
  const [resultsList, setResultsList] = useState([])
  const [announcements, setAnnouncements] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // New Examination Form
  const [showExamModal, setShowExamModal] = useState(false)
  const [examName, setExamName] = useState('')
  const [academicYear, setAcademicYear] = useState('2025-26')
  const [examDate, setExamDate] = useState(new Date().toISOString().slice(0, 10))
  const [examStandard, setExamStandard] = useState('')
  const [examDescription, setExamDescription] = useState('')
  const [submittingExam, setSubmittingExam] = useState(false)

  // New Announcement Form
  const [showAnnounceModal, setShowAnnounceModal] = useState(false)
  const [announceTitle, setAnnounceTitle] = useState('')
  const [announceContent, setAnnounceContent] = useState('')
  const [announceAudience, setAnnounceAudience] = useState('all')
  const [submittingAnnounce, setSubmittingAnnounce] = useState(false)

  // Selected Result for Audit History Modal
  const [selectedResult, setSelectedResult] = useState(null)
  const [auditLogs, setAuditLogs] = useState([])
  const [loadingAudits, setLoadingAudits] = useState(false)

  // Filters
  const [resultsFilterSubject, setResultsFilterSubject] = useState('')
  const [resultsFilterExam, setResultsFilterExam] = useState('')
  const [attendanceFilterDate, setAttendanceFilterDate] = useState('')

  async function loadData() {
    if (!token || !institutionId) return
    setLoading(true)
    setError('')
    try {
      const [examsRes, attendRes, resultsRes, annRes] = await Promise.all([
        apiGet(`/academic/examinations?institution_id=${institutionId}`, token).catch(() => ({ examinations: [] })),
        apiGet(`/academic/attendance?institution_id=${institutionId}&limit=50`, token).catch(() => ({ attendance_records: [] })),
        apiGet(`/academic/results?institution_id=${institutionId}&limit=100`, token).catch(() => ({ results: [] })),
        apiGet(`/academic/announcements?institution_id=${institutionId}`, token).catch(() => ({ announcements: [] })),
      ])

      setExaminations(Array.isArray(examsRes) ? examsRes : (examsRes?.examinations || []))
      setAttendanceRecords(Array.isArray(attendRes) ? attendRes : (attendRes?.attendance_records || []))
      setResultsList(Array.isArray(resultsRes) ? resultsRes : (resultsRes?.results || []))
      setAnnouncements(Array.isArray(annRes) ? annRes : (annRes?.announcements || []))
    } catch (err) {
      setError(err.message || 'Failed to load academic data.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [token, institutionId])

  async function handleCreateExam(e) {
    e.preventDefault()
    if (!examName.trim()) {
      setError('Please provide an examination title.')
      return
    }
    setSubmittingExam(true)
    setError('')
    setSuccess('')
    try {
      await apiPost('/academic/examinations', {
        institution_id: institutionId,
        exam_name: examName.trim(),
        academic_year: academicYear,
        exam_date: examDate,
        standard: examStandard ? parseInt(examStandard, 10) : undefined,
        description: examDescription.trim() || undefined,
      }, token)

      setSuccess(`Examination "${examName}" successfully scheduled.`)
      setShowExamModal(false)
      setExamName('')
      setExamDescription('')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to schedule examination.')
    } finally {
      setSubmittingExam(false)
    }
  }

  async function handleCreateAnnouncement(e) {
    e.preventDefault()
    if (!announceTitle.trim() || !announceContent.trim()) {
      setError('Title and content are required.')
      return
    }
    setSubmittingAnnounce(true)
    setError('')
    setSuccess('')
    try {
      await apiPost('/academic/announcements', {
        institution_id: institutionId,
        title: announceTitle.trim(),
        content: announceContent.trim(),
        target_audience: announceAudience,
        published_date: new Date().toISOString().slice(0, 10),
      }, token)

      setSuccess('Institution announcement successfully published to portal.')
      setShowAnnounceModal(false)
      setAnnounceTitle('')
      setAnnounceContent('')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to publish announcement.')
    } finally {
      setSubmittingAnnounce(false)
    }
  }

  async function viewAuditHistory(resItem) {
    setSelectedResult(resItem)
    setLoadingAudits(true)
    setAuditLogs([])
    try {
      const data = await apiGet(`/academic/results/audits/${resItem.result_id}`, token)
      setAuditLogs(data.audits || [])
    } catch (err) {
      console.error('Audit fetch error:', err)
    } finally {
      setLoadingAudits(false)
    }
  }

  const filteredResults = resultsList.filter(r => {
    if (resultsFilterSubject && r.subject_name !== resultsFilterSubject) return false
    if (resultsFilterExam && r.exam_name !== resultsFilterExam) return false
    return true
  })

  const filteredAttendance = attendanceRecords.filter(a => {
    if (attendanceFilterDate && a.attendance_date !== attendanceFilterDate) return false
    return true
  })

  // Unique lists for filters
  const distinctSubjects = Array.from(new Set(resultsList.map(r => r.subject_name).filter(Boolean)))
  const distinctExams = Array.from(new Set(resultsList.map(r => r.exam_name).filter(Boolean)))

  return (
    <div style={{ marginTop: '1rem' }}>
      {/* Sub-navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {[
            { id: 'overview', label: '📊 Academic Oversight' },
            { id: 'examinations', label: `📝 Examinations (${examinations.length})` },
            { id: 'attendance', label: `📅 Attendance Records (${attendanceRecords.length})` },
            { id: 'results', label: `🎯 Results & Grades (${resultsList.length})` },
            { id: 'announcements', label: `📢 Announcements (${announcements.length})` },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => { setSubTab(tab.id); setError(''); setSuccess(''); }}
              style={{
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                border: 'none',
                fontWeight: subTab === tab.id ? 700 : 500,
                fontSize: '0.875rem',
                cursor: 'pointer',
                background: subTab === tab.id ? '#1a3a6b' : '#f1f5f9',
                color: subTab === tab.id ? '#ffffff' : '#475467',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={() => setShowExamModal(true)}
            style={{ padding: '0.5rem 0.85rem', background: '#0284c7', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.8125rem', cursor: 'pointer' }}
          >
            + Schedule Examination
          </button>
          <button
            onClick={() => setShowAnnounceModal(true)}
            style={{ padding: '0.5rem 0.85rem', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.8125rem', cursor: 'pointer' }}
          >
            + Post Announcement
          </button>
        </div>
      </div>

      {error && <Alert type="error" title="Academic Error" className="mb-4">{error}</Alert>}
      {success && <Alert type="success" title="Success" className="mb-4">{success}</Alert>}

      {loading && (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <LoadingSpinner />
          <p style={{ marginTop: '0.5rem', color: '#64748b' }}>Loading institution academic ledger...</p>
        </div>
      )}

      {/* VIEW 1: OVERVIEW */}
      {!loading && subTab === 'overview' && (
        <div>
          {/* KPI Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Attendance Entries</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', margin: '0.25rem 0' }}>
                {attendanceRecords.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#059669' }}>Recorded across institution standards</div>
            </div>

            <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Examinations Scheduled</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0284c7', margin: '0.25rem 0' }}>
                {examinations.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Active assessment calendar</div>
            </div>

            <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Academic Results Logged</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#1a3a6b', margin: '0.25rem 0' }}>
                {resultsList.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Verified student scores with audit tracking</div>
            </div>

            <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase' }}>Announcements</div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#7c3aed', margin: '0.25rem 0' }}>
                {announcements.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Published to student/parent portals</div>
            </div>
          </div>

          {/* Quick Recent Overview */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.25rem' }}>
            {/* Scheduled Exams */}
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#1a3a6b', fontWeight: 700 }}>Upcoming Examinations</h3>
                <button onClick={() => setSubTab('examinations')} style={{ background: 'none', border: 'none', color: '#0284c7', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                  View All ({examinations.length}) →
                </button>
              </div>
              {examinations.length === 0 ? (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: '#64748b', fontSize: '0.875rem' }}>
                  No examinations scheduled yet for this institution.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {examinations.slice(0, 5).map(ex => (
                    <div key={ex.exam_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.65rem 0.85rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <div>
                        <strong style={{ fontSize: '0.9rem', color: '#0f172a' }}>{ex.exam_name}</strong>
                        <span style={{ fontSize: '0.75rem', color: '#64748b', marginLeft: '0.5rem' }}>({ex.academic_year})</span>
                      </div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, padding: '0.2rem 0.5rem', borderRadius: '4px', background: '#e0f2fe', color: '#0369a1' }}>
                        {ex.exam_date || 'Ongoing'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Recent Gradebook Results */}
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#1a3a6b', fontWeight: 700 }}>Recent Evaluation Results</h3>
                <button onClick={() => setSubTab('results')} style={{ background: 'none', border: 'none', color: '#0284c7', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                  View Gradebook ({resultsList.length}) →
                </button>
              </div>
              {resultsList.length === 0 ? (
                <div style={{ padding: '1.5rem', textAlign: 'center', color: '#64748b', fontSize: '0.875rem' }}>
                  No student marks entered yet. Authorized staff can log marks from the Staff Desk.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {resultsList.slice(0, 5).map(res => (
                    <div key={res.result_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.65rem 0.85rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <div>
                        <strong style={{ fontSize: '0.875rem', color: '#0f172a' }}>{res.student_name}</strong>
                        <span style={{ fontSize: '0.75rem', color: '#64748b', marginLeft: '0.5rem' }}>({res.permanent_student_id}) · {res.subject_name}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#0f172a' }}>{res.marks_obtained}/{res.maximum_marks}</span>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.15rem 0.4rem', borderRadius: '4px', background: ['A+', 'A'].includes(res.grade) ? '#dcfce7' : '#fef3c7', color: ['A+', 'A'].includes(res.grade) ? '#15803d' : '#b45309' }}>
                          {res.grade}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* VIEW 2: EXAMINATIONS */}
      {!loading && subTab === 'examinations' && (
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.2rem', fontWeight: 700 }}>
                Institution Examination Calendar
              </h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>
                Examinations configured for {institutionName} ({institutionId})
              </p>
            </div>
            <button
              onClick={() => setShowExamModal(true)}
              style={{ padding: '0.5rem 1rem', background: '#1a3a6b', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}
            >
              + Create Examination
            </button>
          </div>

          {examinations.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📋</div>
              <h4>No Examinations Scheduled</h4>
              <p style={{ fontSize: '0.875rem' }}>Schedule an examination or assessment to begin entering subject marks.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Exam Name</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Academic Year</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Exam Date</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Target Standard/Program</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Description</th>
                  </tr>
                </thead>
                <tbody>
                  {examinations.map(ex => (
                    <tr key={ex.exam_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700, color: '#0f172a' }}>{ex.exam_name}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>{ex.academic_year}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>{ex.exam_date || '—'}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>{ex.standard ? `Class ${ex.standard}` : 'All Enrolled'}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', padding: '0.2rem 0.5rem', borderRadius: '4px', background: ex.status === 'completed' ? '#dcfce7' : '#e0f2fe', color: ex.status === 'completed' ? '#15803d' : '#0369a1' }}>
                          {ex.status}
                        </span>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', color: '#64748b', fontSize: '0.8rem' }}>{ex.description || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* VIEW 3: ATTENDANCE */}
      {!loading && subTab === 'attendance' && (
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.2rem', fontWeight: 700 }}>
                Attendance Supervision Ledger
              </h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>
                Daily and subject-wise records entered by institution staff
              </p>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <label style={{ fontSize: '0.8rem', color: '#475467', fontWeight: 600 }}>Filter Date:</label>
              <input
                type="date"
                value={attendanceFilterDate}
                onChange={e => setAttendanceFilterDate(e.target.value)}
                style={{ padding: '0.4rem 0.6rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
              />
              {attendanceFilterDate && (
                <button onClick={() => setAttendanceFilterDate('')} style={{ background: 'none', border: 'none', color: '#b42318', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}>
                  Clear
                </button>
              )}
            </div>
          </div>

          {filteredAttendance.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📅</div>
              <h4>No Attendance Records Found</h4>
              <p style={{ fontSize: '0.875rem' }}>Institution staff have not logged attendance entries for the selected filters.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Date</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Student ID</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Student Name</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Standard / Sec</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Subject / Session</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Remarks</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAttendance.map(att => (
                    <tr key={att.attendance_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>{att.attendance_date}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        <code>{att.permanent_student_id}</code>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#0f172a' }}>{att.student_name}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>Class {att.standard}-{att.section}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>{att.subject_name || 'Daily General'}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
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
                      <td style={{ padding: '0.6rem 0.75rem', color: '#64748b', fontSize: '0.8rem' }}>{att.remarks || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* VIEW 4: RESULTS & GRADEBOOK */}
      {!loading && subTab === 'results' && (
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.2rem', fontWeight: 700 }}>
                Institutional Gradebook & Marks Ledger
              </h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>
                Subject marks, percentage calculations, grades, and audit trail
              </p>
            </div>

            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <select
                value={resultsFilterExam}
                onChange={e => setResultsFilterExam(e.target.value)}
                style={{ padding: '0.4rem 0.6rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
              >
                <option value="">All Examinations</option>
                {distinctExams.map(ex => (
                  <option key={ex} value={ex}>{ex}</option>
                ))}
              </select>

              <select
                value={resultsFilterSubject}
                onChange={e => setResultsFilterSubject(e.target.value)}
                style={{ padding: '0.4rem 0.6rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.85rem' }}
              >
                <option value="">All Subjects</option>
                {distinctSubjects.map(sub => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>

              {(resultsFilterExam || resultsFilterSubject) && (
                <button
                  onClick={() => { setResultsFilterExam(''); setResultsFilterSubject(''); }}
                  style={{ background: 'none', border: 'none', color: '#b42318', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600 }}
                >
                  Reset
                </button>
              )}
            </div>
          </div>

          {filteredResults.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🎯</div>
              <h4>No Evaluation Results Found</h4>
              <p style={{ fontSize: '0.875rem' }}>No student examination scores logged matching current filters.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Student ID</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Student Name</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Class / Section</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Exam</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Subject</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Marks Obtained / Max</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Percentage</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Grade</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Audit Trail</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredResults.map(res => (
                    <tr key={res.result_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        <code>{res.permanent_student_id}</code>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#0f172a' }}>{res.student_name}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>Class {res.standard}-{res.section}</td>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>{res.exam_name}</td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>{res.subject_name}</td>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700, color: '#0f172a' }}>
                        {res.marks_obtained} <span style={{ color: '#64748b', fontWeight: 400 }}>/ {res.maximum_marks}</span>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600 }}>{res.percentage}%</td>
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
                          {res.grade}
                        </span>
                      </td>
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        <button
                          onClick={() => viewAuditHistory(res)}
                          style={{ background: '#f1f5f9', border: '1px solid #d0d5dd', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', cursor: 'pointer', fontWeight: 600, color: '#334155' }}
                        >
                          🔍 View Audits
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* VIEW 5: ANNOUNCEMENTS */}
      {!loading && subTab === 'announcements' && (
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.2rem', fontWeight: 700 }}>
                Official Institution Announcements
              </h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>
                Announcements published for students, parents, and institution community
              </p>
            </div>
            <button
              onClick={() => setShowAnnounceModal(true)}
              style={{ padding: '0.5rem 1rem', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}
            >
              + Post New Announcement
            </button>
          </div>

          {announcements.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', color: '#64748b' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📢</div>
              <h4>No Announcements Published</h4>
              <p style={{ fontSize: '0.875rem' }}>Post an announcement to notify students and parents on their dashboards.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {announcements.map(ann => (
                <div key={ann.announcement_id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <div>
                      <h4 style={{ margin: '0 0 0.25rem 0', fontSize: '1.05rem', color: '#1a3a6b' }}>{ann.title}</h4>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                        📅 Published on: <strong>{ann.published_date}</strong> · Target: <span style={{ textTransform: 'capitalize', fontWeight: 600, color: '#0369a1' }}>{ann.target_audience}</span>
                      </div>
                    </div>
                    <span style={{ fontSize: '0.75rem', background: '#ecfdf5', color: '#065f46', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                      Live on Portal
                    </span>
                  </div>
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.875rem', color: '#334155', lineHeight: 1.5 }}>
                    {ann.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* MODAL 1: SCHEDULE EXAMINATION */}
      {showExamModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000 }}>
          <div className="card" style={{ maxWidth: '550px', width: '100%', padding: '1.75rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
              <h3 style={{ margin: 0, color: '#1a3a6b', fontSize: '1.25rem', fontWeight: 700 }}>Schedule New Examination</h3>
              <button onClick={() => setShowExamModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#64748b' }}>✕</button>
            </div>

            <form onSubmit={handleCreateExam}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Examination Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Midterm Examination 2026, Semester 1 Finals"
                  value={examName}
                  onChange={e => setExamName(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Academic Year *</label>
                  <select
                    value={academicYear}
                    onChange={e => setAcademicYear(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                  >
                    <option value="2025-26">2025-26</option>
                    <option value="2026-27">2026-27</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Scheduled Date *</label>
                  <input
                    type="date"
                    required
                    value={examDate}
                    onChange={e => setExamDate(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Target Standard (Optional)</label>
                <input
                  type="number"
                  min="1"
                  max="12"
                  placeholder="e.g. 5 (Leave blank for all standards / institution-wide)"
                  value={examStandard}
                  onChange={e => setExamStandard(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Description / Guidelines</label>
                <textarea
                  rows={2}
                  placeholder="Optional notes or syllabus scope..."
                  value={examDescription}
                  onChange={e => setExamDescription(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" onClick={() => setShowExamModal(false)} style={{ padding: '0.55rem 1rem', background: '#f1f5f9', border: '1px solid #d0d5dd', borderRadius: '6px', fontSize: '0.85rem', cursor: 'pointer' }}>
                  Cancel
                </button>
                <button type="submit" disabled={submittingExam} style={{ padding: '0.55rem 1.25rem', background: '#1a3a6b', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}>
                  {submittingExam ? 'Scheduling...' : 'Save & Publish Exam'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: POST ANNOUNCEMENT */}
      {showAnnounceModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000 }}>
          <div className="card" style={{ maxWidth: '550px', width: '100%', padding: '1.75rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
              <h3 style={{ margin: 0, color: '#1a3a6b', fontSize: '1.25rem', fontWeight: 700 }}>Publish Official Announcement</h3>
              <button onClick={() => setShowAnnounceModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#64748b' }}>✕</button>
            </div>

            <form onSubmit={handleCreateAnnouncement}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Announcement Title *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Annual Sports Day & Academic Evaluation Schedule"
                  value={announceTitle}
                  onChange={e => setAnnounceTitle(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                />
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Target Audience</label>
                <select
                  value={announceAudience}
                  onChange={e => setAnnounceAudience(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                >
                  <option value="all">Everyone (Students & Parents)</option>
                  <option value="students">Students Only</option>
                  <option value="parents">Parents / Guardians Only</option>
                </select>
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Announcement Body / Details *</label>
                <textarea
                  rows={4}
                  required
                  placeholder="Enter the official announcement text..."
                  value={announceContent}
                  onChange={e => setAnnounceContent(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" onClick={() => setShowAnnounceModal(false)} style={{ padding: '0.55rem 1rem', background: '#f1f5f9', border: '1px solid #d0d5dd', borderRadius: '6px', fontSize: '0.85rem', cursor: 'pointer' }}>
                  Cancel
                </button>
                <button type="submit" disabled={submittingAnnounce} style={{ padding: '0.55rem 1.25rem', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}>
                  {submittingAnnounce ? 'Publishing...' : 'Publish to Portals'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: AUDIT HISTORY MODAL */}
      {selectedResult && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000 }}>
          <div className="card" style={{ maxWidth: '650px', width: '100%', padding: '1.75rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
              <div>
                <span className="badge badge--primary" style={{ marginBottom: '0.25rem' }}>AUDIT TRAIL LOG</span>
                <h3 style={{ margin: '0.25rem 0', color: '#1a3a6b', fontSize: '1.2rem', fontWeight: 700 }}>
                  Mark Correction History
                </h3>
                <p style={{ margin: 0, color: '#64748b', fontSize: '0.85rem' }}>
                  Student: <strong>{selectedResult.student_name}</strong> ({selectedResult.permanent_student_id}) · {selectedResult.subject_name}
                </p>
              </div>
              <button onClick={() => setSelectedResult(null)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#64748b' }}>✕</button>
            </div>

            {loadingAudits ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#64748b' }}>Fetching audit ledger...</p>
              </div>
            ) : auditLogs.length === 0 ? (
              <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
                <p>No corrections logged for this score. This mark is at its original entry value ({selectedResult.marks_obtained}/{selectedResult.maximum_marks}).</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: '400px', overflowY: 'auto' }}>
                {auditLogs.map((log, idx) => (
                  <div key={idx} style={{ padding: '0.85rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#b42318' }}>
                        Marks Corrected: {log.previous_marks} → <span style={{ color: '#027a48' }}>{log.new_marks}</span>
                      </span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{log.modified_at}</span>
                    </div>
                    <div style={{ fontSize: '0.825rem', color: '#334155', marginBottom: '0.25rem' }}>
                      <strong>Reason:</strong> {log.reason_for_change || 'Routine grade verification / correction'}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      Staff ID: <code>{log.modified_by_user_id}</code>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ textAlign: 'right', marginTop: '1.25rem' }}>
              <button onClick={() => setSelectedResult(null)} className="btn btn--secondary btn--sm">
                Close Audit Viewer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
