import os

file_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove "10 Centres Register" button from public homepage header
header_btn_old = """                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
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

header_btn_new = """                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>"""

if header_btn_old in text:
    text = text.replace(header_btn_old, header_btn_new, 1)
    print("1. Successfully removed '10 Centres Register' button from public header.")
else:
    print("1. Target for header button not found.")

# 2. In Training Centre Login: remove "Owner Register" link completely, keep "Back to Roles" and "Register Representative"
centre_login_footer_old = """              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
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
                </div>
              </div>"""

centre_login_footer_new = """              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Roles
                </button>
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
              </div>"""

if centre_login_footer_old in text:
    text = text.replace(centre_login_footer_old, centre_login_footer_new, 1)
    print("2. Successfully removed 'Owner Register' button from Training Centre Login modal.")
else:
    print("2. Target for centre login footer not found.")

# 3. In Representative Registration: remove "View 10 Centre Register" completely, keep "Already registered? Centre Sign In"
rep_reg_footer_old = """              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => setAuthPortalView('login_centre')}
                >
                  ← Already registered? Centre Sign In
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                  onClick={() => {
                    fetchCentreRegister();
                    setAuthPortalView('project_owner_register');
                  }}
                >
                  View 10 Centre Register →
                </button>
              </div>"""

rep_reg_footer_new = """              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => setAuthPortalView('login_centre')}
                >
                  ← Already registered? Centre Sign In
                </button>
              </div>"""

if rep_reg_footer_old in text:
    text = text.replace(rep_reg_footer_old, rep_reg_footer_new, 1)
    print("3. Successfully removed 'View 10 Centre Register' button from Representative Registration modal.")
else:
    print("3. Target for rep registration footer not found.")

# 4. In Representative Registration description: ensure exact text matching user request
# "Select your assigned Accredited Training Centre and establish your independent login credentials. Existing institutional records are securely preserved."
reg_desc_old = "Select your assigned Accredited Training Centre (1 of 10) and establish your independent login credentials. Existing institutional records are securely preserved."
reg_desc_new = "Select your assigned Accredited Training Centre (1 of 10) and establish your independent login credentials. Existing institutional records are securely preserved."

# In Training Centre Login description:
# "Authorised workspace for Training Centre Administrators. Centre-level data isolation is strictly enforced."
centre_desc_old = "Authorised workspace for accredited Training Centre Administrators. Centre-level data isolation is strictly enforced."
centre_desc_new = "Authorised workspace for Training Centre Administrators. Centre-level data isolation is strictly enforced."

if centre_desc_old in text:
    text = text.replace(centre_desc_old, centre_desc_new, 1)
    print("4. Updated Training Centre Login description text.")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print("FRONTEND_CLEANUP_APPLIED")
