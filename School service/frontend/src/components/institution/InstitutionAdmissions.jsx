import React from 'react'

export default function InstitutionAdmissions({ admissions, schoolName }) {
  const adm = admissions || {}
  const steps = Array.isArray(adm.process_steps) ? adm.process_steps : []
  const scholarships = Array.isArray(adm.scholarships) ? adm.scholarships : []
  const docs = Array.isArray(adm.required_documents) ? adm.required_documents : []

  return (
    <section id="admissions" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      background: '#ffffff',
      boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem', borderBottom: '2px solid #e8eaed', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>📋</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1a3a6b', margin: 0 }}>
              Admissions & Fee Guidelines
            </h2>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
              Academic admission procedures, eligibility requirements, scholarships, and verification checklists
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            background: '#fef3c7',
            color: '#92400e',
            border: '1px solid #fde68a'
          }}>
            📅 {adm.academic_year || '2026-2027'} Cycle • {adm.status || 'Admissions Active'}
          </span>
        </div>
      </div>

      {/* Eligibility Criteria Callout */}
      {adm.eligibility_criteria && (
        <div style={{
          background: 'linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)',
          border: '1px solid #bbf7d0',
          borderRadius: '8px',
          padding: '1.25rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
            <span style={{ fontSize: '1.2rem' }}>🎯</span>
            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#166534' }}>
              Prescribed Eligibility Criteria
            </h4>
          </div>
          <p style={{ margin: 0, fontSize: '0.9rem', color: '#14532d', lineHeight: 1.5 }}>
            {adm.eligibility_criteria}
          </p>
        </div>
      )}

      {/* Process Walkthrough and Required Documents */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {/* Steps */}
        {steps.length > 0 && (
          <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              📝 Step-by-Step Admission Walkthrough
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {steps.map((st, idx) => (
                <div key={idx} style={{ display: 'flex', gap: '0.6rem', fontSize: '0.875rem', color: '#334155', lineHeight: 1.5 }}>
                  <span style={{
                    width: '22px',
                    height: '22px',
                    borderRadius: '50%',
                    background: '#1a3a6b',
                    color: '#ffffff',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    flexShrink: 0,
                    marginTop: '2px'
                  }}>
                    {idx + 1}
                  </span>
                  <span>{st.replace(/^\d+\.\s*/, '')}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Required Documents */}
        {docs.length > 0 && (
          <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
            <h4 style={{ margin: '0 0 0.75rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              📑 Mandatory Verification Checklist
            </h4>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', fontSize: '0.875rem', color: '#334155', lineHeight: 1.6 }}>
              {docs.map((doc, idx) => (
                <li key={idx} style={{ marginBottom: '0.35rem' }}>{doc}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Scholarship Schemes */}
      {scholarships.length > 0 && (
        <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderRadius: '8px', padding: '1.25rem' }}>
          <h4 style={{ margin: '0 0 0.5rem 0', color: '#92400e', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            💰 Available Scholarship Schemes & Fee Concessions
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem' }}>
            {scholarships.map((sch, idx) => (
              <span key={idx} style={{
                fontSize: '0.825rem',
                fontWeight: 600,
                background: '#ffffff',
                color: '#78350f',
                padding: '0.4rem 0.8rem',
                borderRadius: '6px',
                border: '1px solid #fde68a',
                boxShadow: '0 1px 2px rgba(0,0,0,0.03)'
              }}>
                ✓ {sch}
              </span>
            ))}
          </div>
        </div>
      )}
    </section>
  )
}
