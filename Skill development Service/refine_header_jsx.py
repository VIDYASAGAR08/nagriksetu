app_path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Let's inspect the nav-links and nav-actions structure
old_header_block = """          {/* CENTRE: Navigation Links */}
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
            ) : ("""

# In the mobile drawer, also offer My Profile and Log Out when token exists so mobile user has full access
new_header_block = """          {/* CENTRE: Navigation Links */}
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

            {/* Mobile Drawer Only Profile & Logout items */}
            {token && (
              <div className="mobile-drawer-account-items">
                {userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
                  <button className={`nav-item-btn ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}>
                    <User size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} /> My Profile
                  </button>
                )}
                <button className="nav-item-btn mobile-logout-item" onClick={() => { handleLogout(); setMobileMenuOpen(false); }}>
                  <LogOut size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} /> Log Out ({userName || citizenRef})
                </button>
              </div>
            )}
          </nav>

          {/* RIGHT: User Profile, Account Information & Logout */}
          <div className="nav-actions">
            {token ? (
              <div className="nav-user-account-wrapper">
                {userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
                  <button
                    className={`nav-item-btn nav-profile-link ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}
                  >
                    <User size={13} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} />
                    My Profile
                  </button>
                )}

                {/* Logged-in user badge (cleanly separated) */}
                <div className="nav-user-badge" title={userEmail || userName}>
                  <div className="nav-user-avatar">
                    <User size={12} />
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
                  <LogOut size={13} /> <span>{t('nav.logout')}</span>
                </button>
              </div>
            ) : ("""

assert old_header_block in content, "old_header_block not found in App.tsx"
content = content.replace(old_header_block, new_header_block, 1)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS: App.tsx refined with mobile-drawer-account-items and robust profile alignment!")
