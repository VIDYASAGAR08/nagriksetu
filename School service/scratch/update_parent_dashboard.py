# -*- coding: utf-8 -*-
import sys

path = r"C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add recordModalTab state
target_state = "  const [recordsError, setRecordsError] = useState('')"
replacement_state = """  const [recordsError, setRecordsError] = useState('')
  const [recordModalTab, setRecordModalTab] = useState('summary')"""

if target_state in content:
    content = content.replace(target_state, replacement_state, 1)
else:
    print("Could not find recordsError state")

# 2. Reset recordModalTab in viewRecords
target_view = """  async function viewRecords(child) {
    setSelectedChild(child)
    setLoadingRecords(true)
    setRecordsError('')
    setChildRecords(null)"""

replacement_view = """  async function viewRecords(child) {
    setSelectedChild(child)
    setLoadingRecords(true)
    setRecordsError('')
    setChildRecords(null)
    setRecordModalTab('summary')"""

if target_view in content:
    content = content.replace(target_view, replacement_view, 1)
else:
    print("Could not find viewRecords function")

# 3. Replace Modal: Child Academic Records
# Find start of modal: {/* Modal: Child Academic Records */}
modal_marker = "{/* Modal: Child Academic Records */}"
modal_end_marker = "{/* Modal: Stage 2 Admission Dossier & Document Upload */}"

start_idx = content.find(modal_marker)
end_idx = content.find(modal_end_marker)

if start_idx == -1 or end_idx == -1:
    print("Could not find modal markers!", start_idx, end_idx)
    sys.exit(1)

new_modal_content = """{/* Modal: Child Academic Records & Student Performance */}
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
        """

new_content = content[:start_idx] + new_modal_content + content[end_idx:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("ParentDashboard.jsx updated successfully!")
