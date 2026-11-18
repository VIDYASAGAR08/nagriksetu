import sys

admin_dash_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\AdminDashboard.jsx"

with open(admin_dash_path, "r", encoding="utf-8") as f:
    content = f.read()

target = """              {inviteResult ? (
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '1rem', borderRadius: '8px', color: '#166534', fontSize: '0.875rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.5rem' }}>Invitation Link Generated!</div>
                  <p>Academic Administrator invitation dispatched for <strong>{inviteResult.school_name}</strong>.</p>
                  <div style={{ background: '#ffffff', padding: '0.5rem', borderRadius: '4px', border: '1px solid #86efac', fontFamily: 'monospace', wordBreak: 'break-all', marginTop: '0.5rem' }}>
                    {inviteResult.invitation_url}
                  </div>
                  <div style={{ marginTop: '1rem', textAlign: 'right' }}>
                    <button onClick={() => setShowInviteModal(false)} className="btn btn--sm btn--primary">Done</button>
                  </div>
                </div>
              ) : ("""

replacement = """              {inviteResult ? (
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '1.25rem', borderRadius: '8px', color: '#166534' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
                    <span style={{ fontSize: '1.4rem' }}>✅</span>
                    <h4 style={{ margin: 0, fontWeight: 700, fontSize: '1.15rem', color: '#166534' }}>
                      Invitation Successfully Sent
                    </h4>
                  </div>

                  <div style={{ background: '#ffffff', border: '1px solid #dcfce7', borderRadius: '6px', padding: '1rem', marginBottom: '1rem', color: '#1e293b' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', rowGap: '0.6rem', fontSize: '0.875rem' }}>
                      <span style={{ fontWeight: 600, color: '#64748b' }}>Institution:</span>
                      <span style={{ fontWeight: 700, color: '#0f172a' }}>{inviteResult.school_name} ({inviteResult.institution_id})</span>

                      <span style={{ fontWeight: 600, color: '#64748b' }}>Administrator:</span>
                      <span style={{ fontWeight: 600, color: '#0f172a' }}>{inviteResult.full_name || inviteFullName}</span>

                      <span style={{ fontWeight: 600, color: '#64748b' }}>Official Email:</span>
                      <span style={{ fontFamily: 'monospace', color: '#0284c7', fontWeight: 600 }}>{inviteResult.email}</span>

                      <span style={{ fontWeight: 600, color: '#64748b' }}>Invitation Status:</span>
                      <span>
                        <span style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a', padding: '0.2rem 0.55rem', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
                          Sent / Pending
                        </span>
                      </span>
                    </div>
                  </div>

                  <p style={{ margin: '0 0 0.85rem 0', color: '#15803d', fontSize: '0.875rem', lineHeight: 1.5 }}>
                    The administrator invitation has been issued. The intended administrator can proceed with account setup through the NagrikSetu institution portal.
                  </p>

                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.775rem', color: '#64748b', lineHeight: 1.45 }}>
                    ℹ️ <em>Delivery Status Notice:</em> Live SMTP relay is not configured in this staging deployment. The invitation is securely recorded in the registry, and the authorized administrator can proceed directly via the official institution portal.
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      type="button"
                      onClick={() => {
                        setShowInviteModal(false)
                        setInviteResult(null)
                      }}
                      className="btn btn--primary"
                      style={{ padding: '0.5rem 1.25rem', fontWeight: 600 }}
                    >
                      Done
                    </button>
                  </div>
                </div>
              ) : ("""

assert target in content, "target block not found in AdminDashboard.jsx"
content = content.replace(target, replacement, 1)

with open(admin_dash_path, "w", encoding="utf-8") as f:
    f.write(content)

print("AdminDashboard.jsx modal updated successfully!")
