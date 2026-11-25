import React, { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'
import SeatBadge from '../../components/institution/SeatBadge.jsx'
import NearbyLocationSearch from '../../components/discovery/NearbyLocationSearch.jsx'

export default function SchoolDirectoryPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [institutions, setInstitutions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Filter States
  const [searchQuery, setSearchQuery] = useState(() => searchParams.get('q') || '')
  const [selectedDistrict, setSelectedDistrict] = useState(() => searchParams.get('district') || 'ALL')
  const [categoryFilter, setCategoryFilter] = useState(() => searchParams.get('category') || 'ALL')
  const [selectedAffiliation, setSelectedAffiliation] = useState('ALL')
  const [programmeQuery, setProgrammeQuery] = useState('')
  const [onlyOpenSeats, setOnlyOpenSeats] = useState(false)

  // GPS & Nearby Search States
  const [locationState, setLocationState] = useState(null) // { source, latitude, longitude, label, accuracy }
  const [radiusKm, setRadiusKm] = useState(10)

  useEffect(() => {
    async function fetchInstitutions() {
      try {
        setLoading(true)
        let endpoint = '/schools?limit=100'
        if (locationState?.latitude != null && locationState?.longitude != null) {
          endpoint += `&latitude=${locationState.latitude}&longitude=${locationState.longitude}&radius_km=${radiusKm}`
        }
        const data = await apiGet(endpoint)
        const list = Array.isArray(data) ? data : data.value ?? []
        setInstitutions(list)
      } catch (err) {
        setError(err.message || 'Failed to load institutions. Please verify the backend service is active.')
      } finally {
        setLoading(false)
      }
    }
    fetchInstitutions()
  }, [locationState, radiusKm])

  // Sync category state with URL if URL changes externally
  useEffect(() => {
    const cat = searchParams.get('category')
    if (cat && cat !== categoryFilter) {
      setCategoryFilter(cat)
    }
  }, [searchParams])

  // Keep search params in sync with filter inputs
  function handleFilterChange(newParams) {
    const updated = new URLSearchParams(searchParams)
    Object.entries(newParams).forEach(([key, val]) => {
      if (!val || val === 'ALL') {
        updated.delete(key)
      } else {
        updated.set(key, val)
      }
    })
    setSearchParams(updated)
  }

  function handleResetFilters() {
    setSearchQuery('')
    setSelectedDistrict('ALL')
    setCategoryFilter('ALL')
    setSelectedAffiliation('ALL')
    setProgrammeQuery('')
    setOnlyOpenSeats(false)
    setLocationState(null)
    setRadiusKm(10)
    setSearchParams({})
  }


  // Unique Districts from real data
  const districts = useMemo(() => {
    const set = new Set(institutions.map(s => s.district).filter(Boolean))
    return Array.from(set).sort()
  }, [institutions])

  // Unique Affiliations from real data
  const affiliations = useMemo(() => {
    const set = new Set(institutions.map(s => s.affiliation).filter(Boolean))
    return Array.from(set).sort()
  }, [institutions])

  // Dynamic counts by category from actual database records
  const counts = useMemo(() => {
    const c = { all: institutions.length, schools: 0, pu: 0, degree: 0, universities: 0 }
    for (const inst of institutions) {
      const cat = inst.category || ''
      const type = (inst.school_type || '').toLowerCase()
      if (cat === 'Schools (K-10)' || cat === 'Schools' || type === 'school') {
        c.schools++
      } else if (cat === 'PU Colleges (11-12)' || cat === 'PU Colleges' || type.includes('pu') || type.includes('pre-university')) {
        c.pu++
      } else if (cat === 'Degree Colleges' || type === 'degree college' || (type.includes('engineering') && !type.includes('university') && cat !== 'Universities')) {
        c.degree++
      } else if (cat === 'Universities' || type.includes('university')) {
        c.universities++
      }
    }
    return c
  }, [institutions])

  // Filtered List
  const filtered = useMemo(() => {
    return institutions.filter(s => {
      const q = searchQuery.toLowerCase().trim()
      const matchesSearch = !q ||
        (s.school_name && s.school_name.toLowerCase().includes(q)) ||
        (s.school_id && s.school_id.toLowerCase().includes(q)) ||
        (s.district && s.district.toLowerCase().includes(q)) ||
        (s.address && s.address.toLowerCase().includes(q)) ||
        (s.description && s.description.toLowerCase().includes(q))

      const matchesDistrict = selectedDistrict === 'ALL' || s.district === selectedDistrict
      const matchesAffiliation = selectedAffiliation === 'ALL' || s.affiliation === selectedAffiliation

      let matchesCat = true
      const cat = s.category || ''
      const type = (s.school_type || '').toLowerCase()
      if (categoryFilter === 'SCHOOLS') {
        matchesCat = cat === 'Schools (K-10)' || cat === 'Schools' || type === 'school'
      } else if (categoryFilter === 'PU') {
        matchesCat = cat === 'PU Colleges (11-12)' || cat === 'PU Colleges' || type.includes('pu') || type.includes('pre-university')
      } else if (categoryFilter === 'DEGREE') {
        matchesCat = cat === 'Degree Colleges' || type === 'degree college' || (type.includes('engineering') && !type.includes('university') && cat !== 'Universities')
      } else if (categoryFilter === 'UNIVERSITY') {
        matchesCat = cat === 'Universities' || type.includes('university')
      }

      // Programme query
      let matchesProg = true
      if (programmeQuery.trim()) {
        const pq = programmeQuery.toLowerCase().trim()
        const descMatch = s.description && s.description.toLowerCase().includes(pq)
        const nameMatch = s.school_name && s.school_name.toLowerCase().includes(pq)
        matchesProg = descMatch || nameMatch
      }

      // Open seats only
      let matchesSeats = true
      if (onlyOpenSeats) {
        matchesSeats = (s.available_seats || 0) > 0
      }

      return matchesSearch && matchesDistrict && matchesAffiliation && matchesCat && matchesProg && matchesSeats
    })
  }, [institutions, searchQuery, selectedDistrict, categoryFilter, selectedAffiliation, programmeQuery, onlyOpenSeats])

  return (
    <div className="school-directory-page" style={{ background: '#F5F7FA', minHeight: '85vh', paddingBottom: '6rem' }}>
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Explore Institutions' }
      ]} />

      <div className="container" style={{ maxWidth: '1280px', margin: '1.5rem auto 0 auto', padding: '0 1rem' }}>
        {/* Header Title Section */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          <div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.4rem 0' }}>
              Educational Institutions Directory
            </h1>
            <p style={{ color: '#475467', margin: 0, fontSize: '1.05rem' }}>
              Discover authorized schools, PU colleges, degree colleges, and universities across Karnataka with live seat quotas.
            </p>
          </div>
        </div>

        {error && (
          <Alert type="error" title="Error loading directory" style={{ marginBottom: '1.5rem' }}>
            {error}
          </Alert>
        )}

        {/* ========================================================
            FIND INSTITUTIONS NEAR YOU (GPS & MANUAL PROXIMITY SEARCH)
            Placed immediately below directory heading & above two-column layout
            ======================================================== */}
        <NearbyLocationSearch
          locationState={locationState}
          onLocationChange={(newLoc) => setLocationState(newLoc)}
          radiusKm={radiusKm}
          onRadiusChange={(newRadius) => setRadiusKm(newRadius)}
          onClearLocation={() => setLocationState(null)}
        />

        {/* Two-Column Search Layout */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem', alignItems: 'start' }}>
          
          {/* ========================================================
              LEFT COLUMN: FILTER CONTROLS SIDEBAR
              ======================================================== */}
          <aside style={{
            background: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 1px 3px rgba(16,43,70,0.04)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: 0 }}>
                Filters
              </h2>
              <button
                onClick={handleResetFilters}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: '#155EEF',
                  fontSize: '0.825rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  padding: 0
                }}
              >
                Reset All
              </button>
            </div>

            {/* Keyword Search */}
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.4rem' }}>
                Search Institution
              </label>
              <input
                type="text"
                placeholder="Name, ID, or keyword..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value)
                  handleFilterChange({ q: e.target.value })
                }}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.75rem',
                  borderRadius: '8px',
                  border: '1px solid #D0D5DD',
                  fontSize: '0.9rem',
                  color: '#15233B',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Education Tier / Category Filters */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.5rem' }}>
                Education Category
              </label>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                {[
                  { id: 'ALL', label: 'All Institutions', count: counts.all },
                  { id: 'SCHOOLS', label: 'Schools', count: counts.schools },
                  { id: 'PU', label: 'PU Colleges', count: counts.pu },
                  { id: 'DEGREE', label: 'Degree Colleges', count: counts.degree },
                  { id: 'UNIVERSITY', label: 'Universities', count: counts.universities }
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      setCategoryFilter(item.id)
                      handleFilterChange({ category: item.id })
                    }}
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      padding: '0.5rem 0.75rem',
                      borderRadius: '6px',
                      border: categoryFilter === item.id ? '1px solid #155EEF' : '1px solid transparent',
                      background: categoryFilter === item.id ? '#EFF4FF' : '#FFFFFF',
                      color: categoryFilter === item.id ? '#155EEF' : '#344054',
                      fontWeight: categoryFilter === item.id ? 700 : 500,
                      fontSize: '0.875rem',
                      cursor: 'pointer',
                      textAlign: 'left'
                    }}
                  >
                    <span>{item.label}</span>
                    <span style={{
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      background: categoryFilter === item.id ? '#D1E0FF' : '#F2F4F7',
                      color: categoryFilter === item.id ? '#155EEF' : '#667085',
                      padding: '0.1rem 0.45rem',
                      borderRadius: '10px'
                    }}>
                      {item.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* District Dropdown Filter */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.4rem' }}>
                Karnataka District
              </label>
              <select
                value={selectedDistrict}
                onChange={(e) => {
                  setSelectedDistrict(e.target.value)
                  handleFilterChange({ district: e.target.value })
                }}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.75rem',
                  borderRadius: '8px',
                  border: '1px solid #D0D5DD',
                  fontSize: '0.875rem',
                  color: '#15233B',
                  background: '#FFFFFF',
                  cursor: 'pointer',
                  boxSizing: 'border-box'
                }}
              >
                <option value="ALL">All Districts ({districts.length})</option>
                {districts.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>

            {/* Academic Programme / Subject Search */}
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.4rem' }}>
                Programme / Specialisation
              </label>
              <input
                type="text"
                placeholder="e.g. Science, PCMB, CS, Civil..."
                value={programmeQuery}
                onChange={(e) => setProgrammeQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.75rem',
                  borderRadius: '8px',
                  border: '1px solid #D0D5DD',
                  fontSize: '0.875rem',
                  color: '#15233B',
                  boxSizing: 'border-box'
                }}
              />
            </div>

            {/* Live Admission Quota Toggle */}
            <div style={{
              marginBottom: '1.5rem',
              background: '#F8FAFC',
              padding: '0.75rem',
              borderRadius: '8px',
              border: '1px solid #EAECF0'
            }}>
              <label style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.6rem',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 600,
                color: '#102B46'
              }}>
                <input
                  type="checkbox"
                  checked={onlyOpenSeats}
                  onChange={(e) => setOnlyOpenSeats(e.target.checked)}
                  style={{ width: '16px', height: '16px', cursor: 'pointer', accentColor: '#12B76A' }}
                />
                <span>🟢 Show Only Open Admissions</span>
              </label>
              <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.25rem', paddingLeft: '1.6rem' }}>
                Filter to institutions with available sanctioned seats.
              </div>
            </div>

            {/* Affiliation / Board Filter */}
            {affiliations.length > 0 && (
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.4rem' }}>
                  Regulatory Affiliation
                </label>
                <select
                  value={selectedAffiliation}
                  onChange={(e) => setSelectedAffiliation(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.75rem',
                    borderRadius: '8px',
                    border: '1px solid #D0D5DD',
                    fontSize: '0.875rem',
                    color: '#15233B',
                    background: '#FFFFFF',
                    cursor: 'pointer',
                    boxSizing: 'border-box'
                  }}
                >
                  <option value="ALL">All Boards & Affiliations</option>
                  {affiliations.map((a) => (
                    <option key={a} value={a}>{a}</option>
                  ))}
                </select>
              </div>
            )}
          </aside>

          {/* ========================================================
              RIGHT COLUMN: RESULTS COUNT & INSTITUTION CARDS
              ======================================================== */}
          <main style={{ gridColumn: 'span 2' }}>
            {/* Results Header Bar */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '1rem',
              marginBottom: '1.25rem',
              background: '#FFFFFF',
              padding: '1rem 1.25rem',
              borderRadius: '10px',
              border: '1px solid #E2E8F0'
            }}>
              <div style={{ fontSize: '0.95rem', color: '#475467' }}>
                Showing <strong style={{ color: '#102B46' }}>{filtered.length}</strong> of {institutions.length} Institutions
              </div>

              {/* Active Filter Pills */}
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                {categoryFilter !== 'ALL' && (
                  <span style={{ fontSize: '0.75rem', background: '#EFF4FF', color: '#155EEF', padding: '0.2rem 0.6rem', borderRadius: '4px', fontWeight: 600 }}>
                    Category: {categoryFilter}
                  </span>
                )}
                {selectedDistrict !== 'ALL' && (
                  <span style={{ fontSize: '0.75rem', background: '#F0FDF4', color: '#15803D', padding: '0.2rem 0.6rem', borderRadius: '4px', fontWeight: 600 }}>
                    District: {selectedDistrict}
                  </span>
                )}
                {onlyOpenSeats && (
                  <span style={{ fontSize: '0.75rem', background: '#ECFDF3', color: '#027A48', padding: '0.2rem 0.6rem', borderRadius: '4px', fontWeight: 600 }}>
                    ✓ Open Seats Only
                  </span>
                )}
              </div>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.75rem', color: '#667085' }}>Loading Karnataka institutions catalog...</p>
              </div>
            ) : filtered.length === 0 ? (
              <div style={{
                background: '#FFFFFF',
                borderRadius: '12px',
                border: '1px solid #E2E8F0',
                padding: '3rem 1.5rem',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🔍</div>
                <h3 style={{ fontSize: '1.3rem', color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  No Institutions Found
                </h3>
                <p style={{ color: '#667085', margin: '0 0 1.5rem 0', fontSize: '0.95rem' }}>
                  We could not find any institutions matching your selected search criteria and filters.
                </p>
                <button
                  onClick={handleResetFilters}
                  style={{
                    background: '#155EEF',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.6rem 1.25rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  Clear All Filters
                </button>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                {filtered.map((inst) => {
                  const isHigherEd = inst.school_type?.includes('College') || inst.school_type?.includes('University')

                  return (
                    <div
                      key={inst.school_id}
                      style={{
                        background: '#FFFFFF',
                        border: '1px solid #E2E8F0',
                        borderRadius: '12px',
                        overflow: 'hidden',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        boxShadow: '0 1px 3px rgba(16,43,70,0.04)',
                        transition: 'transform 0.15s ease, box-shadow 0.15s ease'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 6px 16px rgba(16,43,70,0.08)' }}
                      onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 1px 3px rgba(16,43,70,0.04)' }}
                    >
                      {/* Card Cover Banner */}
                      <div style={{
                        height: '110px',
                        background: inst.cover_image_url
                          ? `linear-gradient(rgba(16, 43, 70, 0.4), rgba(16, 43, 70, 0.75)), url("${inst.cover_image_url}") center/cover no-repeat`
                          : 'linear-gradient(135deg, #102B46 0%, #155EEF 100%)',
                        padding: '0.85rem 1rem',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start'
                      }}>
                        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            background: 'rgba(255, 255, 255, 0.95)',
                            color: '#102B46',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px'
                          }}>
                            {inst.school_id}
                          </span>

                          <span style={{
                            fontSize: '0.72rem',
                            fontWeight: 700,
                            background: (inst.category === 'Universities' || inst.school_type === 'University') ? '#444CE7' :
                                        (inst.category === 'Degree Colleges' || inst.school_type === 'Degree College') ? '#155EEF' :
                                        (inst.category === 'PU Colleges (11-12)' || inst.category === 'PU Colleges' || inst.school_type === 'PU College') ? '#C11574' : '#12B76A',
                            color: '#FFFFFF',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px'
                          }}>
                            {(inst.category || inst.school_type || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')}
                          </span>
                        </div>
                      </div>

                      {/* Card Body */}
                      <div style={{ padding: '1.25rem', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.35rem' }}>
                            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: 0, lineHeight: 1.3 }}>
                              {inst.school_name}
                            </h3>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', margin: '0 0 0.5rem 0' }}>
                            <span style={{ fontSize: '0.825rem', color: '#667085' }}>
                              📍 {inst.district}, {inst.state}
                            </span>
                            {inst.distance_km != null && (
                              <span style={{
                                background: '#EFF8FF',
                                border: '1px solid #B2DDFF',
                                color: '#175CD3',
                                fontSize: '0.75rem',
                                fontWeight: 700,
                                padding: '0.15rem 0.5rem',
                                borderRadius: '12px',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem'
                              }}>
                                🎯 {inst.distance_km} km away
                              </span>
                            )}
                          </div>

                          {/* Live Seat Quota Badge */}
                          <div style={{ marginBottom: '0.65rem' }}>
                            <SeatBadge
                              availableSeats={inst.available_seats}
                              totalCapacity={inst.total_capacity}
                            />
                          </div>

                          {inst.affiliation && (
                            <div style={{ fontSize: '0.78rem', color: '#155EEF', fontWeight: 600, marginBottom: '0.6rem' }}>
                              🎓 {inst.affiliation}
                            </div>
                          )}

                          <p style={{
                            fontSize: '0.85rem',
                            color: '#475467',
                            lineHeight: 1.5,
                            margin: '0 0 1rem 0',
                            display: '-webkit-box',
                            WebkitLineClamp: 2,
                            WebkitBoxOrient: 'vertical',
                            overflow: 'hidden'
                          }}>
                            {inst.description || `${inst.school_name} is an authorized state educational institution located in ${inst.district}.`}
                          </p>
                        </div>

                        {/* Card Footer */}
                        <div style={{ borderTop: '1px solid #F2F4F7', paddingTop: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.78rem', color: '#667085' }}>
                            {inst.established_year ? `Est. ${inst.established_year}` : 'Verified'}
                          </span>

                          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>

                            <Link
                              to={`/schools/${inst.school_id}`}
                              style={{
                                background: '#155EEF',
                                color: '#FFFFFF',
                                padding: '0.45rem 0.9rem',
                                borderRadius: '6px',
                                fontSize: '0.825rem',
                                fontWeight: 700,
                                textDecoration: 'none',
                                display: 'inline-flex',
                                alignItems: 'center',
                                gap: '0.25rem'
                              }}
                            >
                              View Profile →
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </main>
        </div>
      </div>
</div>
  )
}
