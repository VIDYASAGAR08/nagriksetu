import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'

export default function InstitutionStudentDirectory({ schoolId, schoolName, schoolType }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [activeTier, setActiveTier] = useState('ALL')
  const [searchTerm, setSearchTerm] = useState('')

  const isHigherEd = schoolType?.includes('College') || schoolType?.includes('University')

  useEffect(() => {
    let isMounted = true
    async function loadStrength() {
      if (!schoolId) return
      try {
        setLoading(true)
        setError(null)
        const res = await apiGet(`/schools/${schoolId}/academic-strength`)
        if (isMounted) setData(res)
      } catch (err) {
        if (isMounted) setError(err.message || 'Academic strength roster could not be loaded.')
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    loadStrength()
    return () => { isMounted = false }
  }, [schoolId])

  const totalEnrolled = data?.total_enrolled_strength ?? 0
  const totalCapacity = data?.total_sanctioned_capacity ?? 0
  const utilizationPct = data?.overall_utilization_percent ?? 0
  const sections = data?.sections_roster || []
  const enrollments = data?.enrollment_breakdown || []
  const languages = data?.languages_offered || []

  // Unique tiers available in sections
  const tiers = Array.from(new Set(sections.map(s => s.education_level).filter(Boolean)))

  // Filtered sections
  const filteredSections = sections.filter(sec => {
    const matchesTier = activeTier === 'ALL' || sec.education_level === activeTier
    const q = searchTerm.toLowerCase().trim()
    const matchesQuery = !q ||
      (sec.program_name && sec.program_name.toLowerCase().includes(q)) ||
      (sec.section_name && sec.section_name.toLowerCase().includes(q)) ||
      (sec.discipline_or_stream && sec.discipline_or_stream.toLowerCase().includes(q)) ||
      (sec.combination_code && sec.combination_code.toLowerCase().includes(q))
    return matchesTier && matchesQuery
  })

  return (
    <section id="students" className="card" style={{
      padding: '2rem',
      marginBottom: '2rem',
      border: '1px solid #D0D5DD',
      borderRadius: '12px',
      background: '#FFFFFF',
      boxShadow: '0 2px 8px rgba(16,43,70,0.05)'
    }}>
      {/* Section Header */}
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
          <span style={{ fontSize: '1.6rem' }}>👥</span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Student Directory & Academic Strength
            </h2>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
              Verified aggregate student enrolments and class strength without disclosing private personal identity
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            padding: '0.35rem 0.8rem',
            borderRadius: '20px',
            background: '#EFF4FF',
            color: '#155EEF',
            border: '1px solid #B2CCFF'
          }}>
            {sections.length} Active Sections Tracked
          </span>
        </div>
      </div>

      {/* Ground Truth Privacy Protection Alert */}
      <div style={{
        background: '#F0F9FF',
        border: '1px solid #B9E6FE',
        borderRadius: '8px',
        padding: '1rem 1.25rem',
        marginBottom: '1.5rem',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.75rem'
      }}>
        <span style={{ fontSize: '1.3rem', lineHeight: 1 }}>🛡️</span>
        <div style={{ fontSize: '0.85rem', color: '#026AA2', lineHeight: 1.5 }}>
          <strong>Karnataka Education Data Privacy Safeguard:</strong> In strict compliance with public education privacy regulations, student names, phone numbers, residential addresses, Aadhaar references, and individual evaluation marks are never publicly indexed. Authorized parents can access their children’s records via verified Parent Login, and school staff access their assigned roster through the Staff Review Desk.
        </div>
      </div>

      {loading ? (
        <div style={{ padding: '3rem', textAlign: 'center' }}>
          <LoadingSpinner />
          <p style={{ color: '#667085', fontSize: '0.9rem', marginTop: '0.5rem' }}>
            Compiling verified academic strength for {schoolName}...
          </p>
        </div>
      ) : error ? (
        <div style={{
          background: '#FFF6ED',
          border: '1px solid #FDCF9E',
          borderRadius: '8px',
          padding: '1rem',
          color: '#B54708',
          fontSize: '0.875rem'
        }}>
          ⚠️ Could not load academic strength roster: {error}
        </div>
      ) : (
        <>
          {/* Key Metric Overview Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '1rem',
            marginBottom: '1.5rem'
          }}>
            <div style={{
              background: '#F8FAFC',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '1.1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>
                Total Active Enrolment
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#102B46', marginTop: '0.2rem' }}>
                {totalEnrolled.toLocaleString()}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#027A48', fontWeight: 600, marginTop: '0.15rem' }}>
                ✓ Official Active Ledgers
              </div>
            </div>

            <div style={{
              background: '#F8FAFC',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '1.1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>
                Sanctioned Capacity
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#344054', marginTop: '0.2rem' }}>
                {totalCapacity > 0 ? totalCapacity.toLocaleString() : 'N/A'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.15rem' }}>
                Regulatory Ceiling
              </div>
            </div>

            <div style={{
              background: '#F8FAFC',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '1.1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>
                Capacity Utilization
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, color: utilizationPct > 90 ? '#B54708' : '#155EEF', marginTop: '0.2rem' }}>
                {utilizationPct}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.15rem' }}>
                Enrolment vs Sanctioned
              </div>
            </div>

            <div style={{
              background: '#F8FAFC',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '1.1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>
                Languages Offered
              </div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', marginTop: '0.45rem', minHeight: '1.85rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.35rem' }}>
                {languages.map((l, i) => (
                  <span key={i} style={{ background: '#E0EAFF', color: '#3538CD', padding: '0.15rem 0.5rem', borderRadius: '4px', fontSize: '0.78rem' }}>
                    {l}
                  </span>
                ))}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.15rem' }}>
                Medium of Instruction
              </div>
            </div>
          </div>

          {/* Filter Bar: Tier Pills and Search */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '0.75rem',
            marginBottom: '1.25rem',
            background: '#F8FAFC',
            padding: '0.85rem 1rem',
            borderRadius: '8px',
            border: '1px solid #EAECF0'
          }}>
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
              <button
                onClick={() => setActiveTier('ALL')}
                style={{
                  padding: '0.35rem 0.75rem',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  borderRadius: '6px',
                  border: activeTier === 'ALL' ? '1px solid #155EEF' : '1px solid #D0D5DD',
                  background: activeTier === 'ALL' ? '#155EEF' : '#FFFFFF',
                  color: activeTier === 'ALL' ? '#FFFFFF' : '#344054',
                  cursor: 'pointer'
                }}
              >
                All Sections ({sections.length})
              </button>
              {tiers.map(t => {
                const label = t === 'school' ? 'Schools'
                  : t === 'higher_secondary' ? 'PU Colleges'
                  : t === 'diploma' ? 'Diploma'
                  : t === 'undergraduate' ? 'Undergraduate' : t
                return (
                  <button
                    key={t}
                    onClick={() => setActiveTier(t)}
                    style={{
                      padding: '0.35rem 0.75rem',
                      fontSize: '0.8rem',
                      fontWeight: 600,
                      borderRadius: '6px',
                      border: activeTier === t ? '1px solid #155EEF' : '1px solid #D0D5DD',
                      background: activeTier === t ? '#155EEF' : '#FFFFFF',
                      color: activeTier === t ? '#FFFFFF' : '#344054',
                      cursor: 'pointer'
                    }}
                  >
                    {label}
                  </button>
                )
              })}
            </div>

            <div style={{ flex: '1 1 200px', maxWidth: '320px' }}>
              <input
                type="text"
                placeholder="Search standard, section or stream..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.45rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #D0D5DD',
                  fontSize: '0.825rem',
                  boxSizing: 'border-box'
                }}
              />
            </div>
          </div>

          {/* Aggregate Student Strength Table */}
          {filteredSections.length === 0 ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#667085', background: '#F9FAFB', borderRadius: '8px' }}>
              No academic sections match the selected filter.
            </div>
          ) : (
            <div style={{ overflowX: 'auto', border: '1px solid #EAECF0', borderRadius: '8px', marginBottom: '1.75rem' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #EAECF0', textAlign: 'left', color: '#475467' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Programme & Discipline</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Level / Standard / Sem</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Section</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Sanctioned Capacity</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Active Strength</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'center', width: '160px' }}>Utilization Bar</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSections.map((sec, idx) => {
                    const cap = sec.capacity || 0
                    const str = sec.current_strength || 0
                    const pct = cap > 0 ? Math.min(100, Math.round((str / cap) * 100)) : 0
                    const isHigh = pct >= 90

                    return (
                      <tr
                        key={sec.section_id || idx}
                        style={{
                          borderBottom: idx === filteredSections.length - 1 ? 'none' : '1px solid #F2F4F7',
                          background: idx % 2 === 0 ? '#FFFFFF' : '#FCFCFD'
                        }}
                      >
                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#102B46' }}>
                          <div>{sec.program_name}</div>
                          {sec.discipline_or_stream && (
                            <div style={{ fontSize: '0.75rem', color: '#667085' }}>
                              Discipline: {sec.discipline_or_stream} {sec.combination_code ? `(${sec.combination_code})` : ''}
                            </div>
                          )}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: '#344054' }}>
                          {sec.education_level === 'school' ? `Standard ${sec.term_or_year}`
                            : sec.education_level === 'higher_secondary' ? (sec.term_or_year === 11 ? '1st PU (Class 11)' : '2nd PU (Class 12)')
                            : sec.semester ? `Year ${sec.term_or_year} • Sem ${sec.semester}` : `Year ${sec.term_or_year}`}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: '#102B46', fontWeight: 700 }}>
                          Section {sec.section_name}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#344054' }}>
                          {cap}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'right', fontWeight: 700, color: '#102B46' }}>
                          {str} Students
                        </td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <div style={{
                              flex: 1,
                              height: '8px',
                              background: '#E4E7EC',
                              borderRadius: '4px',
                              overflow: 'hidden'
                            }}>
                              <div style={{
                                width: `${pct}%`,
                                height: '100%',
                                background: isHigh ? '#F79009' : '#12B76A',
                                borderRadius: '4px'
                              }} />
                            </div>
                            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475467', width: '36px', textAlign: 'right' }}>
                              {pct}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Parent Portal & Authenticated Access Callout */}
          <div style={{
            background: '#F8FAFC',
            border: '1px solid #EAECF0',
            borderRadius: '10px',
            padding: '1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '1.25rem'
          }}>
            <div style={{ flex: 1, minWidth: '280px' }}>
              <h4 style={{ margin: '0 0 0.35rem 0', color: '#102B46', fontSize: '1.05rem', fontWeight: 700 }}>
                Are you a Parent or Guardian of an enrolled student?
              </h4>
              <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467', lineHeight: 1.5 }}>
                Sign in to your verified Parent Account to view your ward's student record, submit demographic update requests, or link new student records through institutional staff verification.
              </p>
            </div>

            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              {!isHigherEd ? (
                <Link
                  to={`/parent?school_id=${schoolId}&school_name=${encodeURIComponent(schoolName)}`}
                  style={{
                    background: '#155EEF',
                    color: '#FFFFFF',
                    padding: '0.65rem 1.25rem',
                    borderRadius: '8px',
                    fontWeight: 700,
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    boxShadow: '0 2px 6px rgba(21,94,239,0.2)'
                  }}
                >
                  Link Student via Parent Portal →
                </Link>
              ) : (
                <Link
                  to="/login"
                  style={{
                    background: '#155EEF',
                    color: '#FFFFFF',
                    padding: '0.65rem 1.25rem',
                    borderRadius: '8px',
                    fontWeight: 700,
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    boxShadow: '0 2px 6px rgba(21,94,239,0.2)'
                  }}
                >
                  Sign In to Access Student Records →
                </Link>
              )}

              <Link
                to="/schools"
                style={{
                  background: '#FFFFFF',
                  color: '#344054',
                  border: '1px solid #D0D5DD',
                  padding: '0.65rem 1rem',
                  borderRadius: '8px',
                  fontWeight: 600,
                  textDecoration: 'none',
                  fontSize: '0.875rem'
                }}
              >
                ← Browse Other Institutions
              </Link>
            </div>
          </div>
        </>
      )}
    </section>
  )
}
