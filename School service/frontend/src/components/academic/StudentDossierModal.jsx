import React, { useState, useEffect } from 'react';
import { apiGet } from '../../utils/api.js';

export default function StudentDossierModal({ isOpen, onClose, studentId, studentName }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && studentId) {
      loadReport(studentId);
    } else {
      setReport(null);
      setError('');
    }
  }, [isOpen, studentId]);

  async function loadReport(id) {
    setLoading(true);
    setError('');
    try {
      const data = await apiGet(`/reports/student/${id}/dossier`);
      setReport(data);
    } catch (err) {
      setError(err?.message || 'Failed to generate official student dossier.');
    } finally {
      setLoading(false);
    }
  }

  function handlePrint() {
    window.print();
  }

  function handleExportJSON() {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${report.metadata.report_serial}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(3px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem',
      }}
      className="print-reset"
    >
      <div
        style={{
          background: '#ffffff',
          width: '100%',
          maxWidth: '920px',
          maxHeight: '94vh',
          borderRadius: '16px',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #cbd5e1',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Top Control Bar (Hidden on print) */}
        <div
          style={{
            background: '#0f172a',
            color: '#ffffff',
            padding: '0.85rem 1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
          className="no-print"
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ fontSize: '1.4rem' }}>📜</span>
            <div>
              <div style={{ fontWeight: 800, fontSize: '0.95rem', letterSpacing: '0.02em' }}>
                Official Student Cumulative Academic Dossier
              </div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                Certified State Board Record • NagrikSetu Educational Matrix
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <button
              onClick={handlePrint}
              disabled={loading || !report}
              style={{
                background: '#2563eb',
                color: '#ffffff',
                border: 'none',
                borderRadius: '8px',
                padding: '0.45rem 0.9rem',
                fontSize: '0.78rem',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}
            >
              <span>🖨️</span> Print / Save PDF
            </button>
            <button
              onClick={handleExportJSON}
              disabled={loading || !report}
              style={{
                background: '#1e293b',
                color: '#e2e8f0',
                border: '1px solid #334155',
                borderRadius: '8px',
                padding: '0.45rem 0.9rem',
                fontSize: '0.78rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Export JSON
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                fontSize: '1.25rem',
                cursor: 'pointer',
                padding: '0.2rem 0.5rem',
              }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Modal Printable Content */}
        <div style={{ padding: '2rem', overflowY: 'auto', background: '#f8fafc' }} className="print-canvas">
          {loading && (
            <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
              <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>⏳</div>
              <div style={{ fontWeight: 700, color: '#334155' }}>Compiling certified academic ledger...</div>
            </div>
          )}

          {error && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '1rem', borderRadius: '8px', color: '#991b1b' }}>
              <strong>Error:</strong> {error}
            </div>
          )}

          {report && (
            <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '2rem' }}>
              
              {/* Official Header */}
              <div style={{ borderBottom: '2px solid #0f172a', paddingBottom: '1.25rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ fontSize: '2.5rem' }}>🏛️</div>
                    <div>
                      <div style={{ fontSize: '0.7rem', fontWeight: 800, letterSpacing: '0.08em', color: '#1e40af', textTransform: 'uppercase' }}>
                        {report.metadata.issuing_authority}
                      </div>
                      <h1 style={{ fontSize: '1.35rem', fontWeight: 900, color: '#0f172a', margin: '0.15rem 0' }}>
                        {report.metadata.report_title}
                      </h1>
                      <div style={{ fontSize: '0.8rem', color: '#475467', fontWeight: 600 }}>
                        {report.school.school_name} · Affiliated to {report.school.affiliation}
                      </div>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <span style={{ background: '#dcfce7', color: '#166534', border: '1px solid #86efac', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 800 }}>
                      ✓ {report.metadata.verification_status}
                    </span>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace', marginTop: '0.35rem' }}>
                      Serial: {report.metadata.report_serial}
                    </div>
                  </div>
                </div>
              </div>

              {/* Student Demographics Grid */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                  1. Student Particulars & Institutional Enrollment
                </div>
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.85rem', fontSize: '0.8rem' }}>
                  <div>
                    <span style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>Student Legal Name</span>
                    <strong style={{ color: '#0f172a', fontSize: '0.95rem' }}>{report.student.student_name}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>Student ID / Roll No</span>
                    <strong style={{ color: '#1d4ed8', fontFamily: 'monospace' }}>{report.student.student_id} ({report.student.roll_number})</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>Permanent Student ID (PSID)</span>
                    <span style={{ color: '#0f172a', fontFamily: 'monospace', fontSize: '0.75rem' }}>{report.student.permanent_student_id}</span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>Standard & Section</span>
                    <strong style={{ color: '#0f172a' }}>Class {report.student.standard} - Section {report.student.section}</strong>
                  </div>
                  <div>
                    <span style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>Date of Birth / Gender</span>
                    <span>{report.student.date_of_birth} ({report.student.gender})</span>
                  </div>
                  <div>
                    <span style={{ color: '#64748b', fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', display: 'block' }}>Blood Group / Status</span>
                    <span><strong>{report.student.blood_group}</strong> · <span style={{ color: '#15803d', fontWeight: 700 }}>{report.student.enrollment_status}</span></span>
                  </div>
                </div>
              </div>

              {/* Academic Performance Table */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>2. Cumulative Academic Performance & Examination Scores</span>
                  <span style={{ background: '#eff6ff', color: '#1e40af', padding: '0.2rem 0.5rem', borderRadius: '6px', fontSize: '0.75rem' }}>
                    Aggregate: <strong>{report.academic_evaluation.overall_percentage}%</strong> · Grade: <strong>{report.academic_evaluation.evaluation_grade}</strong>
                  </span>
                </div>

                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', border: '1px solid #cbd5e1' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', color: '#334155', textAlign: 'left', borderBottom: '1px solid #cbd5e1' }}>
                      <th style={{ padding: '0.55rem 0.75rem' }}>Subject Name</th>
                      <th style={{ padding: '0.55rem 0.75rem' }}>Examination Term</th>
                      <th style={{ padding: '0.55rem 0.75rem' }}>Marks Obtained</th>
                      <th style={{ padding: '0.55rem 0.75rem' }}>Maximum Marks</th>
                      <th style={{ padding: '0.55rem 0.75rem' }}>Grade</th>
                      <th style={{ padding: '0.55rem 0.75rem' }}>Academic Session</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.academic_evaluation.results.map((r, idx) => (
                      <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0', background: idx % 2 === 0 ? '#ffffff' : '#f8fafc' }}>
                        <td style={{ padding: '0.55rem 0.75rem', fontWeight: 600 }}>{r.subject_name}</td>
                        <td style={{ padding: '0.55rem 0.75rem', color: '#475467' }}>{r.exam_name}</td>
                        <td style={{ padding: '0.55rem 0.75rem', fontWeight: 700, color: '#1e40af' }}>{r.marks_obtained}</td>
                        <td style={{ padding: '0.55rem 0.75rem', color: '#64748b' }}>{r.maximum_marks}</td>
                        <td style={{ padding: '0.55rem 0.75rem' }}>
                          <span style={{ background: '#e0f2fe', color: '#0369a1', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>
                            {r.grade || 'A'}
                          </span>
                        </td>
                        <td style={{ padding: '0.55rem 0.75rem', color: '#64748b' }}>{r.academic_year}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Attendance and Linked Guardians */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1rem', fontSize: '0.8rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                    3. Attendance & Conduct Evaluation
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.35rem', marginBottom: '0.35rem' }}>
                    <span style={{ color: '#64748b' }}>Term Attendance</span>
                    <strong style={{ color: '#15803d' }}>{report.academic_evaluation.term_attendance_percentage}% (Eligible)</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.35rem', marginBottom: '0.35rem' }}>
                    <span style={{ color: '#64748b' }}>Conduct & Discipline</span>
                    <strong>{report.academic_evaluation.conduct_character}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#64748b' }}>Annual Status</span>
                    <strong style={{ color: '#1d4ed8' }}>{report.academic_evaluation.promotion_eligibility}</strong>
                  </div>
                </div>

                <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1rem', fontSize: '0.8rem' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                    4. Verified Linked Guardians
                  </div>
                  {report.linked_guardians.map((g, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.35rem', marginBottom: '0.35rem' }}>
                      <span><strong>{g.full_name}</strong> ({g.relationship})</span>
                      <span style={{ color: '#64748b', fontFamily: 'monospace' }}>{g.phone}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* QR Code and Attestation Footer */}
              <div style={{ borderTop: '2px solid #0f172a', paddingTop: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', fontSize: '0.75rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
                  <div style={{ width: '60px', height: '60px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '6px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.75rem' }}>
                    📱
                  </div>
                  <div>
                    <strong style={{ display: 'block', color: '#0f172a' }}>Digital Verification QR</strong>
                    <span style={{ color: '#64748b', fontFamily: 'monospace', fontSize: '0.7rem' }}>
                      {report.metadata.qr_verification_payload}
                    </span>
                  </div>
                </div>

                <div style={{ textAlign: 'right', border: '1px dashed #94a3b8', padding: '0.5rem 1rem', borderRadius: '8px', background: '#f8fafc' }}>
                  <div style={{ color: '#166534', fontWeight: 800, fontSize: '0.75rem' }}>✓ DIGITALLY ACCREDITED</div>
                  <div style={{ color: '#475467', fontSize: '0.7rem' }}>Head of Institution / Principal</div>
                  <div style={{ fontFamily: 'monospace', fontSize: '0.65rem', color: '#94a3b8' }}>
                    {report.metadata.digital_checksum_sha256.substring(0, 20)}...
                  </div>
                </div>
              </div>

            </div>
          )}
        </div>
      </div>
    </div>
  );
}
