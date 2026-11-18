import React, { useState, useEffect } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'

export default function StaffAcademicDesk({ token, schoolId, institutionName }) {
  const [activeTab, setActiveTab] = useState('attendance') // 'attendance' | 'marks' | 'exams'

  // Common Notification State
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // ---------------- ATTENDANCE ENTRY STATE ----------------
  const [attStandard, setAttStandard] = useState(5)
  const [attSection, setAttSection] = useState('A')
  const [attDate, setAttDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [attSubject, setAttSubject] = useState('')
  const [loadingAttRoster, setLoadingAttRoster] = useState(false)
  const [attRoster, setAttRoster] = useState([])
  const [attStatusMap, setAttStatusMap] = useState({}) // { [permanent_student_id]: 'present' | 'absent' | 'leave' }
  const [attRemarksMap, setAttRemarksMap] = useState({}) // { [permanent_student_id]: string }
  const [submittingAtt, setSubmittingAtt] = useState(false)

  // ---------------- MARKS ENTRY STATE ----------------
  const [marksExamId, setMarksExamId] = useState('')
  const [marksExamName, setMarksExamName] = useState('')
  const [marksSubject, setMarksSubject] = useState('Mathematics')
  const [marksMax, setMarksMax] = useState(100)
  const [marksStandard, setMarksStandard] = useState(5)
  const [marksSection, setMarksSection] = useState('A')
  const [loadingMarksRoster, setLoadingMarksRoster] = useState(false)
  const [marksRoster, setMarksRoster] = useState([])
  const [studentMarksMap, setStudentMarksMap] = useState({}) // { [psid]: number | '' }
  const [existingMarksMap, setExistingMarksMap] = useState({}) // { [psid]: existing result obj }
  const [changeReasonsMap, setChangeReasonsMap] = useState({}) // { [psid]: string }
  const [submittingMarks, setSubmittingMarks] = useState(false)

  // ---------------- EXAMINATIONS STATE ----------------
  const [examinations, setExaminations] = useState([])
  const [loadingExams, setLoadingExams] = useState(false)
  const [showExamModal, setShowExamModal] = useState(false)
  const [newExamName, setNewExamName] = useState('')
  const [newExamYear, setNewExamYear] = useState('2025-26')
  const [newExamDate, setNewExamDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [newExamStandard, setNewExamStandard] = useState('')
  const [newExamDesc, setNewExamDesc] = useState('')
  const [submittingNewExam, setSubmittingNewExam] = useState(false)

  // Load Examinations for Institution
  async function loadExaminations() {
    if (!token || !schoolId) return
    setLoadingExams(true)
    try {
      const data = await apiGet(`/academic/examinations?institution_id=${schoolId}`, token)
      const list = Array.isArray(data) ? data : (data?.examinations || [])
      setExaminations(list)
      if (list.length > 0 && !marksExamName) {
        setMarksExamId(list[0].exam_id)
        setMarksExamName(list[0].exam_name)
      }
    } catch (err) {
      console.error('Failed to load examinations:', err)
    } finally {
      setLoadingExams(false)
    }
  }

  useEffect(() => {
    loadExaminations()
  }, [token, schoolId])

  // Helper for grade calculation
  function calculatePreviewGrade(marks, maxMarks) {
    if (marks === '' || marks == null || isNaN(marks)) return '—'
    const m = parseFloat(marks)
    const mm = parseFloat(maxMarks) || 100
    if (mm <= 0) return '—'
    const pct = (m / mm) * 100
    if (pct >= 90) return 'A+'
    if (pct >= 80) return 'A'
    if (pct >= 70) return 'B+'
    if (pct >= 60) return 'B'
    if (pct >= 50) return 'C'
    if (pct >= 35) return 'D'
    return 'F'
  }

  // ---------------- 1. ATTENDANCE FUNCTIONS ----------------
  async function loadAttendanceRoster() {
    if (!token || !schoolId) return
    setLoadingAttRoster(true)
    setError('')
    setSuccess('')
    setAttRoster([])
    setAttStatusMap({})
    setAttRemarksMap({})

    try {
      const data = await apiGet(`/schools/${schoolId}/students?standard=${attStandard}&section=${attSection}&limit=100`, token)
      const list = Array.isArray(data) ? data : (data?.students || [])
      setAttRoster(list)

      // Initialize default statuses as 'present'
      const initialStatus = {}
      list.forEach(st => {
        initialStatus[st.permanent_student_id] = 'present'
      })
      setAttStatusMap(initialStatus)

      if (list.length === 0) {
        setError(`No active students found in Class ${attStandard}-${attSection} for ${schoolId}.`)
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch student roster for attendance.')
    } finally {
      setLoadingAttRoster(false)
    }
  }

  function markAllAttendance(status) {
    const updated = {}
    attRoster.forEach(st => {
      updated[st.permanent_student_id] = status
    })
    setAttStatusMap(updated)
  }

  async function handleBatchAttendanceSubmit(e) {
    e.preventDefault()
    if (attRoster.length === 0) {
      setError('Please load student roster before saving attendance.')
      return
    }

    const records = attRoster.map(st => ({
      permanent_student_id: st.permanent_student_id,
      status: attStatusMap[st.permanent_student_id] || 'present',
      remarks: attRemarksMap[st.permanent_student_id]?.trim() || undefined,
    }))

    setSubmittingAtt(true)
    setError('')
    setSuccess('')
    try {
      const payload = {
        institution_id: schoolId,
        attendance_date: attDate,
        subject_name: attSubject.trim() || undefined,
        records: records,
      }

      const res = await apiPost('/academic/attendance/batch', payload, token)
      setSuccess(`✅ Successfully recorded attendance for ${res.records_count} students on ${attDate}. Summary: ${res.summary?.present || 0} Present, ${res.summary?.absent || 0} Absent, ${res.summary?.leave || 0} Leave.`)
    } catch (err) {
      setError(err.message || 'Failed to submit batch attendance.')
    } finally {
      setSubmittingAtt(false)
    }
  }

  // ---------------- 2. MARKS ENTRY FUNCTIONS ----------------
  async function loadMarksRoster() {
    if (!token || !schoolId) return
    if (!marksExamName) {
      setError('Please select or create an examination first.')
      return
    }
    setLoadingMarksRoster(true)
    setError('')
    setSuccess('')
    setMarksRoster([])
    setStudentMarksMap({})
    setExistingMarksMap({})
    setChangeReasonsMap({})

    try {
      // 1. Load students
      const data = await apiGet(`/schools/${schoolId}/students?standard=${marksStandard}&section=${marksSection}&limit=100`, token)
      const list = Array.isArray(data) ? data : (data?.students || [])
      setMarksRoster(list)

      // 2. Load existing results for this exam & subject
      const existingRes = await apiGet(`/academic/results?institution_id=${schoolId}&exam_name=${encodeURIComponent(marksExamName)}&subject_name=${encodeURIComponent(marksSubject)}&standard=${marksStandard}`, token).catch(() => [])
      const existingArr = Array.isArray(existingRes) ? existingRes : (existingRes?.results || [])
      const existingMap = {}
      const initScores = {}
      existingArr.forEach(r => {
        existingMap[r.permanent_student_id] = r
        initScores[r.permanent_student_id] = r.marks_obtained
      })
      setExistingMarksMap(existingMap)
      setStudentMarksMap(initScores)

      if (list.length === 0) {
        setError(`No active students found in Class ${marksStandard}-${marksSection}.`)
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch student roster for marks entry.')
    } finally {
      setLoadingMarksRoster(false)
    }
  }

  async function handleBatchMarksSubmit(e) {
    e.preventDefault()
    if (marksRoster.length === 0) {
      setError('Please load student roster before saving marks.')
      return
    }

    const records = []
    for (const st of marksRoster) {
      const val = studentMarksMap[st.permanent_student_id]
      if (val !== '' && val != null && !isNaN(val)) {
        const score = parseFloat(val)
        if (score < 0 || score > marksMax) {
          setError(`Invalid score for ${st.student_name}: marks must be between 0 and ${marksMax}.`)
          return
        }
        records.push({
          permanent_student_id: st.permanent_student_id,
          marks_obtained: score,
          reason_for_change: changeReasonsMap[st.permanent_student_id]?.trim() || undefined,
        })
      }
    }

    if (records.length === 0) {
      setError('Please enter marks for at least one student before saving.')
      return
    }

    setSubmittingMarks(true)
    setError('')
    setSuccess('')
    try {
      const payload = {
        institution_id: schoolId,
        exam_id: marksExamId || undefined,
        exam_name: marksExamName,
        academic_year: '2025-26',
        subject_name: marksSubject,
        maximum_marks: parseFloat(marksMax),
        records: records,
      }

      const res = await apiPost('/academic/results/batch', payload, token)
      setSuccess(`✅ Successfully recorded marks for ${res.processed_count} students in ${marksSubject} (${marksExamName}). Calculated grades and logged audit tracking.`)
      // Refresh existing marks map
      loadMarksRoster()
    } catch (err) {
      setError(err.message || 'Failed to submit marks.')
    } finally {
      setSubmittingMarks(false)
    }
  }

  // ---------------- 3. EXAM CREATION FUNCTION ----------------
  async function handleCreateNewExam(e) {
    e.preventDefault()
    if (!newExamName.trim()) {
      setError('Please provide an examination name.')
      return
    }
    setSubmittingNewExam(true)
    setError('')
    setSuccess('')
    try {
      await apiPost('/academic/examinations', {
        institution_id: schoolId,
        exam_name: newExamName.trim(),
        academic_year: newExamYear,
        exam_date: newExamDate,
        standard: newExamStandard ? parseInt(newExamStandard, 10) : undefined,
        description: newExamDesc.trim() || undefined,
      }, token)

      setSuccess(`Examination "${newExamName}" created and added to academic schedule.`)
      setShowExamModal(false)
      setNewExamName('')
      setNewExamDesc('')
      loadExaminations()
    } catch (err) {
      setError(err.message || 'Failed to create examination.')
    } finally {
      setSubmittingNewExam(false)
    }
  }

  return (
    <div style={{ marginTop: '1rem' }}>
      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '2px solid #e2e8f0', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={() => { setActiveTab('attendance'); setError(''); setSuccess(''); }}
          style={{
            padding: '0.65rem 1.25rem',
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'attendance' ? 700 : 500,
            fontSize: '0.9375rem',
            color: activeTab === 'attendance' ? '#1a3a6b' : '#64748b',
            borderBottom: activeTab === 'attendance' ? '3px solid #1a3a6b' : '3px solid transparent',
            marginBottom: '-2px'
          }}
        >
          📅 Daily Attendance Entry
        </button>

        <button
          type="button"
          onClick={() => { setActiveTab('marks'); setError(''); setSuccess(''); }}
          style={{
            padding: '0.65rem 1.25rem',
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'marks' ? 700 : 500,
            fontSize: '0.9375rem',
            color: activeTab === 'marks' ? '#1a3a6b' : '#64748b',
            borderBottom: activeTab === 'marks' ? '3px solid #1a3a6b' : '3px solid transparent',
            marginBottom: '-2px'
          }}
        >
          📝 Examination & Marks Entry
        </button>

        <button
          type="button"
          onClick={() => { setActiveTab('exams'); setError(''); setSuccess(''); }}
          style={{
            padding: '0.65rem 1.25rem',
            border: 'none',
            background: 'none',
            cursor: 'pointer',
            fontWeight: activeTab === 'exams' ? 700 : 500,
            fontSize: '0.9375rem',
            color: activeTab === 'exams' ? '#1a3a6b' : '#64748b',
            borderBottom: activeTab === 'exams' ? '3px solid #1a3a6b' : '3px solid transparent',
            marginBottom: '-2px'
          }}
        >
          📋 Manage Examinations ({examinations.length})
        </button>
      </div>

      {error && <Alert type="error" title="Notice" className="mb-4">{error}</Alert>}
      {success && <Alert type="success" title="Success" className="mb-4">{success}</Alert>}

      {/* ======================================================== */}
      {/* 1. ATTENDANCE ENTRY DESK */}
      {/* ======================================================== */}
      {activeTab === 'attendance' && (
        <div className="card" style={{ padding: '1.75rem', background: '#ffffff', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
          <div style={{ marginBottom: '1.25rem' }}>
            <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.25rem', fontWeight: 700 }}>
              Daily & Subject Attendance Entry Desk
            </h3>
            <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>
              Log instructional attendance for students enrolled in {institutionName} ({schoolId}).
            </p>
          </div>

          {/* Filter / Selector Bar */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.5rem', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Standard / Class *</label>
              <select
                value={attStandard}
                onChange={e => setAttStandard(parseInt(e.target.value, 10))}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              >
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(st => (
                  <option key={st} value={st}>Class {st}</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Section *</label>
              <select
                value={attSection}
                onChange={e => setAttSection(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              >
                <option value="A">Section A</option>
                <option value="B">Section B</option>
                <option value="C">Section C</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Attendance Date *</label>
              <input
                type="date"
                required
                value={attDate}
                onChange={e => setAttDate(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Subject / Session (Optional)</label>
              <input
                type="text"
                placeholder="e.g. Mathematics, Physics, Morning"
                value={attSubject}
                onChange={e => setAttSubject(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              />
            </div>

            <div>
              <button
                type="button"
                onClick={loadAttendanceRoster}
                disabled={loadingAttRoster}
                style={{ width: '100%', padding: '0.6rem', background: '#1a3a6b', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}
              >
                {loadingAttRoster ? 'Loading Class...' : 'Load Class Roster →'}
              </button>
            </div>
          </div>

          {/* Roster & Attendance Form */}
          {attRoster.length > 0 && (
            <form onSubmit={handleBatchAttendanceSubmit}>
              {/* Quick Actions Bar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.9rem', color: '#334155' }}>
                  Enrolled Students: <strong>{attRoster.length}</strong> in Class {attStandard}-{attSection}
                </div>

                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    type="button"
                    onClick={() => markAllAttendance('present')}
                    style={{ padding: '0.35rem 0.75rem', background: '#dcfce7', color: '#15803d', border: '1px solid #86efac', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
                  >
                    ✓ Mark All Present
                  </button>
                  <button
                    type="button"
                    onClick={() => markAllAttendance('absent')}
                    style={{ padding: '0.35rem 0.75rem', background: '#fee2e2', color: '#b91c1c', border: '1px solid #fca5a5', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer' }}
                  >
                    ✕ Mark All Absent
                  </button>
                </div>
              </div>

              {/* Roster Table */}
              <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '6px', marginBottom: '1.5rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                      <th style={{ padding: '0.6rem 0.75rem' }}>#</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Student ID</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Student Name</th>
                      <th style={{ padding: '0.6rem 0.75rem', textAlign: 'center' }}>Attendance Status</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Remarks</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attRoster.map((st, idx) => {
                      const curStatus = attStatusMap[st.permanent_student_id] || 'present'
                      return (
                        <tr key={st.permanent_student_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '0.6rem 0.75rem', color: '#64748b' }}>{idx + 1}</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <code>{st.permanent_student_id}</code>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#0f172a' }}>
                            {st.student_name}
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', textAlign: 'center' }}>
                            <div style={{ display: 'inline-flex', gap: '0.35rem' }}>
                              <button
                                type="button"
                                onClick={() => setAttStatusMap(prev => ({ ...prev, [st.permanent_student_id]: 'present' }))}
                                style={{
                                  padding: '0.25rem 0.6rem',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  cursor: 'pointer',
                                  border: '1px solid',
                                  background: curStatus === 'present' ? '#15803d' : '#f8fafc',
                                  color: curStatus === 'present' ? '#ffffff' : '#64748b',
                                  borderColor: curStatus === 'present' ? '#15803d' : '#d0d5dd',
                                }}
                              >
                                Present
                              </button>
                              <button
                                type="button"
                                onClick={() => setAttStatusMap(prev => ({ ...prev, [st.permanent_student_id]: 'absent' }))}
                                style={{
                                  padding: '0.25rem 0.6rem',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  cursor: 'pointer',
                                  border: '1px solid',
                                  background: curStatus === 'absent' ? '#b91c1c' : '#f8fafc',
                                  color: curStatus === 'absent' ? '#ffffff' : '#64748b',
                                  borderColor: curStatus === 'absent' ? '#b91c1c' : '#d0d5dd',
                                }}
                              >
                                Absent
                              </button>
                              <button
                                type="button"
                                onClick={() => setAttStatusMap(prev => ({ ...prev, [st.permanent_student_id]: 'leave' }))}
                                style={{
                                  padding: '0.25rem 0.6rem',
                                  borderRadius: '4px',
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  cursor: 'pointer',
                                  border: '1px solid',
                                  background: curStatus === 'leave' ? '#b45309' : '#f8fafc',
                                  color: curStatus === 'leave' ? '#ffffff' : '#64748b',
                                  borderColor: curStatus === 'leave' ? '#b45309' : '#d0d5dd',
                                }}
                              >
                                Leave
                              </button>
                            </div>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <input
                              type="text"
                              placeholder="e.g. Medical leave, Late arrival"
                              value={attRemarksMap[st.permanent_student_id] || ''}
                              onChange={e => setAttRemarksMap(prev => ({ ...prev, [st.permanent_student_id]: e.target.value }))}
                              style={{ width: '100%', padding: '0.35rem 0.5rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.8rem' }}
                            />
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              {/* Submit Button */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="submit"
                  disabled={submittingAtt}
                  style={{ padding: '0.65rem 1.5rem', background: '#059669', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer' }}
                >
                  {submittingAtt ? 'Saving Attendance...' : `Save Attendance for ${attRoster.length} Students →`}
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* 2. MARKS ENTRY DESK */}
      {/* ======================================================== */}
      {activeTab === 'marks' && (
        <div className="card" style={{ padding: '1.75rem', background: '#ffffff', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
          <div style={{ marginBottom: '1.25rem' }}>
            <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.25rem', fontWeight: 700 }}>
              Subject Marks Entry & Gradebook Desk
            </h3>
            <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>
              Record examination marks. Grades are automatically computed according to the Karnataka state grading scale. Any mark corrections are logged to the permanent audit trail.
            </p>
          </div>

          {/* Config Bar */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.5rem', alignItems: 'flex-end' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Examination *</label>
              <select
                value={marksExamName}
                onChange={e => {
                  setMarksExamName(e.target.value)
                  const sel = examinations.find(x => x.exam_name === e.target.value)
                  if (sel) setMarksExamId(sel.exam_id)
                }}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              >
                {examinations.length === 0 && <option value="">No exams scheduled</option>}
                {examinations.map(ex => (
                  <option key={ex.exam_id} value={ex.exam_name}>{ex.exam_name} ({ex.academic_year})</option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Subject Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Kannada, English, Mathematics"
                value={marksSubject}
                onChange={e => setMarksSubject(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Max Marks *</label>
              <input
                type="number"
                min="1"
                required
                value={marksMax}
                onChange={e => setMarksMax(e.target.value)}
                style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.35rem' }}>Standard & Section *</label>
              <div style={{ display: 'flex', gap: '0.25rem' }}>
                <select
                  value={marksStandard}
                  onChange={e => setMarksStandard(parseInt(e.target.value, 10))}
                  style={{ width: '60%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(st => (
                    <option key={st} value={st}>Class {st}</option>
                  ))}
                </select>
                <select
                  value={marksSection}
                  onChange={e => setMarksSection(e.target.value)}
                  style={{ width: '40%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                >
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                </select>
              </div>
            </div>

            <div>
              <button
                type="button"
                onClick={loadMarksRoster}
                disabled={loadingMarksRoster}
                style={{ width: '100%', padding: '0.6rem', background: '#1a3a6b', color: '#fff', border: 'none', borderRadius: '4px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}
              >
                {loadingMarksRoster ? 'Loading...' : 'Load Students →'}
              </button>
            </div>
          </div>

          {/* Marks Table */}
          {marksRoster.length > 0 && (
            <form onSubmit={handleBatchMarksSubmit}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
                <div style={{ fontSize: '0.9rem', color: '#334155' }}>
                  Entering marks for <strong>{marksSubject}</strong> ({marksExamName}) · Max Marks: <strong>{marksMax}</strong>
                </div>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Karnataka Scheme: A+ (≥90%), A (≥80%), B+ (≥70%), B (≥60%), C (≥50%), D (≥35%), F (&lt;35%)
                </div>
              </div>

              <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '6px', marginBottom: '1.5rem' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                      <th style={{ padding: '0.6rem 0.75rem' }}>#</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Student ID</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Student Name</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Marks Obtained</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Calculated Grade</th>
                      <th style={{ padding: '0.6rem 0.75rem' }}>Existing / Audit Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {marksRoster.map((st, idx) => {
                      const scoreVal = studentMarksMap[st.permanent_student_id]
                      const existing = existingMarksMap[st.permanent_student_id]
                      const grade = calculatePreviewGrade(scoreVal, marksMax)
                      const isModified = existing && scoreVal != null && scoreVal !== '' && parseFloat(scoreVal) !== parseFloat(existing.marks_obtained)

                      return (
                        <tr key={st.permanent_student_id} style={{ borderBottom: '1px solid #f1f5f9', background: isModified ? '#fffbeb' : '#ffffff' }}>
                          <td style={{ padding: '0.6rem 0.75rem', color: '#64748b' }}>{idx + 1}</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <code>{st.permanent_student_id}</code>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', fontWeight: 600, color: '#0f172a' }}>
                            {st.student_name}
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                              <input
                                type="number"
                                min="0"
                                max={marksMax}
                                step="0.5"
                                placeholder={`0-${marksMax}`}
                                value={scoreVal ?? ''}
                                onChange={e => {
                                  const v = e.target.value
                                  setStudentMarksMap(prev => ({ ...prev, [st.permanent_student_id]: v }))
                                }}
                                style={{ width: '90px', padding: '0.35rem 0.5rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem', fontWeight: 700 }}
                              />
                              <span style={{ color: '#64748b', fontSize: '0.8rem' }}>/ {marksMax}</span>
                            </div>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <span style={{
                              display: 'inline-block',
                              padding: '0.15rem 0.5rem',
                              borderRadius: '4px',
                              fontSize: '0.75rem',
                              fontWeight: 800,
                              background: ['A+', 'A'].includes(grade) ? '#dcfce7' : (['B+', 'B'].includes(grade) ? '#dbeafe' : (grade === 'F' ? '#fee2e2' : '#fef3c7')),
                              color: ['A+', 'A'].includes(grade) ? '#15803d' : (['B+', 'B'].includes(grade) ? '#1d4ed8' : (grade === 'F' ? '#b91c1c' : '#b45309'))
                            }}>
                              {grade}
                            </span>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            {isModified ? (
                              <div>
                                <span style={{ fontSize: '0.75rem', color: '#b45309', fontWeight: 600 }}>
                                  Previously: {existing.marks_obtained}/{existing.maximum_marks} (Correction)
                                </span>
                                <input
                                  type="text"
                                  placeholder="Reason for change (Required for Audit Trail)"
                                  value={changeReasonsMap[st.permanent_student_id] || ''}
                                  onChange={e => setChangeReasonsMap(prev => ({ ...prev, [st.permanent_student_id]: e.target.value }))}
                                  style={{ width: '100%', marginTop: '0.2rem', padding: '0.25rem 0.4rem', border: '1px solid #f59e0b', borderRadius: '4px', fontSize: '0.75rem' }}
                                />
                              </div>
                            ) : existing ? (
                              <span style={{ fontSize: '0.75rem', color: '#059669', fontWeight: 600 }}>
                                Saved: {existing.marks_obtained}/{existing.maximum_marks} ({existing.grade})
                              </span>
                            ) : (
                              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>New entry</span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="submit"
                  disabled={submittingMarks}
                  style={{ padding: '0.65rem 1.5rem', background: '#0284c7', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer' }}
                >
                  {submittingMarks ? 'Recording Gradebook...' : `Save & Publish Marks for ${marksRoster.length} Students →`}
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* 3. EXAMINATIONS CALENDAR */}
      {/* ======================================================== */}
      {activeTab === 'exams' && (
        <div className="card" style={{ padding: '1.75rem', background: '#ffffff', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ margin: '0 0 0.25rem 0', color: '#1a3a6b', fontSize: '1.25rem', fontWeight: 700 }}>
                Institution Examination Calendar
              </h3>
              <p style={{ margin: 0, color: '#64748b', fontSize: '0.875rem' }}>
                Schedule examinations, assessments, and unit tests to enable marks entry.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setShowExamModal(true)}
              style={{ padding: '0.55rem 1rem', background: '#1a3a6b', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.875rem', cursor: 'pointer' }}
            >
              + Create Examination
            </button>
          </div>

          {loadingExams ? (
            <div style={{ textAlign: 'center', padding: '2rem' }}>
              <LoadingSpinner />
              <p style={{ marginTop: '0.5rem', color: '#64748b' }}>Loading examinations...</p>
            </div>
          ) : examinations.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#64748b' }}>
              <p>No examinations scheduled yet. Click "+ Create Examination" to get started.</p>
            </div>
          ) : (
            <div style={{ overflowX: 'auto', border: '1px solid #e2e8f0', borderRadius: '6px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Exam Name</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Academic Year</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Exam Date</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Target Class</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                    <th style={{ padding: '0.6rem 0.75rem' }}>Action</th>
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
                      <td style={{ padding: '0.6rem 0.75rem' }}>
                        <button
                          type="button"
                          onClick={() => {
                            setMarksExamId(ex.exam_id)
                            setMarksExamName(ex.exam_name)
                            if (ex.standard) setMarksStandard(ex.standard)
                            setActiveTab('marks')
                          }}
                          style={{ padding: '0.25rem 0.6rem', background: '#0284c7', color: '#fff', border: 'none', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
                        >
                          Enter Marks →
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

      {/* MODAL: CREATE EXAMINATION */}
      {showExamModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 1000 }}>
          <div className="card" style={{ maxWidth: '520px', width: '100%', padding: '1.75rem', background: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
              <h3 style={{ margin: 0, color: '#1a3a6b', fontSize: '1.2rem', fontWeight: 700 }}>Schedule Examination</h3>
              <button onClick={() => setShowExamModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#64748b' }}>✕</button>
            </div>

            <form onSubmit={handleCreateNewExam}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Exam Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Unit Test 1, Midterm Examination 2026"
                  value={newExamName}
                  onChange={e => setNewExamName(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Academic Year</label>
                  <select
                    value={newExamYear}
                    onChange={e => setNewExamYear(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                  >
                    <option value="2025-26">2025-26</option>
                    <option value="2026-27">2026-27</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Date</label>
                  <input
                    type="date"
                    required
                    value={newExamDate}
                    onChange={e => setNewExamDate(e.target.value)}
                    style={{ width: '100%', padding: '0.55rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                  />
                </div>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Class / Standard (Optional)</label>
                <input
                  type="number"
                  min="1"
                  max="12"
                  placeholder="Leave empty for all classes"
                  value={newExamStandard}
                  onChange={e => setNewExamStandard(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#1e293b', marginBottom: '0.25rem' }}>Description</label>
                <textarea
                  rows={2}
                  placeholder="Notes or instructions..."
                  value={newExamDesc}
                  onChange={e => setNewExamDesc(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', fontSize: '0.875rem', resize: 'vertical' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                <button type="button" onClick={() => setShowExamModal(false)} style={{ padding: '0.55rem 1rem', background: '#f1f5f9', border: '1px solid #d0d5dd', borderRadius: '6px', fontSize: '0.85rem', cursor: 'pointer' }}>
                  Cancel
                </button>
                <button type="submit" disabled={submittingNewExam} style={{ padding: '0.55rem 1.25rem', background: '#1a3a6b', color: '#fff', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}>
                  {submittingNewExam ? 'Saving...' : 'Save Examination'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
