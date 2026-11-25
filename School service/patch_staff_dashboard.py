import sys

file_path = r'C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx'

with open(file_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add state for issuing code
target_state = "  const [success, setSuccess] = useState('')"
replace_state = """  const [success, setSuccess] = useState('')
  const [issuedCodeData, setIssuedCodeData] = useState(null)
  const [issuingCode, setIssuingCode] = useState(false)

  async function handleStaffIssueCode(req) {
    if (!req) return
    try {
      setIssuingCode(true)
      const res = await apiPost(`/school/linking-requests/${req.request_id}/issue-code`, {}, token)
      setIssuedCodeData({ ...res, request: req })
    } catch (err) {
      setError(err.message || 'Failed to generate verification code.')
    } finally {
      setIssuingCode(false)
    }
  }"""

assert target_state in text, "target_state not found in StaffDashboard.jsx"
text = text.replace(target_state, replace_state, 1)

# 2. Update the parent_user_id display and add Issue Code button in table
target_table_cell = """                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{r.parent_name || 'Parent Guardian'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>ID: {r.parent_user_id?.slice(0, 8)}...</div>
                          </td>"""

replace_table_cell = """                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{r.parent_name || 'Parent Guardian'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>ID: <code style={{ fontSize: '0.72rem' }}>{r.parent_user_id}</code></div>
                            {r.parent_email && <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>{r.parent_email}</div>}
                          </td>"""

assert target_table_cell in text, "target_table_cell not found in StaffDashboard.jsx"
text = text.replace(target_table_cell, replace_table_cell, 1)

# 3. Add Issue Code button in table action cell
target_action_cell = """                          <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                            {(r.request_status === 'pending' || r.status === 'pending') ? (
                              <button
                                onClick={() => openReviewModal(r)}
                                className="btn btn--primary btn--sm"
                              >
                                Review Request →
                              </button>
                            ) : (
                              <span style={{ fontSize: '0.8125rem', color: '#6b7280' }}>Reviewed</span>
                            )}
                          </td>"""

replace_action_cell = """                          <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                            {(r.request_status === 'pending' || r.status === 'pending') ? (
                              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', alignItems: 'center' }}>
                                <button
                                  onClick={() => openReviewModal(r)}
                                  className="btn btn--primary btn--sm"
                                >
                                  Review →
                                </button>
                                <button
                                  onClick={() => handleStaffIssueCode(r)}
                                  disabled={issuingCode}
                                  className="btn btn--sm"
                                  style={{ background: '#155EEF', color: '#fff', border: 'none', fontWeight: 600, borderRadius: '4px', padding: '0.35rem 0.65rem' }}
                                  title="Issue official 6-digit verification code"
                                >
                                  🔑 Issue Code
                                </button>
                              </div>
                            ) : (
                              <span style={{ fontSize: '0.8125rem', color: '#6b7280' }}>Reviewed</span>
                            )}
                          </td>"""

assert target_action_cell in text, "target_action_cell not found in StaffDashboard.jsx"
text = text.replace(target_action_cell, replace_action_cell, 1)

# 4. Add modal for issuedCodeData before closing tags
target_modal_end = """        {/* Review & Approval Modal */}"""
assert target_modal_end in text, "target_modal_end not found"

staff_code_modal = """        {/* Official 6-Digit Code Modal for Staff Dispatch */}
        {issuedCodeData && (
          <div style={{
            position: 'fixed',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(15, 23, 42, 0.75)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, padding: '1rem'
          }}>
            <div style={{
              background: '#FFFFFF', borderRadius: '12px',
              maxWidth: '500px', width: '100%', overflow: 'hidden',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
            }}>
              <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#FFFFFF' }}>
                  🔑 Institution Verification Code Issued
                </h3>
                <button
                  onClick={() => setIssuedCodeData(null)}
                  style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '1.4rem', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>
              <div style={{ padding: '1.5rem' }}>
                <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
                  <div style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '0.5rem' }}>
                    Official 6-Digit Authorization Code:
                  </div>
                  <div style={{
                    background: '#F0FDF4', border: '2px dashed #16A34A', borderRadius: '8px',
                    padding: '1rem', display: 'inline-block', minWidth: '200px'
                  }}>
                    <span style={{ fontSize: '2.2rem', fontWeight: 900, fontFamily: 'monospace', letterSpacing: '8px', color: '#15803D' }}>
                      {issuedCodeData.verification_code}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.775rem', color: '#16A34A', marginTop: '0.4rem', fontWeight: 600 }}>
                    ⏱️ Valid for 15 minutes · Single-use authorization
                  </div>
                </div>

                <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem', fontSize: '0.84rem', color: '#334155' }}>
                  <p style={{ margin: '0 0 0.5rem 0', fontWeight: 600 }}>
                    Provide this code to parent <strong>{issuedCodeData.request?.parent_name}</strong> (Parent Account: <code>{issuedCodeData.request?.parent_user_id}</code>).
                  </p>
                  <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748B' }}>
                    The parent will enter this code on the Parent Portal to complete the child verification.
                  </p>
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(issuedCodeData.verification_code)
                      alert('Code copied to clipboard!')
                    }}
                    className="btn btn--secondary btn--sm"
                  >
                    📋 Copy Code
                  </button>
                  <button
                    onClick={() => setIssuedCodeData(null)}
                    className="btn btn--primary btn--sm"
                  >
                    Done
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

"""

text = text.replace(target_modal_end, staff_code_modal + "        {/* Review & Approval Modal */}", 1)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("StaffDashboard.jsx updated successfully!")
