import os

file_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update forgotEmail state to include forgotSource
target_1 = "const [forgotEmail, setForgotEmail] = useState<string>('');"
replacement_1 = "const [forgotEmail, setForgotEmail] = useState<string>('');\n  const [forgotSource, setForgotSource] = useState<'citizen' | 'centre'>('citizen');"

if target_1 in text:
    text = text.replace(target_1, replacement_1, 1)
    print("1. Added forgotSource state")
else:
    print("1. Target 1 not found (may already exist)")

# 2. Add 'security' to centreTab state
target_2 = "const [centreTab, setCentreTab] = useState<'dashboard' | 'applications' | 'programmes' | 'batches' | 'trainers' | 'profile' | 'reports'>('dashboard');"
replacement_2 = "const [centreTab, setCentreTab] = useState<'dashboard' | 'applications' | 'programmes' | 'batches' | 'trainers' | 'profile' | 'reports' | 'security'>('dashboard');"

if target_2 in text:
    text = text.replace(target_2, replacement_2, 1)
    print("2. Added security to centreTab state")
else:
    print("2. Target 2 not found (may already exist)")

# 3. Add Forgot Password button into Training Centre Login modal
target_3 = '''                <div className="form-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Administrator Password:</label>
                  <input
                    type="password"
                    required
                    className="form-control"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Enter centre administrator password"
                  />
                </div>'''

replacement_3 = '''                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Administrator Password:</label>
                    <button
                      type="button"
                      style={{ background: 'none', border: 'none', color: '#0284c7', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', padding: 0 }}
                      onClick={() => {
                        setAuthPortalView('forgot_password');
                        setForgotSource('centre');
                        setForgotEmail(loginEmail);
                        setForgotOtpSent(false);
                        setForgotOtpVerified(false);
                        setForgotOtpRef('');
                        setForgotOtpCode('');
                        setForgotOtpMsg(null);
                        setForgotNewPassword('');
                        setForgotConfirmPassword('');
                      }}
                    >
                      Forgot / Reset Password?
                    </button>
                  </div>
                  <input
                    type="password"
                    required
                    className="form-control"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Enter centre administrator password"
                  />
                </div>'''

if target_3 in text:
    text = text.replace(target_3, replacement_3, 1)
    print("3. Added Forgot Password link to Training Centre Login modal")
else:
    print("3. Target 3 not found")

# 4. Update Citizen Forgot Password link to set forgotSource='citizen'
target_4 = '''                        onClick={() => {
                          setAuthPortalView('forgot_password');
                          setForgotEmail(loginEmail);'''

replacement_4 = '''                        onClick={() => {
                          setAuthPortalView('forgot_password');
                          setForgotSource('citizen');
                          setForgotEmail(loginEmail);'''

if target_4 in text:
    text = text.replace(target_4, replacement_4, 1)
    print("4. Set forgotSource='citizen' on citizen forgot password link")
else:
    print("4. Target 4 not found")

# 5. In forgot password modal, respect forgotSource on Back and on Completion
target_5 = "onClick={() => { setAuthPortalView('login_citizen'); setForgotOtpMsg(null); }}"
replacement_5 = "onClick={() => { setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen'); setForgotOtpMsg(null); }}"

if target_5 in text:
    text = text.replace(target_5, replacement_5)
    print("5. Replaced modal close/back buttons to respect forgotSource")
else:
    print("5. Target 5 not found")

target_5b = "<ArrowLeft size={12} /> Return to Citizen Login"
replacement_5b = "{forgotSource === 'centre' ? '<ArrowLeft size={12} /> Return to Centre Login' : '<ArrowLeft size={12} /> Return to Citizen Login'}"

# Replace the text inside the footer back button
old_footer_back = """                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => setAuthPortalView('login_citizen')}
                >
                  <ArrowLeft size={12} /> Return to Citizen Login
                </button>"""

new_footer_back = """                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen')}
                >
                  <ArrowLeft size={12} /> {forgotSource === 'centre' ? 'Return to Centre Login' : 'Return to Citizen Login'}
                </button>"""

if old_footer_back in text:
    text = text.replace(old_footer_back, new_footer_back, 1)
    print("5b. Replaced footer back button")
else:
    print("5b. Footer back button not found")

# In handleResetPassword redirect:
old_redirect = """      setTimeout(() => {
        setAuthPortalView('login_citizen');
        setForgotSuccess('');"""

new_redirect = """      setTimeout(() => {
        setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen');
        setForgotSuccess('');"""

if old_redirect in text:
    text = text.replace(old_redirect, new_redirect, 1)
    print("5c. Replaced handleResetPassword timeout redirect")
else:
    print("5c. Redirect target not found")

# 6. Add "Security & Password" tab button to Centre Portal Header
target_nav = """                <button
                  className={`nav-item-btn ${centreTab === 'reports' ? 'active' : ''}`}
                  onClick={() => setCentreTab('reports')}
                >
                  <Award size={15} /> Reports & Analytics
                </button>
              </nav>"""

