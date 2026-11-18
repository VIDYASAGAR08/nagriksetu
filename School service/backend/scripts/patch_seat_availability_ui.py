path = r'C:\Users\callm\nagriksetu\frontend\src\components\institution\LiveSeatAvailability.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update component signature
old_sig = 'export default function LiveSeatAvailability({ schoolId, schoolName, onApplyClick }) {'
new_sig = 'export default function LiveSeatAvailability({ schoolId, schoolName, onApplyClick, category, schoolType }) {'
assert old_sig in content, 'old_sig not found'
content = content.replace(old_sig, new_sig)

# 2. Add isPU helper
old_helpers = '''  const totalCapacity = data?.total_sanctioned_capacity ?? 0
  const currentStrength = data?.total_current_strength ?? 0
  const availableSeats = data?.total_available_seats ?? 0
  const academicYear = data?.academic_year || '2025-26'
  const sections = data?.seat_breakdown || []'''

new_helpers = '''  const totalCapacity = data?.total_sanctioned_capacity ?? 0
  const currentStrength = data?.total_current_strength ?? 0
  const availableSeats = data?.total_available_seats ?? 0
  const academicYear = data?.academic_year || '2026-27'
  const sections = data?.seat_breakdown || []

  const isPU = category === 'PU Colleges (11-12)' ||
               schoolType === 'PU College' ||
               data?.category === 'PU Colleges (11-12)' ||
               data?.school_type === 'PU College' ||
               (schoolName && schoolName.toLowerCase().includes('pre-university'))'''

assert old_helpers in content, 'old_helpers not found'
content = content.replace(old_helpers, new_helpers)

# 3. Update Title & Subtitle
old_header = '''            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Live Seat Availability & Quota
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
            Real-time sanctioned strength and available capacity derived directly from official institutional sections.
          </p>'''

new_header = '''            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              {isPU ? 'Pre-University Live Seat Availability & Quotas' : 'Live Seat Availability & Quota'}
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
            {isPU 
              ? 'Real-time sanctioned strength and available capacity across 1st PUC and 2nd PUC academic streams.' 
              : 'Real-time sanctioned strength and available capacity derived directly from official institutional sections.'}
          </p>'''

assert old_header in content, 'old_header not found'
content = content.replace(old_header, new_header)

# 4. Update Metric 4
old_m4 = '''              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Sections Managed
              </div>'''

new_m4 = '''              <div style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {isPU ? 'PU Sections Managed' : 'Sections Managed'}
              </div>'''

assert old_m4 in content, 'old_m4 not found'
content = content.replace(old_m4, new_m4)

# 5. Update Table Header
old_th = '''                  <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #EAECF0', textAlign: 'left', color: '#475467' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Programme / Discipline</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Standard / Year</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Section</th>'''

new_th = '''                  <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #EAECF0', textAlign: 'left', color: '#475467' }}>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Programme / Stream Combination</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{isPU ? 'PU Year / Class' : 'Standard / Year'}</th>
                    <th style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>Section</th>'''

assert old_th in content, 'old_th not found'
content = content.replace(old_th, new_th)

# 6. Update Table Rows (Programme / Stream and Standard / Year)
old_td = '''                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#102B46' }}>
                          <div>{sec.program_name || 'General Programme'}</div>
                          {sec.discipline_or_stream && (
                            <div style={{ fontSize: '0.75rem', color: '#667085' }}>
                              Stream: {sec.discipline_or_stream}
                            </div>
                          )}
                        </td>
                        <td style={{ padding: '0.75rem 1rem', color: '#344054' }}>
                          {sec.term_or_year ? `Std / Yr ${sec.term_or_year}` : (sec.semester ? `Sem ${sec.semester}` : 'All')}
                        </td>'''

new_td = '''                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#102B46' }}>
                          <div style={{ fontSize: '0.92rem' }}>{sec.program_name || 'Pre-University Programme'}</div>
                          {sec.combination_code ? (
                            <div style={{ fontSize: '0.78rem', color: '#155EEF', fontWeight: 600, marginTop: '0.2rem' }}>
                              🏷️ Combination: <strong style={{ color: '#102B46' }}>{sec.combination_code}</strong>
                              {sec.discipline_or_stream && <span style={{ color: '#475467' }}> • Stream: {sec.discipline_or_stream}</span>}
                            </div>
                          ) : sec.discipline_or_stream ? (
                            <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.2rem' }}>
                              Stream: {sec.discipline_or_stream}
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
                          ) : sec.term_or_year ? (
                            `Std / Yr ${sec.term_or_year}`
                          ) : sec.semester ? (
                            `Sem ${sec.semester}`
                          ) : (
                            'All'
                          )}
                        </td>'''

assert old_td in content, 'old_td not found'
content = content.replace(old_td, new_td)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("LiveSeatAvailability.jsx successfully patched!")
