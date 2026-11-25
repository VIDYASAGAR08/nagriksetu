path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Programmes Tab: External Directory Apply / Website section
target_prog_btn = """                          ) : (
                            <div style={{ display: 'grid', gap: '0.5rem' }}>
                              <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic', textAlign: 'center' }}>
                                Verified External Directory Programme • Direct Institutional Admission
                              </div>
                              {publicCentreProfile.website && (
                                <a
                                  href={publicCentreProfile.website}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    display: 'block',
                                    textAlign: 'center',
                                    padding: '0.65rem 1rem',
                                    backgroundColor: '#0f766e',
                                    color: '#ffffff',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    fontSize: '0.85rem',
                                    textDecoration: 'none'
                                  }}
                                >
                                  Visit Institute Website
                                </a>
                              )}
                            </div>
                          )}"""

replacement_prog_btn = """                          ) : (
                            <div style={{ display: 'grid', gap: '0.5rem' }}>
                              <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic', textAlign: 'center' }}>
                                Verified External Directory Programme • Direct Institutional Admission
                              </div>
                              {publicCentreProfile.website && publicCentreProfile.website.startsWith('http') ? (
                                <a
                                  href={publicCentreProfile.website}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    display: 'block',
                                    textAlign: 'center',
                                    padding: '0.65rem 1rem',
                                    backgroundColor: '#0f766e',
                                    color: '#ffffff',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    fontSize: '0.85rem',
                                    textDecoration: 'none'
                                  }}
                                >
                                  Visit Institute Website
                                </a>
                              ) : (
                                <div
                                  style={{
                                    textAlign: 'center',
                                    padding: '0.65rem 1rem',
                                    backgroundColor: '#f1f5f9',
                                    color: '#64748b',
                                    borderRadius: '6px',
                                    fontWeight: 600,
                                    fontSize: '0.85rem',
                                    border: '1px solid #e2e8f0'
                                  }}
                                >
                                  Website not available
                                </div>
                              )}
                            </div>
                          )}"""

if target_prog_btn in content:
    content = content.replace(target_prog_btn, replacement_prog_btn)
    print("Found and replaced target_prog_btn in App.tsx")
else:
    print("Could NOT find target_prog_btn in App.tsx")

# 2. Add Official Website row in Contact & Digital Touchpoints if present or "Website not available"
target_contact = """                      <div><strong style={{ color: '#334155' }}>Official Email:</strong> {publicCentreProfile.contact_email || 'Information not yet available'}</div>
                      <div>
                        <strong style={{ color: '#334155' }}>Institutional Affiliation:</strong>{' '}
                        {publicCentreProfile.source || 'Karnataka Skill Development Mission (KSDM)'}
                      </div>"""

replacement_contact = """                      <div><strong style={{ color: '#334155' }}>Official Email:</strong> {publicCentreProfile.contact_email || 'Information not yet available'}</div>
                      <div>
                        <strong style={{ color: '#334155' }}>Official Website:</strong>{' '}
                        {publicCentreProfile.website && publicCentreProfile.website.startsWith('http') ? (
                          <a
                            href={publicCentreProfile.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: '#0f766e', fontWeight: 600, textDecoration: 'underline' }}
                          >
                            {publicCentreProfile.website}
                          </a>
                        ) : (
                          <span style={{ color: '#64748b' }}>Website not available</span>
                        )}
                      </div>
                      <div>
                        <strong style={{ color: '#334155' }}>Institutional Affiliation:</strong>{' '}
                        {publicCentreProfile.source || 'Karnataka Skill Development Mission (KSDM)'}
                      </div>"""

if target_contact in content:
    content = content.replace(target_contact, replacement_contact)
    print("Found and replaced target_contact in App.tsx")
else:
    print("Could NOT find target_contact in App.tsx")

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated App.tsx successfully.")
