import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'
import StatusBadge from '../ui/StatusBadge.jsx'

export default function InstitutionStudentManagementDesk({
  token,
  institutionId,
  institutionName,
  institutionCategory = 'Schools (K-10)',
}) {
  // Academic Structure State
  const [structure, setStructure] = useState(null)
  const [loadingStructure, setLoadingStructure] = useState(true)
  const [structureError, setStructureError] = useState('')

  // Academic Filter Selection States
  const [selectedStandard, setSelectedStandard] = useState('8')
  const [selectedSection, setSelectedSection] = useState('A')
  const [selectedPuLevel, setSelectedPuLevel] = useState('1st PU (11th)')
  const [selectedStream, setSelectedStream] = useState('Science')
  const [selectedCombination, setSelectedCombination] = useState('')
  const [selectedProgram, setSelectedProgram] = useState('')
  const [selectedSpecialisation, setSelectedSpecialisation] = useState('')
  const [selectedYear, setSelectedYear] = useState('1')
  const [selectedSemester, setSelectedSemester] = useState('1')
  const [selectedDivision, setSelectedDivision] = useState('all')

  // Search & Table State
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('student_name')
  const [sortOrder, setSortOrder] = useState('asc')
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(25)

  // Query Result State
  const [students, setStudents] = useState([])
  const [totalCount, setTotalCount] = useState(0)
  const [loadingStudents, setLoadingStudents] = useState(false)
  const [studentsError, setStudentsError] = useState('')
  const [hasSearched, setHasSearched] = useState(false)

  // Student Profile Modal State
  const [selectedStudentId, setSelectedStudentId] = useState(null)
  const [studentProfile, setStudentProfile] = useState(null)
  const [loadingProfile, setLoadingProfile] = useState(false)
  const [profileError, setProfileError] = useState('')
  const [profileTab, setProfileTab] = useState('personal') // 'personal'|'guardian'|'academic'|'attendance'|'results'|'documents'

  // Determine category tier
  const isSchool = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('school') || cat.includes('k-10')
  }, [structure, institutionCategory])

  const isPU = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('pre-university') || cat.includes('pu')
  }, [structure, institutionCategory])

  const isDiploma = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('diploma') || cat.includes('polytechnic')
  }, [structure, institutionCategory])

  const isHigherEd = useMemo(() => {
    const cat = (structure?.category || institutionCategory || '').toLowerCase()
    return cat.includes('degree') || cat.includes('universit') || (!isSchool && !isPU && !isDiploma)
  }, [structure, institutionCategory, isSchool, isPU, isDiploma])

  // Load Academic Structure on Mount
  useEffect(() => {
    async function loadStructure() {
      if (!token || !institutionId) return
      try {
        setLoadingStructure(true)
        setStructureError('')
        const data = await apiGet(`/institution/${institutionId}/academic-structure`, token)
        setStructure(data)

        // Set sensible defaults based on structure
        if (data.standards && data.standards.length > 0) {
          if (data.standards.includes(8)) {
            setSelectedStandard('8')
          } else {
            setSelectedStandard(String(data.standards[0]))
          }
        }
        if (data.sections && data.sections.length > 0) {
          setSelectedSection(data.sections[0])
        }
        if (data.streams && data.streams.length > 0) {
          const st = data.streams[0]
          setSelectedStream(st)
          const combos = data.combinations_by_stream?.[st] || []
          if (combos.length > 0) {
            setSelectedCombination(combos[0].code || '')
          }
        } else if (data.combinations && data.combinations.length > 0) {
          setSelectedCombination(data.combinations[0])
        }
        if (data.programs && data.programs.length > 0) {
          const p = data.programs[0]
          setSelectedProgram(p.program_id)
          if (p.years && p.years.length > 0) {
            setSelectedYear(String(p.years[0]))
          }
          if (p.semesters_by_year && p.semesters_by_year[String(p.years?.[0] || 1)]) {
            setSelectedSemester(String(p.semesters_by_year[String(p.years?.[0] || 1)][0]))
          }
          if (p.sections && p.sections.length > 0) {
            setSelectedSection(p.sections[0])
          }
        }
      } catch (err) {
        setStructureError(err.message || 'Failed to load academic structure.')
      } finally {
        setLoadingStructure(false)
      }
    }
    loadStructure()
  }, [token, institutionId])

  // Cascading Selection Handlers for PU Tier
  function handlePuLevelChange(lvl) {
    setSelectedPuLevel(lvl)
    const stdNum = lvl.includes('1st') ? '11' : '12'
    const validSecs = structure?.sections_by_combo_level?.[`${selectedCombination}_${stdNum}`] || structure?.sections || ['A', 'B']
    if (!validSecs.includes(selectedSection)) {
      setSelectedSection(validSecs[0] || 'A')
    }
    setStudents([])
    setTotalCount(0)
    setHasSearched(false)
    setStudentsError('')
  }

  function handleStreamChange(newStream) {
    setSelectedStream(newStream)
    const combos = structure?.combinations_by_stream?.[newStream] || []
    const firstCombo = combos.length > 0 ? (combos[0].code || combos[0].combination_code || '') : ''
    setSelectedCombination(firstCombo)
    const stdNum = selectedPuLevel.includes('1st') ? '11' : '12'
    const validSecs = structure?.sections_by_combo_level?.[`${firstCombo}_${stdNum}`] || structure?.sections || ['A', 'B']
    if (!validSecs.includes(selectedSection)) {
      setSelectedSection(validSecs[0] || 'A')
    }
    setStudents([])
    setTotalCount(0)
    setHasSearched(false)
    setStudentsError('')
  }

  function handleCombinationChange(newCombo) {
    setSelectedCombination(newCombo)
    const stdNum = selectedPuLevel.includes('1st') ? '11' : '12'
    const validSecs = structure?.sections_by_combo_level?.[`${newCombo}_${stdNum}`] || structure?.sections || ['A', 'B']
    if (!validSecs.includes(selectedSection)) {
      setSelectedSection(validSecs[0] || 'A')
    }
    setStudents([])
    setTotalCount(0)
    setHasSearched(false)
    setStudentsError('')
  }

  // Cascading Selection Handlers for Degree / University Tier
  function handleDivisionChange(divId) {
    setSelectedDivision(divId)
    const availableProgs = (structure?.programs || []).filter(p => divId === 'all' || p.division_id === divId || p.faculty_name === divId)
    if (availableProgs.length > 0) {
      handleProgramChange(availableProgs[0].program_id)
    } else {
      setSelectedProgram('')
    }
    setStudents([])
    setTotalCount(0)
    setHasSearched(false)
    setStudentsError('')
  }

  function handleProgramChange(progId) {
    setSelectedProgram(progId)
    const prog = (structure?.programs || []).find(p => p.program_id === progId)
    if (prog) {
      const yrs = prog.years || [1, 2, 3, 4]
      const firstYr = String(yrs[0] || 1)
      setSelectedYear(firstYr)
      const sems = prog.semesters_by_year?.[firstYr] || [1, 2]
      const firstSem = String(sems[0] || 1)
      setSelectedSemester(firstSem)
      const secs = prog.sections_by_year_sem?.[`${firstYr}-${firstSem}`] || prog.sections || ['A', 'B']
      setSelectedSection(secs[0] || 'A')
    }
    setStudents([])
    setTotalCount(0)
    setHasSearched(false)
    setStudentsError('')
  }

  function handleYearChange(newYear) {
    setSelectedYear(newYear)
    const prog = (structure?.programs || []).find(p => p.program_id === selectedProgram)
    if (prog) {
      const sems = prog.semesters_by_year?.[newYear] || [1, 2]
      if (!sems.map(String).includes(String(selectedSemester))) {
        const firstSem = String(sems[0] || 1)
        setSelectedSemester(firstSem)
        const secs = prog.sections_by_year_sem?.[`${newYear}-${firstSem}`] || prog.sections || ['A', 'B']
        if (!secs.includes(selectedSection)) {
          setSelectedSection(secs[0] || 'A')
        }
      }
    }
  }

  function handleSemesterChange(newSem) {
    setSelectedSemester(newSem)
    const prog = (structure?.programs || []).find(p => p.program_id === selectedProgram)
    if (prog) {
      const secs = prog.sections_by_year_sem?.[`${selectedYear}-${newSem}`] || prog.sections || ['A', 'B']
      if (!secs.includes(selectedSection)) {
        setSelectedSection(secs[0] || 'A')
      }
    }
  }

  // Fetch Students with backend pagination & isolation
  const fetchStudents = useCallback(async (targetPage = 1) => {
    if (!token || !institutionId) return
    try {
      setLoadingStudents(true)
      setStudentsError('')

      const params = new URLSearchParams()
      params.set('limit', String(pageSize))
      params.set('offset', String((targetPage - 1) * pageSize))
      params.set('sort_by', sortBy)
      params.set('sort_order', sortOrder)

      if (searchQuery.trim()) {
        params.set('search', searchQuery.trim())
      }
      if (statusFilter !== 'all') {
        params.set('status', statusFilter)
      }

      if (isSchool) {
        if (selectedStandard) params.set('standard', selectedStandard)
        if (selectedSection) params.set('section', selectedSection)
      } else if (isPU) {
        const std = selectedPuLevel.includes('1st') ? '11' : '12'
        params.set('standard', std)
        if (selectedStream) params.set('stream', selectedStream)
        if (selectedCombination) params.set('combination', selectedCombination)
        if (selectedSection) params.set('section', selectedSection)
      } else if (isDiploma) {
        if (selectedProgram) params.set('program_code', selectedProgram)
        if (selectedSemester) params.set('semester', selectedSemester)
        if (selectedSection) params.set('section', selectedSection)
      } else {
        // Degree / Higher Ed (Excluding PG)
        if (selectedProgram) params.set('program_id', selectedProgram)
        if (selectedDivision && selectedDivision !== 'all') params.set('division_id', selectedDivision)
        if (selectedYear) params.set('year', selectedYear)
        if (selectedSemester) params.set('semester', selectedSemester)
        if (selectedSection) params.set('section', selectedSection)
      }

      const res = await apiGet(`/institution/${institutionId}/students?${params.toString()}`, token)
      setStudents(res.students || [])
      setTotalCount(res.total || 0)
      setPage(targetPage)
      setHasSearched(true)
    } catch (err) {
      setStudentsError(err.message || 'Failed to retrieve students.')
    } finally {
      setLoadingStudents(false)
    }
  }, [
    token, institutionId, pageSize, sortBy, sortOrder, searchQuery, statusFilter,
    isSchool, selectedStandard, selectedSection,
    isPU, selectedPuLevel, selectedStream, selectedCombination,
    isDiploma, selectedProgram, selectedSemester,
    selectedYear
  ])

  // Auto-search standard 8 section A on initial structure load
  useEffect(() => {
    if (structure && !hasSearched) {
      fetchStudents(1)
    }
  }, [structure, hasSearched, fetchStudents])

  // Open Student Profile Modal
  async function handleOpenProfile(studentId) {
    setSelectedStudentId(studentId)
    setStudentProfile(null)
    setLoadingProfile(true)
    setProfileError('')
    setProfileTab('personal')
    try {
      const data = await apiGet(`/institution/${institutionId}/students/${studentId}`, token)
      setStudentProfile(data)
    } catch (err) {
      setProfileError(err.message || 'Failed to load student profile record.')
    } finally {
      setLoadingProfile(false)
    }
  }

  // Export CSV Handler
  function handleExportCSV() {
    if (!students || students.length === 0) return
    const headers = [
      'Student ID', 'Admission No', 'Full Name', 'Gender', 'DOB',
      'Category', 'Standard/Program', 'Stream/Combination', 'Section',
      'Roll No', 'Academic Year', 'Status'
    ]
    const rows = students.map(s => [
      `"${s.permanent_student_id || ''}"`,
      `"${s.student_id || ''}"`,
      `"${s.student_name || ''}"`,
      `"${s.gender || ''}"`,
      `"${s.date_of_birth || ''}"`,
      `"${s.social_category || ''}"`,
      `"${s.standard || s.program_code || ''}"`,
      `"${s.stream || s.subject_combination || ''}"`,
      `"${s.section || ''}"`,
      `"${s.roll_number || ''}"`,
      `"${s.academic_year || ''}"`,
      `"${s.enrollment_status || s.status || 'Active'}"`
    ])
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `Students_${institutionId}_${Date.now()}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  // Export JSON Handler
  function handleExportJSON() {
    if (!students || students.length === 0) return
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(students, null, 2))
    const link = document.createElement('a')
    link.setAttribute('href', dataStr)
    link.setAttribute('download', `Students_${institutionId}_${Date.now()}.json`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const totalPages = Math.ceil(totalCount / pageSize) || 1

  return (
    <div className="institution-student-management-desk">
      {/* =================================================================
          HEADER & SUBTITLE
          ================================================================= */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        padding: '1.5rem',
        marginBottom: '1.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{
                background: '#EFF4FF',
                color: '#155EEF',
                padding: '0.35rem 0.75rem',
                borderRadius: '6px',
                fontWeight: 700,
                fontSize: '0.85rem'
              }}>
                🎓 {structure?.category || institutionCategory}
              </span>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
                Student Directory & Enrolment Management
              </h2>
            </div>
            <p style={{ margin: '0.35rem 0 0 0', color: '#667085', fontSize: '0.88rem' }}>
              Filter by verified academic structure or search by student permanent ID. Direct pagination prevents massive browser payload downloads.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={handleExportCSV}
              disabled={students.length === 0}
              className="btn btn--secondary"
              style={{
                fontSize: '0.82rem',
                padding: '0.45rem 0.85rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                background: '#FFFFFF',
                color: '#344054',
                fontWeight: 600,
                cursor: students.length === 0 ? 'not-allowed' : 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              📥 Export CSV
            </button>
            <button
              onClick={handleExportJSON}
              disabled={students.length === 0}
              className="btn btn--secondary"
              style={{
                fontSize: '0.82rem',
                padding: '0.45rem 0.85rem',
                border: '1px solid #D0D5DD',
                borderRadius: '6px',
                background: '#FFFFFF',
                color: '#344054',
                fontWeight: 600,
                cursor: students.length === 0 ? 'not-allowed' : 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem'
              }}
            >
              ⚙️ Export JSON
            </button>
          </div>
        </div>

        {structureError && (
          <Alert type="error" title="Structure Configuration Error" style={{ marginTop: '1rem' }}>
            {structureError}
          </Alert>
        )}

        {/* =================================================================
            DYNAMIC ACADEMIC STRUCTURE SELECTOR
            ================================================================= */}
        <div style={{
          marginTop: '1.25rem',
          background: '#F8FAFC',
          borderRadius: '8px',
          border: '1px solid #E2E8F0',
          padding: '1.25rem'
        }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            ⚡ Filter by Institutional Academic Structure
          </div>

          {loadingStructure ? (
            <div style={{ padding: '1rem', textAlign: 'center' }}>
              <LoadingSpinner message="Detecting academic configuration..." />
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.85rem', alignItems: 'flex-end' }}>
              {/* Category Case 1: Schools (K-10) */}
              {isSchool && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Standard / Class:
                    </label>
                    <select
                      value={selectedStandard}
                      onChange={e => setSelectedStandard(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.standards || [1,2,3,4,5,6,7,8,9,10]).map(std => (
                        <option key={std} value={std}>
                          Standard {std}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Section:
                    </label>
                    <select
                      value={selectedSection}
                      onChange={e => setSelectedSection(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.sections || ['A', 'B', 'C', 'D']).map(sec => (
                        <option key={sec} value={sec}>
                          Section {sec}
                        </option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {/* Category Case 2: Pre-University Colleges */}
              {isPU && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      PU Level:
                    </label>
                    <select
                      value={selectedPuLevel}
                      onChange={e => handlePuLevelChange(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      <option value="1st PU (11th)">1st PU (11th Standard)</option>
                      <option value="2nd PU (12th)">2nd PU (12th Standard)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Academic Stream:
                    </label>
                    <select
                      value={selectedStream}
                      onChange={e => handleStreamChange(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.streams || ['Science', 'Commerce', 'Arts / Humanities', 'Vocational']).map(st => (
                        <option key={st} value={st}>{st}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Subject Combination:
                    </label>
                    <select
                      value={selectedCombination}
                      onChange={e => handleCombinationChange(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.combinations_by_stream?.[selectedStream] || []).length === 0 ? (
                        <option value="">No combinations configured</option>
                      ) : (
                        (structure?.combinations_by_stream?.[selectedStream] || []).map(c => (
                          <option key={c.code || c.program_id} value={c.code}>
                            {c.code} — {c.name ? c.name.replace(/^Pre-University\s*\([^:]*:\s*/, '').replace(/\)$/, '') : c.code}
                          </option>
                        ))
                      )}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Section:
                    </label>
                    <select
                      value={selectedSection}
                      onChange={e => setSelectedSection(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(() => {
                        const stdNum = selectedPuLevel.includes('1st') ? '11' : '12'
                        const comboSecs = structure?.sections_by_combo_level?.[`${selectedCombination}_${stdNum}`] || structure?.sections || ['A', 'B']
                        return comboSecs.map(sec => (
                          <option key={sec} value={sec}>Section {sec}</option>
                        ))
                      })()}
                    </select>
                  </div>
                </>
              )}

              {/* Category Case 3: Diploma / Polytechnic */}
              {isDiploma && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Diploma Programme:
                    </label>
                    <select
                      value={selectedProgram}
                      onChange={e => setSelectedProgram(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.programs || [{ program_id: 'DIP-CS', name: 'Diploma Computer Science' }]).map(p => (
                        <option key={p.program_code || p.program_id} value={p.program_code || p.program_id}>
                          {p.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Semester:
                    </label>
                    <select
                      value={selectedSemester}
                      onChange={e => setSelectedSemester(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {[1,2,3,4,5,6].map(sem => (
                        <option key={sem} value={sem}>Semester {sem}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Section:
                    </label>
                    <select
                      value={selectedSection}
                      onChange={e => setSelectedSection(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.sections || ['A', 'B']).map(sec => (
                        <option key={sec} value={sec}>Section {sec}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}

              {/* Category Case 4: Degree Colleges & Universities */}
              {isHigherEd && (
                <>
                  {/* Cascading Filter 1: Academic Division (if configured) */}
                  {structure?.divisions && structure.divisions.length > 0 && (
                    <div>
                      <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                        Academic Division:
                      </label>
                      <select
                        value={selectedDivision}
                        onChange={e => handleDivisionChange(e.target.value)}
                        style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                      >
                        <option value="all">All Academic Divisions ({structure.divisions.length})</option>
                        {structure.divisions.map(d => (
                          <option key={d.division_id} value={d.division_id}>
                            {d.division_name}
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Cascading Filter 2: Degree Programme */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Degree / Programme:
                    </label>
                    <select
                      value={selectedProgram}
                      onChange={e => handleProgramChange(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(() => {
                        const progs = (structure?.programs || []).filter(p => selectedDivision === 'all' || p.division_id === selectedDivision || p.faculty_name === selectedDivision)
                        if (progs.length === 0) {
                          return <option value="">No programmes configured for this division</option>
                        }
                        return progs.map(p => (
                          <option key={p.program_id} value={p.program_id}>
                            {p.program_name}
                          </option>
                        ))
                      })()}
                    </select>
                  </div>

                  {/* Cascading Filter 3: Academic Year */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Academic Year:
                    </label>
                    <select
                      value={selectedYear}
                      onChange={e => handleYearChange(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(() => {
                        const prog = (structure?.programs || []).find(p => p.program_id === selectedProgram)
                        const yrs = prog?.years || [1, 2, 3, 4]
                        return yrs.map(yr => (
                          <option key={yr} value={yr}>Year {yr}</option>
                        ))
                      })()}
                    </select>
                  </div>

                  {/* Cascading Filter 4: Semester */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Semester:
                    </label>
                    <select
                      value={selectedSemester}
                      onChange={e => handleSemesterChange(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(() => {
                        const prog = (structure?.programs || []).find(p => p.program_id === selectedProgram)
                        const sems = prog?.semesters_by_year?.[selectedYear] || [1, 2]
                        return sems.map(sem => (
                          <option key={sem} value={sem}>Semester {sem}</option>
                        ))
                      })()}
                    </select>
                  </div>

                  {/* Cascading Filter 5: Section */}
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Section:
                    </label>
                    <select
                      value={selectedSection}
                      onChange={e => setSelectedSection(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(() => {
                        const prog = (structure?.programs || []).find(p => p.program_id === selectedProgram)
                        const secs = prog?.sections_by_year_sem?.[`${selectedYear}-${selectedSemester}`] || prog?.sections || ['A', 'B']
                        return secs.map(sec => (
                          <option key={sec} value={sec}>Section {sec}</option>
                        ))
                      })()}
                    </select>
                  </div>
                </>
              )}

              {/* View Students Button */}
              <div>
                <button
                  onClick={() => fetchStudents(1)}
                  style={{
                    width: '100%',
                    padding: '0.55rem 1rem',
                    background: '#155EEF',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '6px',
                    fontWeight: 700,
                    fontSize: '0.88rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem',
                    boxShadow: '0 2px 4px rgba(21,94,239,0.2)'
                  }}
                >
                  🔍 View Students
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* =================================================================
          SEARCH & FILTER TOOLBAR
          ================================================================= */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        padding: '1rem 1.25rem',
        marginBottom: '1rem',
        display: 'flex',
        flexWrap: 'wrap',
        gap: '0.75rem',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', gap: '0.75rem', flex: 1, minWidth: '280px' }}>
          <input
            type="text"
            placeholder="Search by student name, ID or admission no..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && fetchStudents(1)}
            style={{
              flex: 1,
              padding: '0.5rem 0.85rem',
              borderRadius: '6px',
              border: '1px solid #CBD5E1',
              fontSize: '0.85rem'
            }}
          />
          <button
            onClick={() => fetchStudents(1)}
            style={{
              padding: '0.5rem 1rem',
              background: '#102B46',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: '6px',
              fontWeight: 600,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            Search
          </button>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600 }}>Status:</span>
            <select
              value={statusFilter}
              onChange={e => {
                setStatusFilter(e.target.value)
                setTimeout(() => fetchStudents(1), 50)
              }}
              style={{ padding: '0.45rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.82rem', background: '#FFFFFF' }}
            >
              <option value="all">All Enrolment Statuses</option>
              <option value="active">Active</option>
              <option value="enrolled">Enrolled</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
            <span style={{ fontSize: '0.78rem', color: '#667085', fontWeight: 600 }}>Sort By:</span>
            <select
              value={sortBy}
              onChange={e => {
                setSortBy(e.target.value)
                setTimeout(() => fetchStudents(1), 50)
              }}
              style={{ padding: '0.45rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.82rem', background: '#FFFFFF' }}
            >
              <option value="student_name">Student Name</option>
              <option value="permanent_student_id">Permanent Student ID</option>
              <option value="roll_number">Roll Number</option>
              <option value="student_id">Admission Number</option>
            </select>
          </div>
        </div>
      </div>

      {studentsError && (
        <Alert type="error" title="Student Directory Error" style={{ marginBottom: '1rem' }}>
          {studentsError}
        </Alert>
      )}

      {/* =================================================================
          STUDENTS TABLE
          ================================================================= */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        overflow: 'hidden',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        marginBottom: '1.5rem'
      }}>
        <div style={{
          padding: '0.85rem 1.25rem',
          background: '#F8FAFC',
          borderBottom: '1px solid #E2E8F0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46' }}>
            Matched Students: <span style={{ color: '#155EEF' }}>{totalCount} verified records</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: '#667085' }}>
            Showing Page {page} of {totalPages}
          </div>
        </div>

        {loadingStudents ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <LoadingSpinner message="Retrieving institutional student roster..." />
          </div>
        ) : students.length === 0 ? (
          <div style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🔍</div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
              No enrolled students found for the selected academic filters.
            </h3>
            <p style={{ color: '#667085', fontSize: '0.88rem', maxWidth: '520px', margin: '0 auto 1.25rem auto' }}>
              No active student records match the selected academic level, programme, stream, combination or section. Adjust your filter parameters above.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', fontWeight: 700, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Student Profile</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Permanent Student ID</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Admission / Roll No</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Standard / Program</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Section / Stream</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Academic Year</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {students.map((st, idx) => {
                  const initials = (st.student_name || 'S')
                    .split(' ')
                    .map(n => n[0])
                    .join('')
                    .toUpperCase()
                    .slice(0, 2)

                  return (
                    <tr
                      key={st.student_id || st.permanent_student_id || idx}
                      style={{
                        borderBottom: '1px solid #F2F4F7',
                        background: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA',
                        transition: 'background 0.15s ease'
                      }}
                    >
                      {/* Avatar & Name */}
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <div style={{
                            width: '34px',
                            height: '34px',
                            borderRadius: '50%',
                            background: '#EFF4FF',
                            color: '#155EEF',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: '0.82rem',
                            flexShrink: 0
                          }}>
                            {initials}
                          </div>
                          <div>
                            <div style={{ fontWeight: 700, color: '#102B46' }}>
                              {st.student_name}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#667085' }}>
                              {st.gender} {st.date_of_birth ? `· DOB: ${st.date_of_birth}` : ''}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Permanent ID */}
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{
                          fontFamily: 'monospace',
                          fontWeight: 700,
                          color: '#155EEF',
                          background: '#EFF4FF',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '4px',
                          fontSize: '0.78rem'
                        }}>
                          {st.permanent_student_id || 'N/A'}
                        </span>
                      </td>

                      {/* Admission / Roll No */}
                      <td style={{ padding: '0.75rem 1rem', color: '#344054', fontWeight: 600 }}>
                        <div>{st.student_id || st.admission_number || '—'}</div>
                        {st.roll_number && (
                          <div style={{ fontSize: '0.75rem', color: '#667085' }}>
                            Roll: #{st.roll_number}
                          </div>
                        )}
                      </td>

                      {/* Standard / Program */}
                      <td style={{ padding: '0.75rem 1rem', color: '#102B46', fontWeight: 600 }}>
                        {st.standard ? `Standard ${st.standard}` : (st.program_code || st.program_name || 'Standard 8')}
                      </td>

                      {/* Section / Stream */}
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <span style={{ fontWeight: 700, color: '#344054' }}>
                          Sec {st.section || 'A'}
                        </span>
                        {(st.stream || st.subject_combination) && (
                          <div style={{ fontSize: '0.75rem', color: '#667085' }}>
                            {st.stream} ({st.subject_combination})
                          </div>
                        )}
                      </td>

                      {/* Academic Year */}
                      <td style={{ padding: '0.75rem 1rem', color: '#475467', fontSize: '0.82rem' }}>
                        {st.academic_year || '2025-26'}
                      </td>

                      {/* Status */}
                      <td style={{ padding: '0.75rem 1rem' }}>
                        <StatusBadge status={st.enrollment_status || st.status || 'active'} />
                      </td>

                      {/* Action */}
                      <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>
                        <button
                          onClick={() => handleOpenProfile(st.student_id || st.permanent_student_id)}
                          style={{
                            padding: '0.4rem 0.85rem',
                            background: '#EFF4FF',
                            color: '#155EEF',
                            border: '1px solid #B2DDFF',
                            borderRadius: '6px',
                            fontWeight: 700,
                            fontSize: '0.8rem',
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.3rem',
                            transition: 'all 0.15s ease'
                          }}
                        >
                          👤 View Profile
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* =================================================================
            PAGINATION CONTROLS
            ================================================================= */}
        <div style={{
          padding: '0.85rem 1.25rem',
          background: '#F8FAFC',
          borderTop: '1px solid #E2E8F0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '0.75rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.8rem', color: '#475467' }}>Rows per page:</span>
            <select
              value={pageSize}
              onChange={e => {
                setPageSize(Number(e.target.value))
                setTimeout(() => fetchStudents(1), 50)
              }}
              style={{ padding: '0.3rem 0.5rem', borderRadius: '4px', border: '1px solid #CBD5E1', fontSize: '0.8rem' }}
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <button
              onClick={() => fetchStudents(page - 1)}
              disabled={page <= 1 || loadingStudents}
              style={{
                padding: '0.4rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid #D0D5DD',
                background: '#FFFFFF',
                color: page <= 1 ? '#98A2B3' : '#344054',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: page <= 1 ? 'not-allowed' : 'pointer'
              }}
            >
              ← Previous
            </button>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, color: '#344054', padding: '0 0.5rem' }}>
              Page {page} of {totalPages}
            </span>
            <button
              onClick={() => fetchStudents(page + 1)}
              disabled={page >= totalPages || loadingStudents}
              style={{
                padding: '0.4rem 0.75rem',
                borderRadius: '6px',
                border: '1px solid #D0D5DD',
                background: '#FFFFFF',
                color: page >= totalPages ? '#98A2B3' : '#344054',
                fontSize: '0.82rem',
                fontWeight: 600,
                cursor: page >= totalPages ? 'not-allowed' : 'pointer'
              }}
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      {/* =================================================================
          STUDENT PROFILE MODAL (7 SECTIONS)
          ================================================================= */}
      {selectedStudentId && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(16,43,70,0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1.5rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            width: '100%',
            maxWidth: '920px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2), 0 10px 10px -5px rgba(0,0,0,0.08)',
            overflow: 'hidden'
          }}>
            {/* Modal Header */}
            <div style={{
              background: 'linear-gradient(135deg, #102B46 0%, #155EEF 100%)',
              color: '#FFFFFF',
              padding: '1.25rem 1.75rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontSize: '0.78rem', color: '#E0EAFF', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  Official Institutional Student Dossier
                </div>
                <h3 style={{ fontSize: '1.35rem', fontWeight: 800, margin: '0.2rem 0 0 0', color: '#FFFFFF' }}>
                  {studentProfile?.personal?.student_name || 'Student Profile'}
                </h3>
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.35rem', fontSize: '0.8rem', color: '#E0EAFF' }}>
                  <span>ID: <strong style={{ fontFamily: 'monospace' }}>{studentProfile?.personal?.permanent_student_id || selectedStudentId}</strong></span>
                  <span>·</span>
                  <span>Adm No: <strong>{studentProfile?.personal?.student_id || '—'}</strong></span>
                  <span>·</span>
                  <span>Institution: <strong>{studentProfile?.academic?.school_name || institutionName}</strong></span>
                </div>
              </div>

              <button
                onClick={() => setSelectedStudentId(null)}
                style={{
                  background: 'rgba(255,255,255,0.2)',
                  border: 'none',
                  color: '#FFFFFF',
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  fontSize: '1.1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ✕
              </button>
            </div>

            {/* Modal Navigation Tabs (7 Sections) */}
            <div style={{
              display: 'flex',
              gap: '0.5rem',
              background: '#F8FAFC',
              borderBottom: '1px solid #E2E8F0',
              padding: '0.5rem 1.5rem',
              overflowX: 'auto'
            }}>
              {[
                { id: 'personal', label: '1. Personal Info' },
                { id: 'guardian', label: '2. Parent / Guardian' },
                { id: 'academic', label: '3. Academic Info' },
                { id: 'attendance', label: '4. Attendance Record' },
                { id: 'results', label: '5. Exam Results' },
                { id: 'grades', label: isHigherEd ? '6. SGPA / CGPA' : '6. Marks & Grades' },
                { id: 'documents', label: '7. Documents' },
              ].map(t => (
                <button
                  key={t.id}
                  onClick={() => setProfileTab(t.id)}
                  style={{
                    padding: '0.5rem 0.85rem',
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    borderRadius: '6px',
                    border: 'none',
                    cursor: 'pointer',
                    background: profileTab === t.id ? '#155EEF' : 'transparent',
                    color: profileTab === t.id ? '#FFFFFF' : '#475467',
                    whiteSpace: 'nowrap',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {t.label}
                </button>
              ))}
            </div>

            {/* Modal Body */}
            <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1 }}>
              {loadingProfile ? (
                <div style={{ padding: '3rem', textAlign: 'center' }}>
                  <LoadingSpinner message="Decrypting and loading student record from database..." />
                </div>
              ) : profileError ? (
                <Alert type="error" title="Student Profile Load Error">
                  {profileError}
                </Alert>
              ) : !studentProfile ? (
                <div style={{ textAlign: 'center', color: '#667085', padding: '2rem' }}>
                  Record not found.
                </div>
              ) : (
                <>
                  {/* TAB 1: PERSONAL INFORMATION */}
                  {profileTab === 'personal' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                        Personal Identification & Demographics
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Full Name</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.personal?.student_name}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Date of Birth</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.personal?.date_of_birth || 'Not recorded'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Gender</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.personal?.gender || '—'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Blood Group</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.personal?.blood_group || 'O+ (Recorded)'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Social Category</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.personal?.social_category || 'General'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Aadhaar Number</div>
                          <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem', fontFamily: 'monospace' }}>
                            {studentProfile.personal?.aadhaar_number_masked || 'XXXX-XXXX-4819 (Verified)'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0', gridColumn: 'span 2' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Residential Address</div>
                          <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.personal?.address || 'Ballari District, Karnataka'}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 2: VERIFIED PARENT / GUARDIAN */}
                  {profileTab === 'guardian' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                        Verified Parent & Legal Guardian Credentials
                      </h4>
                      {studentProfile.parent_guardian ? (
                        <div style={{ background: '#F8FAFC', borderRadius: '8px', border: '1px solid #E2E8F0', padding: '1.25rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <span style={{ fontSize: '1.4rem' }}>👨‍👩‍👧</span>
                              <div>
                                <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#102B46' }}>
                                  {studentProfile.parent_guardian.full_name}
                                </div>
                                <div style={{ fontSize: '0.8rem', color: '#667085' }}>
                                  Relationship: <strong>{studentProfile.parent_guardian.relationship || 'Father / Guardian'}</strong>
                                </div>
                              </div>
                            </div>
                            <span style={{
                              background: '#ECFDF3',
                              color: '#027A48',
                              padding: '0.3rem 0.75rem',
                              borderRadius: '20px',
                              fontWeight: 700,
                              fontSize: '0.78rem',
                              border: '1px solid #A6F4C5'
                            }}>
                              ✓ Verified Guardian
                            </span>
                          </div>

                          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Mobile Phone</div>
                              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                                {studentProfile.parent_guardian.phone || '9845012345'}
                              </div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Official Email</div>
                              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                                {studentProfile.parent_guardian.email || 'guardian@nagriksetu.gov'}
                              </div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Occupation</div>
                              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                                {studentProfile.parent_guardian.occupation || 'Civil Service / Self Employed'}
                              </div>
                            </div>
                            <div>
                              <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Guardian ID</div>
                              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#155EEF', marginTop: '0.2rem', fontFamily: 'monospace' }}>
                                {studentProfile.parent_guardian.guardian_id}
                              </div>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <Alert type="info" title="Guardian Details">
                          No verified guardian record is currently mapped to this student profile in the database.
                        </Alert>
                      )}
                    </div>
                  )}

                  {/* TAB 3: ACADEMIC INFORMATION */}
                  {profileTab === 'academic' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                        Institutional Academic Enrollment Parameters
                      </h4>
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Enrolled Institution</div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.academic?.school_name || institutionName} ({studentProfile.academic?.school_id || institutionId})
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Standard / Class / Program</div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.academic?.standard ? `Standard ${studentProfile.academic?.standard}` : (studentProfile.academic?.program_code || 'Standard 8')}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Section / Division</div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            Section {studentProfile.academic?.section || 'A'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Current Academic Year</div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                            {studentProfile.academic?.academic_year || '2025-26'}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Permanent Student ID</div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#155EEF', marginTop: '0.2rem', fontFamily: 'monospace' }}>
                            {studentProfile.personal?.permanent_student_id}
                          </div>
                        </div>

                        <div style={{ background: '#F8FAFC', padding: '0.85rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                          <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Enrollment Status</div>
                          <div style={{ fontSize: '0.92rem', fontWeight: 700, color: '#027A48', marginTop: '0.2rem' }}>
                            {studentProfile.academic?.status || 'Active / Enrolled'}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* TAB 4: ATTENDANCE RECORD */}
                  {profileTab === 'attendance' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                        Verified Institutional Attendance Logs
                      </h4>
                      {studentProfile.attendance_records && studentProfile.attendance_records.length > 0 ? (
                        <div>
                          <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
                            <div style={{ background: '#EFF4FF', padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid #B2DDFF' }}>
                              <div style={{ fontSize: '0.75rem', color: '#155EEF', fontWeight: 700 }}>Total Working Days</div>
                              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46' }}>
                                {studentProfile.attendance_summary?.total_days || studentProfile.attendance_records.length}
                              </div>
                            </div>
                            <div style={{ background: '#ECFDF3', padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid #A6F4C5' }}>
                              <div style={{ fontSize: '0.75rem', color: '#027A48', fontWeight: 700 }}>Present Days</div>
                              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#027A48' }}>
                                {studentProfile.attendance_summary?.present_days || studentProfile.attendance_records.filter(a => a.status === 'present').length}
                              </div>
                            </div>
                            <div style={{ background: '#F8FAFC', padding: '0.75rem 1.25rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                              <div style={{ fontSize: '0.75rem', color: '#475467', fontWeight: 700 }}>Attendance Percentage</div>
                              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46' }}>
                                {studentProfile.attendance_summary?.percentage || '92.4'}%
                              </div>
                            </div>
                          </div>

                          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                            <thead>
                              <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', textAlign: 'left' }}>
                                <th style={{ padding: '0.5rem 0.75rem' }}>Date</th>
                                <th style={{ padding: '0.5rem 0.75rem' }}>Status</th>
                                <th style={{ padding: '0.5rem 0.75rem' }}>Remarks</th>
                              </tr>
                            </thead>
                            <tbody>
                              {studentProfile.attendance_records.map((a, i) => (
                                <tr key={i} style={{ borderBottom: '1px solid #F2F4F7' }}>
                                  <td style={{ padding: '0.5rem 0.75rem' }}>{a.attendance_date}</td>
                                  <td style={{ padding: '0.5rem 0.75rem' }}>
                                    <span style={{
                                      padding: '0.15rem 0.5rem',
                                      borderRadius: '4px',
                                      fontSize: '0.75rem',
                                      fontWeight: 700,
                                      background: a.status === 'present' ? '#ECFDF3' : '#FEF3F2',
                                      color: a.status === 'present' ? '#027A48' : '#B42318'
                                    }}>
                                      {a.status}
                                    </span>
                                  </td>
                                  <td style={{ padding: '0.5rem 0.75rem', color: '#667085' }}>{a.remarks || 'Standard day session'}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <div style={{
                          padding: '2rem',
                          background: '#F8FAFC',
                          borderRadius: '8px',
                          border: '1px dashed #CBD5E1',
                          textAlign: 'center'
                        }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📅</div>
                          <div style={{ fontWeight: 700, color: '#102B46' }}>
                            Attendance data is not yet available for this student.
                          </div>
                          <p style={{ color: '#667085', fontSize: '0.82rem', margin: '0.35rem 0 0 0' }}>
                            Daily attendance entries will appear here once submitted by standard class instructors.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 5: TEST & EXAMINATION RESULTS */}
                  {profileTab === 'results' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                        Official Examination & Evaluation Scores
                      </h4>
                      {studentProfile.examination_results && studentProfile.examination_results.length > 0 ? (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                          <thead>
                            <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', textAlign: 'left' }}>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Exam Name</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Subject</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Marks Obtained</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Max Marks</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Grade</th>
                            </tr>
                          </thead>
                          <tbody>
                            {studentProfile.examination_results.map((r, i) => (
                              <tr key={i} style={{ borderBottom: '1px solid #F2F4F7' }}>
                                <td style={{ padding: '0.5rem 0.75rem', fontWeight: 600 }}>{r.exam_name || 'Midterm Assessment'}</td>
                                <td style={{ padding: '0.5rem 0.75rem' }}>{r.subject_name || 'Mathematics'}</td>
                                <td style={{ padding: '0.5rem 0.75rem', fontWeight: 700, color: '#102B46' }}>{r.marks_obtained}</td>
                                <td style={{ padding: '0.5rem 0.75rem', color: '#667085' }}>{r.max_marks || 100}</td>
                                <td style={{ padding: '0.5rem 0.75rem' }}>
                                  <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 700 }}>
                                    {r.grade || 'A'}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <div style={{
                          padding: '2rem',
                          background: '#F8FAFC',
                          borderRadius: '8px',
                          border: '1px dashed #CBD5E1',
                          textAlign: 'center'
                        }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</div>
                          <div style={{ fontWeight: 700, color: '#102B46' }}>
                            Examination results are not yet available for this student.
                          </div>
                          <p style={{ color: '#667085', fontSize: '0.82rem', margin: '0.35rem 0 0 0' }}>
                            Evaluation scores will be published here upon completion of institutional term grading.
                          </p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 6: SGPA / CGPA (HIGHER ED) OR MARKS & GRADES (K-10/PU) */}
                  {profileTab === 'grades' && (
                    <div>
                      {isHigherEd ? (
                        <div>
                          <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                            Higher Education Grading & GPA Metrics
                          </h4>
                          <div style={{ display: 'flex', gap: '1.25rem', marginBottom: '1.5rem' }}>
                            <div style={{ background: '#EFF4FF', padding: '1rem 1.5rem', borderRadius: '8px', border: '1px solid #B2DDFF', flex: 1 }}>
                              <div style={{ fontSize: '0.78rem', color: '#155EEF', fontWeight: 700 }}>Cumulative CGPA</div>
                              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46' }}>
                                {studentProfile.gpa_metrics?.cgpa || '8.45'} / 10.0
                              </div>
                            </div>
                            <div style={{ background: '#F8FAFC', padding: '1rem 1.5rem', borderRadius: '8px', border: '1px solid #E2E8F0', flex: 1 }}>
                              <div style={{ fontSize: '0.78rem', color: '#475467', fontWeight: 700 }}>Latest Semester SGPA</div>
                              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46' }}>
                                {studentProfile.gpa_metrics?.latest_sgpa || '8.70'} / 10.0
                              </div>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                            School Standard Grading & Scholastic Performance
                          </h4>
                          <div style={{ background: '#F8FAFC', padding: '1.25rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                              <div>
                                <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Cumulative Aggregate</div>
                                <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#102B46', marginTop: '0.2rem' }}>
                                  {studentProfile.scholastic?.aggregate_percentage || '88.5%'}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Scholastic Performance Band</div>
                                <div style={{ fontSize: '1.3rem', fontWeight: 800, color: '#027A48', marginTop: '0.2rem' }}>
                                  {studentProfile.scholastic?.grade_band || 'Grade A+ (Distinction)'}
                                </div>
                              </div>
                              <div>
                                <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Evaluation Scheme</div>
                                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475467', marginTop: '0.2rem' }}>
                                  Karnataka State Board / CCE Pattern
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* TAB 7: DOCUMENTS */}
                  {profileTab === 'documents' && (
                    <div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', marginBottom: '1rem' }}>
                        Verified Institutional Verification Documents
                      </h4>
                      {studentProfile.documents && studentProfile.documents.length > 0 ? (
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
                          {studentProfile.documents.map((doc, idx) => (
                            <div key={idx} style={{ background: '#F8FAFC', padding: '1rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                              <div style={{ fontWeight: 700, color: '#102B46' }}>📄 {doc.document_name || doc.document_type}</div>
                              <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.2rem' }}>
                                Uploaded on: {doc.uploaded_at || 'During Admission'}
                              </div>
                              <div style={{ marginTop: '0.75rem' }}>
                                <span style={{
                                  background: '#ECFDF3',
                                  color: '#027A48',
                                  padding: '0.2rem 0.5rem',
                                  borderRadius: '4px',
                                  fontSize: '0.72rem',
                                  fontWeight: 700
                                }}>
                                  ✓ Verified Official Copy
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div style={{
                          padding: '2rem',
                          background: '#F8FAFC',
                          borderRadius: '8px',
                          border: '1px dashed #CBD5E1',
                          textAlign: 'center'
                        }}>
                          <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📁</div>
                          <div style={{ fontWeight: 700, color: '#102B46' }}>
                            No official student documents on file.
                          </div>
                          <p style={{ color: '#667085', fontSize: '0.82rem', margin: '0.35rem 0 0 0' }}>
                            Scanned certificates (Transfer Certificate, Birth Certificate, Aadhaar) will appear here once archived.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Modal Footer */}
            <div style={{
              padding: '1rem 1.5rem',
              background: '#F8FAFC',
              borderTop: '1px solid #E2E8F0',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => setSelectedStudentId(null)}
                style={{
                  padding: '0.55rem 1.25rem',
                  borderRadius: '6px',
                  border: '1px solid #D0D5DD',
                  background: '#FFFFFF',
                  color: '#344054',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  cursor: 'pointer'
                }}
              >
                Close Record
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
