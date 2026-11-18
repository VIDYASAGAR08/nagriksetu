import React from 'react'

export default function InstitutionDivisions({ divisions, schoolName, isParentGroup }) {
  const divs = divisions || []

  return (
    <section id="divisions" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #D0D5DD',
      borderRadius: '12px',
      background: '#FFFFFF',
      boxShadow: '0 2px 8px rgba(16,43,70,0.05)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.25rem',
        borderBottom: '2px solid #EAECF0',
        paddingBottom: '0.85rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.6rem' }}>🏛️</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Academic Divisions & Campus Architecture
            </h2>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
              Multi-division structure linking Parent Group &rarr; Campus &rarr; Academic Division &rarr; Programmes &rarr; Sections
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            padding: '0.35rem 0.8rem',
            borderRadius: '20px',
            background: divs.length > 0 ? '#F9F5FF' : '#F8FAFC',
            color: divs.length > 0 ? '#6941C6' : '#475467',
            border: `1px solid ${divs.length > 0 ? '#E9D7FE' : '#EAECF0'}`
          }}>
            {divs.length > 0 ? `${divs.length} Integrated Divisions` : 'Standalone Campus'}
          </span>
        </div>
      </div>

      {/* Multi-Division Architecture Visual Breadcrumb */}
      <div style={{
        background: '#F8FAFC',
        border: '1px solid #EAECF0',
        borderRadius: '8px',
        padding: '0.85rem 1.25rem',
        marginBottom: '1.5rem',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        flexWrap: 'wrap',
        fontSize: '0.825rem',
        color: '#475467'
      }}>
        <span style={{ fontWeight: 700, color: '#102B46' }}>Governance Model:</span>
        <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>Parent Group</span>
        <span>→</span>
        <span style={{ background: '#F0FDF4', color: '#15803D', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>Campus</span>
        <span>→</span>
        <span style={{ background: '#F9F5FF', color: '#6941C6', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>Academic Division</span>
        <span>→</span>
        <span style={{ background: '#FFFAEB', color: '#B54708', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>Programme</span>
        <span>→</span>
        <span style={{ background: '#FEF3F2', color: '#B42318', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 600 }}>Sections & Students</span>
      </div>

      {divs.length === 0 ? (
        <div style={{
          background: '#F8FAFC',
          border: '1px dashed #D0D5DD',
          borderRadius: '10px',
          padding: '2rem',
          textAlign: 'center'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>🏫</div>
          <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.35rem 0' }}>
            Single-Campus Autonomous Institution
          </h4>
          <p style={{ color: '#475467', margin: 0, fontSize: '0.9rem', maxWidth: '600px', marginInline: 'auto', lineHeight: 1.5 }}>
            {schoolName} operates as a unified standalone institution without auxiliary constituent divisions. All academic programmes, facilities, and student services are administered directly from the primary campus headquarters.
          </p>
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
          {divs.map((d) => (
            <div
              key={d.division_id}
              style={{
                border: '1px solid #EAECF0',
                borderRadius: '10px',
                padding: '1.35rem',
                background: '#FFFFFF',
                boxShadow: '0 1px 3px rgba(16,43,70,0.04)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.65rem' }}>
                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    padding: '0.2rem 0.55rem',
                    borderRadius: '4px',
                    background: '#F9F5FF',
                    color: '#6941C6',
                    border: '1px solid #E9D7FE'
                  }}>
                    {d.division_type}
                  </span>

                  <span style={{ fontSize: '0.72rem', color: '#667085', fontWeight: 600 }}>
                    ID: {d.division_id}
                  </span>
                </div>

                <h4 style={{ margin: '0 0 0.4rem 0', color: '#102B46', fontSize: '1.1rem', fontWeight: 700, lineHeight: 1.35 }}>
                  {d.division_name}
                </h4>

                <p style={{ margin: '0 0 0.65rem 0', fontSize: '0.825rem', color: '#475467' }}>
                  📍 {d.campus_location}
                </p>

                {d.description && (
                  <p style={{ margin: '0 0 0.75rem 0', fontSize: '0.85rem', color: '#344054', lineHeight: 1.5 }}>
                    {d.description}
                  </p>
                )}

                {d.facilities_summary && (
                  <div style={{
                    background: '#F8FAFC',
                    border: '1px solid #EAECF0',
                    borderRadius: '6px',
                    padding: '0.65rem 0.85rem',
                    fontSize: '0.8rem',
                    color: '#475467',
                    marginBottom: '0.75rem',
                    lineHeight: 1.45
                  }}>
                    <strong style={{ color: '#102B46' }}>Division Infrastructure: </strong>
                    {d.facilities_summary}
                  </div>
                )}
              </div>

              <div style={{
                borderTop: '1px solid #F2F4F7',
                paddingTop: '0.75rem',
                fontSize: '0.8rem',
                color: '#667085',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.25rem'
              }}>
                {d.head_of_division && (
                  <div>Head / Principal: <strong style={{ color: '#102B46' }}>{d.head_of_division}</strong></div>
                )}
                {d.contact_phone && (
                  <div>Direct Phone: <a href={`tel:${d.contact_phone}`} style={{ color: '#155EEF', textDecoration: 'none', fontWeight: 500 }}>{d.contact_phone}</a></div>
                )}
                {d.contact_email && (
                  <div>Official Email: <a href={`mailto:${d.contact_email}`} style={{ color: '#155EEF', textDecoration: 'none', fontWeight: 500 }}>{d.contact_email}</a></div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
