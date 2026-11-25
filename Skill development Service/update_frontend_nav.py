with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate top navbar sign in / register buttons and add Project Owner Register pill
navbar_target = """                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>"""

navbar_replacement = """                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>
                <button
                  type="button"
                  style={{
                    backgroundColor: '#0f2444',
                    color: '#38bdf8',
                    border: '1px solid #1e3a8a',
                    padding: '0.45rem 0.85rem',
                    borderRadius: '6px',
                    fontSize: '0.78rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.06)'
                  }}
                  onClick={() => {
                    fetchCentreRegister();
                    setAuthPortalView('project_owner_register');
                    setAuthError('');
                  }}
                  title="View 10 Training Centre Accounts, Setup Status & Demonstration Access"
                >
                  <Shield size={13} color="#38bdf8" /> 10 Centres Register
                </button>"""

if navbar_target in text and "10 Centres Register" not in text:
    text = text.replace(navbar_target, navbar_replacement, 1)
    print("Added 10 Centres Register button to Navbar")
else:
    print("Navbar button already added or target not found")

# Now let's add option in Option 2 (Training Centre Login) and Select Role modal
# In Select Role modal:
select_role_target = """                {/* Option 2: Training Centre */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthPortalView('login_centre');
                    setIsAdminLogin(true);
                    setAuthError('');
                    setLoginEmail('centre.bengaluru@nagriksetu.local');
                    setLoginPassword('CentreAdmin@2026!');
                  }}"""

select_role_replacement = """                {/* Option 2: Training Centre */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthPortalView('login_centre');
                    setIsAdminLogin(true);
                    setAuthError('');
                    setLoginEmail('centre.bengaluru@nagriksetu.local');
                    setLoginPassword('CentreAdmin@2026!');
                  }}"""

# In Training Centre Login modal, add buttons: "Representative Self-Registration" and "Project Owner Register"
centre_login_target = """                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Account Selection
                </button>
                <span style={{ color: '#94a3b8', fontSize: '0.74rem' }}>Managed by National Mission</span>"""

centre_login_replacement = """                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Roles
                </button>
                <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                  <button
                    type="button"
                    style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer', fontSize: '0.76rem' }}
                    onClick={() => {
                      fetchCentreRegister();
                      setAuthPortalView('register_centre_rep');
                      setRepMsg(null);
                    }}
                  >
                    Register Representative →
                  </button>
                  <button
                    type="button"
                    style={{ background: 'none', border: 'none', color: '#0f766e', fontWeight: 700, cursor: 'pointer', fontSize: '0.76rem' }}
                    onClick={() => {
                      fetchCentreRegister();
                      setAuthPortalView('project_owner_register');
                    }}
                  >
                    Owner Register
                  </button>
                </div>"""

if centre_login_target in text:
    text = text.replace(centre_login_target, centre_login_replacement, 1)
    print("Added register links to Training Centre login modal")
else:
    print("Centre login target not matched")

with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
