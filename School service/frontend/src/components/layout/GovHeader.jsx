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
      {/* Administrative Top Bar when browsing public catalog */}
      {isViewingPublicSite && (
        <div style={{ background: '#0B2036', color: '#E0EAFF', padding: '0.45rem 1rem', fontSize: '0.82rem', borderBottom: '1px solid #1E3A8A' }}>
          <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ background: '#F59E0B', color: '#1E293B', fontWeight: 700, fontSize: '0.7rem', padding: '0.15rem 0.5rem', borderRadius: '4px', textTransform: 'uppercase' }}>
                ADMIN MODE
              </span>
              <span>Browsing public institution portal as <strong>{roleLabel}</strong></span>
            </div>
            <Link
              to={getDashboardPath()}
              style={{
                background: '#155EEF',
                color: '#ffffff',
                padding: '0.2rem 0.75rem',
                borderRadius: '4px',
                textDecoration: 'none',
                fontWeight: 600,
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

      {/* Utility bar */}
      <div className="utility-bar" role="banner">
        <div className="container utility-bar__inner">
          <div className="utility-bar__left">
            <span className="utility-bar__badge">DEMO</span>
            <span>NagrikSetu · School Service Portal · Karnataka</span>
          </div>
          <span>This is a demonstration application. Not an official government service.</span>
        </div>
      </div>

      {/* Main header */}
      <div className="gov-header" style={{ borderBottom: '1px solid #e8eaed', background: '#ffffff' }}>
        <div className="container gov-header__inner" style={{ padding: '0.85rem 1rem' }}>
          <Link to={getBrandDestination()} className="gov-header__brand" aria-label="NagrikSetu Home" style={{ textDecoration: 'none' }}>
            <div className="gov-header__logo" aria-hidden="true" style={{ background: 'linear-gradient(135deg, #102B46 0%, #155EEF 100%)', color: '#ffffff', fontWeight: 800 }}>NS</div>
            <div className="gov-header__name">
              <div className="gov-header__title" style={{ color: '#102B46', fontWeight: 800, fontSize: '1.4rem' }}>NagrikSetu</div>
              <div className="gov-header__subtitle" style={{ color: '#475467', fontWeight: 600, fontSize: '0.78rem' }}>Education Information Platform</div>
            </div>
          </Link>

          <div className="gov-header__actions">
            {isAuthenticated ? (
              <>
                <div className="gov-header__user" style={{ background: '#F1F6FC', padding: '0.35rem 0.75rem', borderRadius: '20px', border: '1px solid #D0D5DD', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <div className="gov-header__avatar" aria-hidden="true" style={{ background: '#102B46', color: '#ffffff' }}>
                    {(user?.email ?? user?.phone ?? 'U').charAt(0).toUpperCase()}
                  </div>
                  <div className="hide-mobile" style={{ display: 'flex', flexDirection: 'column', lineHeight: 1.2 }}>
                    <span style={{ color: '#102B46', fontWeight: 600, fontSize: '0.875rem' }}>
                      {user?.full_name ?? user?.email ?? user?.phone ?? 'User'}
                    </span>
                    <span style={{ color: '#667085', fontSize: '0.72rem', fontWeight: 500 }}>
                      {roleLabel}
                    </span>
                  </div>
                </div>
                <NotificationBellDropdown />
                <Link to={getDashboardPath()} className="btn btn--secondary btn--sm" style={{ background: '#102B46', color: '#ffffff', border: 'none' }}>
                  Dashboard
                </Link>
                <button className="btn btn--ghost btn--sm" onClick={handleLogout}>
                  Sign Out
                </button>
              </>
            ) : (
              <>
                <Link to="/login"    className="btn btn--secondary btn--sm" style={{ borderColor: '#D0D5DD', color: '#102B46', fontWeight: 600 }}>Login</Link>
                <Link to="/register" className="btn btn--primary btn--sm" style={{ background: '#155EEF', border: 'none', fontWeight: 600 }}>Sign Up</Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Navigation bar */}
      <nav className="nav-bar" aria-label="Main navigation" style={{ background: '#102B46' }}>
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

