import React from 'react'

export default function InstitutionHero({ institution, activeSection, onNavigate, onApplyClick }) {
  if (!institution) return null

  const about = institution.about || {}
  const parsedFac = institution.parsedFacilities || {}
  const naacGrade = institution.accreditations?.find(a => a.includes('NAAC')) || parsedFac.naac_grade
  const nirfRank = institution.accreditations?.find(a => a.includes('NIRF')) || parsedFac.nirf_rank

  return (
    <div className="institution-hero card" style={{
      padding: '0',
      overflow: 'hidden',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      marginBottom: '2rem',
      background: '#ffffff',
      boxShadow: '0 4px 12px rgba(0,0,0,0.06)'
    }}>
      {/* Cover Banner */}
      <div style={{
        height: '240px',
        position: 'relative',
        background: institution.cover_image_url
          ? `linear-gradient(rgba(26, 58, 107, 0.75), rgba(18, 42, 82, 0.88)), url("${institution.cover_image_url}") center/cover no-repeat`
          : 'linear-gradient(135deg, #1a3a6b 0%, #122a52 100%)',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-end',
        color: '#ffffff'
      }}>
        {/* Top Floating Badges */}
        <div style={{ position: 'absolute', top: '1.25rem', left: '1.5rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            background: 'rgba(255, 255, 255, 0.95)',
            color: '#1a3a6b',
            padding: '0.3rem 0.7rem',
            borderRadius: '4px',
            letterSpacing: '0.5px'
          }}>
            DISE / INST CODE: {institution.school_id}
          </span>

          <span style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            background: '#e07b00',
            color: '#ffffff',
            padding: '0.3rem 0.7rem',
            borderRadius: '4px'
          }}>
            {institution.school_type}
          </span>

          {institution.recognition && (
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              background: '#15803d',
              color: '#ffffff',
              padding: '0.3rem 0.7rem',
              borderRadius: '4px'
            }}>
              ✓ {institution.recognition}
            </span>
          )}

          {naacGrade && (
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              background: 'rgba(0, 0, 0, 0.65)',
              color: '#facc15',
              padding: '0.3rem 0.7rem',
              borderRadius: '4px',
              border: '1px solid rgba(250, 204, 21, 0.4)'
            }}>
              ★ {naacGrade}
            </span>
          )}

          {nirfRank && (
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              background: 'rgba(0, 0, 0, 0.65)',
              color: '#ffffff',
              padding: '0.3rem 0.7rem',
              borderRadius: '4px'
            }}>
              🏆 {nirfRank}
            </span>
          )}

          {institution.seat_summary && (
            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              background: institution.seat_summary.available_seats > 10 ? '#ECFDF3' : institution.seat_summary.available_seats > 0 ? '#FFFAEB' : '#FEF3F2',
              color: institution.seat_summary.available_seats > 10 ? '#027A48' : institution.seat_summary.available_seats > 0 ? '#B54708' : '#B42318',
              padding: '0.3rem 0.7rem',
              borderRadius: '4px',
              border: `1px solid ${institution.seat_summary.available_seats > 10 ? '#A6F4C5' : '#FEDF89'}`
            }}>
              📊 {institution.seat_summary.available_seats > 0 ? `${institution.seat_summary.available_seats} Seats Available` : 'Quota Full'}
            </span>
          )}
        </div>

        {/* Institution Title Banner */}
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1.5rem', flexWrap: 'wrap' }}>
          {institution.logo_url && (
            <div style={{
              width: '84px',
              height: '84px',
              background: '#ffffff',
              borderRadius: '10px',
              padding: '6px',
              boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0
            }}>
              <img
                src={institution.logo_url}
                alt={`${institution.school_name} Logo`}
                style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                onError={(e) => { e.target.style.display = 'none' }}
              />
            </div>
          )}

          <div style={{ flex: 1, minWidth: '280px' }}>
            <h1 style={{
              fontSize: '2rem',
              fontWeight: 800,
              color: '#ffffff',
              margin: '0 0 0.25rem 0',
              lineHeight: 1.2,
              textShadow: '0 2px 4px rgba(0,0,0,0.4)'
            }}>
              {institution.school_name}
            </h1>
            <p style={{
              margin: 0,
              fontSize: '0.95rem',
              color: '#e2e8f0',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              flexWrap: 'wrap'
            }}>
              {institution.campus_name && <span>🏛️ {institution.campus_name} •</span>}
              <span>📍 {institution.district}, {institution.state}</span>
              {institution.established_year && <span>• Est. {institution.established_year}</span>}
            </p>
          </div>
        </div>
      </div>

      {/* Hero Meta & Contact Bar */}
      <div style={{
        padding: '1.25rem 1.75rem',
        background: '#f8fafc',
        borderBottom: '1px solid #e8eaed',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        {/* Contact info pills */}
        <div style={{ display: 'flex', gap: '1.25rem', flexWrap: 'wrap', fontSize: '0.875rem', color: '#4b5563' }}>
          {institution.affiliation && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: '#EFF8FF', padding: '0.25rem 0.6rem', borderRadius: '4px', border: '1px solid #B2DDFF' }}>
              <span style={{ color: '#175CD3', fontWeight: 700 }}>
                {institution.category === 'Universities' || institution.school_type === 'University'
                  ? '🏛️ Statutory Charter:'
                  : institution.category === 'Degree Colleges' || institution.school_type === 'Degree College'
                  ? '🏛️ Affiliated to:'
                  : 'Affiliation:'}
              </span>
              <span style={{ color: '#102B46', fontWeight: 600 }}>{institution.affiliation}</span>
            </div>
          )}

          {institution.public_phone && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span>📞</span>
              <a href={`tel:${institution.public_phone}`} style={{ color: '#1a3a6b', textDecoration: 'none', fontWeight: 500 }}>
                {institution.public_phone}
              </a>
            </div>
          )}

          {institution.email && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span>✉️</span>
              <a href={`mailto:${institution.email}`} style={{ color: '#1a3a6b', textDecoration: 'none', fontWeight: 500 }}>
                {institution.email}
              </a>
            </div>
          )}

          {institution.website && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <span>🌐</span>
              <a href={institution.website} target="_blank" rel="noopener noreferrer" style={{ color: '#1a3a6b', textDecoration: 'underline', fontWeight: 600 }}>
                Official Portal
              </a>
            </div>
          )}
        </div>

        {/* Action Button: Map, Apply & Verification */}
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          {onApplyClick && (
            <button
              onClick={onApplyClick}
              style={{
                fontSize: '0.85rem',
                padding: '0.45rem 1.1rem',
                display: 'flex',
                alignItems: 'center',
                gap: '0.4rem',
                background: '#155EEF',
                color: '#ffffff',
                border: 'none',
                borderRadius: '6px',
                fontWeight: 700,
                cursor: 'pointer',
                boxShadow: '0 2px 6px rgba(21, 94, 239, 0.25)'
              }}
            >
              ✍️ Apply for Admission
            </button>
          )}
          {institution.map_url && (
            <a
              href={institution.map_url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn--secondary"
              style={{ fontSize: '0.85rem', padding: '0.45rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.4rem', textDecoration: 'none' }}
            >
              📍 View on Map
            </a>
          )}
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 600,
            padding: '0.4rem 0.75rem',
            background: '#dcfce7',
            color: '#15803d',
            borderRadius: '6px',
            border: '1px solid #bbf7d0',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem'
          }}>
            🛡️ Verified Institution
          </span>
        </div>
      </div>

      {/* Quick Navigation Sticky Bar */}
      <div style={{
        display: 'flex',
        gap: '0.25rem',
        background: '#ffffff',
        padding: '0.5rem 1.5rem',
        borderTop: '1px solid #f1f5f9',
        overflowX: 'auto',
        whiteSpace: 'nowrap'
      }}>
        {[
          { id: 'about', label: 'About & Vision' },
          { id: 'seat-availability', label: '📊 Live Seats' },
          { id: 'facilities', label: 'Facilities (13)' },
          { id: 'hostel', label: 'Hostel' },
          { id: 'transport', label: 'Transport' },
          { id: 'academics', label: 'Academics & Degrees' },
          { id: 'admissions', label: 'Admissions & Fees' },
          { id: 'achievements', label: 'Achievements' },
          { id: 'divisions', label: 'Campuses & Divisions' },
          { id: 'students', label: 'Enrolled Students' }
        ].map((sec) => (
          <button
            key={sec.id}
            onClick={() => onNavigate(sec.id)}
            style={{
              padding: '0.5rem 0.9rem',
              fontSize: '0.875rem',
              fontWeight: activeSection === sec.id ? 700 : 500,
              color: activeSection === sec.id ? '#1a3a6b' : '#6b7280',
              background: activeSection === sec.id ? '#e8eaed' : 'transparent',
              borderRadius: '6px',
              border: 'none',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            {sec.label}
          </button>
        ))}
      </div>
    </div>
  )
}
