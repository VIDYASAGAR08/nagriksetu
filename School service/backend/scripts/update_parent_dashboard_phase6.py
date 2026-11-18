path = r"C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx"
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

old_banner = """                    {/* Final Admission Confirmed Banner */}
                    {(app.status === 'final_admission_confirmed' || app.status === 'enrolled') && (
                      <div style={{ background: '#FDF4FF', border: '1px solid #FCCEEE', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#C11574', fontSize: '0.875rem' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                          🎓 Official Admission Confirmed!
                        </div>
                        <p style={{ margin: 0, color: '#9E165F', fontSize: '0.85rem' }}>
                          Your student is officially enrolled at this institution. Permanent student identification and academic ledger record created.
                        </p>
                      </div>
                    )}"""

new_banner = """                    {/* Final Admission Confirmed & Enrolled Banner */}
                    {(app.status === 'final_admission_confirmed' || app.status === 'enrolled') && (
                      <div style={{ background: '#FDF4FF', border: '1px solid #FCCEEE', borderRadius: '10px', padding: '1.25rem', marginTop: '1rem', color: '#701A75', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '1.1rem' }}>🎓</span>
                              <strong style={{ fontSize: '1rem', color: '#4A044E' }}>
                                Official Admission Confirmed & Student Enrolled!
                              </strong>
                            </div>
                            <p style={{ margin: '0 0 0.5rem 0', color: '#86198F', fontSize: '0.85rem' }}>
                              Your child has been allotted a permanent institutional seat. The official student ledger and academic enrollment record are live.
                            </p>
                            {app.enrolled_student_id && (
                              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', background: '#ffffff', padding: '0.35rem 0.75rem', borderRadius: '6px', border: '1px solid #F5D0FE' }}>
                                <span style={{ fontSize: '0.75rem', color: '#701A75', fontWeight: 600 }}>PERMANENT STUDENT ID:</span>
                                <code style={{ fontSize: '0.85rem', fontWeight: 800, color: '#4A044E' }}>{app.enrolled_student_id}</code>
                              </div>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => switchTab('children')}
                            style={{ background: '#701A75', color: '#ffffff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', fontSize: '0.85rem' }}
                          >
                            View Child in Student Portal →
                          </button>
                        </div>
                      </div>
                    )}"""

text = text.replace(old_banner, new_banner)

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("ParentDashboard.jsx updated with official enrolled dossier card.")
