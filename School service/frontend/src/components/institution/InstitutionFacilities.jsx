import React, { useState } from 'react'

export default function InstitutionFacilities({ facilities }) {
  const fac = facilities || {}

  // 13 standard facility definitions
  const standardCategories = [
    { key: 'classrooms', icon: '🏫', title: 'Classrooms & Lecture Halls' },
    { key: 'science_labs', icon: '🔬', title: 'Science Laboratories' },
    { key: 'computer_labs', icon: '💻', title: 'Computer Labs & IT Suites' },
    { key: 'library', icon: '📖', title: 'Automated Central Library' },
    { key: 'digital_learning', icon: '🖥️', title: 'Digital & Smartboard Learning' },
    { key: 'sports', icon: '⚽', title: 'Sports, Grounds & Athletics' },
    { key: 'auditorium', icon: '🎭', title: 'Auditoriums & Seminar Halls' },
    { key: 'cafeteria', icon: '🍽️', title: 'Cafeteria & Hygienic Dining' },
    { key: 'medical_room', icon: '🩺', title: 'Medical Infirmary & Health Centre' },
    { key: 'internet', icon: '📶', title: 'High-Speed Internet & Wi-Fi' },
    { key: 'accessibility', icon: '♿', title: 'Campus Accessibility (CWSN/PwD)' },
    { key: 'security', icon: '🛡️', title: '24/7 Security & CCTV Surveillance' },
    { key: 'transport_hub', icon: '🅿️', title: 'Campus Transit & Vehicle Parking' }
  ]

  const [activeFilter, setActiveFilter] = useState('ALL')

  const availableCount = standardCategories.filter(cat => {
    const item = fac[cat.key]
    return item && item.available !== false
  }).length

  return (
    <section id="facilities" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      background: '#ffffff',
      boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem', borderBottom: '2px solid #e8eaed', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🏢</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1a3a6b', margin: 0 }}>
              Facilities & Infrastructure
            </h2>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
              Standard 13-category physical and digital infrastructure audit
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            background: '#dcfce7',
            color: '#15803d',
            border: '1px solid #bbf7d0'
          }}>
            ✓ {availableCount} of 13 Available
          </span>
        </div>
      </div>

      {/* Facilities Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.25rem'
      }}>
        {standardCategories.map((cat) => {
          const item = fac[cat.key] || {}
          const isAvail = item.available !== false && (item.count !== undefined || item.details || item.speed || item.features || item.description)

          return (
            <div
              key={cat.key}
              style={{
                border: isAvail ? '1px solid #e2e8f0' : '1px dashed #cbd5e1',
                borderRadius: '10px',
                padding: '1.25rem',
                background: isAvail ? '#ffffff' : '#f8fafc',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <span style={{ fontSize: '1.3rem' }}>{cat.icon}</span>
                    <h4 style={{ margin: 0, fontSize: '0.95rem', fontWeight: 700, color: isAvail ? '#1a3a6b' : '#9ca3af' }}>
                      {cat.title}
                    </h4>
                  </div>
                  {isAvail ? (
                    <span style={{ fontSize: '0.7rem', fontWeight: 700, padding: '0.15rem 0.5rem', borderRadius: '4px', background: '#dcfce7', color: '#15803d' }}>
                      Available
                    </span>
                  ) : (
                    <span style={{ fontSize: '0.7rem', fontWeight: 600, padding: '0.15rem 0.5rem', borderRadius: '4px', background: '#f3f4f6', color: '#9ca3af' }}>
                      N/A
                    </span>
                  )}
                </div>

                {/* Counts or metrics */}
                {item.count !== undefined && item.count !== null && (
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e07b00', marginBottom: '0.4rem' }}>
                    Total Units: {item.count}
                  </div>
                )}

                {item.speed && (
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#2563eb', marginBottom: '0.4rem' }}>
                    ⚡ {item.speed}
                  </div>
                )}

                {/* Text details */}
                <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.85rem', color: isAvail ? '#4b5563' : '#9ca3af', lineHeight: 1.5 }}>
                  {item.description || item.details || (isAvail ? 'Modern facility available for student use.' : 'Facility not available on campus premises.')}
                </p>

                {/* Feature tags */}
                {Array.isArray(item.features) && item.features.length > 0 && (
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.5rem' }}>
                    {item.features.map((feat, idx) => (
                      <span key={idx} style={{
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        background: '#eff6ff',
                        color: '#1d4ed8',
                        padding: '0.15rem 0.45rem',
                        borderRadius: '4px',
                        border: '1px solid #bfdbfe'
                      }}>
                        ✓ {feat}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
