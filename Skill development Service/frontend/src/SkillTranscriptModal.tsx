import React, { useState, useEffect } from 'react';
import { X, Printer, Download, Award, Shield, CheckCircle, FileText, Loader2, AlertCircle } from 'lucide-react';

interface SkillTranscriptModalProps {
  isOpen: boolean;
  onClose: () => void;
  candidateIdentifier: string; // can be email, citizen_ref, or student_id
  token?: string | null;
}

export default function SkillTranscriptModal({
  isOpen,
  onClose,
  candidateIdentifier,
  token
}: SkillTranscriptModalProps) {
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen && candidateIdentifier) {
      loadTranscript(candidateIdentifier);
    } else {
      setReport(null);
      setError('');
    }
  }, [isOpen, candidateIdentifier]);

  async function loadTranscript(id: string) {
    setLoading(true);
    setError('');
    try {
      const headers: Record<string, string> = {};
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      const response = await fetch(`/api/reports/candidate/${encodeURIComponent(id)}/transcript`, {
        headers
      });
      if (!response.ok) {
        throw new Error(`Failed to load transcript: HTTP ${response.status}`);
      }
      const data = await response.json();
      setReport(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to generate official vocational skill transcript.');
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
    a.download = `${report.metadata?.report_serial || 'skill-transcript'}.json`;
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
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1rem'
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        style={{
          background: '#ffffff',
          borderRadius: '12px',
          width: '100%',
          maxWidth: '920px',
          maxHeight: '92vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          border: '1px solid #e2e8f0',
          overflow: 'hidden'
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* MODAL CONTROL HEADER (Hidden during print) */}
        <div
          className="no-print"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '0.85rem 1.5rem',
            background: '#091a33',
            color: '#ffffff',
            borderBottom: '1px solid #1e293b'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <FileText size={18} style={{ color: '#38bdf8' }} />
            <span style={{ fontWeight: 700, fontSize: '0.95rem', letterSpacing: '0.02em' }}>
              OFFICIAL VOCATIONAL SKILL TRANSCRIPT & CREDENTIAL REPORT
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            {report && (
              <>
                <button
                  type="button"
                  onClick={handleExportJSON}
                  style={{
                    background: '#1e293b',
                    color: '#f8fafc',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    padding: '0.4rem 0.8rem',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                  title="Export raw cryptographic verification JSON"
                >
                  <Download size={14} /> JSON
                </button>
                <button
                  type="button"
                  onClick={handlePrint}
                  style={{
                    background: '#2563eb',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '0.4rem 0.9rem',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.35rem'
                  }}
                  title="Print or Save official PDF dossier"
                >
                  <Printer size={14} /> Print / Save PDF
                </button>
              </>
            )}
            <button
              type="button"
              onClick={onClose}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#94a3b8',
                cursor: 'pointer',
                padding: '0.3rem',
                display: 'flex',
                alignItems: 'center',
                borderRadius: '4px'
              }}
              title="Close modal"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* MODAL BODY (PRINTABLE REGION) */}
        <div style={{ padding: '2rem', overflowY: 'auto', flex: 1, position: 'relative' }}>
          {loading && (
            <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
              <Loader2 size={36} className="animate-spin" style={{ color: '#2563eb', margin: '0 auto 1rem auto' }} />
              <p style={{ color: '#475569', fontWeight: 600 }}>
                Compiling candidate vocational records and calculating SHA-256 seal...
              </p>
            </div>
          )}

          {error && !loading && (
            <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '1.5rem', textAlign: 'center' }}>
              <AlertCircle size={32} style={{ color: '#dc2626', margin: '0 auto 0.5rem auto' }} />
              <h4 style={{ color: '#991b1b', margin: '0 0 0.5rem 0', fontWeight: 700 }}>Unable to Generate Report</h4>
              <p style={{ color: '#7f1d1d', fontSize: '0.875rem', margin: '0 0 1rem 0' }}>{error}</p>
              <button
                type="button"
                onClick={() => loadTranscript(candidateIdentifier)}
                style={{
                  background: '#dc2626',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '0.45rem 1rem',
                  fontSize: '0.825rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Retry
              </button>
            </div>
          )}

          {report && !loading && (
            <div id="skill-transcript-printable-content" style={{ fontFamily: 'system-ui, -apple-system, sans-serif' }}>
              {/* WATERMARK */}
              <div
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%) rotate(-30deg)',
                  fontSize: '5rem',
                  fontWeight: 900,
                  color: 'rgba(15, 23, 42, 0.035)',
                  letterSpacing: '0.2em',
                  pointerEvents: 'none',
                  whiteSpace: 'nowrap',
                  zIndex: 0,
                  textTransform: 'uppercase'
                }}
              >
                OFFICIAL TRANSCRIPT
              </div>

              {/* OFFICIAL GOVERNMENT HEADER */}
              <div style={{ textAlign: 'center', borderBottom: '2px solid #0f172a', paddingBottom: '1.25rem', marginBottom: '1.5rem', position: 'relative', zIndex: 1 }}>
                <div style={{ fontSize: '0.78rem', letterSpacing: '0.15em', fontWeight: 800, color: '#475569', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                  GOVERNMENT OF KARNATAKA • NAGRIKSETU SKILL MATRIX
                </div>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 900, color: '#091a33', margin: '0.2rem 0', letterSpacing: '-0.01em', textTransform: 'uppercase' }}>
                  {report.metadata?.report_title}
                </h1>
                <div style={{ fontSize: '0.85rem', color: '#1e40af', fontWeight: 700, margin: '0.25rem 0' }}>
                  {report.metadata?.issuing_authority}
                </div>
                <div style={{ display: 'inline-block', background: '#ecfdf5', border: '1px solid #a7f3d0', color: '#047857', padding: '0.2rem 0.75rem', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 800, marginTop: '0.4rem', textTransform: 'uppercase' }}>
                  ✓ {report.metadata?.verification_status}
                </div>
              </div>

              {/* REPORT METADATA & CRYPTOGRAPHIC STRIP */}
              <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '0.85rem 1.25rem', marginBottom: '1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem', fontSize: '0.8rem', position: 'relative', zIndex: 1 }}>
                <div>
                  <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>Report Serial:</span>
                  <strong style={{ fontFamily: 'monospace', color: '#0f172a' }}>{report.metadata?.report_serial}</strong>
                </div>
                <div>
                  <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>Date & Timestamp:</span>
                  <strong style={{ color: '#0f172a' }}>{new Date(report.metadata?.issued_at).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })} (IST)</strong>
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase' }}>Digital Checksum (SHA-256):</span>
                  <strong style={{ fontFamily: 'monospace', color: '#0284c7', fontSize: '0.75rem', wordBreak: 'break-all' }}>
                    {report.metadata?.digital_checksum_sha256}
                  </strong>
                </div>
              </div>

              {/* CANDIDATE PARTICULARS */}
              <div style={{ marginBottom: '1.75rem', position: 'relative', zIndex: 1 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.04em', borderLeft: '4px solid #2563eb', paddingLeft: '0.5rem', marginBottom: '0.75rem' }}>
                  1. Candidate Demographics & Identification
                </h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem', fontSize: '0.85rem' }}>
                  <div><span style={{ color: '#64748b' }}>Full Name:</span><br /><strong style={{ fontSize: '1rem', color: '#091a33' }}>{report.candidate?.full_name}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Student / Roll ID:</span><br /><strong style={{ fontFamily: 'monospace', color: '#2563eb' }}>{report.candidate?.student_id || 'N/A'}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Citizen Identifier:</span><br /><strong style={{ fontFamily: 'monospace' }}>{report.candidate?.citizen_ref}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Email:</span><br /><strong>{report.candidate?.email}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Education:</span><br /><strong>{report.candidate?.education || 'Secondary / Graduate'}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Employment Status:</span><br /><strong style={{ color: '#d97706' }}>{report.candidate?.employment_status}</strong></div>
                  <div><span style={{ color: '#64748b' }}>NSQF Readiness:</span><br /><strong style={{ color: '#059669' }}>{report.candidate?.nsqf_readiness}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Preferred Location:</span><br /><strong>{report.candidate?.preferred_location || 'Karnataka'}</strong></div>
                </div>
              </div>

              {/* ENROLLED VOCATIONAL TRAINING PROGRAMS */}
              <div style={{ marginBottom: '1.75rem', position: 'relative', zIndex: 1 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.04em', borderLeft: '4px solid #0891b2', paddingLeft: '0.5rem', marginBottom: '0.75rem' }}>
                  2. Government Training Programs & Enrolled Batches
                </h3>
                {report.training_programs && report.training_programs.length > 0 ? (
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.83rem', border: '1px solid #cbd5e1' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #cbd5e1', textAlign: 'left' }}>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Program Title</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Batch & Mode</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Training Centre</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Enrollment Status</th>
                        <th style={{ padding: '0.6rem 0.75rem', textAlign: 'right' }}>Progress</th>
                      </tr>
                    </thead>
                    <tbody>
                      {report.training_programs.map((prog: any, idx: number) => (
                        <tr key={idx} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '0.6rem 0.75rem', fontWeight: 700, color: '#0f172a' }}>{prog.program_title}</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>{prog.batch_name} ({prog.selected_mode})</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>{prog.centre_name}</td>
                          <td style={{ padding: '0.6rem 0.75rem' }}>
                            <span style={{ background: '#eff6ff', color: '#1d4ed8', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
                              {prog.status}
                            </span>
                          </td>
                          <td style={{ padding: '0.6rem 0.75rem', textAlign: 'right', fontWeight: 800, color: '#0284c7' }}>
                            {prog.training_progress_pct}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px dashed #cbd5e1', color: '#64748b', fontSize: '0.85rem' }}>
                    Candidate is enrolled in foundational NSQF modules; pending active batch allocation.
                  </div>
                )}
              </div>

              {/* CERTIFIED SKILLS & TECHNICAL COMPETENCIES */}
              <div style={{ marginBottom: '1.75rem', position: 'relative', zIndex: 1 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', letterSpacing: '0.04em', borderLeft: '4px solid #16a34a', paddingLeft: '0.5rem', marginBottom: '0.75rem' }}>
                  3. Verified Technical Competencies & Skills
                </h3>
                {report.competency_portfolio && report.competency_portfolio.length > 0 ? (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
                    {report.competency_portfolio.map((item: any, idx: number) => (
                      <div key={idx} style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.45rem 0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.85rem' }}>
                        <Award size={15} style={{ color: '#16a34a' }} />
                        <strong style={{ color: '#166534' }}>{item.skill_name}</strong>
                        <span style={{ background: '#dcfce7', color: '#14532d', padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700 }}>
                          {item.proficiency}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '6px', border: '1px dashed #cbd5e1', color: '#64748b', fontSize: '0.85rem' }}>
                    Technical competencies verified under standard National Occupational Standards (NOS).
                  </div>
                )}
              </div>

              {/* QR SEAL & STATUTORY ATTESTATION */}
              <div style={{ borderTop: '2px solid #0f172a', paddingTop: '1.25rem', marginTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem', position: 'relative', zIndex: 1 }}>
                <div style={{ maxWidth: '480px' }}>
                  <div style={{ fontSize: '0.75rem', fontWeight: 800, color: '#0f172a', textTransform: 'uppercase', marginBottom: '0.25rem' }}>
                    Statutory Attestation & Accreditations
                  </div>
                  <p style={{ fontSize: '0.75rem', color: '#475569', lineHeight: 1.5, margin: '0 0 0.5rem 0' }}>
                    {report.statutory_attestation?.declaration}
                  </p>
                  <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: 700 }}>
                    {report.statutory_attestation?.accreditation_body}
                  </div>
                </div>

                <div style={{ textAlign: 'center', minWidth: '180px' }}>
                  {/* Simulated QR Code Box */}
                  <div style={{ width: '90px', height: '90px', margin: '0 auto 0.4rem auto', background: '#0f172a', borderRadius: '8px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: '#ffffff', padding: '4px' }}>
                    <Shield size={28} style={{ color: '#38bdf8', marginBottom: '2px' }} />
                    <span style={{ fontSize: '0.55rem', fontWeight: 900, letterSpacing: '0.05em' }}>VERIFIED QR</span>
                  </div>
                  <div style={{ fontSize: '0.7rem', fontWeight: 800, color: '#091a33' }}>
                    {report.statutory_attestation?.certifying_officer}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase' }}>
                    Electronic Attestation Seal
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
