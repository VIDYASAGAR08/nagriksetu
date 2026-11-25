app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Locate header-main in App.tsx
old_header = """      <header className="header-main">
        <div className="header-container">
          <div className="brand-wrapper" onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
            <div className="brand-emblem">
              <Award size={24} />
            </div>
            <div className="brand-text">
              <h1>
                NagrikSetu
              </h1>
              <p>Skill Development Service</p>
            </div>
          </div>

          <button
            type="button"
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <nav className={`nav-links ${mobileMenuOpen ? 'nav-open' : ''}`}>
            <button className={`nav-item-btn ${activeTab === 'home' ? 'active' : ''}`} onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
              {t('nav.home')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'explore_skills' || activeTab === 'category_details' ? 'active' : ''}`} onClick={() => { setActiveTab('explore_skills'); setMobileMenuOpen(false); }}>
              <Compass size={15} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} /> Explore Skills
            </button>
            <button className={`nav-item-btn ${activeTab === 'courses' ? 'active' : ''}`} onClick={() => { setActiveTab('courses'); setMobileMenuOpen(false); }}>
              All Courses
            </button>
            <button className={`nav-item-btn ${activeTab === 'programmes' ? 'active' : ''}`} onClick={() => { setActiveTab('programmes'); setMobileMenuOpen(false); }}>
              {t('nav.training_programmes')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'centres' ? 'active' : ''}`} onClick={() => { setActiveTab('centres'); setMobileMenuOpen(false); }}>
              {t('nav.centres')}
            </button>

            {token && userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
              <>
                <button className={`nav-item-btn ${activeTab === 'applications' ? 'active' : ''}`} onClick={() => { setActiveTab('applications'); setMobileMenuOpen(false); }}>
                  My Applications
                </button>
                {isStudent && (
                  <button
                    className={`nav-item-btn ${activeTab === 'student_portal' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('student_portal'); setMobileMenuOpen(false); }}
                    style={{
                      color: activeTab === 'student_portal' ? '#ffffff' : '#0284c7',
                      backgroundColor: activeTab === 'student_portal' ? '#0284c7' : '#f0f9ff',
                      fontWeight: 700,
                      borderRadius: '6px',
                      padding: '0.35rem 0.65rem',
                      border: '1px solid #bae6fd'
                    }}
                  >
                    <GraduationCap size={15} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'middle' }} />
                    Student Portal {studentId ? `(${studentId})` : ''}
                  </button>
                )}
                <button className={`nav-item-btn ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}>
                  My Profile
                </button>
              </>
            )}
            <button className={`nav-item-btn ${activeTab === 'gap' ? 'active' : ''}`} onClick={() => { setActiveTab('gap'); setMobileMenuOpen(false); }}>
              {t('nav.gap_analysis')}
            </button>
          </nav>

          <div className="nav-actions">
            {token ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#334155' }}>
                  {userName || citizenRef}
                </span>
                {userRole === 'SKILL_DEPARTMENT_ADMIN' && (
                  <button className="btn-admin-pill" onClick={() => setAdminTab('applications')}>
                    <Shield size={14} /> Admin Desk
                  </button>
                )}
                <button className="btn-navy-outline" onClick={handleLogout}>
                  <LogOut size={14} /> {t('nav.logout')}
                </button>
              </div>
            ) : (
              <>
                <button className="btn-navy-outline" onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}>
                  <LogIn size={14} /> {t('nav.sign_in')}
                </button>
                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>
              </>
            )}
          </div>
        </div>
      </header>"""

new_header = """      <header className="header-main">
        <div className="header-container">
          {/* LEFT: NagrikSetu logo and Skill Development Service branding */}
          <div className="brand-wrapper" onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
            <div className="brand-emblem">
              <Award size={22} />
            </div>
            <div className="brand-text">
              <h1>NagrikSetu</h1>
              <p>Skill Development Service</p>
            </div>
          </div>

          {/* MOBILE HAMBURGER TOGGLE */}
          <button
            type="button"
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          {/* CENTRE: Navigation Links */}
          <nav className={`nav-links ${mobileMenuOpen ? 'nav-open' : ''}`}>
            <button className={`nav-item-btn ${activeTab === 'home' ? 'active' : ''}`} onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
              {t('nav.home')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'explore_skills' || activeTab === 'category_details' ? 'active' : ''}`} onClick={() => { setActiveTab('explore_skills'); setMobileMenuOpen(false); }}>
              <Compass size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} /> Explore Skills
            </button>
            <button className={`nav-item-btn ${activeTab === 'courses' ? 'active' : ''}`} onClick={() => { setActiveTab('courses'); setMobileMenuOpen(false); }}>
              All Courses
            </button>
            <button className={`nav-item-btn ${activeTab === 'programmes' ? 'active' : ''}`} onClick={() => { setActiveTab('programmes'); setMobileMenuOpen(false); }}>
              {t('nav.training_programmes')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'centres' ? 'active' : ''}`} onClick={() => { setActiveTab('centres'); setMobileMenuOpen(false); }}>
              {t('nav.centres')}
            </button>

            {token && userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
              <>
                <button className={`nav-item-btn ${activeTab === 'applications' ? 'active' : ''}`} onClick={() => { setActiveTab('applications'); setMobileMenuOpen(false); }}>
                  My Applications
                </button>
                {isStudent && (
                  <button
                    className={`nav-item-btn nav-student-portal-btn ${activeTab === 'student_portal' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('student_portal'); setMobileMenuOpen(false); }}
                  >
                    <GraduationCap size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} />
                    Student Portal
                  </button>
                )}
              </>
            )}
            <button className={`nav-item-btn ${activeTab === 'gap' ? 'active' : ''}`} onClick={() => { setActiveTab('gap'); setMobileMenuOpen(false); }}>
              {t('nav.gap_analysis')}
            </button>
          </nav>

          {/* RIGHT: User Profile, Account Information & Logout */}
          <div className="nav-actions">
            {token ? (
              <div className="nav-user-account-wrapper">
                {userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
                  <button
                    className={`nav-item-btn nav-profile-link ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}
                    style={{ marginRight: '0.25rem' }}
                  >
                    <User size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} />
                    My Profile
                  </button>
                )}

                {/* Logged-in user badge (cleanly separated) */}
                <div className="nav-user-badge" title={userEmail || userName}>
                  <div className="nav-user-avatar">
                    <User size={13} />
                  </div>
                  <div className="nav-user-info">
                    <span className="nav-user-name">{userName || citizenRef || 'User'}</span>
                    {isStudent && studentId && (
                      <span className="nav-user-subtag">{studentId}</span>
                    )}
                  </div>
                </div>

                {userRole === 'SKILL_DEPARTMENT_ADMIN' && (
                  <button className="btn-admin-pill" onClick={() => setAdminTab('applications')}>
                    <Shield size={13} /> Admin Desk
                  </button>
                )}

                <button className="btn-logout" onClick={handleLogout} title={t('nav.logout')}>
                  <LogOut size={14} /> <span>{t('nav.logout')}</span>
                </button>
              </div>
            ) : (
              <div className="nav-guest-actions">
                <button className="btn-navy-outline" onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}>
                  <LogIn size={14} /> {t('nav.sign_in')}
                </button>
                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>
              </div>
            )}
          </div>
        </div>
      </header>"""

assert old_header in content, "old_header not found in App.tsx"
content = content.replace(old_header, new_header, 1)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: App.tsx header structure refactored!")
