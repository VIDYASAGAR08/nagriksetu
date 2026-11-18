with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add selectedDivision state after selectedSemester
old_state = "  const [selectedSemester, setSelectedSemester] = useState('1')"
new_state = """  const [selectedSemester, setSelectedSemester] = useState('1')
  const [selectedDivision, setSelectedDivision] = useState('all')"""

assert old_state in text, "old_state not found"
text = text.replace(old_state, new_state, 1)

# 2. Update loadStructure defaults
old_load_def = """        if (data.combinations && data.combinations.length > 0) {
          setSelectedCombination(data.combinations[0])
        }
        if (data.programs && data.programs.length > 0) {
          setSelectedProgram(data.programs[0].program_code || data.programs[0].program_id)
        }"""

new_load_def = """        if (data.streams && data.streams.length > 0) {
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
        }"""

assert old_load_def in text, "old_load_def not found"
text = text.replace(old_load_def, new_load_def, 1)

# 3. Add cascading handlers before fetchStudents
cascading_handlers = """  // Cascading Selection Handlers for PU Tier
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
"""

marker_fetch = "  // Fetch Students with backend pagination & isolation"
assert marker_fetch in text, "marker_fetch not found"
text = text.replace(marker_fetch, cascading_handlers + "\n" + marker_fetch, 1)

# 4. Update fetchStudents params for degree
old_degree_params = """        // Degree / Higher Ed (Excluding PG)
        if (selectedProgram) params.set('program_code', selectedProgram)
        if (selectedYear) params.set('year', selectedYear)
        if (selectedSemester) params.set('semester', selectedSemester)
        if (selectedSection) params.set('section', selectedSection)"""

new_degree_params = """        // Degree / Higher Ed (Excluding PG)
        if (selectedProgram) params.set('program_id', selectedProgram)
        if (selectedDivision && selectedDivision !== 'all') params.set('division_id', selectedDivision)
        if (selectedYear) params.set('year', selectedYear)
        if (selectedSemester) params.set('semester', selectedSemester)
        if (selectedSection) params.set('section', selectedSection)"""

assert old_degree_params in text, "old_degree_params not found"
text = text.replace(old_degree_params, new_degree_params, 1)

# 5. Replace PU JSX
old_pu_jsx = """              {/* Category Case 2: Pre-University Colleges */}
              {isPU && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      PU Level:
                    </label>
                    <select
                      value={selectedPuLevel}
                      onChange={e => setSelectedPuLevel(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      <option value="1st PU (11th)">1st PU (Class 11)</option>
                      <option value="2nd PU (12th)">2nd PU (Class 12)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Academic Stream:
                    </label>
                    <select
                      value={selectedStream}
                      onChange={e => setSelectedStream(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.streams || ['Science', 'Commerce', 'Arts']).map(st => (
                        <option key={st} value={st}>{st}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Combination:
                    </label>
                    <select
                      value={selectedCombination}
                      onChange={e => setSelectedCombination(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      <option value="">All Combinations</option>
                      {(structure?.combinations || ['PCMB', 'PCMC', 'PCME', 'SEBA', 'EBAC']).map(c => (
                        <option key={c} value={c}>{c}</option>
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
                        <option key={sec} value={sec}>Section {sec}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}"""

new_pu_jsx = """              {/* Category Case 2: Pre-University Colleges */}
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
                            {c.code} — {c.name ? c.name.replace(/^Pre-University\\s*\\([^:]*:\\s*/, '').replace(/\\)$/, '') : c.code}
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
              )}"""

assert old_pu_jsx in text, "old_pu_jsx not found"
text = text.replace(old_pu_jsx, new_pu_jsx, 1)

# 6. Replace Degree Filter JSX with Division -> Degree Programme -> Year -> Semester -> Section
old_degree_jsx = """              {/* Category Case 4: Degree / Undergraduate (Excludes PG) */}
              {isHigherEd && (
                <>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Undergraduate Degree:
                    </label>
                    <select
                      value={selectedProgram}
                      onChange={e => setSelectedProgram(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {(structure?.programs || [{ program_code: 'BTECH-CS', name: 'B.Tech Computer Science' }]).map(p => (
                        <option key={p.program_code || p.program_id} value={p.program_code || p.program_id}>
                          {p.name} ({p.program_code})
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.3rem' }}>
                      Year:
                    </label>
                    <select
                      value={selectedYear}
                      onChange={e => setSelectedYear(e.target.value)}
                      style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', background: '#FFFFFF', fontWeight: 600 }}
                    >
                      {[1,2,3,4].map(yr => (
                        <option key={yr} value={yr}>Year {yr}</option>
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
                      {[1,2,3,4,5,6,7,8].map(sem => (
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
                      {(structure?.sections || ['A', 'B', 'C']).map(sec => (
                        <option key={sec} value={sec}>Section {sec}</option>
                      ))}
                    </select>
                  </div>
                </>
              )}"""

new_degree_jsx = """              {/* Category Case 4: Degree Colleges & Universities */}
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
              )}"""

assert old_degree_jsx in text, "old_degree_jsx not found"
text = text.replace(old_degree_jsx, new_degree_jsx, 1)

# 7. Update Empty State Message
old_empty = """            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
              No Students Found in Current Selection
            </h3>
            <p style={{ color: '#667085', fontSize: '0.88rem', maxWidth: '480px', margin: '0 auto 1.25rem auto' }}>
              No active student records match the selected academic level, stream, or section. Adjust your filter parameters or search query above.
            </p>"""

new_empty = """            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
              No enrolled students found for the selected academic filters.
            </h3>
            <p style={{ color: '#667085', fontSize: '0.88rem', maxWidth: '520px', margin: '0 auto 1.25rem auto' }}>
              No active student records match the selected academic level, programme, stream, combination or section. Adjust your filter parameters above.
            </p>"""

assert old_empty in text, "old_empty not found"
text = text.replace(old_empty, new_empty, 1)

with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionStudentManagementDesk.jsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("InstitutionStudentManagementDesk.jsx successfully updated.")