replacement_nav = """                <button
                  className={`nav-item-btn ${centreTab === 'reports' ? 'active' : ''}`}
                  onClick={() => setCentreTab('reports')}
                >
                  <Award size={15} /> Reports & Analytics
                </button>
                <button
                  className={`nav-item-btn ${centreTab === 'security' ? 'active' : ''}`}
                  onClick={() => setCentreTab('security')}
                >
                  <Lock size={15} /> Security & Password
                </button>
              </nav>"""

if target_nav in text:
    text = text.replace(target_nav, replacement_nav, 1)
    print("6. Added Security & Password tab button to Centre Portal Header")
else:
    print("6. Target nav not found")

# 7. Add Security & Password tab content to Centre Portal
reports_tab_end = """            {/* TAB: REPORTS */}
            {centreTab === 'reports' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Training Analytics & Completion Metrics</h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem' }}>Official NSQF progress and attendance tracking</p>
                {centreReports && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>Attendance Overview</h4>
                      <div style={{ fontSize: '0.82rem', lineHeight: '1.8' }}>
                        <div><strong>Above 90% (Distinction):</strong> {centreReports.attendance_distribution.above_90} Students</div>
                        <div><strong>75% - 90% (Compliant):</strong> {centreReports.attendance_distribution['75_to_90']} Students</div>
                        <div><strong>Below 75% (At Risk):</strong> {centreReports.attendance_distribution.below_75} Students</div>
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>Curriculum Progress</h4>
                      <div style={{ fontSize: '0.82rem', lineHeight: '1.8' }}>
                        <div><strong>Above 80% Completed:</strong> {centreReports.progress_distribution.above_80} Students</div>
                        <div><strong>50% - 80% In Progress:</strong> {centreReports.progress_distribution['50_to_80']} Students</div>
                        <div><strong>Below 50% Early Stage:</strong> {centreReports.progress_distribution.below_50} Students</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}"""

security_tab_content = """            {/* TAB: SECURITY & INDEPENDENT PASSWORD MANAGEMENT */}
            {centreTab === 'security' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', paddingBottom: '1rem', borderBottom: '1px solid #f1f5f9' }}>
                  <div style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '0.6rem', borderRadius: '8px' }}>
                    <Lock size={22} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      Representative Account Security & Password Management
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748b' }}>
                      Independently manage and update your unique Training Centre administrator password (Argon2id cryptographic hash stored in MySQL)
                    </p>
                  </div>
                </div>

                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.85rem 1rem', marginBottom: '1.5rem', fontSize: '0.82rem', color: '#166534' }}>
                  <strong>Security Enforcement:</strong> Training Centre representatives independently manage their own access. Passwords are never shared across centres, never displayed in plaintext, and securely hashed with Argon2id.
                </div>

                {changePasswordMsg && (
                  <div style={{
                    backgroundColor: changePasswordMsg.type === 'success' ? '#f0fdf4' : '#fee2e2',
                    color: changePasswordMsg.type === 'success' ? '#166534' : '#b91c1c',
                    border: changePasswordMsg.type === 'success' ? '1px solid #bbf7d0' : '1px solid #fecaca',
                    padding: '0.75rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    marginBottom: '1.5rem'
                  }}>
                    {changePasswordMsg.text}
                  </div>
                )}

                <form onSubmit={handleChangePassword} style={{ maxWidth: '520px' }}>
                  <div className="form-group" style={{ marginBottom: '1.2rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                      Current Representative Password:
                    </label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showChangeCurrentPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={changeCurrentPassword}
                        onChange={(e) => setChangeCurrentPassword(e.target.value)}
                        placeholder="Enter current password"
                      />
                      <button
                        type="button"
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                        onClick={() => setShowChangeCurrentPassword(!showChangeCurrentPassword)}
                      >
                        {showChangeCurrentPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.2rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                      New Unique Password (minimum 8 characters):
                    </label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showChangeNewPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={changeNewPassword}
                        onChange={(e) => setChangeNewPassword(e.target.value)}
                        placeholder="Enter strong unique password"
                      />
                      <button
                        type="button"
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                        onClick={() => setShowChangeNewPassword(!showChangeNewPassword)}
                      >
                        {showChangeNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                      Confirm New Password:
                    </label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showChangeConfirmPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={changeConfirmPassword}
                        onChange={(e) => setChangeConfirmPassword(e.target.value)}
                        placeholder="Re-enter new password"
                      />
                      <button
                        type="button"
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                        onClick={() => setShowChangeConfirmPassword(!showChangeConfirmPassword)}
                      >
                        {showChangeConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn-primary-orange"
                    style={{ backgroundColor: '#0f766e', borderColor: '#0f766e', padding: '0.6rem 1.25rem', fontSize: '0.85rem' }}
                    disabled={changePasswordLoading || !changeCurrentPassword || !changeNewPassword || changeNewPassword.length < 8 || changeNewPassword !== changeConfirmPassword}
                  >
                    {changePasswordLoading ? 'Updating Password...' : 'Update Representative Password'}
                  </button>
                </form>
              </div>
            )}"""

if reports_tab_end in text:
    text = text.replace(reports_tab_end, reports_tab_end + "\n\n" + security_tab_content, 1)
    print("7. Appended Security & Password tab content to Centre Portal")
else:
    print("7. Target reports tab not found")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)
print("APP_TSX_UPDATE_COMPLETE")
