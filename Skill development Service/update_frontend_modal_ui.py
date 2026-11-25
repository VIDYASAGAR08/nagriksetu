with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the body of project_owner_register modal
old_modal_start = "{authPortalView === 'project_owner_register' && ("
old_modal_end = "{authPortalView === 'login_centre' && ("

idx_start = text.find(old_modal_start)
idx_end = text.find(old_modal_end)

new_project_owner_modal = """{authPortalView === 'project_owner_register' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '920px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.3)' }}>
            {/* Modal Header */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#38bdf8' }}>
                  <Shield size={18} />
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#38bdf8', fontWeight: 700 }}>
                    Governance & Demonstration Console
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Project Owner Centre Account Register
                  </h3>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {ownerAuthToken && (
                  <button
                    type="button"
                    style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '6px', color: '#fca5a5', cursor: 'pointer', padding: '0.35rem 0.65rem', fontSize: '0.72rem', fontWeight: 700 }}
                    onClick={handleOwnerSignOut}
                  >
                    Lock Console (Sign Out)
                  </button>
                )}
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem 0.6rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => fetchCentreRegister()}
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
              {/* Project Owner Authentication Gate / Status Banner */}
              {!ownerAuthToken ? (
                <div style={{ backgroundColor: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#92400e', fontWeight: 700, fontSize: '0.85rem' }}>
                      <Lock size={16} /> Privacy Protected: Sensitive Representative Emails Masked
                    </div>
                    <span style={{ fontSize: '0.72rem', color: '#b45309', fontWeight: 600 }}>Public View</span>
                  </div>
                  <p style={{ fontSize: '0.78rem', color: '#78350f', margin: '0 0 0.75rem 0', lineHeight: 1.45 }}>
                    To protect institutional representatives, registered emails and mobile numbers are masked for public visitors. Authenticate with your protected Project Owner Key to unlock unmasked directory access and password management.
                  </p>
                  {ownerAuthMsg && (
                    <div style={{
                      backgroundColor: ownerAuthMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                      color: ownerAuthMsg.type === 'success' ? '#15803d' : '#b91c1c',
                      padding: '0.4rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.5rem'
                    }}>
                      {ownerAuthMsg.text}
                    </div>
                  )}
                  <form onSubmit={handleOwnerAuthenticate} style={{ display: 'flex', gap: '0.5rem', maxWidth: '480px' }}>
                    <input
                      type="password"
                      required
                      className="form-control"
                      style={{ fontSize: '0.8rem', padding: '0.4rem 0.65rem' }}
                      value={ownerKeyInput}
                      onChange={(e) => setOwnerKeyInput(e.target.value)}
                      placeholder="Enter Protected Project Owner Key"
                    />
                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ fontSize: '0.78rem', padding: '0.4rem 0.85rem', whiteSpace: 'nowrap' }}
                      disabled={ownerAuthLoading}
                    >
                      {ownerAuthLoading ? 'Verifying...' : 'Unlock Console'}
                    </button>
                  </form>
                </div>
              ) : (
                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.75rem 1rem', marginBottom: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#166534', fontSize: '0.82rem', fontWeight: 700 }}>
                    <CheckCircle2 size={16} color="#16a34a" />
                    <span>Project Owner Session Active: Full Unmasked Directory & Password Governance Unlocked</span>
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
              )}

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
                        <th style={{ padding: '0.65rem 0.75rem' }}>District</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>Representative Login Email</th>
                        <th style={{ padding: '0.65rem 0.75rem', textAlign: 'center' }}>Setup Status</th>
                        <th style={{ padding: '0.65rem 0.75rem', textAlign: 'right' }}>Actions</th>
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
                            {c.district}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <div style={{ fontFamily: 'monospace', fontWeight: 600, color: c.is_masked ? '#64748b' : '#0369a1' }}>
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
                                  setLoginEmail(c.registered_email && !c.is_masked ? c.registered_email : '');
                                  setLoginPassword('');
                                  setAuthPortalView('login_centre');
                                }}
                                title="Open Centre Workspace Login with prefilled email"
                              >
                                Sign In
                              </button>
                              {ownerAuthToken && (
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
                                  title="Initiate authorized password reset"
                                >
                                  Reset Access
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Password Reset Section inside Register (Authorized Project Owner Only) */}
              {ownerResetCentreId && ownerAuthToken && (
                <div style={{ marginTop: '1.5rem', padding: '1rem 1.25rem', backgroundColor: '#f8fafc', border: '1.5px solid #cbd5e1', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: '#0f2444' }}>
                      Authorized Argon2id Password Reset for Centre #{ownerResetCentreId}
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

                  <form onSubmit={handleOwnerResetPassword} style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.75rem', alignItems: 'flex-end' }}>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>New Unique Password (Argon2id Hash in MySQL):</label>
                      <input
                        type="password"
                        required
                        className="form-control"
                        style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                        value={ownerResetNewPassword}
                        onChange={(e) => setOwnerResetNewPassword(e.target.value)}
                        placeholder="Enter minimum 8 characters"
                      />
                    </div>
                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ fontSize: '0.78rem', padding: '0.45rem 1rem', height: 'fit-content' }}
                      disabled={ownerResetSubmitting}
                    >
                      {ownerResetSubmitting ? 'Updating...' : 'Set Argon2id Hash'}
                    </button>
                  </form>
                </div>
              )}

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <span style={{ color: '#64748b' }}>
                  Argon2id cryptographic hashing enforced. Rate limiting and security audit logs active on all access endpoints.
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
      )}\n\n      """

if idx_start != -1 and idx_end != -1:
    text = text[:idx_start] + new_project_owner_modal + text[idx_end:]
    with open(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Replaced project_owner_register modal with secured version successfully")
else:
    print("ERROR: Could not locate modal indices", idx_start, idx_end)
