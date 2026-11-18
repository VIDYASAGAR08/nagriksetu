import { useState } from 'react'
import { Link, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import NotificationBellDropdown from '../notifications/NotificationBellDropdown.jsx'

export default function GovHeader() {
  const { isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)

  function handleLogout() {
    logout()
    navigate('/')
  }

  function getDashboardPath() {
    if (!user) return '/'
    switch (user.role) {
      case 'parent':        return '/parent'
      case 'student':       return '/student'
      case 'school_admin':  return '/institution-admin'
      case 'school_staff':
      case 'admissions_officer':
      case 'academic_admin':
      case 'student_records_officer':
      case 'general_staff': return '/staff'
      case 'platform_admin':return '/admin'
      default:              return '/'
    }
  }

  function getBrandDestination() {
    if (!isAuthenticated || !user) return '/'
    // Administrators and students return to their specific dashboard when clicking the main logo
    if (['platform_admin', 'school_admin', 'institution_admin', 'school_staff', 'admissions_officer', 'academic_admin', 'student_records_officer', 'student'].includes(user.role)) {
      return getDashboardPath()
    }
    return '/'
  }

  const isAdministrativeUser = isAuthenticated && ['platform_admin', 'school_admin', 'institution_admin', 'school_staff', 'admissions_officer', 'academic_admin'].includes(user?.role)
  const isViewingPublicSite = isAdministrativeUser && (
    location.pathname === '/schools' ||
    location.pathname.startsWith('/schools/') ||
    location.pathname === '/about' ||
    location.pathname === '/help' ||
    location.pathname === '/contact' ||
    (location.pathname === '/' && location.search.includes('view=public'))
  )

  const roleLabel = {
    platform_admin: 'Central Directorate (Platform Admin)',
    school_admin: 'Institution Administrator',
    institution_admin: 'Institution Administrator',
    school_staff: 'Institution Staff',
    admissions_officer: 'Admissions Officer',
    academic_admin: 'Academic Administrator',
    student_records_officer: 'Student Records Officer',
    student: 'Student',
    parent: 'Citizen / Parent',
  }[user?.role] || 'User'

  return (
    <header>
      {/* National Flag Tricolor Ribbon */}
      <div style={{ height: '5px', width: '100%', background: 'linear-gradient(to right, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%)' }} />

      {/* Official Government Utility Bar */}
      <div style={{ background: '#081c33', color: '#f8fafc', padding: '0.4rem 1rem', fontSize: '0.78rem', borderBottom: '1px solid #1e293b' }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{ color: '#FF9933', fontWeight: 800 }}>भारत सरकार</span>
            <span style={{ color: '#475467' }}>|</span>
            <span style={{ fontWeight: 600 }}>Government of India</span>
            <span style={{ color: '#475467' }} className="hide-mobile">|</span>
            <span style={{ color: '#94a3b8' }} className="hide-mobile">शिक्षा सेवा पोर्टल (Education Portal · Karnataka)</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <a
              href="http://localhost:5173"
              style={{
                background: 'rgba(255, 153, 51, 0.15)',
                color: '#FF9933',
                border: '1px solid rgba(255, 153, 51, 0.4)',
                padding: '0.2rem 0.65rem',
                borderRadius: '6px',
                textDecoration: 'none',
                fontWeight: 700,
                fontSize: '0.75rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}
            >
              🏛️ Central Portal (Port 5173)
            </a>
          </div>
        </div>
      </div>

      {/* Administrative Top Bar when browsing public catalog */}
      {isViewingPublicSite && (
        <div style={{ background: '#0B2036', color: '#E0EAFF', padding: '0.45rem 1rem', fontSize: '0.82rem', borderBottom: '1px solid #1E3A8A' }}>
          <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ background: '#FF9933', color: '#081c33', fontWeight: 800, fontSize: '0.7rem', padding: '0.15rem 0.5rem', borderRadius: '4px', textTransform: 'uppercase' }}>
                ADMIN MODE
              </span>
              <span>Browsing public institution portal as <strong>{roleLabel}</strong></span>
            </div>
            <Link
              to={getDashboardPath()}
              style={{
                background: '#FF9933',
                color: '#081c33',
                padding: '0.2rem 0.75rem',
                borderRadius: '4px',
                textDecoration: 'none',
                fontWeight: 700,
                fontSize: '0.78rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
              }}
            >
              ← Return to Dashboard
            </Link>
          </div>
        </div>
      )}

      {/* Main header */}
      <div className="gov-header" style={{ borderBottom: '1px solid #e2e8f0', background: '#ffffff' }}>
        <div className="container gov-header__inner" style={{ padding: '0.85rem 1rem' }}>
          <Link to={getBrandDestination()} className="gov-header__brand" aria-label="NagrikSetu Home" style={{ textDecoration: 'none' }}>
            <div className="gov-header__logo" aria-hidden="true" style={{ background: 'linear-gradient(135deg, #081c33 0%, #1e3a8a 100%)', color: '#FF9933', fontWeight: 900, border: '2px solid #FF9933' }}>
              NS
            </div>
            <div className="gov-header__name">
              <div className="gov-header__title" style={{ color: '#081c33', fontWeight: 900, fontSize: '1.45rem', letterSpacing: '-0.02em' }}>
                नागरिक सेतु <span style={{ color: '#FF9933', fontWeight: 800, fontSize: '1.25rem' }}>· NagrikSetu</span>
              </div>
              <div className="gov-header__subtitle" style={{ color: '#64748b', fontWeight: 600, fontSize: '0.78rem' }}>
                शिक्षा सेवा पोर्टल (Department of School & Higher Education · Karnataka)
              </div>
            </div>
          </Link>

          <div className="gov-header__actions">
            {isAuthenticated ? (
              <>
                <div className="gov-header__user" style={{ background: '#f8fafc', padding: '0.35rem 0.75rem', borderRadius: '20px', border: '1px solid #cbd5e1', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div className="gov-header__avatar" aria-hidden="true" style={{ background: '#081c33', color: '#FF9933' }}>
                    {(user?.email ?? user?.phone ?? 'U').charAt(0).toUpperCase()}
                  </div>
                  <div className="hide-mobile" style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
                    <span style={{ color: '#081c33', fontWeight: 700, fontSize: '0.875rem' }}>
                      {user?.full_name ?? user?.email ?? user?.phone ?? 'User'}
                    </span>
                    <span style={{ color: '#64748b', fontSize: '0.72rem', fontWeight: 600 }}>
                      {roleLabel}
                    </span>
                  </div>
                </div>
                <NotificationBellDropdown />
                <Link to={getDashboardPath()} className="btn btn--secondary btn--sm" style={{ background: '#081c33', color: '#ffffff', border: 'none' }}>
                  Dashboard
                </Link>
                <button className="btn btn--ghost btn--sm" onClick={handleLogout}>
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="btn btn--secondary btn--sm" style={{ borderColor: '#cbd5e1', color: '#081c33', fontWeight: 700 }}>Login</Link>
                <Link to="/register" className="btn btn--primary btn--sm" style={{ background: '#FF9933', color: '#081c33', border: 'none', fontWeight: 800 }}>Sign Up</Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <nav className="nav-bar" aria-label="Main navigation" style={{ background: '#081c33' }}>
        <div className="container nav-bar__inner">
          <button
            className="nav-bar__toggle"
            aria-label="Toggle navigation"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(o => !o)}
          >
            ☰
          </button>

          <ul className={`nav-bar__list${menuOpen ? ' open' : ''}`} role="list">
            <li className="nav-bar__item">
              <NavLink to={isAuthenticated && isAdministrativeUser ? '/?view=public' : '/'} end className="nav-bar__link" onClick={() => setMenuOpen(false)}>
                Home
              </NavLink>
            </li>
            <li className="nav-bar__item">
              <NavLink to="/schools" className="nav-bar__link" onClick={() => setMenuOpen(false)}>
                Explore Institutions
              </NavLink>
            </li>
            {isAuthenticated && (
              <li className="nav-bar__item">
                <NavLink to={getDashboardPath()} className="nav-bar__link" onClick={() => setMenuOpen(false)} style={{ color: '#93C5FD', fontWeight: 600 }}>
                  My Dashboard
                </NavLink>
              </li>
            )}
            <li className="nav-bar__item">
              <NavLink to="/about" className="nav-bar__link" onClick={() => setMenuOpen(false)}>
                About Us
              </NavLink>
            </li>
            <li className="nav-bar__item">
              <NavLink to="/help" className="nav-bar__link" onClick={() => setMenuOpen(false)}>
                Help
              </NavLink>
            </li>
            <li className="nav-bar__item">
              <NavLink to="/contact" className="nav-bar__link" onClick={() => setMenuOpen(false)}>
                Contact
              </NavLink>
            </li>
          </ul>
        </div>
      </nav>
    </header>
  )
}

