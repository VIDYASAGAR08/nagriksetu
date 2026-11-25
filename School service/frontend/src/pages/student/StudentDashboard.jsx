import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import RequesterPortalView from '../../components/requests/RequesterPortalView.jsx'

export default function StudentDashboard() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  const [loading, setLoading] = useState(true)
  const [profileData, setProfileData] = useState(null)
  const [error, setError] = useState('')
  const [studentTab, setStudentTab] = useState('academic')

  useEffect(() => {
    if (!user) return
    if (user.role !== 'student') {
      setError('Access restricted: This dashboard is reserved strictly for authenticated student accounts.')
      setLoading(false)
      return
    }

    async function fetchProfile() {
      try {
        setLoading(true)
        setError('')
        const data = await apiGet('/student/profile', token)
        setProfileData(data)
      } catch (err) {
        setError(err.message || 'Failed to load student academic profile.')
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [user, token])

  if (!user || user.role !== 'student') {
    return (
      <div className="container" style={{ padding: '3rem 1rem', maxWidth: '700px' }}>
        <Alert type="error" title="Access Denied">
          {error || 'You must be signed in as an authenticated student to view this dashboard.'}
        </Alert>
        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <button
            onClick={() => {
              logout()
              navigate('/login?category=student')
            }}
            className="btn btn--primary"
          >
            Go to Student Login
          </button>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', gap: '1rem' }}>
        <LoadingSpinner size="lg" />
        <p style={{ color: '#475467', fontSize: '0.9375rem', fontWeight: 500 }}>
          Retrieving official academic records from NagrikSetu...
        </p>
      </div>
    )
  }

  const student = profileData?.student || {}
  const school = profileData?.school || {}
  const enrollments = profileData?.enrollments || []
  const guardians = profileData?.guardians || []
  const tests = profileData?.tests || []
  const attendance = profileData?.attendance || {}
  const subjectPerformance = profileData?.subject_performance || []
  const academicProgress = profileData?.academic_progress || []
  const upcomingExams = profileData?.upcoming_examinations || []
  const announcements = profileData?.announcements || []

  const residentialAddress = profileData?.residential_address || 'Not available'
  const attendancePercentage = profileData?.attendance_percentage != null ? `${profileData.attendance_percentage}%` : 'Not available'
  const totalWorkingDays = attendance?.total_working_days > 0 ? `${attendance.total_working_days} Days` : 'Not available'
  const presentDays = attendance?.total_working_days > 0 ? attendance.present_days : 'Not available'
  const absentDays = attendance?.total_working_days > 0 ? attendance.absent_days : 'Not available'

  // Calculate overall academic average
  let overallAvgPct = 'Not available'
  let overallGrade = null
  if (tests.length > 0) {
    const totalScored = tests.reduce((acc, t) => acc + (t.marks_obtained || 0), 0)
    const totalMax = tests.reduce((acc, t) => acc + (t.maximum_marks || 0), 0)
    if (totalMax > 0) {
      const pct = Math.round((totalScored / totalMax) * 1000) / 10
      overallAvgPct = `${pct}%`
      if (pct >= 90) overallGrade = 'A+'
      else if (pct >= 80) overallGrade = 'A'
      else if (pct >= 70) overallGrade = 'B+'
      else if (pct >= 60) overallGrade = 'B'
      else if (pct >= 50) overallGrade = 'C'
      else if (pct >= 35) overallGrade = 'D'
      else overallGrade = 'F'
    }
  }

  function getGradeBadgeStyle(grade) {
    switch (grade) {
      case 'A+':
      case 'A':
        return { background: '#dcfce7', color: '#15803d', border: '1px solid #bbf7d0' }
      case 'B+':
      case 'B':
        return { background: '#eff6ff', color: '#1d4ed8', border: '1px solid #bfdbfe' }
      case 'C':
      case 'D':
        return { background: '#fef9c3', color: '#a16207', border: '1px solid #fef08a' }
      case 'F':
        return { background: '#fee2e2', color: '#b91c1c', border: '1px solid #fecaca' }
      default:
        return { background: '#f1f5f9', color: '#475467', border: '1px solid #e2e8f0' }
    }
  }

  return (
    <div className="student-dashboard" style={{ background: '#f8fafc', minHeight: 'calc(100vh - 200px)', padding: '2rem 1rem' }}>
      <div className="container" style={{ maxWidth: '1140px', margin: '0 auto' }}>
        
        {/* Top Header Banner */}
        <div style={{
          background: 'linear-gradient(135deg, #102B46 0%, #155EEF 100%)',
          color: '#ffffff',
          borderRadius: '12px',
          padding: '2rem',
          marginBottom: '2rem',
          boxShadow: '0 4px 12px rgba(16, 43, 70, 0.15)',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1.5rem'
        }}>
          <div>
            <div style={{
              display: 'inline-block',
              background: 'rgba(255, 255, 255, 0.2)',
              color: '#ffffff',
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '0.25rem 0.65rem',
              borderRadius: '20px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '0.75rem'
            }}>
              Official Student Academic Portal
            </div>
            <h1 style={{ margin: 0, fontSize: '1.875rem', fontWeight: 800 }}>
              Welcome, {student.student_name || user.full_name || 'Student'}
            </h1>
            <p style={{ margin: '0.5rem 0 0 0', opacity: 0.9, fontSize: '0.9375rem' }}>
              Enrolled at <strong>{school.school_name || 'Karnataka Educational Institution'}</strong> ({school.school_id})
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              onClick={() => {
                logout()
                navigate('/')
              }}
              className="btn btn--ghost btn--sm"
              style={{ color: '#ffffff', border: '1px solid rgba(255, 255, 255, 0.4)' }}
            >
              Sign Out
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div style={{
          display: 'flex',
          borderBottom: '2px solid #e2e8f0',
          marginBottom: '1.5rem',
          background: '#ffffff',
          borderRadius: '8px 8px 0 0',
          padding: '0 0.5rem'
        }}>
          <button
            onClick={() => setStudentTab('academic')}
            style={{
              padding: '0.85rem 1.5rem',
              fontWeight: 700,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: studentTab === 'academic' ? '#155EEF' : '#64748B',
              borderBottom: studentTab === 'academic' ? '3px solid #155EEF' : '3px solid transparent',
              marginBottom: '-2px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            <span>📊</span> Academic Profile & Grades
          </button>

          <button
            onClick={() => setStudentTab('requests')}
            style={{
              padding: '0.85rem 1.5rem',
              fontWeight: 700,
              fontSize: '0.9375rem',
              border: 'none',
              background: 'none',
              cursor: 'pointer',
              color: studentTab === 'requests' ? '#155EEF' : '#64748B',
              borderBottom: studentTab === 'requests' ? '3px solid #155EEF' : '3px solid transparent',
              marginBottom: '-2px',
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem'
            }}
          >
            <span>📋</span> My Requests, Complaints & Corrections
          </button>
        </div>

        {error && <Alert type="error" title="Notice" className="mb-4">{error}</Alert>}

        {studentTab === 'requests' ? (
          <RequesterPortalView token={token} userRole="student" studentSelf={student} />
        ) : (
          <div>
            {/* 4 Core Academic KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
          
          {/* Attendance KPI */}
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Attendance Percentage
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: attendancePercentage === 'Not available' ? '#64748b' : '#15803d', marginTop: '0.35rem' }}>
              {attendancePercentage}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.35rem' }}>
              {attendance?.total_working_days > 0 ? (
                <span>Present: <strong>{attendance.present_days}</strong> &bull; Absent: <strong>{attendance.absent_days}</strong> {attendance.leave_days > 0 && `• Leave: ${attendance.leave_days}`}</span>
              ) : 'No official attendance records logged yet'}
            </div>
          </div>

          {/* Working Days KPI */}
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Total Working Days
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: totalWorkingDays === 'Not available' ? '#64748b' : '#102B46', marginTop: '0.35rem' }}>
              {totalWorkingDays}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.35rem' }}>
              Official Academic Session 2026-2027
            </div>
          </div>

          {/* Examinations & Performance KPI */}
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Academic Performance
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: overallAvgPct === 'Not available' ? '#64748b' : '#1d4ed8', marginTop: '0.35rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {overallAvgPct}
              {overallGrade && (
                <span style={{ fontSize: '0.85rem', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', ...getGradeBadgeStyle(overallGrade) }}>
                  Grade {overallGrade}
                </span>
              )}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.35rem' }}>
              {tests.length > 0 ? `${tests.length} assessment(s) evaluated` : 'No evaluation records logged yet'}
            </div>
          </div>

          {/* Upcoming Examinations KPI */}
          <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Upcoming Examinations
            </div>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: upcomingExams.length > 0 ? '#102B46' : '#64748b', marginTop: '0.35rem' }}>
              {upcomingExams.length > 0 ? `${upcomingExams.length} Scheduled` : 'Not available'}
            </div>
            <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.35rem' }}>
              {upcomingExams.length > 0 ? `Next: ${upcomingExams[0].exam_name} (${upcomingExams[0].start_date})` : 'No upcoming schedules published'}
            </div>
          </div>
        </div>

        {/* Section 1: Detailed Attendance Management View */}
        <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: 0 }}>
                Student Attendance Ledger & Monthly Summary
              </h2>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8125rem', color: '#64748b' }}>
                Daily student attendance tracking with present, absent, and approved leave records
              </p>
            </div>
            <span style={{
              background: attendancePercentage === 'Not available' ? '#f1f5f9' : '#dcfce7',
              color: attendancePercentage === 'Not available' ? '#64748b' : '#15803d',
              fontSize: '0.8125rem',
              fontWeight: 700,
              padding: '0.25rem 0.65rem',
              borderRadius: '12px'
            }}>
              Attendance: {attendancePercentage}
            </span>
          </div>

          {attendance?.total_working_days === 0 || !attendance?.total_working_days ? (
            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', color: '#64748b', fontSize: '0.875rem', textAlign: 'center' }}>
              Attendance records: <strong>Not available</strong> &mdash; No attendance records have been officially logged by the institution staff for this student yet.
            </div>
          ) : (
            <div>
              {/* Attendance metrics bar */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem', marginBottom: '1.25rem' }}>
                <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Working Days</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>{attendance.total_working_days}</div>
                </div>
                <div style={{ background: '#f0fdf4', padding: '0.75rem', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                  <div style={{ fontSize: '0.72rem', color: '#166534', fontWeight: 600, textTransform: 'uppercase' }}>Days Present</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#15803d', marginTop: '0.2rem' }}>{attendance.present_days}</div>
                </div>
                <div style={{ background: '#fef2f2', padding: '0.75rem', borderRadius: '6px', border: '1px solid #fecaca' }}>
                  <div style={{ fontSize: '0.72rem', color: '#991b1b', fontWeight: 600, textTransform: 'uppercase' }}>Days Absent</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#b91c1c', marginTop: '0.2rem' }}>{attendance.absent_days}</div>
                </div>
                <div style={{ background: '#fefce8', padding: '0.75rem', borderRadius: '6px', border: '1px solid #fef08a' }}>
                  <div style={{ fontSize: '0.72rem', color: '#854d0e', fontWeight: 600, textTransform: 'uppercase' }}>Approved Leave</div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#a16207', marginTop: '0.2rem' }}>{attendance.leave_days}</div>
                </div>
              </div>

              {/* Monthly attendance breakdown */}
              {attendance.monthly_breakdown?.length > 0 && (
                <div style={{ marginBottom: '1.5rem' }}>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46', marginBottom: '0.5rem' }}>
                    Monthly Attendance Summaries
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
                    {attendance.monthly_breakdown.map((m, idx) => (
                      <div key={idx} style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.75rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontWeight: 700, color: '#102B46', fontSize: '0.85rem' }}>{m.month}</span>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: m.percentage >= 75 ? '#15803d' : '#b91c1c' }}>
                            {m.percentage}%
                          </span>
                        </div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                          Present: {m.present}/{m.total} days &bull; Abs: {m.absent}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent daily records table */}
              {attendance.recent_records?.length > 0 && (
                <div>
                  <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46', marginBottom: '0.5rem' }}>
                    Recent Daily Attendance Logs
                  </h3>
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0', textAlign: 'left' }}>
                          <th style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>Date</th>
                          <th style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>Status</th>
                          <th style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>Subject / Session</th>
                          <th style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>Remarks</th>
                        </tr>
                      </thead>
                      <tbody>
                        {attendance.recent_records.map((r, idx) => (
                          <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                            <td style={{ padding: '0.5rem 0.75rem', fontWeight: 600, color: '#102B46' }}>{r.attendance_date}</td>
                            <td style={{ padding: '0.5rem 0.75rem' }}>
                              <span style={{
                                textTransform: 'capitalize',
                                padding: '0.15rem 0.5rem',
                                borderRadius: '4px',
                                fontSize: '0.75rem',
                                fontWeight: 700,
                                ...(r.status === 'present' ? { background: '#dcfce7', color: '#15803d' } :
                                   r.status === 'leave' ? { background: '#fef9c3', color: '#a16207' } :
                                   { background: '#fee2e2', color: '#b91c1c' })
                              }}>
                                {r.status}
                              </span>
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>{r.subject_name || 'General Daily Session'}</td>
                            <td style={{ padding: '0.5rem 0.75rem', color: '#64748b' }}>{r.remarks || '—'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Section 2: Examination Results & History */}
        <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <div>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: 0 }}>
                Official Examination Results & Evaluations
              </h2>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.8125rem', color: '#64748b' }}>
                Verified subject-wise marks, maximum marks, percentages, and grade calculations
              </p>
            </div>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Total results: <strong>{tests.length > 0 ? tests.length : 'Not available'}</strong>
            </span>
          </div>

          {tests.length === 0 ? (
            <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', color: '#64748b', fontSize: '0.875rem', textAlign: 'center' }}>
              Examination results: <strong>Not available</strong> &mdash; No periodic assessments or board results published yet for this student.
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Exam / Evaluation</th>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Subject</th>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Marks Obtained</th>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Maximum Marks</th>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Percentage</th>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Grade</th>
                    <th style={{ padding: '0.65rem 0.75rem', color: '#475467', fontWeight: 600 }}>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {tests.map((t, idx) => (
                    <tr key={t.result_id || idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '0.65rem 0.75rem', fontWeight: 600, color: '#102B46' }}>{t.exam_name}</td>
                      <td style={{ padding: '0.65rem 0.75rem', color: '#334155' }}>{t.subject_name}</td>
                      <td style={{ padding: '0.65rem 0.75rem', color: '#15803d', fontWeight: 700 }}>{t.marks_obtained}</td>
                      <td style={{ padding: '0.65rem 0.75rem', color: '#64748b' }}>{t.maximum_marks}</td>
                      <td style={{ padding: '0.65rem 0.75rem', fontWeight: 700, color: '#102B46' }}>
                        {t.percentage != null ? `${t.percentage}%` : `${Math.round((t.marks_obtained / t.maximum_marks) * 100)}%`}
                      </td>
                      <td style={{ padding: '0.65rem 0.75rem' }}>
                        <span style={{
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          ...getGradeBadgeStyle(t.grade)
                        }}>
                          Grade {t.grade || '—'}
                        </span>
                      </td>
                      <td style={{ padding: '0.65rem 0.75rem', color: '#64748b', fontSize: '0.8rem' }}>{t.exam_date || t.academic_year || '2026'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Section 3: Subject-Wise Performance & Academic Progress Over Time */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          
          {/* Subject-Wise Performance */}
          <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: '0 0 1rem 0' }}>
              Subject-Wise Performance
            </h2>

            {subjectPerformance.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                Subject performance: <strong>Not available</strong> &mdash; No graded subjects recorded yet.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {subjectPerformance.map((subj, idx) => (
                  <div key={idx} style={{ background: '#f8fafc', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                      <span style={{ fontWeight: 600, color: '#102B46', fontSize: '0.875rem' }}>{subj.subject_name}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '0.15rem 0.45rem', borderRadius: '4px', ...getGradeBadgeStyle(subj.overall_grade) }}>
                        Grade {subj.overall_grade} ({subj.average_percentage}%)
                      </span>
                    </div>
                    {/* Progress bar */}
                    <div style={{ background: '#e2e8f0', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{
                        background: subj.average_percentage >= 75 ? '#16a34a' : subj.average_percentage >= 50 ? '#2563eb' : '#dc2626',
                        width: `${Math.min(100, Math.max(0, subj.average_percentage))}%`,
                        height: '100%'
                      }} />
                    </div>
                    <div style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.25rem' }}>
                      Based on {subj.assessments_count} evaluation(s)
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Academic Progress Over Time */}
          <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: '0 0 1rem 0' }}>
              Academic Progress Over Time
            </h2>

            {academicProgress.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                Academic progress: <strong>Not available</strong> &mdash; Assessments have not been conducted across multiple exam cycles yet.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {academicProgress.map((prog, idx) => (
                  <div key={idx} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.75rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div>
                      <div style={{ fontWeight: 600, color: '#102B46', fontSize: '0.875rem' }}>{prog.exam_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Date: {prog.exam_date} &bull; Subjects: {prog.subjects_evaluated}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 800, color: '#102B46', fontSize: '1rem' }}>{prog.overall_percentage}%</div>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, padding: '0.1rem 0.4rem', borderRadius: '4px', ...getGradeBadgeStyle(prog.grade) }}>
                        Grade {prog.grade}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Section 4: Upcoming Examinations & Institution Announcements */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          
          {/* Upcoming Examinations Card */}
          <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: '0 0 1rem 0' }}>
              Upcoming Scheduled Examinations
            </h2>

            {upcomingExams.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                Upcoming examinations: <strong>Not available</strong> &mdash; No scheduled examination notifications published for your class.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {upcomingExams.map((ex, idx) => (
                  <div key={idx} style={{ background: '#f8fafc', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <strong style={{ color: '#102B46', fontSize: '0.9rem' }}>{ex.exam_name}</strong>
                      <span style={{ background: '#eff6ff', color: '#1d4ed8', fontSize: '0.72rem', fontWeight: 700, padding: '0.15rem 0.5rem', borderRadius: '10px' }}>
                        {ex.status.toUpperCase()}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.25rem' }}>
                      Start Date: <strong>{ex.start_date}</strong> {ex.end_date && `to ${ex.end_date}`}
                    </div>
                    {ex.description && (
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>
                        {ex.description}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Institution Announcements */}
          <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: '0 0 1rem 0' }}>
              Official Institution Announcements
            </h2>

            {announcements.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
                Institution announcements: <strong>Not available</strong> &mdash; No active circulars or announcements posted by the administration.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {announcements.map((a, idx) => (
                  <div key={idx} style={{ background: '#f8fafc', padding: '0.75rem 1rem', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                    <div style={{ fontWeight: 700, color: '#102B46', fontSize: '0.875rem' }}>{a.title}</div>
                    <div style={{ fontSize: '0.78rem', color: '#475467', marginTop: '0.25rem', lineHeight: 1.4 }}>{a.content}</div>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '0.35rem' }}>
                      Published: {a.published_date}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Section 5: Student Identity & Enrolled Institution Details */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          
          {/* Identity & Verification Card */}
          <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: '0 0 1rem 0' }}>
              Student Identity & Verification
            </h2>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', fontSize: '0.875rem' }}>
              <div>
                <span style={{ color: '#64748b', fontSize: '0.78rem', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>
                  Full Name
                </span>
                <strong style={{ color: '#102B46', fontSize: '0.9375rem' }}>
                  {student.student_name || user.full_name || 'N/A'}
                </strong>
              </div>

              <div>
                <span style={{ color: '#64748b', fontSize: '0.78rem', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>
                  Permanent Student ID
                </span>
                <strong style={{ color: '#102B46', fontSize: '0.9375rem', fontFamily: 'monospace' }}>
                  {student.student_id || 'N/A'}
                </strong>
              </div>

              <div>
                <span style={{ color: '#64748b', fontSize: '0.78rem', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>
                  Current Standard / Level
                </span>
                <strong style={{ color: '#102B46' }}>
                  Standard {student.standard || 'N/A'} (Section {student.section || 'N/A'})
                </strong>
              </div>

              <div>
                <span style={{ color: '#64748b', fontSize: '0.78rem', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>
                  Enrolment Status
                </span>
                <span style={{ color: '#16a34a', fontWeight: 600, textTransform: 'capitalize' }}>
                  {student.enrollment_status || 'Active'}
                </span>
              </div>

              <div>
                <span style={{ color: '#64748b', fontSize: '0.78rem', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>
                  Admission Year / Date
                </span>
                <span style={{ color: '#334155' }}>
                  {student.admission_date || 'Enrolled 2026'}
                </span>
              </div>

              <div>
                <span style={{ color: '#64748b', fontSize: '0.78rem', display: 'block', textTransform: 'uppercase', fontWeight: 600 }}>
                  Residential Address
                </span>
                <span style={{ color: '#334155', fontWeight: 500 }}>
                  {residentialAddress}
                </span>
              </div>
            </div>
          </div>

          {/* Enrolled Institution Card */}
          <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: '0 0 1rem 0' }}>
              Enrolled Institution
            </h2>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', marginBottom: '0.25rem' }}>
                {school.school_name || 'Karnataka State Institution'}
              </div>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
                Institution Code: <strong>{school.school_id}</strong> &bull; Category: <strong>{(school.category || 'Government Recognized').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')}</strong>
              </div>
              <div style={{ fontSize: '0.85rem', color: '#475467', marginTop: '0.5rem', lineHeight: 1.4 }}>
                {school.address || 'Address not listed'}, {school.district || 'Karnataka'}, {school.state || 'Karnataka'}
              </div>
            </div>

            <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px dashed #e2e8f0' }}>
              <Link
                to={`/schools/${school.school_id}`}
                className="btn btn--secondary btn--sm"
                style={{ width: '100%', textAlign: 'center', display: 'block', background: '#f1f5f9', borderColor: '#cbd5e1', color: '#102B46' }}
              >
                View Complete Institution Profile & Programmes
              </Link>
            </div>
          </div>
        </div>

        {/* Verified Guardian Information Card */}
        <div className="card" style={{ background: '#ffffff', borderRadius: '10px', padding: '1.5rem', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#102B46', margin: 0 }}>
              Verified Parent / Legal Guardian Information
            </h2>
            <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
              Verified Guardians: <strong>{guardians.length}</strong>
            </span>
          </div>

          {guardians.length === 0 ? (
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', color: '#64748b', fontSize: '0.875rem' }}>
              No verified legal guardian is currently linked to this student record. Parents can request linking via the Parent Portal.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
              {guardians.map((g, idx) => (
                <div key={idx} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                  <div style={{ fontWeight: 700, color: '#102B46', fontSize: '0.9375rem' }}>
                    {g.full_name}
                  </div>
                  <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600, marginTop: '0.2rem' }}>
                    Relationship: {g.relationship || 'Guardian'} (Verified)
                  </div>
                  {g.phone && (
                    <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.35rem' }}>
                      Contact Phone: {g.phone}
                    </div>
                  )}
                  {g.email && (
                    <div style={{ fontSize: '0.8rem', color: '#475467', marginTop: '0.15rem' }}>
                      Email: {g.email}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Privacy & Safe Contacts Info */}
        <div style={{
          background: '#eff6ff',
          border: '1px solid #bfdbfe',
          borderRadius: '10px',
          padding: '1.25rem 1.5rem',
          display: 'flex',
          alignItems: 'flex-start',
          gap: '1rem'
        }}>
          <div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 700, color: '#1e40af', marginBottom: '0.25rem' }}>
              Student Privacy & Academic Integrity Notice
            </div>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#1e3a8a', lineHeight: 1.5 }}>
              Your student dashboard strictly displays verified academic records linked exclusively to your Permanent Student ID. Cross-student records are fully isolated. Official attendance and examination records can only be authorized by institution faculty and cannot be modified by students.
            </p>
          </div>
        </div>
          </div>
        )}

      </div>
    </div>
  )
}
