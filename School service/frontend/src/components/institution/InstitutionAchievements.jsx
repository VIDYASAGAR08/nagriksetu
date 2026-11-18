import React from 'react'

export default function InstitutionAchievements({ achievements, schoolName }) {
  const achs = achievements || []

  return (
    <section id="achievements" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      background: '#ffffff',
      boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem', borderBottom: '2px solid #e8eaed', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🏆</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1a3a6b', margin: 0 }}>
              Verified Institutional Achievements & Accreditations
            </h2>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
              Recognized awards, NIRF/NAAC distinctions, and competition laurels issued by verified authorities
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.85rem',
            fontWeight: 700,
            padding: '0.35rem 0.75rem',
            borderRadius: '20px',
            background: '#dcfce7',
            color: '#15803d',
            border: '1px solid #bbf7d0'
          }}>
            ✓ {achs.length} Verified Laurels
          </span>
        </div>
      </div>

      {achs.length === 0 ? (
        <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', textAlign: 'center', color: '#6b7280' }}>
          Institutional achievements and regulatory records are currently undergoing verification by the education department.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {achs.map((ach) => (
            <div
              key={ach.achievement_id}
              style={{
                border: '1px solid #e2e8f0',
                borderRadius: '10px',
                padding: '1.25rem',
                background: '#ffffff',
                boxShadow: '0 1px 3px rgba(0,0,0,0.04)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.55rem',
                    borderRadius: '4px',
                    background: ach.award_level === 'National' ? '#fef3c7' : '#e0e7ff',
                    color: ach.award_level === 'National' ? '#92400e' : '#3730a3'
                  }}>
                    {ach.award_level || 'State'} Distinction
                  </span>

                  {ach.year && (
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#1a3a6b' }}>
                      Year: {ach.year}
                    </span>
                  )}
                </div>

                <h4 style={{ margin: '0 0 0.4rem 0', color: '#1a3a6b', fontSize: '1.05rem', fontWeight: 700 }}>
                  {ach.title}
                </h4>

                <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.5 }}>
                  {ach.description}
                </p>
              </div>

              <div style={{
                borderTop: '1px solid #f1f5f9',
                paddingTop: '0.6rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '0.78rem',
                color: '#6b7280'
              }}>
                <span>
                  Awarded by: <strong>{ach.issuing_authority || 'Regulatory Council'}</strong>
                </span>

                {ach.public_document_url && (
                  <a
                    href={ach.public_document_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: '#1a3a6b', fontWeight: 600, textDecoration: 'underline' }}
                  >
                    View Record ↗
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
