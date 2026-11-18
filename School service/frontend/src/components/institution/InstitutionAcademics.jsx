import React, { useState, useMemo } from 'react'

export default function InstitutionAcademics({
  programs = [],
  schoolType = '',
  category = '',
  affiliation = '',
  recognition = '',
  schoolName = ''
}) {
  const isUniv = category === 'Universities' || schoolType === 'University'
  const isCollege = category === 'Degree Colleges' || schoolType === 'Degree College'
  const isPU = category === 'PU Colleges (11-12)' ||
               schoolType === 'PU College' ||
               (programs && programs.length > 0 && programs.every(p => p.education_level === 'higher_secondary'))
  const isSchool = category === 'Schools (K-10)' || schoolType === 'School'

  const [selectedLevel, setSelectedLevel] = useState('ALL')
  const [selectedFaculty, setSelectedFaculty] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')

  // Filter programs based on user controls
  const filtered = useMemo(() => {
    return (programs || []).filter(p => {
      const matchesLevel = selectedLevel === 'ALL' || p.education_level === selectedLevel
      const matchesFaculty = selectedFaculty === 'ALL' || (p.faculty_name || 'General') === selectedFaculty
      const q = searchQuery.toLowerCase().trim()
      const matchesSearch = !q ||
        (p.program_name && p.program_name.toLowerCase().includes(q)) ||
        (p.degree_type && p.degree_type.toLowerCase().includes(q)) ||
        (p.discipline_or_stream && p.discipline_or_stream.toLowerCase().includes(q)) ||
        (p.department_name && p.department_name.toLowerCase().includes(q)) ||
        (p.faculty_name && p.faculty_name.toLowerCase().includes(q)) ||
        (p.combination_code && p.combination_code.toLowerCase().includes(q))
      return matchesLevel && matchesFaculty && matchesSearch
    })
  }, [programs, selectedLevel, selectedFaculty, searchQuery])

  // Available faculties for universities
  const availableFaculties = useMemo(() => {
    const set = new Set((programs || []).map(p => p.faculty_name).filter(Boolean))
    return Array.from(set)
  }, [programs])

  // Available levels
  const availableLevels = useMemo(() => {
    const set = new Set((programs || []).map(p => p.education_level).filter(Boolean))
    return Array.from(set)
  }, [programs])

  // University Hierarchy Grouping: Faculty -> Department -> Programmes
  const universityHierarchy = useMemo(() => {
    if (!isUniv) return {}
    const hierarchy = {}

    filtered.forEach(p => {
      const facName = p.faculty_name || 'Faculty of General Studies'
      const deptName = p.department_name || p.discipline_or_stream || 'Department of Interdisciplinary Studies'

      if (!hierarchy[facName]) {
        hierarchy[facName] = {
          faculty_name: facName,
          departments: {}
        }
      }

      if (!hierarchy[facName].departments[deptName]) {
        hierarchy[facName].departments[deptName] = {
          department_name: deptName,
          programmes: []
        }
      }

      hierarchy[facName].departments[deptName].programmes.push(p)
    })

    return hierarchy
  }, [isUniv, filtered])

  // Standard flat grouping by level for non-university
  const groupedByLevel = useMemo(() => {
    if (isUniv) return {}
    const map = {}
    filtered.forEach(p => {
      const lvl = p.education_level || 'other'
      if (!map[lvl]) map[lvl] = []
      map[lvl].push(p)
    })
    return map
  }, [isUniv, filtered])

  const levelLabels = {
    school: 'School Education (Standards 1–10)',
    higher_secondary: 'Pre-University Education (1st PUC & 2nd PUC)',
    diploma: 'Polytechnic Diploma Curricula',
    undergraduate: 'Undergraduate Degree Programmes (3–4 Years)',
    postgraduate: 'Postgraduate Degree Programmes (2 Years)',
    doctoral: 'Doctoral / Ph.D. Research Programmes (3+ Years)'
  }

  return (
    <section id="academics" className="card" style={{
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
          <span style={{ fontSize: '1.6rem' }}>
            {isUniv ? '🏛️' : isCollege ? '🎓' : isPU ? '🏫' : '📚'}
          </span>
          <div>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              {isUniv
                ? 'University Academic Structure & Faculty Hierarchy'
                : isCollege
                ? 'Undergraduate Degree Programmes & Course Curricula'
                : isPU
                ? 'Pre-University Academic Streams & Combinations'
                : 'Academic Structure & Programme Curricula'}
            </h2>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#475467' }}>
              {isUniv
                ? 'Degree-awarding university structure organised hierarchically: University ➔ Faculty ➔ Department ➔ Programme ➔ Level.'
                : isCollege
                ? `Approved collegiate degree curricula offering undergraduate programmes affiliated with ${affiliation || 'State University'}.`
                : isPU
                ? 'Department of Pre-University Education (DPUE) approved combinations across Science, Commerce, and Arts streams.'
                : 'Recognized state curricula across school standards and learning streams.'}
            </p>
          </div>
        </div>

        <div>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 700,
            padding: '0.35rem 0.8rem',
            borderRadius: '20px',
            background: isUniv ? '#F9F5FF' : isCollege ? '#EFF4FF' : isPU ? '#FDF2FA' : '#F0FDF4',
            color: isUniv ? '#6941C6' : isCollege ? '#155EEF' : isPU ? '#C11574' : '#15803D',
            border: `1px solid ${isUniv ? '#E9D7FE' : isCollege ? '#B2CCFF' : isPU ? '#FCE7F6' : '#BBF7D0'}`
          }}>
            {programs?.length || 0} {isUniv ? 'Hierarchical Programmes' : isCollege ? 'Degree Courses Configured' : isPU ? 'PU Combinations' : 'Programmes'}
          </span>
        </div>
      </div>

      {/* Distinction Callout: Degree College Affiliation vs University Degree-Awarding Status */}
      {isCollege && (
        <div style={{
          background: '#EFF8FF',
          border: '1px solid #B2DDFF',
          borderRadius: '8px',
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.4rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.25rem' }}>🏛️</span>
              <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#175CD3' }}>
                University Affiliation:
              </span>
              <strong style={{ fontSize: '0.95rem', color: '#102B46' }}>
                {affiliation || 'Visvesvaraya Technological University (VTU), Belagavi'}
              </strong>
            </div>
            {recognition && (
              <span style={{
                background: '#FFFFFF',
                border: '1px solid #B2DDFF',
                color: '#175CD3',
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px'
              }}>
                ✓ {recognition}
              </span>
            )}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#1E40AF', lineHeight: 1.45 }}>
            <strong>Important Statutory Distinction:</strong> {schoolName || 'This institution'} is an autonomous affiliated Degree College offering undergraduate courses under <strong>{affiliation}</strong>. Academic degrees are conferred and certified by the affiliating university upon programme completion.
          </div>
        </div>
      )}

      {isUniv && (
        <div style={{
          background: '#F9F5FF',
          border: '1px solid #E9D7FE',
          borderRadius: '8px',
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          gap: '0.5rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ fontSize: '1.25rem' }}>👑</span>
              <span style={{ fontSize: '0.95rem', fontWeight: 800, color: '#6941C6' }}>
                Degree-Awarding Higher Education University
              </span>
            </div>
            {affiliation && (
              <span style={{
                background: '#FFFFFF',
                border: '1px solid #D6BBFB',
                color: '#6941C6',
                fontSize: '0.75rem',
                fontWeight: 700,
                padding: '0.2rem 0.6rem',
                borderRadius: '12px'
              }}>
                Statutory Charter: {affiliation}
              </span>
            )}
          </div>
          {/* Visual Academic Hierarchy Breadcrumb */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            flexWrap: 'wrap',
            fontSize: '0.78rem',
            color: '#475467',
            background: '#FFFFFF',
            padding: '0.5rem 0.75rem',
            borderRadius: '6px',
            border: '1px solid #EAECF0'
          }}>
            <span style={{ fontWeight: 700, color: '#102B46' }}>Academic Architecture:</span>
            <span style={{ background: '#F9F5FF', color: '#6941C6', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>University</span>
            <span>➔</span>
            <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>Faculty / School</span>
            <span>➔</span>
            <span style={{ background: '#ECFDF3', color: '#027A48', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>Department</span>
            <span>➔</span>
            <span style={{ background: '#FFFAEB', color: '#B54708', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>Programme (UG / PG / Doctoral)</span>
            <span>➔</span>
            <span style={{ background: '#F8FAFC', color: '#344054', padding: '0.15rem 0.45rem', borderRadius: '4px', fontWeight: 700 }}>Academic Year & Level</span>
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div style={{
        display: 'flex',
        gap: '0.75rem',
        flexWrap: 'wrap',
        marginBottom: '1.5rem',
        alignItems: 'center',
        background: '#F8FAFC',
        padding: '0.85rem 1rem',
        borderRadius: '8px',
        border: '1px solid #EAECF0'
      }}>
        <div style={{ flex: 1, minWidth: '240px' }}>
          <input
            type="text"
            placeholder={isUniv ? "Search university programs, departments, or faculties..." : isCollege ? "Search undergraduate courses, specialisations (e.g. B.Tech, CSE, BBA)..." : "Search academic programmes..."}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 0.8rem',
              borderRadius: '6px',
              border: '1px solid #D0D5DD',
              fontSize: '0.875rem',
              boxSizing: 'border-box'
            }}
          />
        </div>

        {/* Level Filters */}
        <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
          <button
            onClick={() => setSelectedLevel('ALL')}
            style={{
              padding: '0.4rem 0.75rem',
              fontSize: '0.8rem',
              fontWeight: 600,
              borderRadius: '6px',
              border: selectedLevel === 'ALL' ? '1px solid #155EEF' : '1px solid #D0D5DD',
              background: selectedLevel === 'ALL' ? '#155EEF' : '#FFFFFF',
              color: selectedLevel === 'ALL' ? '#FFFFFF' : '#344054',
              cursor: 'pointer'
            }}
          >
            All Levels
          </button>

          {availableLevels.includes('undergraduate') && (
            <button
              onClick={() => setSelectedLevel('undergraduate')}
              style={{
                padding: '0.4rem 0.75rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                borderRadius: '6px',
                border: selectedLevel === 'undergraduate' ? '1px solid #155EEF' : '1px solid #D0D5DD',
                background: selectedLevel === 'undergraduate' ? '#155EEF' : '#FFFFFF',
                color: selectedLevel === 'undergraduate' ? '#FFFFFF' : '#344054',
                cursor: 'pointer'
              }}
            >
              Undergraduate (UG)
            </button>
          )}

          {availableLevels.includes('postgraduate') && (
            <button
              onClick={() => setSelectedLevel('postgraduate')}
              style={{
                padding: '0.4rem 0.75rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                borderRadius: '6px',
                border: selectedLevel === 'postgraduate' ? '1px solid #6941C6' : '1px solid #D0D5DD',
                background: selectedLevel === 'postgraduate' ? '#6941C6' : '#FFFFFF',
                color: selectedLevel === 'postgraduate' ? '#FFFFFF' : '#344054',
                cursor: 'pointer'
              }}
            >
              Postgraduate (PG)
            </button>
          )}

          {availableLevels.includes('doctoral') && (
            <button
              onClick={() => setSelectedLevel('doctoral')}
              style={{
                padding: '0.4rem 0.75rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                borderRadius: '6px',
                border: selectedLevel === 'doctoral' ? '1px solid #027A48' : '1px solid #D0D5DD',
                background: selectedLevel === 'doctoral' ? '#027A48' : '#FFFFFF',
                color: selectedLevel === 'doctoral' ? '#FFFFFF' : '#344054',
                cursor: 'pointer'
              }}
            >
              Doctoral / Ph.D.
            </button>
          )}
        </div>

        {/* Faculty Dropdown Filter for Universities */}
        {isUniv && availableFaculties.length > 1 && (
          <div>
            <select
              value={selectedFaculty}
              onChange={(e) => setSelectedFaculty(e.target.value)}
              style={{
                padding: '0.45rem 0.75rem',
                fontSize: '0.8rem',
                fontWeight: 600,
                borderRadius: '6px',
                border: '1px solid #D0D5DD',
                background: '#FFFFFF',
                color: '#344054'
              }}
            >
              <option value="ALL">All University Faculties</option>
              {availableFaculties.map(fac => (
                <option key={fac} value={fac}>{fac}</option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Program Listings */}
      {filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2.5rem', color: '#667085', background: '#F9FAFB', borderRadius: '8px' }}>
          No academic programmes matching the filter criteria.
        </div>
      ) : isUniv ? (
        /* ================= UNIVERSITIES: HIERARCHICAL RENDERING ================= */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {Object.entries(universityHierarchy).map(([facName, facData]) => (
            <div
              key={facName}
              style={{
                border: '1px solid #E4E7EC',
                borderRadius: '10px',
                overflow: 'hidden',
                background: '#FFFFFF',
                boxShadow: '0 2px 6px rgba(16,43,70,0.04)'
              }}
            >
              {/* Faculty Level Header */}
              <div style={{
                background: 'linear-gradient(90deg, #102B46 0%, #1A3A6B 100%)',
                color: '#FFFFFF',
                padding: '1rem 1.25rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '0.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span style={{ fontSize: '1.3rem' }}>🏛️</span>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: '#FFFFFF' }}>
                      {facName}
                    </h3>
                    <div style={{ fontSize: '0.78rem', color: '#CBD5E1', marginTop: '0.1rem' }}>
                      Constituent Faculty of {schoolName || 'University'}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    background: 'rgba(255, 255, 255, 0.2)',
                    color: '#FFFFFF',
                    padding: '0.2rem 0.6rem',
                    borderRadius: '12px'
                  }}>
                    {Object.keys(facData.departments).length} Departments
                  </span>
                </div>
              </div>

              {/* Departments Container */}
              <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', background: '#FAFAFB' }}>
                {Object.entries(facData.departments).map(([deptName, deptData]) => (
                  <div
                    key={deptName}
                    style={{
                      background: '#FFFFFF',
                      border: '1px solid #EAECF0',
                      borderRadius: '8px',
                      padding: '1rem 1.25rem',
                      boxShadow: '0 1px 3px rgba(16,43,70,0.02)'
                    }}
                  >
                    {/* Department Header */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: '0.5rem',
                      marginBottom: '1rem',
                      borderBottom: '1px solid #F2F4F7',
                      paddingBottom: '0.6rem'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '1.1rem' }}>🏢</span>
                        <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#102B46' }}>
                          {deptName}
                        </h4>
                      </div>
                      <span style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>
                        {deptData.programmes.length} {deptData.programmes.length === 1 ? 'Degree Programme' : 'Degree Programmes'}
                      </span>
                    </div>

                    {/* Programmes Grid under Department */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1rem' }}>
                      {deptData.programmes.map((p) => {
                        const isDoctoral = p.education_level === 'doctoral'
                        const isPG = p.education_level === 'postgraduate'
                        const isUG = p.education_level === 'undergraduate'

                        return (
                          <div
                            key={p.program_id}
                            style={{
                              border: '1px solid #E4E7EC',
                              borderRadius: '8px',
                              padding: '1rem',
                              background: '#FFFFFF',
                              display: 'flex',
                              flexDirection: 'column',
                              justifyContent: 'space-between'
                            }}
                          >
                            <div>
                              {/* Top Level and Degree Badges */}
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                                <span style={{
                                  fontSize: '0.72rem',
                                  fontWeight: 800,
                                  textTransform: 'uppercase',
                                  letterSpacing: '0.04em',
                                  background: isDoctoral ? '#ECFDF3' : isPG ? '#F9F5FF' : '#EFF4FF',
                                  color: isDoctoral ? '#027A48' : isPG ? '#6941C6' : '#155EEF',
                                  padding: '0.2rem 0.55rem',
                                  borderRadius: '4px',
                                  border: `1px solid ${isDoctoral ? '#A6F4C5' : isPG ? '#E9D7FE' : '#B2CCFF'}`
                                }}>
                                  {isDoctoral ? 'Doctoral / Ph.D.' : isPG ? 'Postgraduate' : 'Undergraduate'}
                                </span>

                                <span style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>
                                  ⏱️ {p.duration_years} {p.duration_years === 1 ? 'Year' : 'Years'}
                                </span>
                              </div>

                              {/* Title */}
                              <h5 style={{ margin: '0 0 0.4rem 0', color: '#102B46', fontSize: '0.98rem', fontWeight: 700, lineHeight: 1.35 }}>
                                {p.program_name}
                              </h5>

                              {/* Discipline / Stream */}
                              {p.discipline_or_stream && (
                                <div style={{ fontSize: '0.78rem', color: '#475467', marginBottom: '0.5rem' }}>
                                  Discipline: <strong>{p.discipline_or_stream}</strong>
                                </div>
                              )}
                            </div>

                            {/* Capacity and Availability Meta */}
                            <div style={{
                              borderTop: '1px solid #F2F4F7',
                              paddingTop: '0.6rem',
                              marginTop: '0.5rem',
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              fontSize: '0.76rem'
                            }}>
                              <span style={{ color: '#155EEF', fontWeight: 600 }}>
                                ID: {p.program_id}
                              </span>
                              {p.total_capacity > 0 && (
                                <span style={{
                                  color: p.available_seats > 0 ? '#027A48' : '#B42318',
                                  fontWeight: 700
                                }}>
                                  {p.available_seats > 0 ? `${p.available_seats} Available` : 'Quota Full'} ({p.total_capacity} Cap)
                                </span>
                              )}
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* ================= DEGREE COLLEGES, PU COLLEGES, SCHOOLS ================= */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          {Object.entries(groupedByLevel).map(([lvl, progList]) => (
            <div key={lvl}>
              {/* Group Header */}
              <div style={{
                background: '#F0F4F8',
                padding: '0.65rem 1rem',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontWeight: 700,
                color: '#102B46',
                fontSize: '0.9rem',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                borderLeft: '4px solid #155EEF'
              }}>
                <span>{levelLabels[lvl] || lvl.toUpperCase()}</span>
                <span style={{ fontSize: '0.78rem', color: '#475467', background: '#FFFFFF', padding: '0.15rem 0.5rem', borderRadius: '12px' }}>
                  {progList.length} Offerings
                </span>
              </div>

              {/* Program Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                {progList.map((p) => {
                  const isSchoolProg = p.education_level === 'school'
                  const isPUProg = p.education_level === 'higher_secondary'
                  const isUGProg = p.education_level === 'undergraduate'
                  const isPGProg = p.education_level === 'postgraduate'

                  return (
                    <div
                      key={p.program_id}
                      style={{
                        border: '1px solid #EAECF0',
                        borderRadius: '10px',
                        padding: '1.25rem',
                        background: '#FFFFFF',
                        boxShadow: '0 1px 3px rgba(16,43,70,0.04)',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between'
                      }}
                    >
                      <div>
                        {/* Top Meta Badges */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.6rem' }}>
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            background: isSchoolProg ? '#F0FDF4' : isPUProg ? '#EFF4FF' : isPGProg ? '#F9F5FF' : '#EFF8FF',
                            color: isSchoolProg ? '#15803D' : isPUProg ? '#155EEF' : isPGProg ? '#6941C6' : '#175CD3',
                            padding: '0.2rem 0.55rem',
                            borderRadius: '4px',
                            border: `1px solid ${isSchoolProg ? '#BBF7D0' : isPUProg ? '#B2CCFF' : isPGProg ? '#E9D7FE' : '#B2DDFF'}`
                          }}>
                            {p.degree_type !== 'None' ? p.degree_type : (p.discipline_or_stream || 'General')}
                          </span>

                          <span style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>
                            ⏱️ {p.duration_years} {p.duration_years === 1 ? 'Year' : 'Years'}
                          </span>
                        </div>

                        {/* Title */}
                        <h4 style={{ margin: '0 0 0.5rem 0', color: '#102B46', fontSize: '1.05rem', fontWeight: 700, lineHeight: 1.35 }}>
                          {p.program_name}
                        </h4>

                        {/* Department / Faculty for Degree Colleges */}
                        {isCollege && p.department_name && (
                          <div style={{ fontSize: '0.8rem', color: '#344054', marginBottom: '0.4rem' }}>
                            🏢 <strong>Department:</strong> {p.department_name}
                          </div>
                        )}

                        {/* Stream / Branch */}
                        {p.discipline_or_stream && (
                          <div style={{ fontSize: '0.8rem', color: '#475467', marginBottom: '0.4rem' }}>
                            🏷️ <strong>Branch / Specialisation:</strong> {p.discipline_or_stream}
                          </div>
                        )}

                        {/* PU Combination Code */}
                        {isPUProg && p.combination_code && (
                          <div style={{
                            fontSize: '0.8rem',
                            color: '#344054',
                            marginBottom: '0.65rem',
                            background: '#F8FAFC',
                            padding: '0.35rem 0.6rem',
                            borderRadius: '4px',
                            display: 'inline-block'
                          }}>
                            Combination: <strong>{p.combination_code}</strong>
                          </div>
                        )}

                        {/* Degree College Affiliation note */}
                        {isCollege && (
                          <div style={{ fontSize: '0.78rem', color: '#1E40AF', marginTop: '0.4rem' }}>
                            🏛️ Degree conferred by: <strong>{affiliation || 'Visvesvaraya Technological University (VTU), Belagavi'}</strong>
                          </div>
                        )}
                      </div>

                      {/* Footer Info */}
                      <div style={{
                        borderTop: '1px solid #F2F4F7',
                        paddingTop: '0.65rem',
                        marginTop: '0.75rem',
                        fontSize: '0.78rem',
                        color: '#667085',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}>
                        <span style={{ color: '#155EEF', fontWeight: 600 }}>
                          Code: {p.program_id}
                        </span>
                        {p.total_capacity > 0 ? (
                          <span style={{ color: p.available_seats > 0 ? '#027A48' : '#B42318', fontWeight: 600 }}>
                            {p.available_seats > 0 ? `${p.available_seats} Seats Available` : 'Full'}
                          </span>
                        ) : (
                          <span style={{ color: '#027A48', fontWeight: 600 }}>
                            ✓ Active Programme
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
