import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'

export default function InstitutionCompareModal({
  isOpen,
  onClose,
  schoolIds = [],
  onRemoveSchool
}) {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!isOpen || schoolIds.length === 0) return

    async function fetchComparison() {
      try {
        setLoading(true)
        setError(null)
        const res = await apiPost('/schools/compare', { school_ids: schoolIds })
        // res is a list of school records with enriched details
        setData(Array.isArray(res) ? res : res.schools || [])
      } catch (err) {
        setError(err.message || 'Failed to generate comparison matrix.')
      } finally {
        setLoading(false)
      }
    }

    fetchComparison()
  }, [isOpen, schoolIds])

  if (!isOpen) return null

  function formatBool(val, labelTrue = 'Available', labelFalse = 'Not Available') {
    if (val === true || val === 'yes' || val === 'available') {
      return <span style={{ color: '#027A48', fontWeight: 600 }}>✓ {labelTrue}</span>
    }
    if (val === false || val === 'no' || val === 'not_available') {
      return <span style={{ color: '#98A2B3' }}>— {labelFalse}</span>
    }
    return <span style={{ color: '#667085' }}>{val || 'Not Disclosed'}</span>
  }

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(16, 43, 70, 0.75)',
        backdropFilter: 'blur(4px)',
        zIndex: 2000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem'
      }}
    >
      <div
        style={{
          background: '#FFFFFF',
          borderRadius: '14px',
          width: '100%',
          maxWidth: '1360px',
          height: '92vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.35)',
          overflow: 'hidden'
        }}
      >
        {/* Modal Header */}
        <div style={{
          padding: '1.25rem 2rem',
          background: '#102B46',
          color: '#FFFFFF',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexShrink: 0
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ fontSize: '1.4rem' }}>⚖️</span>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0, color: '#FFFFFF' }}>
                Institution Comparison Matrix
              </h2>
              <span style={{
                background: '#155EEF',
                color: '#FFFFFF',
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px'
              }}>
                {data.length} Institutions
              </span>
            </div>
            <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.825rem', color: '#CBD5E1' }}>
              Side-by-side evidence-based comparison of facilities, verified seat quota, accommodation and academics.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              onClick={() => window.print()}
              style={{
                background: 'rgba(255, 255, 255, 0.15)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                color: '#FFFFFF',
                borderRadius: '6px',
                padding: '0.45rem 0.9rem',
                fontSize: '0.825rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              🖨️ Print Matrix
            </button>
            <button
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: '#FFFFFF',
                fontSize: '1.6rem',
                cursor: 'pointer',
                padding: '0 0.5rem',
                lineHeight: 1
              }}
            >
              ✕
            </button>
          </div>
        </div>

        {/* Modal Body / Scrollable Table */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem 2rem' }}>
          {loading ? (
            <div style={{ padding: '6rem 0', textAlign: 'center' }}>
              <LoadingSpinner />
              <p style={{ marginTop: '1rem', color: '#667085', fontSize: '0.95rem' }}>
                Compiling multi-institution side-by-side matrix...
              </p>
            </div>
          ) : error ? (
            <div style={{
              background: '#FFF6ED',
              border: '1px solid #FDCF9E',
              borderRadius: '8px',
              padding: '1.5rem',
              color: '#B54708',
              margin: '2rem 0'
            }}>
              ⚠️ Error compiling comparison: {error}
            </div>
          ) : data.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem 0', color: '#667085' }}>
              No institutions selected for comparison.
            </div>
          ) : (
            <div style={{ overflowX: 'auto', border: '1px solid #EAECF0', borderRadius: '10px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                {/* Column Headers: Institution Cards */}
                <thead>
                  <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #D0D5DD' }}>
                    <th style={{
                      position: 'sticky',
                      left: 0,
                      background: '#F8FAFC',
                      zIndex: 3,
                      padding: '1rem 1.25rem',
                      textAlign: 'left',
                      minWidth: '220px',
                      color: '#475467',
                      fontWeight: 700,
                      borderRight: '1px solid #EAECF0'
                    }}>
                      Key Criteria
                    </th>

                    {data.map((inst) => (
                      <th
                        key={inst.school_id}
                        style={{
                          padding: '1.25rem',
                          textAlign: 'left',
                          minWidth: '260px',
                          maxWidth: '300px',
                          verticalAlign: 'top',
                          borderRight: '1px solid #EAECF0',
                          background: '#FFFFFF'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                          <span style={{
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            padding: '0.15rem 0.45rem',
                            borderRadius: '4px',
                            background: '#EFF4FF',
                            color: '#155EEF'
                          }}>
                            {inst.school_id}
                          </span>

                          {data.length > 2 && (
                            <button
                              onClick={() => onRemoveSchool(inst.school_id)}
                              title="Remove column"
                              style={{
                                background: 'none',
                                border: 'none',
                                color: '#98A2B3',
                                cursor: 'pointer',
                                fontSize: '0.85rem'
                              }}
                            >
                              ✕
                            </button>
                          )}
                        </div>

                        <div style={{ fontSize: '1.05rem', fontWeight: 800, color: '#102B46', lineHeight: 1.3, marginBottom: '0.35rem' }}>
                          {inst.school_name}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#667085', marginBottom: '0.65rem' }}>
                          📍 {inst.district}, {inst.state}
                        </div>

                        <Link
                          to={`/schools/${inst.school_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: '0.78rem',
                            color: '#155EEF',
                            fontWeight: 700,
                            textDecoration: 'none'
                          }}
                        >
                          Open Profile ↗
                        </Link>
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {/* SECTION 1: LIVE SEAT AVAILABILITY */}
                  <tr style={{ background: '#EFF4FF', fontWeight: 700, color: '#155EEF' }}>
                    <td colSpan={data.length + 1} style={{ padding: '0.6rem 1.25rem', fontSize: '0.825rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      📊 Live Seat Availability (AY 2025–26)
                    </td>
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Available Seats
                    </td>
                    {data.map((inst) => {
                      const avail = inst.seat_summary?.available_seats ?? 0
                      const isFull = avail <= 0
                      const isLimited = avail > 0 && avail <= 10
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          <span style={{
                            fontSize: '0.8rem',
                            fontWeight: 700,
                            padding: '0.25rem 0.65rem',
                            borderRadius: '12px',
                            background: isFull ? '#FEF3F2' : isLimited ? '#FFFAEB' : '#ECFDF3',
                            color: isFull ? '#B42318' : isLimited ? '#B54708' : '#027A48',
                            border: `1px solid ${isFull ? '#FECDCA' : isLimited ? '#FEDF89' : '#A6F4C5'}`
                          }}>
                            {isFull ? '🔴 0 Seats (Full)' : isLimited ? `🟡 ${avail} Seats (Limited)` : `🟢 ${avail} Seats Open`}
                          </span>
                        </td>
                      )
                    })}
                  </tr>

                  <tr style={{ background: '#FAFAFA' }}>
                    <td style={{ position: 'sticky', left: 0, background: '#FAFAFA', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Sanctioned Capacity
                    </td>
                    {data.map((inst) => (
                      <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0', color: '#102B46', fontWeight: 600 }}>
                        {inst.seat_summary?.sanctioned_capacity ?? 'N/A'} Seats
                      </td>
                    ))}
                  </tr>

                  {/* SECTION 2: INSTITUTION PROFILE & RECOGNITION */}
                  <tr style={{ background: '#F2F4F7', fontWeight: 700, color: '#344054' }}>
                    <td colSpan={data.length + 1} style={{ padding: '0.6rem 1.25rem', fontSize: '0.825rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      🏛️ Institution Profile & Governance
                    </td>
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Institution Type
                    </td>
                    {data.map((inst) => (
                      <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0', color: '#102B46' }}>
                        {inst.school_type}
                      </td>
                    ))}
                  </tr>

                  <tr style={{ background: '#FAFAFA' }}>
                    <td style={{ position: 'sticky', left: 0, background: '#FAFAFA', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Board / Regulatory Body
                    </td>
                    {data.map((inst) => (
                      <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0', color: '#155EEF', fontWeight: 600 }}>
                        {inst.affiliation || 'Department of School Education'}
                      </td>
                    ))}
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Established Year
                    </td>
                    {data.map((inst) => (
                      <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0', color: '#475467' }}>
                        {inst.established_year || 'Disclosed'}
                      </td>
                    ))}
                  </tr>

                  {/* SECTION 3: FACILITIES & INFRASTRUCTURE */}
                  <tr style={{ background: '#F2F4F7', fontWeight: 700, color: '#344054' }}>
                    <td colSpan={data.length + 1} style={{ padding: '0.6rem 1.25rem', fontSize: '0.825rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      🏢 Infrastructure & Amenities
                    </td>
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Science & Tech Labs
                    </td>
                    {data.map((inst) => {
                      const fac = inst.facilities || {}
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          {formatBool(fac.science_labs ?? fac.has_science_lab)}
                        </td>
                      )
                    })}
                  </tr>

                  <tr style={{ background: '#FAFAFA' }}>
                    <td style={{ position: 'sticky', left: 0, background: '#FAFAFA', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Computer Labs & Digital ICT
                    </td>
                    {data.map((inst) => {
                      const fac = inst.facilities || {}
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          {formatBool(fac.computer_labs ?? fac.has_computer_lab)}
                        </td>
                      )
                    })}
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Library & Reading Room
                    </td>
                    {data.map((inst) => {
                      const fac = inst.facilities || {}
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          {formatBool(fac.library ?? fac.has_library)}
                        </td>
                      )
                    })}
                  </tr>

                  <tr style={{ background: '#FAFAFA' }}>
                    <td style={{ position: 'sticky', left: 0, background: '#FAFAFA', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Sports Grounds & Courts
                    </td>
                    {data.map((inst) => {
                      const fac = inst.facilities || {}
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          {formatBool(fac.playground ?? fac.sports_facilities)}
                        </td>
                      )
                    })}
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Accessibility & Security
                    </td>
                    {data.map((inst) => {
                      const fac = inst.facilities || {}
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0', fontSize: '0.8rem' }}>
                          <div>🛡️ CCTV: {fac.cctv_surveillance ? 'Active' : 'Disclosed'}</div>
                          <div>♿ Ramps: {fac.ramp_accessibility ? 'Yes' : 'Disclosed'}</div>
                        </td>
                      )
                    })}
                  </tr>

                  {/* SECTION 4: RESIDENTIAL & TRANSPORT */}
                  <tr style={{ background: '#F2F4F7', fontWeight: 700, color: '#344054' }}>
                    <td colSpan={data.length + 1} style={{ padding: '0.6rem 1.25rem', fontSize: '0.825rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                      🚌 Accommodation & Transportation
                    </td>
                  </tr>

                  <tr>
                    <td style={{ position: 'sticky', left: 0, background: '#FFFFFF', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      Hostel / Residential
                    </td>
                    {data.map((inst) => {
                      const h = inst.hostel || {}
                      const hasHostel = h.available || h.boys_hostel || h.girls_hostel
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          {hasHostel ? (
                            <span style={{ color: '#027A48', fontWeight: 600 }}>
                              ✓ Available ({h.boys_capacity ? `B: ${h.boys_capacity}` : ''} {h.girls_capacity ? `G: ${h.girls_capacity}` : ''})
                            </span>
                          ) : (
                            <span style={{ color: '#667085' }}>Day Scholar Only</span>
                          )}
                        </td>
                      )
                    })}
                  </tr>

                  <tr style={{ background: '#FAFAFA' }}>
                    <td style={{ position: 'sticky', left: 0, background: '#FAFAFA', padding: '0.75rem 1.25rem', fontWeight: 600, color: '#344054', borderRight: '1px solid #EAECF0' }}>
                      School Bus Fleet
                    </td>
                    {data.map((inst) => {
                      const t = inst.transport || {}
                      return (
                        <td key={inst.school_id} style={{ padding: '0.75rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                          {t.available ? (
                            <span style={{ color: '#027A48', fontWeight: 600 }}>
                              ✓ {t.buses_count ? `${t.buses_count} Buses Operational` : 'Transport Available'}
                            </span>
                          ) : (
                            <span style={{ color: '#667085' }}>Self / Public Transport</span>
                          )}
                        </td>
                      )
                    })}
                  </tr>

                  {/* SECTION 5: CONTACT & ADMISSION ACTION */}
                  <tr style={{ background: '#F8FAFC', borderTop: '2px solid #EAECF0' }}>
                    <td style={{ position: 'sticky', left: 0, background: '#F8FAFC', padding: '1rem 1.25rem', fontWeight: 700, color: '#102B46', borderRight: '1px solid #EAECF0' }}>
                      Direct Action
                    </td>
                    {data.map((inst) => (
                      <td key={inst.school_id} style={{ padding: '1rem 1.25rem', borderRight: '1px solid #EAECF0' }}>
                        <Link
                          to={`/schools/${inst.school_id}`}
                          onClick={onClose}
                          style={{
                            display: 'block',
                            background: '#155EEF',
                            color: '#FFFFFF',
                            textAlign: 'center',
                            padding: '0.6rem 1rem',
                            borderRadius: '6px',
                            fontWeight: 700,
                            textDecoration: 'none',
                            fontSize: '0.85rem',
                            boxShadow: '0 2px 4px rgba(21,94,239,0.2)'
                          }}
                        >
                          View & Apply →
                        </Link>
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div style={{
          padding: '1rem 2rem',
          background: '#F8FAFC',
          borderTop: '1px solid #EAECF0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexShrink: 0
        }}>
          <div style={{ fontSize: '0.78rem', color: '#667085' }}>
            ℹ️ All institutional capacity figures are dynamically synchronized with official section allocations. NagrikSetu does not rank or promote individual institutions.
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#344054',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              padding: '0.5rem 1.25rem',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            Close Matrix
          </button>
        </div>
      </div>
    </div>
  )
}
