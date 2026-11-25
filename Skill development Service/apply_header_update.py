# -*- coding: utf-8 -*-
import sys

app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. State: add centreMobileMenuOpen
target_state = '  const [adminMobileMenuOpen, setAdminMobileMenuOpen] = useState<boolean>(false);\n'
new_state = '  const [adminMobileMenuOpen, setAdminMobileMenuOpen] = useState<boolean>(false);\n  const [centreMobileMenuOpen, setCentreMobileMenuOpen] = useState<boolean>(false);\n'

if 'centreMobileMenuOpen' not in content:
    assert target_state in content, 'target_state not found'
    content = content.replace(target_state, new_state, 1)
    print('State centreMobileMenuOpen added.')
else:
    print('centreMobileMenuOpen already exists.')

# 2. Slice from gov_idx to header_end_idx
gov_idx = content.find('      {/* 1. Official Government Top Bar */}')
header_end_idx = content.find('          </header>', gov_idx) + len('          </header>')
assert gov_idx != -1 and header_end_idx != -1, 'Indices not found'

old_block = content[gov_idx:header_end_idx]

replacement = '''      {/* Official Government Top Bar for Non-Centre Portals */}
      {userRole !== 'TRAINING_CENTRE_ADMIN' && (
        <div className="gov-top-bar">
          <span>
            <Landmark size={14} className="text-orange-400" />
            Government of India • National Citizen Portal • National Skilling Initiative
          </span>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span>Accessibility: WCAG 2.2 AA Standard</span>
            <span style={{ fontSize: '0.72rem', color: '#cbd5e1' }}>English</span>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TRAINING CENTRE ADMINISTRATOR DESK & WORKSPACE                           */}
      {/* Strict separation: Centre Admin only accesses Centre-scoped APIs         */}
      {/* ========================================================================= */}
      {userRole === 'TRAINING_CENTRE_ADMIN' ? (
        <div>
          {/* DEDICATED 3-SECTION TRAINING CENTRE HEADER & NAVIGATION ARCHITECTURE */}
          <header className="tc-header-wrapper" role="banner">
            {/* SECTION A: Official Government Information Bar */}
            <div className="tc-gov-bar">
              <div className="tc-gov-container">
                <div className="tc-gov-left">
                  <Landmark size={14} className="text-orange-400" />
                  <span>Government of India • National Citizen Portal • National Skilling Initiative</span>
                </div>
                <div className="tc-gov-right">
                  <span>Accessibility: WCAG 2.2 AA Standard</span>
                  <select 
                    className="tc-lang-select" 
                    aria-label="Language Selector"
                    defaultValue="en"
                  >
                    <option value="en">English</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION B: Branding & Authenticated Centre Identity */}
            <div className="tc-identity-bar">
              <div className="tc-identity-container">
                {/* Left: Branding & Subtitle */}
                <div 
                  className="tc-brand-left" 
                  onClick={() => { setCentreTab('dashboard'); setCentreMobileMenuOpen(false); }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { setCentreTab('dashboard'); setCentreMobileMenuOpen(false); } }}
                  aria-label="NagrikSetu Training Centre Portal Home"
                >
                  <div className="tc-brand-icon">
                    <Building2 size={24} color="#ffffff" />
                  </div>
                  <div>
                    <h1 className="tc-brand-title">NagrikSetu</h1>
                    <div className="tc-brand-subtitle">Training Centre Portal</div>
                  </div>
                </div>

                {/* Right: Centre Identity & Verification */}
                <div className="tc-centre-right">
                  {/* Multi-Centre Switcher Dropdown (if assigned multiple centres) */}
                  {assignedCentres && assignedCentres.length > 1 && (
                    <div className="tc-centre-switcher">
                      <Building2 size={14} color="#0f766e" />
                      <select
                        value={centreId || (assignedCentres[0]?.id ? String(assignedCentres[0].id) : '')}
                        onChange={(e) => switchAdminCentre(e.target.value)}
                        aria-label="Select Training Centre"
                      >
                        {assignedCentres.map((ac: any) => (
                          <option key={ac.id} value={String(ac.id)}>
                            {ac.name} ({ac.district})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div className="tc-centre-info-card">
                    <div className="tc-centre-name" title={centreProfile?.name || 'Authorized Training Centre'}>
                      {centreProfile?.name || 'Authorized Training Centre'}
                    </div>
                    <div className="tc-centre-badge-row">
                      <span className="tc-pulse-dot" aria-hidden="true"></span>
                      <span className="tc-verified-label">CENTRE ADMIN VERIFIED</span>
                      {userName && (
                        <span className="tc-admin-user">• {userName}</span>
                      )}
                    </div>
                  </div>

                  {/* Mobile Hamburger Menu Toggle Button */}
                  <button
                    type="button"
                    className="tc-mobile-toggle"
                    onClick={() => setCentreMobileMenuOpen(!centreMobileMenuOpen)}
                    aria-label="Toggle training centre navigation menu"
                    aria-expanded={centreMobileMenuOpen}
                  >
                    {centreMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                  </button>
                </div>
              </div>
            </div>

            {/* SECTION C: Primary Desktop Navigation Bar */}
            <div className="tc-nav-bar">
              <div className="tc-nav-container">
                <nav className="tc-nav-links-desktop" aria-label="Training Centre Navigation">
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'dashboard' ? 'active' : ''}`}
                    onClick={() => setCentreTab('dashboard')}
                  >
                    <Target size={15} /> Dashboard & Stats
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'applications' ? 'active' : ''}`}
                    onClick={() => setCentreTab('applications')}
                  >
                    <FileText size={15} /> Applications
                    <span className="tc-nav-count">{centreEnrollments.length}</span>
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'programmes' ? 'active' : ''}`}
                    onClick={() => setCentreTab('programmes')}
                  >
                    <GraduationCap size={15} /> Courses & Batches
                    <span className="tc-nav-count">{centreProgrammes.length}</span>
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'trainers' ? 'active' : ''}`}
                    onClick={() => setCentreTab('trainers')}
                  >
                    <Users size={15} /> Trainers
                    <span className="tc-nav-count">{centreTrainers.length}</span>
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setCentreTab('profile')}
                  >
                    <Building2 size={15} /> Centre Profile & Labs
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'reports' ? 'active' : ''}`}
                    onClick={() => setCentreTab('reports')}
                  >
                    <Award size={15} /> Reports & Analytics
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'security' ? 'active' : ''}`}
                    onClick={() => setCentreTab('security')}
                  >
                    <Lock size={15} /> Security & Password
                  </button>
                </nav>

                {/* Far-Right Outlined Logout Button */}
                <button 
                  type="button"
                  className="tc-logout-btn" 
                  onClick={handleLogout}
                  aria-label="Log out of Training Centre Portal"
                >
                  <LogOut size={15} /> {t('nav.logout')}
                </button>
              </div>
            </div>

            {/* Mobile / Compact Navigation Drawer */}
            <div className={`tc-mobile-drawer ${centreMobileMenuOpen ? 'open' : ''}`} role="dialog" aria-label="Mobile Navigation Drawer">
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => { setCentreTab('dashboard'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Target size={16} /> Dashboard & Stats</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'applications' ? 'active' : ''}`}
                onClick={() => { setCentreTab('applications'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FileText size={16} /> Applications</span>
                <span className="tc-nav-count">{centreEnrollments.length}</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'programmes' ? 'active' : ''}`}
                onClick={() => { setCentreTab('programmes'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><GraduationCap size={16} /> Courses & Batches</span>
                <span className="tc-nav-count">{centreProgrammes.length}</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'trainers' ? 'active' : ''}`}
                onClick={() => { setCentreTab('trainers'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Users size={16} /> Trainers</span>
                <span className="tc-nav-count">{centreTrainers.length}</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'profile' ? 'active' : ''}`}
                onClick={() => { setCentreTab('profile'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Building2 size={16} /> Centre Profile & Labs</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'reports' ? 'active' : ''}`}
                onClick={() => { setCentreTab('reports'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Award size={16} /> Reports & Analytics</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'security' ? 'active' : ''}`}
                onClick={() => { setCentreTab('security'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Lock size={16} /> Security & Password</span>
              </button>

              <button 
                type="button"
                className="tc-mobile-logout" 
                onClick={handleLogout}
              >
                <LogOut size={16} /> {t('nav.logout')}
              </button>
            </div>
          </header>'''

content = content[:gov_idx] + replacement + content[header_end_idx:]

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('App.tsx successfully updated with 3-section header architecture!')
