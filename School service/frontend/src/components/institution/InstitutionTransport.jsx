import React from 'react'

export default function InstitutionTransport({ transport }) {
  const t = transport || {}
  const isAvailable = Boolean(t.available && t.fleet_size > 0)
  const routes = Array.isArray(t.routes) ? t.routes : []

  return (
    <section id="transport" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #d0d5dd',
      borderRadius: '12px',
      background: '#ffffff',
      boxShadow: '0 2px 6px rgba(0,0,0,0.04)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem', borderBottom: '2px solid #e8eaed', paddingBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span style={{ fontSize: '1.5rem' }}>🚌</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#1a3a6b', margin: 0 }}>
              Transportation & Bus Fleet
            </h2>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
              Institutional transit network, fleet details, daily routes, and coordinator contacts
            </p>
          </div>
        </div>

        <div>
          {isAvailable ? (
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              {t.gps_enabled && (
                <span style={{
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  padding: '0.3rem 0.65rem',
                  borderRadius: '20px',
                  background: '#e0e7ff',
                  color: '#3730a3',
                  border: '1px solid #c7d2fe'
                }}>
                  📡 GPS Tracked
                </span>
              )}
              <span style={{
                fontSize: '0.85rem',
                fontWeight: 700,
                padding: '0.35rem 0.75rem',
                borderRadius: '20px',
                background: '#dcfce7',
                color: '#15803d',
                border: '1px solid #bbf7d0'
              }}>
                ✓ Bus Service Available ({t.fleet_size} Buses)
              </span>
            </div>
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
              Public Transit Transit Zone
            </span>
          )}
        </div>
      </div>

      {!isAvailable ? (
        <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', color: '#4b5563' }}>
          <p style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem' }}>
            {t.transport_coordinator || 'This institution is centrally situated near public transit hubs (BMTC/KSRTC and Namma Metro stations). Institutional dedicated bus fleets are not operated.'}
          </p>
          <p style={{ margin: 0, fontSize: '0.85rem', color: '#6b7280' }}>
            Students are eligible for subsidized state government and student bus passes.
          </p>
        </div>
      ) : (
        <div>
          {/* Key Transport Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: '#eff6ff', padding: '1rem', borderRadius: '8px', border: '1px solid #bfdbfe' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#1d4ed8' }}>Fleet Strength</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#1e40af' }}>{t.fleet_size} Dedicated Buses</div>
            </div>

            <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#15803d' }}>Live Safety</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#166534' }}>{t.gps_enabled ? 'GPS & Speed Governor' : 'Regulated'}</div>
            </div>

            <div style={{ background: '#faf5ff', padding: '1rem', borderRadius: '8px', border: '1px solid #e9d5ff' }}>
              <div style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#7e22ce' }}>Transport Desk</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#6b21a8', marginTop: '0.25rem' }}>
                {t.transport_coordinator || 'Campus Transport Office'}
              </div>
            </div>
          </div>

          {/* Active Route Cards */}
          {routes.length > 0 && (
            <div>
              <h4 style={{ margin: '0 0 0.75rem 0', color: '#1a3a6b', fontSize: '1rem', fontWeight: 700 }}>
                Major Campus Transit Routes:
              </h4>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1rem' }}>
                {routes.map((rt, idx) => (
                  <div key={idx} style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '1rem',
                    background: '#f8fafc'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#1a3a6b', background: '#e2e8f0', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                        {rt.route_number}
                      </span>
                      <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#15803d' }}>
                        ⏱️ Starts: {rt.pickup_time}
                      </span>
                    </div>

                    <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#1f2937', marginBottom: '0.35rem' }}>
                      Origin: {rt.origin}
                    </div>

                    <div style={{ fontSize: '0.8rem', color: '#4b5563', lineHeight: 1.4 }}>
                      <span style={{ fontWeight: 600 }}>Key Stops: </span>
                      {Array.isArray(rt.stops) ? rt.stops.join(' → ') : rt.stops}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
