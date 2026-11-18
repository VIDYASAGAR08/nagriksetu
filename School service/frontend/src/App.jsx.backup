
import { useEffect, useState } from 'react'
import './App.css'

const API_URL = `http://${window.location.hostname}:8001`

function App() {
  const [schools, setSchools] = useState([])
  const [search, setSearch] = useState('')
  const [selectedSchool, setSelectedSchool] = useState(null)
  const [students, setStudents] = useState([])
  const [standard, setStandard] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activePage, setActivePage] = useState('dashboard')

  useEffect(() => {
    async function loadSchools() {
      try {
        const response = await fetch(`${API_URL}/schools?limit=100`)
        if (!response.ok) throw new Error('Could not load schools')
        setSchools(await response.json())
      } catch {
        setError('Unable to connect to the backend. Make sure FastAPI is running.')
      } finally {
        setLoading(false)
      }
    }

    loadSchools()
  }, [])

  async function openSchool(school) {
    setSelectedSchool(school)
    setStudents([])
    setStandard('')
    setError('')
    setActivePage('students')

    try {
      const response = await fetch(
        `${API_URL}/schools/${school.school_id}/students?limit=100`
      )
      if (!response.ok) throw new Error('Could not load students')
      setStudents(await response.json())
    } catch {
      setError('Unable to load students. Please check the backend.')
    }
  }

  async function filterStandard(value) {
    setStandard(value)
    if (!selectedSchool) return

    try {
      const query = value
        ? `?standard=${value}&limit=100`
        : '?limit=100'

      const response = await fetch(
        `${API_URL}/schools/${selectedSchool.school_id}/students${query}`
      )
      if (!response.ok) throw new Error('Could not load students')
      setStudents(await response.json())
    } catch {
      setError('Unable to filter students. Please try again.')
    }
  }

  const filteredSchools = schools.filter((school) => {
    const text = `${school.school_name} ${school.district} ${school.school_id}`
    return text.toLowerCase().includes(search.toLowerCase())
  })

  function showDashboard() {
    setActivePage('dashboard')
    setSelectedSchool(null)
    setError('')
  }

  function showDirectory() {
    setActivePage('directory')
    setSelectedSchool(null)
    setError('')
  }

  function showStudents() {
    setActivePage('students')
    setError('')
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">N</div>
          <div>
            <h2>NagrikSetu</h2>
            <p>School Service</p>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <button
          className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={showDashboard}
        >
          â–¦ &nbsp; Dashboard
        </button>

        <button
          className={`nav-item ${activePage === 'directory' ? 'active' : ''}`}
          onClick={showDirectory}
        >
          âŒ‚ &nbsp; School Directory
        </button>

        <button
          className={`nav-item ${activePage === 'students' ? 'active' : ''}`}
          onClick={showStudents}
        >
          â™™ &nbsp; Student Records
        </button>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          Local database connected
          <p>ANVAYA Platform</p>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">ANVAYA PLATFORM / EDUCATION</p>
            <h1>
              {activePage === 'dashboard' && 'School Service Dashboard'}
              {activePage === 'directory' && 'School Directory'}
              {activePage === 'students' && 'Student Records'}
            </h1>
          </div>

          <div className="admin-chip">
            <div className="avatar">A</div>
            <span>Administrator</span>
          </div>
        </header>

        {activePage === 'dashboard' && (
          <>
            <section className="welcome">
              <div>
                <p className="eyebrow light">EDUCATION OVERVIEW</p>
                <h2>Welcome to NagrikSetu</h2>
                <p>Explore schools and access student records in one place.</p>
              </div>
              <div className="welcome-symbol">âŒ‚</div>
            </section>

            <section className="stats">
              <div className="stat-card">
                <div className="stat-icon blue">â–¦</div>
                <p>Total Schools</p>
                <h2>{schools.length}</h2>
                <span>Registered institutions</span>
              </div>

              <div className="stat-card">
                <div className="stat-icon purple">â™™</div>
                <p>Total Students</p>
                <h2>6,000</h2>
                <span>Across all schools</span>
              </div>

              <div className="stat-card">
                <div className="stat-icon green">âœ“</div>
                <p>Standards</p>
                <h2>10</h2>
                <span>Standards 1 to 10</span>
              </div>

              <div className="stat-card">
                <div className="stat-icon orange">âŒ–</div>
                <p>State</p>
                <h2>Karnataka</h2>
                <span>School directory coverage</span>
              </div>
            </section>

            <section className="directory">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">DISCOVER</p>
                  <h2>School Directory</h2>
                  <p>Search and select a school to view its students.</p>
                </div>
                <button className="close-button" onClick={showDirectory}>
                  View all schools
                </button>
              </div>

              <SchoolList
                loading={loading}
                schools={filteredSchools.slice(0, 3)}
                search={search}
                setSearch={setSearch}
                openSchool={openSchool}
              />
            </section>
          </>
        )}

        {activePage === 'directory' && (
          <section className="directory">
            <div className="section-heading">
              <div>
                <p className="eyebrow">DISCOVER</p>
                <h2>All Schools</h2>
                <p>Search by school name, district, or school ID.</p>
              </div>
              <span className="count-badge">{filteredSchools.length} schools</span>
            </div>

            <SchoolList
              loading={loading}
              schools={filteredSchools}
              search={search}
              setSearch={setSearch}
              openSchool={openSchool}
            />
          </section>
        )}

        {activePage === 'students' && (
          <section className="directory student-section">
            {!selectedSchool ? (
              <>
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">STUDENT MANAGEMENT</p>
                    <h2>Select a school</h2>
                    <p>Choose a school below to view its student records.</p>
                  </div>
                </div>

                <SchoolList
                  loading={loading}
                  schools={filteredSchools}
                  search={search}
                  setSearch={setSearch}
                  openSchool={openSchool}
                />
              </>
            ) : (
              <>
                <div className="section-heading">
                  <div>
                    <p className="eyebrow">SCHOOL DETAILS</p>
                    <h2>{selectedSchool.school_name}</h2>
                    <p>
                      {selectedSchool.school_id} Â· {selectedSchool.district}
                    </p>
                  </div>

                  <button className="close-button" onClick={showDirectory}>
                    Back to schools
                  </button>
                </div>

                <div className="student-toolbar">
                  <label htmlFor="standard">Filter by standard</label>
                  <select
                    id="standard"
                    value={standard}
                    onChange={(event) => filterStandard(event.target.value)}
                  >
                    <option value="">All standards</option>
                    {Array.from({ length: 10 }, (_, index) => (
                      <option key={index + 1} value={index + 1}>
                        Standard {index + 1}
                      </option>
                    ))}
                  </select>
                  <span>{students.length} records shown</span>
                </div>

                <div className="table-scroll">
                  <table>
                    <thead>
                      <tr>
                        <th>Student ID</th>
                        <th>Student Name</th>
                        <th>Standard</th>
                        <th>Section</th>
                        <th>Age</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map((student) => (
                        <tr key={student.student_id}>
                          <td>{student.student_id}</td>
                          <td>{student.student_name}</td>
                          <td>Standard {student.standard}</td>
                          <td>{student.section}</td>
                          <td>{student.age}</td>
                        </tr>
                      ))}
                      {students.length === 0 && (
                        <tr>
                          <td colSpan="5">No student records to display.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </section>
        )}

        {error && <div className="error-message">{error}</div>}

        <footer>
          NagrikSetu Â· ANVAYA School Service
          <span>Powered by FastAPI and SQLite</span>
        </footer>
      </main>
    </div>
  )
}

function SchoolList({ loading, schools, search, setSearch, openSchool }) {
  if (loading) {
    return <p className="message">Loading schools from the database...</p>
  }

  return (
    <>
      <div className="search-wrap">
        <span>âŒ•</span>
        <input
          type="search"
          placeholder="Search schools or districts..."
          value={search}
          onChange={(event) => setSearch(event.target.value)}
        />
      </div>

      {schools.length === 0 ? (
        <p className="message">No schools found. Try another search.</p>
      ) : (
        <div className="school-grid">
          {schools.map((school, index) => (
            <article className="school-card" key={school.school_id}>
              <div className={`school-symbol symbol-${index % 4}`}>
                {school.school_name.charAt(0)}
              </div>

              <span className="school-id">{school.school_id}</span>
              <h3>{school.school_name}</h3>
              <p className="district">âŒ– &nbsp; {school.district}</p>

              <div className="school-meta">
                <span>{school.school_type}</span>
                <span>{school.state}</span>
              </div>

              <button onClick={() => openSchool(school)}>
                View students <span>â†’</span>
              </button>
            </article>
          ))}
        </div>
      )}
    </>
  )
}

export default App

