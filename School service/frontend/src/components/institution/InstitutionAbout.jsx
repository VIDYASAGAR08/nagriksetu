import React from 'react'

export default function InstitutionAbout({ about, schoolName }) {
  if (!about || Object.keys(about).length === 0) {
    return (
      <div id="about" className="card" style={{ padding: '2rem', marginBottom: '2rem', border: '1px solid #d0d5dd', borderRadius: '10px' }}>
        <h2 style={{ color: '#1a3a6b', margin: '0 0 1rem 0' }}>About {schoolName}</h2>
        <p style={{ color: '#6b7280' }}>Comprehensive institutional history and vision are being updated by the administration.</p>
      </div>
    )
  }

  const missions = Array.isArray(about.mission) ? about.mission : (about.mission ? [about.mission] : [])

  return (
    <section id="about" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      background: '#ffffff',
      boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', borderBottom: '2px solid #e8eaed', paddingBottom: '0.75rem' }}>
        <span style={{ fontSize: '1.5rem' }}>🏛️</span>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1a3a6b', margin: 0 }}>
            About the Institution
          </h2>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
            History, academic philosophy, vision, and core mission
          </p>
        </div>
      </div>

      {/* Introduction */}
      {about.introduction && (
        <div style={{ marginBottom: '1.5rem', lineHeight: '1.7', color: '#374151', fontSize: '1rem' }}>
          {about.introduction}
        </div>
      )}

      {/* Vision & Mission Highlight Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.75rem' }}>
        {/* Vision Card */}
        {about.vision && (
          <div style={{
            background: 'linear-gradient(135deg, #f0f7ff 0%, #e0effe 100%)',
            border: '1px solid #bfdbfe',
            borderRadius: '10px',
            padding: '1.25rem',
            position: 'relative'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '1.2rem' }}>🔭</span>
              <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#1e40af', fontWeight: 700 }}>Institutional Vision</h3>
            </div>
            <p style={{ margin: 0, color: '#1e3a8a', fontStyle: 'italic', lineHeight: 1.6, fontSize: '0.95rem' }}>
              "{about.vision}"
            </p>
          </div>
        )}

        {/* Mission Card */}
        {missions.length > 0 && (
          <div style={{
            background: 'linear-gradient(135deg, #fdf4ff 0%, #fae8ff 100%)',
            border: '1px solid #f0abfc',
            borderRadius: '10px',
            padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span style={{ fontSize: '1.2rem' }}>🎯</span>
              <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#86198f', fontWeight: 700 }}>Core Mission</h3>
            </div>
            <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#701a75', lineHeight: 1.6, fontSize: '0.9rem' }}>
              {missions.map((m, idx) => (
                <li key={idx} style={{ marginBottom: '0.25rem' }}>{m}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* History, Philosophy, Methodology & Environment Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
        {about.history && (
          <div style={{ background: '#f9fafb', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              📜 History & Legacy
            </h4>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.6 }}>
              {about.history}
            </p>
          </div>
        )}

        {about.educational_philosophy && (
          <div style={{ background: '#f9fafb', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              💡 Educational Philosophy
            </h4>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.6 }}>
              {about.educational_philosophy}
            </p>
          </div>
        )}

        {about.teaching_methodology && (
          <div style={{ background: '#f9fafb', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              📚 Teaching Methodology
            </h4>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.6 }}>
              {about.teaching_methodology}
            </p>
          </div>
        )}

        {about.academic_environment && (
          <div style={{ background: '#f9fafb', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
            <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              🌳 Academic Environment
            </h4>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.6 }}>
              {about.academic_environment}
            </p>
          </div>
        )}
      </div>
    </section>
  )
}
