with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

modals_jsx = """
      {/* 3B. REPRESENTATIVE SELF-REGISTRATION MODAL */}
      {authPortalView === 'register_centre_rep' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '520px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            <div style={{ backgroundColor: '#0f766e', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.15)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('login_centre'); setRepMsg(null); }}
                  title="Back to Training Centre Login"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#99f6e4', fontWeight: 700 }}>
                    Official Representative Setup
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Register Centre Representative
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#ccfbf1', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setRepMsg(null); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem', maxHeight: '82vh', overflowY: 'auto' }}>
              <div style={{ backgroundColor: '#f0fdfa', border: '1px solid #99f6e4', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.78rem', color: '#0f766e', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <Building2 size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>Select your assigned Accredited Training Centre (1 of 10) and establish your independent login credentials. Existing institutional records are securely preserved.</span>
              </div>

              {repMsg && (
                <div style={{
                  backgroundColor: repMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                  color: repMsg.type === 'success' ? '#15803d' : '#b91c1c',
                  border: `1px solid ${repMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
                  padding: '0.65rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem'
                }}>
                  {repMsg.text}
                </div>
              )}

              <form onSubmit={handleRegisterRepresentative}>
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f2444' }}>Select Accredited Training Centre:</label>
                  <select
                    className="form-control"
                    value={repSelectedCentreId}
                    onChange={(e) => setRepSelectedCentreId(Number(e.target.value))}
                    required
                    style={{ fontSize: '0.85rem', fontWeight: 600 }}
                  >
                    {centreRegisterList.length > 0 ? (
                      centreRegisterList.map((c) => (
                        <option key={c.centre_id} value={c.centre_id}>
                          [{c.centre_code}] {c.centre_name} ({c.district})
                        </option>
                      ))
                    ) : (
                      <>
                        <option value={1}>[CTR-0001] Bengaluru Central Skill Hub (Rajajinagar)</option>
                        <option value={2}>[CTR-0002] Mysuru Regional Skilling Institute</option>
                        <option value={3}>[CTR-0003] Hubballi-Dharwad Tech Development Centre</option>
                        <option value={4}>[CTR-0004] Mangaluru Coastal Skill Academy</option>
                        <option value={5}>[CTR-0005] NagrikSetu Virtual Learning Portal</option>
                        <option value={6}>[CTR-0006] Dharwad Innovation & Regional Skilling Centre</option>
                        <option value={8}>[CTR-0007] Belagavi Regional Skilling Hub</option>
                        <option value={9}>[CTR-0008] Davanagere Vocational & Technical Institute</option>
                        <option value={10}>[CTR-0009] Kalaburagi Regional Skill Development Centre</option>
                        <option value={11}>[CTR-0010] Shivamogga Malnad Skill Development Centre</option>
                      </>
                    )}
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Representative Official Full Name:</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={repName}
                    onChange={(e) => setRepName(e.target.value)}
                    placeholder="e.g. Dr. Rajeshwari Patil"
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Representative Email (Login ID):</label>
                    <input
                      type="email"
                      required
                      className="form-control"
                      value={repEmail}
                      onChange={(e) => setRepEmail(e.target.value)}
                      placeholder="e.g. rep.bengaluru@nagriksetu.local"
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Contact Phone Number:</label>
                    <input
                      type="tel"
                      required
                      className="form-control"
                      value={repPhone}
                      onChange={(e) => setRepPhone(e.target.value)}
                      placeholder="10-digit mobile number"
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Representative Password:</label>
                    <input
                      type="password"
                      required
                      className="form-control"
                      value={repPassword}
                      onChange={(e) => setRepPassword(e.target.value)}
                      placeholder="Min 6 characters"
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Confirm Password:</label>
                    <input
                      type="password"
                      required
                      className="form-control"
                      value={repConfirmPassword}
                      onChange={(e) => setRepConfirmPassword(e.target.value)}
                      placeholder="Re-enter password"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn-primary-orange"
                  style={{ width: '100%', justifyContent: 'center', backgroundColor: '#0f766e', borderColor: '#0f766e', padding: '0.75rem' }}
                  disabled={repSubmitting}
                >
                  {repSubmitting ? 'Registering Representative...' : 'Establish Representative Account'}
                </button>
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
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
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3C. PROJECT OWNER CENTRE ACCOUNT REGISTER MODAL */}
      {authPortalView === 'project_owner_register' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '880px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.3)' }}>
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#38bdf8' }}>
                  <Shield size={18} />
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#38bdf8', fontWeight: 700 }}>
                    Demonstration & Verification Console
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Project Owner Centre Account Register
                  </h3>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem 0.6rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={fetchCentreRegister}
                >
                  <RefreshCw size={13} /> Refresh
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                  onClick={() => { setAuthPortalView('none'); setOwnerResetCentreId(null); }}
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem', maxHeight: '82vh', overflowY: 'auto' }}>
              <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '6px', padding: '0.75rem 1rem', marginBottom: '1.25rem', fontSize: '0.8rem', color: '#1e40af', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckCircle2 size={16} color="#2563eb" />
                  <span><strong>10 Independent Training Centres Verified:</strong> Each centre has an isolated representative login, separate dashboard, and independent application queue.</span>
                </div>
                <button
                  type="button"
                  className="btn-navy-outline"
                  style={{ fontSize: '0.74rem', padding: '0.3rem 0.6rem', whiteSpace: 'nowrap' }}
                  onClick={() => {
                    setAuthPortalView('register_centre_rep');
                    setRepMsg(null);
                  }}
                >
                  + Register Representative
                </button>
              </div>

              {centreRegisterLoading ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  <Loader2 size={24} className="spin" style={{ margin: '0 auto 0.5rem auto' }} />
                  <div>Loading 10 Training Centre Account Records...</div>
                </div>
              ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem' }}>
                    <thead style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontWeight: 700 }}>
                      <tr>
                        <th style={{ padding: '0.65rem 0.75rem' }}>ID & Code</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>Accredited Centre Name</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>Location / District</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>Registered Representative Login</th>
                        <th style={{ padding: '0.65rem 0.75rem', textAlign: 'center' }}>Status</th>
                        <th style={{ padding: '0.65rem 0.75rem', textAlign: 'right' }}>Demonstration Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {centreRegisterList.map((c, idx) => (
                        <tr key={c.centre_id} style={{ borderBottom: '1px solid #f1f5f9', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fcfcfd' }}>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <span style={{ fontWeight: 700, color: '#0f2444' }}>#{c.centre_id}</span>
                            <div style={{ fontSize: '0.72rem', color: '#64748b', fontFamily: 'monospace' }}>{c.centre_code}</div>
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <div style={{ fontWeight: 700, color: '#0f2444' }}>{c.centre_name}</div>
                            {c.representative_name && (
                              <div style={{ fontSize: '0.72rem', color: '#059669' }}>Rep: {c.representative_name}</div>
                            )}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem', color: '#475569' }}>
                            {c.location || c.district}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <div style={{ fontFamily: 'monospace', fontWeight: 600, color: '#0369a1' }}>
                              {c.registered_email || 'Not Configured'}
                            </div>
                            {c.representative_phone && (
                              <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Ph: {c.representative_phone}</div>
                            )}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem', textAlign: 'center' }}>
                            <span style={{
                              display: 'inline-block',
                              padding: '0.2rem 0.5rem',
                              borderRadius: '9999px',
                              fontSize: '0.68rem',
                              fontWeight: 700,
                              backgroundColor: c.is_configured ? '#dcfce7' : '#fee2e2',
                              color: c.is_configured ? '#15803d' : '#b91c1c'
                            }}>
                              {c.status}
                            </span>
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem', textAlign: 'right' }}>
                            <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end' }}>
                              <button
                                type="button"
                                style={{
                                  backgroundColor: '#0284c7',
                                  color: '#ffffff',
                                  border: 'none',
                                  borderRadius: '4px',
                                  padding: '0.3rem 0.6rem',
                                  fontSize: '0.72rem',
                                  fontWeight: 600,
                                  cursor: 'pointer'
                                }}
                                onClick={() => {
                                  setLoginEmail(c.registered_email || '');
                                  setLoginPassword('CentreAdmin@2026!');
                                  setAuthPortalView('login_centre');
                                }}
                                title="Open Centre Workspace Login with prefilled email"
                              >
                                Sign In
                              </button>
                              <button
                                type="button"
                                style={{
                                  backgroundColor: '#f1f5f9',
                                  color: '#334155',
                                  border: '1px solid #cbd5e1',
                                  borderRadius: '4px',
                                  padding: '0.3rem 0.5rem',
                                  fontSize: '0.72rem',
                                  fontWeight: 600,
                                  cursor: 'pointer'
                                }}
                                onClick={() => {
                                  setOwnerResetCentreId(c.centre_id);
                                  setOwnerResetMsg(null);
                                }}
                                title="Initiate secure password reset"
                              >
                                Reset Access
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Password Reset Section inside Register */}
              {ownerResetCentreId && (
                <div style={{ marginTop: '1.5rem', padding: '1rem 1.25rem', backgroundColor: '#f8fafc', border: '1.5px solid #cbd5e1', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: '#0f2444' }}>
                      Secure Demonstration Password Reset for Centre #{ownerResetCentreId}
                    </h4>
                    <button
                      type="button"
                      style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                      onClick={() => setOwnerResetCentreId(null)}
                    >
                      <X size={16} />
                    </button>
                  </div>

                  {ownerResetMsg && (
                    <div style={{
                      backgroundColor: ownerResetMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                      color: ownerResetMsg.type === 'success' ? '#15803d' : '#b91c1c',
                      padding: '0.5rem 0.75rem', borderRadius: '4px', fontSize: '0.78rem', marginBottom: '0.75rem'
                    }}>
                      {ownerResetMsg.text}
                    </div>
                  )}

                  <form onSubmit={handleOwnerResetPassword} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '0.75rem', alignItems: 'flex-end' }}>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Project Demonstration Key:</label>
                      <input
                        type="password"
                        required
                        className="form-control"
                        style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                        value={ownerResetSecretKey}
                        onChange={(e) => setOwnerResetSecretKey(e.target.value)}
                        placeholder="NagrikSetu@Owner2026!"
                      />
                    </div>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>New Password to Hash in DB:</label>
                      <input
                        type="password"
                        required
                        className="form-control"
                        style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                        value={ownerResetNewPassword}
                        onChange={(e) => setOwnerResetNewPassword(e.target.value)}
                        placeholder="Min 6 characters"
                      />
                    </div>
                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ fontSize: '0.78rem', padding: '0.45rem 1rem', height: 'fit-content' }}
                      disabled={ownerResetSubmitting}
                    >
                      {ownerResetSubmitting ? 'Updating...' : 'Set Password Hash'}
                    </button>
                  </form>
                </div>
              )}

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <span style={{ color: '#64748b' }}>
                  Note: Plaintext passwords are never revealed or stored. Passwords are saved as salted cryptographic hashes.
                </span>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => setAuthPortalView('select_role')}
                >
                  ← Return to Role Selection
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
"""

target = "{authPortalView === 'login_centre' && ("
if target in text:
    text = text.replace(target, modals_jsx + "\n      " + target, 1)
    with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("SUCCESS: Modals injected into App.tsx")
else:
    print("ERROR: target not found")
