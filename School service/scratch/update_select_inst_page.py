import sys

page_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\auth\SelectInstitutionPage.jsx"

with open(page_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace the INVITED and ACCEPTED_PENDING_PASSWORD modal bodies
start_marker = "                    {/* MODAL CASE 2: INVITED */}"
end_marker = "                    {/* MODAL CASE 4: SUSPENDED */}"

assert start_marker in content, "start_marker not found"
assert end_marker in content, "end_marker not found"

before = content[:content.find(start_marker)]
after = content[content.find(end_marker):]

new_cases = """                    {/* MODAL CASE 2: INVITED */}
                    {activeModal.type === 'INVITED' && (
                      <div>
                        <div style={{ background: '#F0F9FF', border: '1px solid #B9E6FE', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                          <p style={{ margin: '0 0 0.4rem 0', color: '#026AA2', fontSize: '0.95rem', fontWeight: 700 }}>
                            Administrator Invitation Available
                          </p>
                          <p style={{ margin: 0, color: '#0369A1', fontSize: '0.85rem', lineHeight: 1.5 }}>
                            An official Academic Administrator invitation has been issued for <strong>{activeModal.inst.school_name}</strong> (<strong>{activeModal.inst.school_id}</strong>).
                          </p>
                        </div>

                        <p style={{ margin: '0 0 1.25rem 0', color: '#344054', fontSize: '0.875rem', lineHeight: 1.5 }}>
                          The appointed educational administrator can proceed directly to verify their credentials and finalize account setup.
                        </p>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                          <button
                            type="button"
                            onClick={() => setActiveModal(null)}
                            style={{
                              background: '#FFFFFF',
                              color: '#344054',
                              border: '1px solid #D0D5DD',
                              borderRadius: '6px',
                              padding: '0.6rem 1rem',
                              fontSize: '0.875rem',
                              fontWeight: 600,
                              cursor: 'pointer'
                            }}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              const sid = activeModal.inst.school_id
                              setActiveModal(null)
                              navigate(`/accept-invitation?school_id=${encodeURIComponent(sid)}`)
                            }}
                            style={{
                              background: '#026AA2',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.6rem 1.25rem',
                              fontSize: '0.875rem',
                              fontWeight: 700,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.35rem',
                              boxShadow: '0 2px 4px rgba(2,106,162,0.2)'
                            }}
                          >
                            Proceed to Account Setup →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* MODAL CASE 3: ACCEPTED PENDING PASSWORD */}
                    {activeModal.type === 'ACCEPTED_PENDING_PASSWORD' && (
                      <div>
                        <div style={{ background: '#F9F5FF', border: '1px solid #E9D7FE', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                          <p style={{ margin: '0 0 0.4rem 0', color: '#6941C6', fontSize: '0.95rem', fontWeight: 700 }}>
                            Account Setup Incomplete
                          </p>
                          <p style={{ margin: 0, color: '#53389E', fontSize: '0.85rem', lineHeight: 1.5 }}>
                            The administrator invitation for <strong>{activeModal.inst.school_name}</strong> (<strong>{activeModal.inst.school_id}</strong>) has been verified. Final password configuration is pending.
                          </p>
                        </div>

                        <p style={{ margin: '0 0 1.25rem 0', color: '#344054', fontSize: '0.875rem', lineHeight: 1.5 }}>
                          The appointed administrator can proceed directly to complete their password setup and activate the administrative desk.
                        </p>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                          <button
                            type="button"
                            onClick={() => setActiveModal(null)}
                            style={{
                              background: '#FFFFFF',
                              color: '#344054',
                              border: '1px solid #D0D5DD',
                              borderRadius: '6px',
                              padding: '0.6rem 1rem',
                              fontSize: '0.875rem',
                              fontWeight: 600,
                              cursor: 'pointer'
                            }}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              const sid = activeModal.inst.school_id
                              setActiveModal(null)
                              navigate(`/accept-invitation?school_id=${encodeURIComponent(sid)}`)
                            }}
                            style={{
                              background: '#6941C6',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.6rem 1.25rem',
                              fontSize: '0.875rem',
                              fontWeight: 700,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.35rem',
                              boxShadow: '0 2px 4px rgba(105,65,198,0.2)'
                            }}
                          >
                            Proceed to Account Setup →
                          </button>
                        </div>
                      </div>
                    )}

"""

content = before + new_cases + after

with open(page_path, "w", encoding="utf-8") as f:
    f.write(content)

print("SelectInstitutionPage.jsx modal cases updated successfully!")
