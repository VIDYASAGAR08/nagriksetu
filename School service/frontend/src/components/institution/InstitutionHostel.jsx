import React from 'react'

export default function InstitutionHostel({ hostel }) {
  const h = hostel || {}
  const isAvailable = Boolean(h.available)

  return (
    <section id="hostel" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      background: '#ffffff',
      boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem', borderBottom: '2px solid #e8eaed', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🛏️</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1a3a6b', margin: 0 }}>
              Hostel & Residential Accommodation
            </h2>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
              Student residential boarding, dining, safety, and warden supervision
            </p>
          </div>
        </div>

        <div>
          {isAvailable ? (
            <span style={{
              fontSize: '0.85rem',
              fontWeight: 700,
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              background: '#dcfce7',
              color: '#15803d',
              border: '1px solid #bbf7d0'
            }}>
              ✓ On-Campus Hostel Available
            </span>
          ) : (
            <span style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              padding: '0.35rem 0.75rem',
              borderRadius: '20px',
              background: '#f3f4f6',
              color: '#6b7280',
              border: '1px solid #e5e7eb'
            }}>
              Day Scholar Institution (No Hostel)
            </span>
          )}
        </div>
      </div>

      {!isAvailable ? (
        <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', textAlign: 'center', color: '#4b5563' }}>
          <p style={{ margin: 0, fontSize: '0.95rem' }}>
            This institution operates exclusively as a <strong>Day-Scholar Institution</strong>. Residential hostel accommodation is not provided on campus.
          </p>
        </div>
      ) : (
        <div>
          {/* Capacity and Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: '#eff6ff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#1d4ed8', marginBottom: '0.25rem' }}>
                Boys' Hostel Capacity
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#1e40af' }}>
                {h.boys_capacity ? `${h.boys_capacity.toLocaleString()} Beds` : 'Capacity on request'}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#3b82f6', marginTop: '0.25rem' }}>
                Resident Wardens & Security
              </div>
            </div>

            <div style={{ background: '#fdf2f8', padding: '1.25rem', borderRadius: '8px', border: '1px solid #fbcfe8' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#db2777', marginBottom: '0.25rem' }}>
                Girls' Hostel Capacity
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#be185d' }}>
                {h.girls_capacity ? `${h.girls_capacity.toLocaleString()} Beds` : 'Capacity on request'}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#ec4899', marginTop: '0.25rem' }}>
                24/7 Dedicated Female Wardens
              </div>
            </div>

            <div style={{ background: '#f0fdf4', padding: '1.25rem', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#15803d', marginBottom: '0.25rem' }}>
                Hostel Administration
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#166534', marginTop: '0.25rem' }}>
                {h.contact_phone || 'Contact Admissions'}
              </div>
              <div style={{ fontSize: '0.8rem', color: '#22c55e', marginTop: '0.25rem' }}>
                Official Desk & Grievance Cell
              </div>
            </div>
          </div>

          {/* Dining and Supervision Details */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '1.25rem' }}>
            {h.food_details && (
              <div style={{ background: '#f9fafb', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  🥗 Mess & Nutrition
                </h4>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.5 }}>
                  {h.food_details}
                </p>
              </div>
            )}

            {h.supervision && (
              <div style={{ background: '#f9fafb', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  🛡️ Warden Supervision & Safety
                </h4>
                <p style={{ margin: 0, fontSize: '0.875rem', color: '#4b5563', lineHeight: 1.5 }}>
                  {h.supervision}
                </p>
              </div>
            )}
          </div>

          {/* Amenities Pills */}
          {Array.isArray(h.amenities) && h.amenities.length > 0 && (
            <div>
              <h4 style={{ margin: '0 0 0.5rem 0', color: '#1a3a6b', fontSize: '0.9rem', fontWeight: 700 }}>
                Included Residential Amenities:
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {h.amenities.map((amenity, idx) => (
                  <span key={idx} style={{
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    background: '#e0e7ff',
                    color: '#3730a3',
                    padding: '0.35rem 0.75rem',
                    borderRadius: '6px',
                    border: '1px solid #c7d2fe'
                  }}>
                    ✓ {amenity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
