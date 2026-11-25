import React, { useEffect, useState } from 'react'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'

export default function LiveSeatAvailability({ schoolId, schoolName, onApplyClick, category, schoolType }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [showApplyInfo, setShowApplyInfo] = useState(false)

  useEffect(() => {
    let isMounted = true
    async function fetchSeatData() {
      if (!schoolId) return
      try {
        setLoading(true)
        setError(null)
        const res = await apiGet(`/schools/${schoolId}/seat-availability`)
        if (isMounted) setData(res)
      } catch (err) {
        if (isMounted) setError(err.message || 'Seat availability figures could not be retrieved.')
      } finally {
        if (isMounted) setLoading(false)
      }
    }
    fetchSeatData()
    return () => { isMounted = false }
  }, [schoolId])

  const totalCapacity = data?.total_sanctioned_capacity ?? 0
  const currentStrength = data?.total_current_strength ?? 0
  const availableSeats = data?.total_available_seats ?? 0
  const academicYear = data?.academic_year || '2026-27'
  const sections = data?.seat_breakdown || []

  const isUniv = category === 'Universities' ||
                 schoolType === 'University' ||
                 data?.category === 'Universities' ||
                 data?.school_type === 'University'

  const isCollege = category === 'Degree Colleges' ||
                    schoolType === 'Degree College' ||
                    data?.category === 'Degree Colleges' ||
                    data?.school_type === 'Degree College'

  const isPU = category === 'PU Colleges (11-12)' ||
               category === 'PU Colleges' ||
               schoolType === 'PU College' ||
               data?.category === 'PU Colleges (11-12)' ||
               data?.category === 'PU Colleges' ||
               data?.school_type === 'PU College' ||
               (schoolName && schoolName.toLowerCase().includes('pre-university'))

  return (
    <section
      id="seat-availability"
      style={{
        background: '#FFFFFF',
        border: '1px solid #D0D5DD',
        borderRadius: '12px',
        padding: '1.75rem',
        marginBottom: '2rem',
        boxShadow: '0 2px 8px rgba(16,43,70,0.05)'
      }}
    >
      {/* Section Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.25rem',
        borderBottom: '1px solid #EAECF0',
        paddingBottom: '1rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
            <span style={{ fontSize: '1.35rem' }}>📊</span>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              {isUniv
                ? 'University Academic Quotas & Live Seat Availability'
                : isCollege
                ? 'Collegiate Degree Seat Quotas & Live Availability'
                : isPU
                ? 'Pre-University Live Seat Availability & Quotas'
                : 'Live Seat Availability & Quota'}
            </h2>
            <span style={{
              background: '#EFF4FF',
              color: '#155EEF',
              fontSize: '0.75rem',
              fontWeight: 700,
              padding: '0.2rem 0.6rem',
              borderRadius: '12px',
              border: '1px solid #B2CCFF'
            }}>
              AY {academicYear}
            </span>
          </div>
          <p style={{ color: '#475467', margin: 0, fontSize: '0.9rem' }}>
            {isUniv
              ? 'Real-time sanctioned strength and available capacity across university faculties, departments, and research centres.'
              : isCollege
              ? 'Real-time sanctioned strength and available capacity across collegiate undergraduate degree branches.'
              : isPU
              ? 'Real-time sanctioned strength and available capacity across 1st PUC and 2nd PUC academic streams.'
              : 'Real-time sanctioned strength and available capacity derived directly from official institutional sections.'}
          </p>
        </div>

        <button
          onClick={() => {
            if (onApplyClick) {
              onApplyClick()
            } else {
              setShowApplyInfo(true)
            }
          }}
          style={{
            background: availableSeats > 0 ? '#155EEF' : '#475467',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '8px',
            padding: '0.65rem 1.25rem',
            fontSize: '0.9rem',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            boxShadow: '0 2px 6px rgba(21,94,239,0.2)'
          }}
        >
          <span>✍️</span>
          <span>Apply for Initial Admission</span>
        </button>
      </div>

      {loading ? (
        <div style={{ padding: '2rem', textAlign: 'center' }}>
          <LoadingSpinner />
          <p style={{ color: '#667085', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Fetching verified seat quota for {schoolName || schoolId}...
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
          ⚠️ Seat quota figures are temporarily unavailable: {error}. Please contact the institution directly for current admission availability.
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
              padding: '1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Sanctioned Capacity
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#102B46', marginTop: '0.2rem' }}>
                {totalCapacity > 0 ? totalCapacity : 'N/A'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#98A2B3', marginTop: '0.15rem' }}>
                Approved regulatory capacity
              </div>
            </div>

            <div style={{
              background: '#F8FAFC',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Current Enrolment
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#344054', marginTop: '0.2rem' }}>
                {currentStrength}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#98A2B3', marginTop: '0.15rem' }}>
                Active enrolled students
              </div>
            </div>

            <div style={{
              background: availableSeats > 10 ? '#ECFDF3' : availableSeats > 0 ? '#FFFAEB' : '#FEF3F2',
              border: `1px solid ${availableSeats > 10 ? '#A6F4C5' : availableSeats > 0 ? '#FEDF89' : '#FECDCA'}`,
              borderRadius: '8px',
              padding: '1rem',
              textAlign: 'center'
            }}>
              <div style={{
                fontSize: '0.78rem',
                color: availableSeats > 10 ? '#027A48' : availableSeats > 0 ? '#B54708' : '#B42318',
                fontWeight: 700,
                textTransform: 'uppercase',
                letterSpacing: '0.04em'
              }}>
                Available Seats
              </div>
              <div style={{
                fontSize: '1.8rem',
                fontWeight: 800,
                color: availableSeats > 10 ? '#027A48' : availableSeats > 0 ? '#B54708' : '#B42318',
                marginTop: '0.2rem'
              }}>
                {availableSeats}
              </div>
              <div style={{
                fontSize: '0.75rem',
                fontWeight: 600,
                color: availableSeats > 10 ? '#027A48' : availableSeats > 0 ? '#B54708' : '#B42318',
                marginTop: '0.15rem'
              }}>
                {availableSeats > 10 ? '● Admissions Open' : availableSeats > 0 ? '▲ Limited Capacity' : '■ Quota Full / Waitlist'}
              </div>
            </div>

            <div style={{
              background: '#F8FAFC',
              border: '1px solid #EAECF0',
              borderRadius: '8px',
              padding: '1rem',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {isUniv ? 'Academic Batches' : isCollege ? 'Degree Sections' : isPU ? 'PU Sections' : 'Sections'}
              </div>
              <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#102B46', marginTop: '0.2rem' }}>
                {sections.length}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#98A2B3', marginTop: '0.15rem' }}>
                Sections / batches tracked
              </div>
            </div>
          </div>

          {/* Detailed Section Breakdown Table */}
          {sections.length === 0 ? (
            <div style={{
              padding: '1.5rem',
              background: '#F9FAFB',
              borderRadius: '8px',
              textAlign: 'center',
              color: '#667085',
              fontSize: '0.9rem'
            }}>
              ℹ️ Standard section capacity breakdown has not yet been itemized by institutional administrators for {academicYear}.
            </div>
          ) : (
            <div style={{ overflowX: 'auto', border: '1px solid #EAECF0', borderRadius: '8px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #EAECF0', textAlign: 'left', color: '#475467' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Programme / Course Branch</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>
                      {isUniv ? 'Academic Level & Year' : isCollege ? 'Academic Year' : isPU ? 'PU Year / Class' : 'Standard / Year'}
                    </th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Section / Batch</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Capacity</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Enrolled</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'right' }}>Available</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600, textAlign: 'center' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {sections.map((sec, idx) => {
                    const secAvail = sec.available_seats ?? Math.max(0, (sec.capacity || 0) - (sec.current_strength || 0))
                    const isFull = secAvail <= 0
                    const isLimited = secAvail > 0 && secAvail <= 5

                    return (
                      <tr
                        key={sec.section_id || idx}
                        style={{
                          borderBottom: idx === sections.length - 1 ? 'none' : '1px solid #F2F4F7',
                          background: idx % 2 === 0 ? '#FFFFFF' : '#FCFCFD'
                        }}
                      >
                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#102B46' }}>
                          <div style={{ fontSize: '0.92rem' }}>{sec.program_name || 'Academic Programme'}</div>
                          {sec.combination_code ? (
                            <div style={{ fontSize: '0.78rem', color: '#155EEF', fontWeight: 600, marginTop: '0.2rem' }}>
                              🏷️ Combination: <strong style={{ color: '#102B46' }}>{sec.combination_code}</strong>
                              {sec.discipline_or_stream && <span style={{ color: '#475467' }}> • Stream: {sec.discipline_or_stream}</span>}
                            </div>
                          ) : sec.discipline_or_stream ? (
                            <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.2rem' }}>
                              Branch: {sec.discipline_or_stream}
                            </div>
                          ) : null}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: '#344054', fontWeight: 600 }}>
                          {isPU || sec.education_level === 'higher_secondary' ? (
                            sec.term_or_year === 11 || sec.term_or_year === '11' ? (
                              <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.2rem 0.55rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>
                                1st PUC (Class 11)
                              </span>
                            ) : sec.term_or_year === 12 || sec.term_or_year === '12' ? (
                              <span style={{ background: '#FDF2FA', color: '#C11574', padding: '0.2rem 0.55rem', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 700 }}>
                                2nd PUC (Class 12)
                              </span>
                            ) : (
                              `PU Year ${sec.term_or_year}`
                            )
                          ) : isUniv ? (
                            sec.education_level === 'doctoral' ? (
                              <span style={{ background: '#ECFDF3', color: '#027A48', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.78rem', fontWeight: 700 }}>
                                Ph.D. Research
                              </span>
                            ) : sec.education_level === 'postgraduate' ? (
                              <span style={{ background: '#F9F5FF', color: '#6941C6', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.78rem', fontWeight: 700 }}>
                                PG Year {sec.term_or_year || 1}
                              </span>
                            ) : (
                              <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.78rem', fontWeight: 700 }}>
                                UG Year {sec.term_or_year || 1}
                              </span>
                            )
                          ) : isCollege ? (
                            <span style={{ background: '#EFF8FF', color: '#175CD3', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.78rem', fontWeight: 700 }}>
                              Year {sec.term_or_year || 1}
                            </span>
                          ) : sec.term_or_year ? (
                            `Std / Yr ${sec.term_or_year}`
                          ) : sec.semester ? (
                            `Sem ${sec.semester}`
                          ) : (
                            'All'
                          )}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: '#344054', fontWeight: 600 }}>
                          Section {sec.section_name || 'A'}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#344054' }}>
                          {sec.capacity ?? '—'}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'right', color: '#344054' }}>
                          {sec.current_strength ?? 0}
                        </td>
                        <td style={{
                          padding: '0.75rem 1rem',
                          textAlign: 'right',
                          fontWeight: 700,
                          color: isFull ? '#B42318' : isLimited ? '#B54708' : '#027A48'
                        }}>
                          {secAvail}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>
                          <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 700,
                            padding: '0.2rem 0.55rem',
                            borderRadius: '4px',
                            background: isFull ? '#FEF3F2' : isLimited ? '#FFFAEB' : '#ECFDF3',
                            color: isFull ? '#B42318' : isLimited ? '#B54708' : '#027A48',
                            border: `1px solid ${isFull ? '#FECDCA' : isLimited ? '#FEDF89' : '#A6F4C5'}`
                          }}>
                            {isFull ? 'Waitlist' : isLimited ? 'Few Left' : 'Available'}
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  )
}
