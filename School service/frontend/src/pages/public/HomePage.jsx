import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet } from '../../utils/api.js'
import vidhanaSoudhaImg from '../../assets/vidhana_soudha.jpg'

export default function HomePage() {
  const { isAuthenticated, user } = useAuth()
  const navigate = useNavigate()

  // Search Bar States
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDistrict, setSelectedDistrict] = useState('ALL')
  const [selectedCategory, setSelectedCategory] = useState('ALL')

  // Featured Institutions
  const [featuredInstitutions, setFeaturedInstitutions] = useState([])
  const [loadingFeatured, setLoadingFeatured] = useState(true)

  useEffect(() => {
    async function fetchFeatured() {
      try {
        setLoadingFeatured(true)
        const data = await apiGet('/schools?limit=6')
        const list = Array.isArray(data) ? data : data.value || []
        setFeaturedInstitutions(list.slice(0, 6))
      } catch {
        setFeaturedInstitutions([])
      } finally {
        setLoadingFeatured(false)
      }
    }
    fetchFeatured()
  }, [])

  function handleSearchSubmit(e) {
    e.preventDefault()
    const params = new URLSearchParams()
    if (searchQuery.trim()) params.set('q', searchQuery.trim())
    if (selectedDistrict !== 'ALL') params.set('district', selectedDistrict)
    if (selectedCategory !== 'ALL') params.set('category', selectedCategory)
    navigate(`/schools?${params.toString()}`)
  }

  const karnatakaDistricts = [
    { name: 'Bengaluru Urban', count: 7, icon: '🏙️' },
    { name: 'Mysuru', count: 4, icon: '🏰' },
    { name: 'Belagavi', count: 2, icon: '🏞️' },
    { name: 'Dharwad', count: 3, icon: '📚' },
    { name: 'Tumakuru', count: 3, icon: '🌾' },
    { name: 'Udupi', count: 2, icon: '🏖️' },
    { name: 'Shivamogga', count: 2, icon: '🌿' },
    { name: 'Ballari', count: 2, icon: '⚒️' },
    { name: 'Kalaburagi', count: 2, icon: '🏛️' },
    { name: 'Vijayapura', count: 1, icon: '🕌' },
    { name: 'Mandya', count: 1, icon: '🌱' },
    { name: 'Hassan', count: 1, icon: '🏺' }
  ]

  return (
    <div className="home-page" style={{ background: '#F5F7FA', color: '#15233B' }}>
      {/* ========================================================
          HERO SECTION – EXACT VIDHANA SOUDHA VISUAL REFERENCE
          ======================================================== */}
      <section style={{
        position: 'relative',
        minHeight: '560px',
        display: 'flex',
        alignItems: 'center',
        background: `linear-gradient(90deg, rgba(16, 43, 70, 0.94) 0%, rgba(16, 43, 70, 0.82) 48%, rgba(16, 43, 70, 0.42) 100%), url(${vidhanaSoudhaImg}) center right / cover no-repeat`,
        color: '#FFFFFF',
        padding: '3.5rem 1.5rem',
        borderBottom: '4px solid #FF9933'
      }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto', width: '100%' }}>
          <div style={{ maxWidth: '820px' }}>
            {/* Government Sub-Badge & Central Portal Link */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem' }}>
              <div style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                background: 'rgba(255, 153, 51, 0.18)',
                backdropFilter: 'blur(6px)',
                border: '1px solid rgba(255, 153, 51, 0.45)',
                borderRadius: '20px',
                padding: '0.35rem 0.85rem',
                fontSize: '0.8rem',
                fontWeight: 700,
                color: '#FF9933',
                letterSpacing: '0.04em'
              }}>
                <span>🇮🇳</span>
                <span>NAGRIKSETU · EDUCATION DISCOVERY PORTAL</span>
              </div>
              <a
                href="http://localhost:5173"
                style={{
                  background: '#081c33',
                  color: '#FF9933',
                  border: '1px solid #FF9933',
                  padding: '0.35rem 0.85rem',
                  borderRadius: '20px',
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  textDecoration: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  boxShadow: '0 2px 6px rgba(0,0,0,0.3)'
                }}
              >
                ← Back to Central Portal (Port 5173)
              </a>
            </div>

            {/* Main Headline */}
            <h1 style={{
              fontSize: '3.25rem',
              fontWeight: 800,
              lineHeight: 1.15,
              margin: '0 0 1rem 0',
              color: '#FFFFFF',
              letterSpacing: '-0.02em',
              textShadow: '0 2px 8px rgba(0,0,0,0.3)'
            }}>
              Discover. Learn. Grow.
            </h1>

            {/* Subtitle */}
            <p style={{
              fontSize: '1.25rem',
              lineHeight: 1.5,
              color: '#FFFFFF',
              margin: '0 0 0.5rem 0',
              maxWidth: '680px',
              fontWeight: 600,
              textShadow: '0 1px 4px rgba(0,0,0,0.2)'
            }}>
              Find the right educational institution for your child's future.
            </p>

            {/* Supporting Text */}
            <p style={{
              fontSize: '1.05rem',
              lineHeight: 1.55,
              color: '#E0E7FF',
              margin: '0 0 1.75rem 0',
              maxWidth: '680px',
              fontWeight: 400
            }}>
              Explore schools, PU colleges, degree colleges, and universities across Karnataka in one place.
            </p>

            {/* Search Bar Container */}
            <form
              onSubmit={handleSearchSubmit}
              style={{
                background: '#FFFFFF',
                borderRadius: '12px',
                padding: '0.6rem',
                boxShadow: '0 8px 30px rgba(16, 43, 70, 0.25)',
                display: 'flex',
                gap: '0.5rem',
                flexWrap: 'wrap',
                alignItems: 'center'
              }}
            >
              {/* Keyword Search Input */}
              <div style={{ flex: '2 1 220px', display: 'flex', alignItems: 'center', padding: '0 0.75rem' }}>
                <span style={{ fontSize: '1.2rem', marginRight: '0.5rem', color: '#667085' }}>🔍</span>
                <input
                  type="text"
                  placeholder="Institution name, city, or DISE code..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    border: 'none',
                    outline: 'none',
                    fontSize: '0.95rem',
                    color: '#15233B',
                    background: 'transparent'
                  }}
                />
              </div>

              {/* District Dropdown */}
              <div style={{ flex: '1 1 150px', borderLeft: '1px solid #E4E7EC', padding: '0 0.75rem' }}>
                <select
                  value={selectedDistrict}
                  onChange={(e) => setSelectedDistrict(e.target.value)}
                  style={{
                    width: '100%',
                    border: 'none',
                    outline: 'none',
                    fontSize: '0.9rem',
                    color: '#344054',
                    background: 'transparent',
                    cursor: 'pointer'
                  }}
                >
                  <option value="ALL">All Districts</option>
                  <option value="Bengaluru Urban">Bengaluru Urban</option>
                  <option value="Mysuru">Mysuru</option>
                  <option value="Belagavi">Belagavi</option>
                  <option value="Dharwad">Dharwad</option>
                  <option value="Tumakuru">Tumakuru</option>
                  <option value="Udupi">Udupi</option>
                  <option value="Shivamogga">Shivamogga</option>
                  <option value="Ballari">Ballari</option>
                  <option value="Kalaburagi">Kalaburagi</option>
                  <option value="Vijayapura">Vijayapura</option>
                  <option value="Mandya">Mandya</option>
                  <option value="Hassan">Hassan</option>
                </select>
              </div>

              {/* Category Dropdown */}
              <div style={{ flex: '1 1 150px', borderLeft: '1px solid #E4E7EC', padding: '0 0.75rem' }}>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  style={{
                    width: '100%',
                    border: 'none',
                    outline: 'none',
                    fontSize: '0.9rem',
                    color: '#344054',
                    background: 'transparent',
                    cursor: 'pointer'
                  }}
                >
                  <option value="ALL">All Categories</option>
                  <option value="SCHOOLS">Schools (K-10)</option>
                  <option value="PU">PU Colleges (11-12)</option>
                  <option value="DEGREE">Degree Colleges</option>
                  <option value="UNIVERSITY">Universities</option>
                </select>
              </div>

              {/* Search Submit Button */}
              <button
                type="submit"
                style={{
                  background: '#081c33',
                  color: '#FF9933',
                  border: '1px solid #FF9933',
                  borderRadius: '8px',
                  padding: '0.75rem 1.35rem',
                  fontSize: '0.95rem',
                  fontWeight: 800,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  flexShrink: 0
                }}
              >
                Search Institutions →
              </button>
            </form>

            {/* Disclaimer & Transparency Note */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              marginTop: '0.85rem',
              fontSize: '0.78rem',
              color: 'rgba(255, 255, 255, 0.75)'
            }}>
              <span>🛡️</span>
              <span>NagrikSetu is a transparent public educational discovery and admission facilitation platform. Not an official endorsement of individual non-government institutions.</span>
            </div>

            {/* Popular Category Quick Pills */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginTop: '1.25rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.85rem', color: '#E0E7FF', fontWeight: 600 }}>Popular:</span>
              {[
                { label: 'Schools (K–10)', cat: 'SCHOOLS' },
                { label: 'PU Colleges (11–12)', cat: 'PU' },
                { label: 'Degree Colleges', cat: 'DEGREE' },
                { label: 'Universities', cat: 'UNIVERSITY' }
              ].map((p, idx) => (
                <Link
                  key={idx}
                  to={`/schools?category=${p.cat}`}
                  style={{
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    background: 'rgba(255, 255, 255, 0.16)',
                    color: '#FFFFFF',
                    padding: '0.25rem 0.65rem',
                    borderRadius: '20px',
                    textDecoration: 'none',
                    border: '1px solid rgba(255, 255, 255, 0.25)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {p.label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================
          SECTION 1B: USER PORTAL ENTRY CATEGORIES
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#F8F9FC', borderBottom: '1px solid #EAECF0' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#b45309', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              CITIZEN & STAKEHOLDER PORTALS
            </span>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46', margin: '0.35rem 0 0.5rem 0' }}>
              Choose Your Portal Experience
            </h2>
            <p style={{ color: '#475467', margin: 0, fontSize: '0.95rem', maxWidth: '680px', marginLeft: 'auto', marginRight: 'auto' }}>
              Select your user category below to access public institutional registries or log in to verified educational services.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
            {/* 1. Public / Citizen */}
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #D0D5DD',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 1px 3px rgba(16, 24, 40, 0.05)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#EFF8FF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid #B2DDFF' }}>
                    🌐
                  </div>
                  <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px' }}>
                    Open Public Access
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  Public / Citizen
                </h3>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Browse, search, and discover verified profiles, facilities, curricula, and seat quotas across all 30 Karnataka institutions without authentication.
                </p>
              </div>
              <Link
                to="/schools"
                className="btn btn--secondary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#102B46',
                  borderColor: '#D0D5DD',
                  textDecoration: 'none'
                }}
              >
                Explore Institutions Directory →
              </Link>
            </div>

            {/* 2. Student */}
            <div style={{
              background: '#FFFFFF',
              border: '2px solid #081c33',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 4px 12px rgba(21, 94, 239, 0.08)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#EEF4FF', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid #C7D7FE' }}>
                    🎓
                  </div>
                  <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px' }}>
                    Enrolled Students
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  Student Portal
                </h3>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Dedicated student workspace. Access daily attendance records, examination gradebooks, upcoming timetables, and personal academic standing.
                </p>
              </div>
              <Link
                to="/login?category=student"
                className="btn btn--primary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  background: '#081c33',
                  color: '#FFFFFF',
                  border: 'none',
                  textDecoration: 'none'
                }}
              >
                Student Sign In & Activation →
              </Link>
            </div>

            {/* 3. Parent / Guardian */}
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #D0D5DD',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 1px 3px rgba(16, 24, 40, 0.05)',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: '#FEF0C7', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid #FEDF89' }}>
                    👨‍👩‍👧‍👦
                  </div>
                  <span style={{ background: '#FFFAEB', color: '#B54708', border: '1px solid #FEDF89', fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '12px' }}>
                    Verified Guardians
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  Parent / Guardian
                </h3>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Apply for Stage 1 admissions, monitor real-time review decisions, inspect linked children's attendance, evaluation cards, and official notices.
                </p>
              </div>
              <Link
                to="/login?category=parent"
                className="btn btn--secondary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  color: '#102B46',
                  borderColor: '#D0D5DD',
                  textDecoration: 'none'
                }}
              >
                Parent Portal Sign In →
              </Link>
            </div>

            {/* 4. Administrator & Staff */}
            <div style={{
              background: '#102B46',
              border: '1px solid #0B1E32',
              borderRadius: '12px',
              padding: '1.75rem 1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              boxShadow: '0 4px 12px rgba(16, 43, 70, 0.15)',
              color: '#FFFFFF',
              transition: 'transform 0.15s ease, box-shadow 0.15s ease'
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', border: '1px solid rgba(255, 255, 255, 0.25)' }}>
                    🏛️
                  </div>
                  <span style={{ background: '#FEF08A', color: '#854D0E', fontSize: '0.72rem', fontWeight: 800, padding: '2px 8px', borderRadius: '12px' }}>
                    Official Access Only
                  </span>
                </div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#FFFFFF', margin: '0 0 0.5rem 0' }}>
                  Administrator & Staff
                </h3>
                <p style={{ color: '#E0E7FF', fontSize: '0.85rem', lineHeight: 1.5, margin: '0 0 1.25rem 0' }}>
                  Official login gateway for Institution Administrators across 30 institutions, permitted staff workspaces, and Central Platform Administrators.
                </p>
              </div>
              <Link
                to="/login?category=admin"
                className="btn btn--primary"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '0.75rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  background: '#081c33',
                  color: '#FFFFFF',
                  border: 'none',
                  textDecoration: 'none'
                }}
              >
                Admin / Staff Login →
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================
          SECTION 2: FOUR EDUCATION CATEGORY CARDS
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#FFFFFF', borderBottom: '1px solid #E4E7EC' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#b45309', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
              STRUCTURED EDUCATION TIERS
            </span>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46', margin: '0.35rem 0 0.5rem 0' }}>
              Explore Educational Pathways
            </h2>
            <p style={{ color: '#475467', margin: 0, fontSize: '1rem', maxWidth: '650px', marginLeft: 'auto', marginRight: 'auto' }}>
              Navigate Karnataka's multi-tier educational hierarchy from foundational schooling to higher professional degrees.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem' }}>
            {/* Card 1: Schools */}
            <Link
              to="/schools?category=SCHOOLS"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#EFF4FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #D1E0FF'
                }}>
                  🏫
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Schools (K–10)
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#081c33', marginBottom: '0.6rem' }}>
                  Standards 1 – 10 (Foundational to High School)
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Foundational, primary, middle, and high schools under KSEAB state syllabus, CBSE, and ICSE.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#081c33', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 15 Schools →
              </div>
            </Link>

            {/* Card 2: PU Colleges */}
            <Link
              to="/schools?category=PU"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#FDF2FA',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #FCE7F6'
                }}>
                  🔬
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  PU Colleges (11–12)
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#C11574', marginBottom: '0.6rem' }}>
                  Classes 11 – 12 (Higher Secondary)
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Science (PCMB, PCMC, PCME), Commerce (SEBA, CEBA), and Arts Pre-University education.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#C11574', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 5 PU Colleges →
              </div>
            </Link>

            {/* Card 3: Degree Colleges */}
            <Link
              to="/schools?category=DEGREE"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#ECFDF3',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #D1FADF'
                }}>
                  🏛️
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Degree Colleges
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#027A48', marginBottom: '0.6rem' }}>
                  Undergraduate & Engineering
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Premier autonomous engineering institutes and affiliated undergraduate colleges (B.E., B.Com, B.Sc., BCA).
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#027A48', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 5 Degree Colleges →
              </div>
            </Link>

            {/* Card 4: Universities */}
            <Link
              to="/schools?category=UNIVERSITY"
              style={{
                textDecoration: 'none',
                background: '#F8FAFC',
                border: '1px solid #E2E8F0',
                borderRadius: '12px',
                padding: '1.75rem',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'transform 0.15s ease, box-shadow 0.15s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = '0 8px 20px rgba(16,43,70,0.08)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none' }}
            >
              <div>
                <div style={{
                  width: '52px',
                  height: '52px',
                  borderRadius: '12px',
                  background: '#EEF4FF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '1.6rem',
                  marginBottom: '1rem',
                  border: '1px solid #C7D7FE'
                }}>
                  🎓
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0' }}>
                  Universities
                </h3>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#444CE7', marginBottom: '0.6rem' }}>
                  State & Statutory Universities
                </div>
                <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                  Statutory state and multi-disciplinary universities offering comprehensive undergraduate, postgraduate, and doctoral degrees.
                </p>
              </div>
              <div style={{ marginTop: '1.25rem', color: '#444CE7', fontWeight: 700, fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                Browse 5 Universities →
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* ========================================================
          SECTION 3: BROWSE BY DISTRICT COMPONENT
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#F1F6FC', borderBottom: '1px solid #E4E7EC' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#b45309', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                GEOGRAPHIC DISCOVERY
              </span>
              <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46', margin: '0.35rem 0 0.25rem 0' }}>
                Browse by Karnataka District
              </h2>
              <p style={{ color: '#475467', margin: 0, fontSize: '0.95rem' }}>
                Explore educational opportunities across verified regional headquarters and urban zones.
              </p>
            </div>
            <Link to="/schools" style={{ color: '#081c33', fontWeight: 700, textDecoration: 'none', fontSize: '0.9rem' }}>
              View All 30 Institutions across Karnataka →
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(175px, 1fr))', gap: '1rem' }}>
            {karnatakaDistricts.map((dist, idx) => (
              <Link
                key={idx}
                to={`/schools?district=${encodeURIComponent(dist.name)}`}
                style={{
                  textDecoration: 'none',
                  background: '#FFFFFF',
                  border: '1px solid #E2E8F0',
                  borderRadius: '10px',
                  padding: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  transition: 'all 0.15s ease',
                  boxShadow: '0 1px 3px rgba(16,43,70,0.04)'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.borderColor = '#FF9933'; e.currentTarget.style.transform = 'translateY(-2px)' }}
                onMouseLeave={(e) => { e.currentTarget.style.borderColor = '#E2E8F0'; e.currentTarget.style.transform = 'translateY(0)' }}
              >
                <span style={{ fontSize: '1.5rem' }}>{dist.icon}</span>
                <div>
                  <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46' }}>
                    {dist.name}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.15rem' }}>
                    {dist.count} {dist.count === 1 ? 'Institution' : 'Institutions'}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* ========================================================
          SECTION 4: FEATURED INSTITUTIONS SHOWCASE
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#FFFFFF', borderBottom: '1px solid #E4E7EC' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#b45309', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                FEATURED RECORD CATALOG
              </span>
              <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46', margin: '0.35rem 0 0.25rem 0' }}>
                Prominent State Institutions
              </h2>
              <p style={{ color: '#475467', margin: 0, fontSize: '0.95rem' }}>
                Institutions featuring complete institutional profiles, verified achievements, and transparent data.
              </p>
            </div>
            <Link to="/schools" style={{ color: '#081c33', fontWeight: 700, textDecoration: 'none', fontSize: '0.9rem' }}>
              Explore Full Directory →
            </Link>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(330px, 1fr))', gap: '1.5rem' }}>
            {featuredInstitutions.map((inst) => (
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
                  boxShadow: '0 2px 8px rgba(16,43,70,0.04)',
                  transition: 'box-shadow 0.15s ease'
                }}
              >
                {/* Institution Image Header */}
                <div style={{
                  height: '140px',
                  background: inst.cover_image_url
                    ? `linear-gradient(rgba(16, 43, 70, 0.4), rgba(16, 43, 70, 0.7)), url("${inst.cover_image_url}") center/cover no-repeat`
                    : 'linear-gradient(135deg, #102B46 0%, #081c33 100%)',
                  padding: '1rem',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      background: 'rgba(255, 255, 255, 0.95)',
                      color: '#102B46',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px'
                    }}>
                      CODE: {inst.school_id}
                    </span>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      background: '#081c33',
                      color: '#FFFFFF',
                      padding: '0.2rem 0.5rem',
                      borderRadius: '4px'
                    }}>
                      {inst.school_type}
                    </span>
                  </div>
                </div>

                {/* Institution Body */}
                <div style={{ padding: '1.25rem', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.35rem 0', lineHeight: 1.3 }}>
                      {inst.school_name}
                    </h3>
                    <p style={{ fontSize: '0.825rem', color: '#667085', margin: '0 0 0.75rem 0' }}>
                      📍 {inst.district}, {inst.state}
                    </p>
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
                      {inst.description || `${inst.school_name} is an authorized educational institution offering verified curricula in ${inst.district}.`}
                    </p>
                  </div>

                  <div style={{ borderTop: '1px solid #F2F4F7', paddingTop: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', color: '#667085' }}>
                      🏛️ Est. {inst.established_year || '1962'}
                    </span>
                    <Link
                      to={`/schools/${inst.school_id}`}
                      style={{
                        fontSize: '0.85rem',
                        fontWeight: 700,
                        color: '#081c33',
                        textDecoration: 'none',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}
                    >
                      View Profile →
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========================================================
          SECTION 5: CITIZEN PARENT SERVICES PANEL
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#F8FAFC', borderBottom: '1px solid #E4E7EC' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto' }}>
          <div style={{
            background: 'linear-gradient(135deg, #102B46 0%, #1A3D63 100%)',
            borderRadius: '16px',
            padding: '2.5rem',
            color: '#FFFFFF',
            boxShadow: '0 8px 30px rgba(16,43,70,0.12)'
          }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#93C5FD', letterSpacing: '0.05em' }}>
                  SECURE PARENT SERVICES
                </span>
                <h2 style={{ fontSize: '2.2rem', fontWeight: 800, margin: '0.35rem 0 0.75rem 0', color: '#FFFFFF' }}>
                  Parent & Guardian Access Portal
                </h2>
                <p style={{ color: '#E0E7FF', fontSize: '1rem', lineHeight: 1.6, margin: '0 0 1.5rem 0' }}>
                  Securely link your enrolled children, inspect verified school progress, and submit demographic information corrections using registered admission contacts.
                </p>

                <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                  {!isAuthenticated ? (
                    <>
                      <Link
                        to="/login"
                        style={{
                          background: '#081c33',
                          color: '#FFFFFF',
                          padding: '0.75rem 1.5rem',
                          borderRadius: '8px',
                          fontWeight: 700,
                          textDecoration: 'none',
                          fontSize: '0.95rem'
                        }}
                      >
                        Parent Login →
                      </Link>
                      <Link
                        to="/register"
                        style={{
                          background: 'rgba(255, 255, 255, 0.12)',
                          color: '#FFFFFF',
                          padding: '0.75rem 1.5rem',
                          borderRadius: '8px',
                          fontWeight: 600,
                          textDecoration: 'none',
                          fontSize: '0.95rem',
                          border: '1px solid rgba(255, 255, 255, 0.25)'
                        }}
                      >
                        Register New Parent
                      </Link>
                    </>
                  ) : (
                    <Link
                      to={user?.role === 'parent' ? '/parent' : '/staff'}
                      style={{
                        background: '#081c33',
                        color: '#FFFFFF',
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        fontWeight: 700,
                        textDecoration: 'none',
                        fontSize: '0.95rem'
                      }}
                    >
                      Open Your Dashboard ({user?.role?.replace('_', ' ').toUpperCase()}) →
                    </Link>
                  )}
                </div>
              </div>

              {/* Action Cards */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{ background: 'rgba(255, 255, 255, 0.08)', borderRadius: '10px', padding: '1.25rem', border: '1px solid rgba(255, 255, 255, 0.15)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    <span style={{ fontSize: '1.2rem' }}>📱</span>
                    <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#FFFFFF' }}>Admission Contact Authentication</h4>
                  </div>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: '#CBD5E1', lineHeight: 1.4 }}>
                    Parents authenticate using registered admission phone numbers, ensuring zero public exposure of private numbers.
                  </p>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.08)', borderRadius: '10px', padding: '1.25rem', border: '1px solid rgba(255, 255, 255, 0.15)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
                    <span style={{ fontSize: '1.2rem' }}>✏️</span>
                    <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700, color: '#FFFFFF' }}>Request Student Demographic Updates</h4>
                  </div>
                  <p style={{ margin: 0, fontSize: '0.85rem', color: '#CBD5E1', lineHeight: 1.4 }}>
                    Submit spelling corrections, address updates, or contact revisions directly to school staff review desks.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ========================================================
          SECTION 6: HOW NAGRIKSETU WORKS (3 STEPS)
          ======================================================== */}
      <section style={{ padding: '3.5rem 1.5rem', background: '#FFFFFF', borderBottom: '1px solid #E4E7EC' }}>
        <div className="container" style={{ maxWidth: '1180px', margin: '0 auto', textAlign: 'center' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#b45309', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
            PORTAL GUIDE
          </span>
          <h2 style={{ fontSize: '2rem', fontWeight: 800, color: '#102B46', margin: '0.35rem 0 2.5rem 0' }}>
            How NagrikSetu Works in 3 Simple Steps
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
            <div style={{ padding: '1.5rem', background: '#F8FAFC', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: '#081c33',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '1.1rem',
                margin: '0 auto 1rem auto'
              }}>
                1
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                Search & Filter
              </h3>
              <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                Find institutions across Karnataka using real district location filters, education categories, and verified institutional codes.
              </p>
            </div>

            <div style={{ padding: '1.5rem', background: '#F8FAFC', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: '#081c33',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '1.1rem',
                margin: '0 auto 1rem auto'
              }}>
                2
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                Explore Comprehensive Profiles
              </h3>
              <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                Inspect physical infrastructure, 13-category facility audits, hostels, transit routes, and academic programme capacities.
              </p>
            </div>

            <div style={{ padding: '1.5rem', background: '#F8FAFC', borderRadius: '12px', border: '1px solid #E2E8F0' }}>
              <div style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: '#081c33',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '1.1rem',
                margin: '0 auto 1rem auto'
              }}>
                3
              </div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                Access Verified Services
              </h3>
              <p style={{ color: '#475467', fontSize: '0.875rem', lineHeight: 1.5, margin: 0 }}>
                Parents and staff authenticate to link enrolled children, review update requests, and manage institutional records safely.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
