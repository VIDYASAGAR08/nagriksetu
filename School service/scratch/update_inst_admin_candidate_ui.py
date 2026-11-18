import os

file_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Target right after Staff Section Header in mainTab === 'staff'
target_header = """            {/* Staff Section Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
              <div>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.25rem 0' }}>
                  Institution Staff Management & Role Permissions
                </h2>
                <p style={{ color: '#667085', fontSize: '0.875rem', margin: 0 }}>
                  Manage authorized educators, admissions officers, and academic coordinators assigned to <strong>{overview?.institution_name || institutionId}</strong>.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <button
                  onClick={() => {
                    setShowInviteModal(true)
                    setInviteResult(null)
                    setInviteError('')
                    setInviteFullName('')
                    setInviteEmail('')
                    setInvitePhone('')
                    setInviteRole('admissions_officer')
                  }}
                  style={{
                    background: '#155EEF',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.6rem 1.15rem',
                    fontSize: '0.875rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    boxShadow: '0 2px 4px rgba(21, 94, 239, 0.2)'
                  }}
                >
                  ➕ Invite New Staff Member
                </button>

                <button
                  onClick={loadStaffList}
                  style={{
                    background: '#F8F9FA',
                    color: '#344054',
                    border: '1px solid #D0D5DD',
                    borderRadius: '8px',
                    padding: '0.6rem 1rem',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  ↻ Refresh
                </button>
              </div>
            </div>"""

replacement_header = """            {/* Staff Section Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.25rem 0' }}>
                  Institution Staff Management & Role Permissions
                </h2>
                <p style={{ color: '#667085', fontSize: '0.875rem', margin: 0 }}>
                  Manage authorized educators, admissions officers, and candidate applications for <strong>{overview?.institution_name || institutionId}</strong>.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                <button
                  onClick={() => {
                    setShowCandidateInviteModal(true)
                    setCandInviteResult(null)
                    setCandInviteError('')
                    setCandInviteName('')
                    setCandInviteEmail('')
                    setCandInvitePhone('')
                    setCandInviteRole('admissions_officer')
                  }}
                  style={{
                    background: '#027A48',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.6rem 1.15rem',
                    fontSize: '0.875rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    boxShadow: '0 2px 4px rgba(2, 122, 72, 0.2)'
                  }}
                >
                  📝 Invite Staff Candidate (Three-Level)
                </button>

                <button
                  onClick={() => {
                    setShowInviteModal(true)
                    setInviteResult(null)
                    setInviteError('')
                    setInviteFullName('')
                    setInviteEmail('')
                    setInvitePhone('')
                    setInviteRole('admissions_officer')
                  }}
                  style={{
                    background: '#155EEF',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.6rem 1.15rem',
                    fontSize: '0.875rem',
                    fontWeight: 700,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    boxShadow: '0 2px 4px rgba(21, 94, 239, 0.2)'
                  }}
                >
                  ➕ Direct Staff Invite
                </button>

                <button
                  onClick={() => {
                    loadStaffList()
                    loadCandidateApps()
                  }}
                  style={{
                    background: '#F8F9FA',
                    color: '#344054',
                    border: '1px solid #D0D5DD',
                    borderRadius: '8px',
                    padding: '0.6rem 1rem',
                    fontSize: '0.875rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  ↻ Refresh
                </button>
              </div>
            </div>

            {/* Sub-Tabs: Active Staff Roster vs Candidate Applications */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', borderBottom: '1px solid #EAECF0' }}>
              <button
                onClick={() => setStaffSubTab('roster')}
                style={{
                  padding: '0.6rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  border: 'none',
                  background: 'none',
                  borderBottom: staffSubTab === 'roster' ? '3px solid #155EEF' : '3px solid transparent',
                  color: staffSubTab === 'roster' ? '#155EEF' : '#667085',
                  cursor: 'pointer',
                  marginBottom: '-1px'
                }}
              >
                👥 Active Staff Roster ({filteredStaff.length})
              </button>

              <button
                onClick={() => setStaffSubTab('candidates')}
                style={{
                  padding: '0.6rem 1rem',
                  fontSize: '0.875rem',
                  fontWeight: 700,
                  border: 'none',
                  background: 'none',
                  borderBottom: staffSubTab === 'candidates' ? '3px solid #155EEF' : '3px solid transparent',
                  color: staffSubTab === 'candidates' ? '#155EEF' : '#667085',
                  cursor: 'pointer',
                  marginBottom: '-1px'
                }}
              >
                📝 Candidate Applications & Onboarding ({candidateApps.length})
              </button>
            </div>"""

assert target_header in content, "target_header not found"
content = content.replace(target_header, replacement_header, 1)

# 2. Wrap Staff Roster in staffSubTab === 'roster'
target_roster_top = """            {/* Staff KPI Summary Cards */}"""
replacement_roster_top = """            {staffSubTab === 'roster' && (
            <div>
            {/* Staff KPI Summary Cards */}"""

assert target_roster_top in content, "target_roster_top not found"
content = content.replace(target_roster_top, replacement_roster_top, 1)

# Target end of roster table: before closing div of mainTab === 'staff'
target_roster_bottom = """                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}"""

replacement_roster_bottom = """                  </tbody>
                </table>
              </div>
            )}
            </div>
            )}

            {/* Candidate Applications Sub-Tab */}
            {staffSubTab === 'candidates' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <div style={{ fontSize: '0.9rem', color: '#475467', fontWeight: 600 }}>
                    Candidate applications requiring evaluation, correction review, or formal appointment approval.
                  </div>
                  <button
                    onClick={() => {
                      setShowCandidateInviteModal(true)
                      setCandInviteResult(null)
                      setCandInviteError('')
                      setCandInviteName('')
                      setCandInviteEmail('')
                      setCandInvitePhone('')
                    }}
                    className="btn btn--primary btn--sm"
                  >
                    + Invite New Candidate
                  </button>
                </div>

                {loadingCandidates ? (
                  <div style={{ textAlign: 'center', padding: '3rem' }}>
                    <LoadingSpinner />
                    <p style={{ marginTop: '0.5rem', color: '#667085', fontSize: '0.85rem' }}>Loading candidate dossiers...</p>
                  </div>
                ) : candidateApps.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '3rem', background: '#F8F9FA', borderRadius: '8px' }}>
                    <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📝</div>
                    <div style={{ fontWeight: 700, color: '#102B46' }}>No Candidate Applications</div>
                    <div style={{ fontSize: '0.85rem', color: '#667085', marginTop: '0.25rem' }}>
                      Invite candidates to submit their qualifications and employment credentials for review.
                    </div>
                  </div>
                ) : (
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem', textAlign: 'left' }}>
                      <thead>
                        <tr style={{ background: '#F8F9FA', borderBottom: '2px solid #EAECF0', color: '#475467', fontWeight: 700 }}>
                          <th style={{ padding: '0.75rem 1rem' }}>Application ID</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Candidate Name</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Target Role</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Credentials</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Last Updated</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {candidateApps.map((app) => (
                          <tr key={app.application_id} style={{ borderBottom: '1px solid #EAECF0' }}>
                            <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#102B46' }}>
                              {app.application_id}
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 700, color: '#102B46' }}>{app.candidate_name}</div>
                              <div style={{ fontSize: '0.78rem', color: '#667085' }}>{app.candidate_email}</div>
                              {app.candidate_phone && <div style={{ fontSize: '0.72rem', color: '#98A2B3' }}>📞 {app.candidate_phone}</div>}
                            </td>
                            <td style={{ padding: '0.75rem 1rem', textTransform: 'capitalize' }}>
                              <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.2rem 0.55rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
                                {app.role_id?.replace('_', ' ')}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span style={{
                                padding: '0.2rem 0.55rem',
                                borderRadius: '12px',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                background: app.status === 'activated' ? '#ECFDF3' : app.status === 'approved' ? '#EFF8FF' : app.status === 'declined' ? '#FEF3F2' : app.status === 'correction_requested' ? '#FEF08A' : '#FFFAEB',
                                color: app.status === 'activated' ? '#027A48' : app.status === 'approved' ? '#175CD3' : app.status === 'declined' ? '#B42318' : app.status === 'correction_requested' ? '#854D0E' : '#B54708'
                              }}>
                                {app.status?.replace('_', ' ')}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem', fontSize: '0.78rem', color: '#475467' }}>
                              {app.qualifications?.length ? `${app.qualifications.length} Quals` : 'None'} · {app.documents?.length ? `${app.documents.length} Docs` : 'No Docs'}
                            </td>
                            <td style={{ padding: '0.75rem 1rem', color: '#667085', fontSize: '0.78rem' }}>
                              {app.updated_at ? new Date(app.updated_at).toLocaleDateString() : '-'}
                            </td>
                            <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                              <button
                                onClick={() => handleInspectCandidateApp(app)}
                                style={{
                                  background: '#155EEF',
                                  color: '#FFFFFF',
                                  border: 'none',
                                  borderRadius: '4px',
                                  padding: '0.35rem 0.65rem',
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  cursor: 'pointer'
                                }}
                              >
                                🔍 Inspect Dossier
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}"""

assert target_roster_bottom in content, "target_roster_bottom not found"
content = content.replace(target_roster_bottom, replacement_roster_bottom, 1)

# 3. Add Candidate Modals before closing </div></div>
target_modals_end = """        {selectedApp && ("""

candidate_modals_jsx = """        {/* Candidate Invite Modal */}
        {showCandidateInviteModal && (
          <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(16, 43, 70, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 9999
          }}>
            <div style={{ background: '#FFFFFF', borderRadius: '12px', maxWidth: '600px', width: '100%', padding: '1.75rem', boxShadow: '0 20px 40px rgba(0,0,0,0.2)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#102B46', fontWeight: 800 }}>
                  Invite Staff Candidate (Three-Level Onboarding)
                </h3>
                <button onClick={() => setShowCandidateInviteModal(false)} style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
              </div>

              {candInviteError && <Alert type="error" title="Error" style={{ marginBottom: '1rem' }}>{candInviteError}</Alert>}

              {candInviteResult ? (
                <div>
                  <Alert type="success" title="Candidate Invitation Generated!">
                    Candidate invitation link created for <strong>{candInviteResult.candidate_email}</strong>.
                    Submission will create a pending application for your review before activation.
                  </Alert>

                  <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', margin: '1rem 0' }}>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', marginBottom: '0.35rem' }}>
                      Candidate Application Link:
                    </label>
                    <input
                      type="text"
                      readOnly
                      value={`${window.location.origin}/#/staff-application?token=${candInviteResult.candidate_token}`}
                      style={{ width: '100%', padding: '0.5rem', fontFamily: 'monospace', fontSize: '0.8rem', borderRadius: '4px', border: '1px solid #D0D5DD', background: '#FFFFFF' }}
                    />
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(`${window.location.origin}/#/staff-application?token=${candInviteResult.candidate_token}`)
                        alert('Candidate link copied to clipboard!')
                      }}
                      className="btn btn--secondary btn--sm"
                      style={{ marginTop: '0.5rem' }}
                    >
                      📋 Copy Candidate Link
                    </button>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <button onClick={() => setShowCandidateInviteModal(false)} className="btn btn--primary">Done</button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleInviteCandidateSubmit}>
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>Candidate Full Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Dr. Kavitha Murthy"
                      value={candInviteName}
                      onChange={(e) => setCandInviteName(e.target.value)}
                      style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>Work Email *</label>
                      <input
                        type="email"
                        required
                        placeholder="e.g. kavitha@institution.edu"
                        value={candInviteEmail}
                        onChange={(e) => setCandInviteEmail(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>Contact Phone</label>
                      <input
                        type="text"
                        placeholder="e.g. 9845012345"
                        value={candInvitePhone}
                        onChange={(e) => setCandInvitePhone(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                      />
                    </div>
                  </div>

                  <div style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>Target Institutional Role</label>
                    <select
                      value={candInviteRole}
                      onChange={(e) => setCandInviteRole(e.target.value)}
                      style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', background: '#FFFFFF' }}
                    >
                      <option value="admissions_officer">Admissions Officer</option>
                      <option value="academic_admin">Academic Administrator</option>
                      <option value="student_records_officer">Student Records Officer</option>
                      <option value="school_staff">General Staff Member</option>
                    </select>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <button type="button" onClick={() => setShowCandidateInviteModal(false)} className="btn btn--secondary">Cancel</button>
                    <button type="submit" disabled={submittingCandInvite} className="btn btn--primary">
                      {submittingCandInvite ? 'Generating Invitation...' : 'Generate Candidate Invitation →'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Candidate Dossier Inspection & Action Modal */}
        {selectedCandidateApp && (
          <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(16, 43, 70, 0.65)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem', zIndex: 9999
          }}>
            <div style={{
              background: '#FFFFFF', borderRadius: '12px', maxWidth: '800px', width: '100%', maxHeight: '92vh', overflowY: 'auto',
              boxShadow: '0 20px 40px rgba(0,0,0,0.2)', display: 'flex', flexDirection: 'column'
            }}>
              <div style={{ background: '#102B46', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#98A2B3', textTransform: 'uppercase', fontWeight: 700 }}>Staff Candidate Dossier Inspection</div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, marginTop: '0.2rem' }}>
                    {selectedCandidateApp.candidate_name} ({selectedCandidateApp.application_id})
                  </div>
                </div>
                <button onClick={() => setSelectedCandidateApp(null)} style={{ background: 'none', border: 'none', color: '#FFFFFF', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>
              </div>

              <div style={{ padding: '1.5rem', flex: 1 }}>
                {candidateActionFeedback && (
                  <Alert type={candidateActionFeedback.type} title="Action Completed" style={{ marginBottom: '1.25rem' }}>
                    {candidateActionFeedback.message}
                  </Alert>
                )}

                {/* Candidate Summary Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', background: '#F8F9FA', padding: '1rem', borderRadius: '8px', marginBottom: '1.25rem' }}>
                  <div><span style={{ color: '#667085', fontSize: '0.75rem' }}>Email:</span> <strong style={{ display: 'block', fontSize: '0.85rem' }}>{selectedCandidateApp.candidate_email}</strong></div>
                  <div><span style={{ color: '#667085', fontSize: '0.75rem' }}>Phone:</span> <strong style={{ display: 'block', fontSize: '0.85rem' }}>{selectedCandidateApp.candidate_phone || 'None'}</strong></div>
                  <div><span style={{ color: '#667085', fontSize: '0.75rem' }}>Role:</span> <strong style={{ display: 'block', fontSize: '0.85rem', textTransform: 'capitalize' }}>{selectedCandidateApp.role_id?.replace('_', ' ')}</strong></div>
                  <div><span style={{ color: '#667085', fontSize: '0.75rem' }}>Status:</span> <strong style={{ display: 'block', fontSize: '0.85rem', textTransform: 'uppercase', color: selectedCandidateApp.status === 'approved' ? '#12B76A' : '#155EEF' }}>{selectedCandidateApp.status?.replace('_', ' ')}</strong></div>
                </div>

                {/* Qualifications */}
                <div style={{ marginBottom: '1.25rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#102B46', fontWeight: 700 }}>Educational Qualifications</h4>
                  {selectedCandidateApp.qualifications?.length > 0 ? (
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                        <thead>
                          <tr style={{ background: '#F8F9FA', borderBottom: '1px solid #EAECF0', color: '#475467' }}>
                            <th style={{ padding: '0.5rem' }}>Degree / Certificate</th>
                            <th style={{ padding: '0.5rem' }}>Institution</th>
                            <th style={{ padding: '0.5rem' }}>Year</th>
                            <th style={{ padding: '0.5rem' }}>Marks / %</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedCandidateApp.qualifications.map((q, i) => (
                            <tr key={i} style={{ borderBottom: '1px solid #EAECF0' }}>
                              <td style={{ padding: '0.5rem', fontWeight: 600 }}>{q.degree}</td>
                              <td style={{ padding: '0.5rem' }}>{q.institution || '-'}</td>
                              <td style={{ padding: '0.5rem' }}>{q.year || '-'}</td>
                              <td style={{ padding: '0.5rem' }}>{q.marks_percentage || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : <div style={{ color: '#667085', fontSize: '0.8rem' }}>No qualifications submitted yet.</div>}
                </div>

                {/* Employment Details */}
                <div style={{ marginBottom: '1.25rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#102B46', fontWeight: 700 }}>Employment History</h4>
                  <div style={{ background: '#F8F9FA', padding: '0.85rem', borderRadius: '6px', fontSize: '0.825rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.5rem' }}>
                    <div><span style={{ color: '#667085' }}>Current Employer:</span> <strong>{selectedCandidateApp.employment_details?.current_employer || 'None specified'}</strong></div>
                    <div><span style={{ color: '#667085' }}>Designation:</span> <strong>{selectedCandidateApp.employment_details?.designation || '-'}</strong></div>
                    <div><span style={{ color: '#667085' }}>Experience:</span> <strong>{selectedCandidateApp.employment_details?.experience_years ? `${selectedCandidateApp.employment_details.experience_years} Years` : '-'}</strong></div>
                    <div><span style={{ color: '#667085' }}>Notice Period:</span> <strong>{selectedCandidateApp.employment_details?.notice_period || '-'}</strong></div>
                  </div>
                </div>

                {/* Documents */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', fontSize: '0.95rem', color: '#102B46', fontWeight: 700 }}>Supporting Documents</h4>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    {(selectedCandidateApp.documents || []).map((d, i) => (
                      <span key={i} style={{ background: '#EFF8FF', border: '1px solid #B2DDFF', color: '#175CD3', padding: '0.25rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                        📄 {d.doc_type?.replace('_', ' ')}: {d.filename}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Action Panels */}
                {selectedCandidateApp.activation_url && (
                  <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
                    <div style={{ color: '#027A48', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                      ✓ Application Approved! Candidate Activation Link:
                    </div>
                    <input
                      type="text"
                      readOnly
                      value={`${window.location.origin}/#${selectedCandidateApp.activation_url}`}
                      style={{ width: '100%', padding: '0.45rem', fontSize: '0.8rem', fontFamily: 'monospace', borderRadius: '4px', border: '1px solid #A6F4C5', background: '#FFFFFF' }}
                    />
                  </div>
                )}

                {selectedCandidateApp.status in {'submitted': 1, 'resubmitted': 1} && (
                  <div style={{ borderTop: '1px solid #EAECF0', paddingTop: '1rem' }}>
                    <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                      Institutional Administrator Decisions
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
                      <button
                        onClick={() => setCandidateActionTab('correct')}
                        className={`btn btn--sm ${candidateActionTab === 'correct' ? 'btn--accent' : 'btn--ghost'}`}
                      >
                        💬 Request Correction
                      </button>
                      <button
                        onClick={() => setCandidateActionTab('approve')}
                        className={`btn btn--sm ${candidateActionTab === 'approve' ? 'btn--primary' : 'btn--ghost'}`}
                      >
                        ✓ Approve Application
                      </button>
                      <button
                        onClick={() => setCandidateActionTab('decline')}
                        className={`btn btn--sm ${candidateActionTab === 'decline' ? 'btn--secondary' : 'btn--ghost'}`}
                      >
                        ✕ Decline Application
                      </button>
                    </div>

                    {candidateActionTab === 'correct' && (
                      <form onSubmit={handleRequestCorrectionSubmit} style={{ background: '#FEF08A', padding: '1rem', borderRadius: '8px' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#854D0E', marginBottom: '0.35rem' }}>
                          Specify Missing Information or Corrections Needed *
                        </label>
                        <textarea
                          rows={2}
                          required
                          value={correctionInput}
                          onChange={(e) => setCorrectionInput(e.target.value)}
                          placeholder="e.g. Please attach degree marks statement and specify notice period."
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #FACC15', fontSize: '0.85rem', marginBottom: '0.5rem' }}
                        />
                        <button type="submit" disabled={candidateActionSubmitting} className="btn btn--primary btn--sm">
                          {candidateActionSubmitting ? 'Dispatching...' : 'Dispatch Correction Request'}
                        </button>
                      </form>
                    )}

                    {candidateActionTab === 'approve' && (
                      <form onSubmit={handleApproveCandidateSubmit} style={{ background: '#ECFDF3', padding: '1rem', borderRadius: '8px' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#027A48', marginBottom: '0.35rem' }}>
                          Appointment / Approval Notes (Optional)
                        </label>
                        <input
                          type="text"
                          value={approvalNotesInput}
                          onChange={(e) => setApprovalNotesInput(e.target.value)}
                          placeholder="e.g. Approved for Admissions Officer post in Ballari Education School."
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #A6F4C5', fontSize: '0.85rem', marginBottom: '0.5rem' }}
                        />
                        <button type="submit" disabled={candidateActionSubmitting} className="btn btn--primary btn--sm">
                          {candidateActionSubmitting ? 'Approving...' : 'Confirm Approval & Generate Activation Link'}
                        </button>
                      </form>
                    )}

                    {candidateActionTab === 'decline' && (
                      <form onSubmit={handleDeclineCandidateSubmit} style={{ background: '#FEF3F2', padding: '1rem', borderRadius: '8px' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#B42318', marginBottom: '0.35rem' }}>
                          Official Reason for Declining *
                        </label>
                        <input
                          type="text"
                          required
                          value={declineInput}
                          onChange={(e) => setDeclineInput(e.target.value)}
                          placeholder="e.g. Qualifications do not match statutory eligibility criteria."
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #FECDCA', fontSize: '0.85rem', marginBottom: '0.5rem' }}
                        />
                        <button type="submit" disabled={candidateActionSubmitting} className="btn btn--secondary btn--sm" style={{ background: '#B42318', color: '#FFFFFF' }}>
                          {candidateActionSubmitting ? 'Declining...' : 'Confirm Decline with Reason'}
                        </button>
                      </form>
                    )}
                  </div>
                )}
              </div>

              <div style={{ padding: '1rem 1.5rem', background: '#F8F9FA', borderTop: '1px solid #EAECF0', textAlign: 'right' }}>
                <button onClick={() => setSelectedCandidateApp(null)} className="btn btn--secondary btn--sm">Close Dossier</button>
              </div>
            </div>
          </div>
        )}

        {selectedApp && ("""

assert target_modals_end in content, "target_modals_end not found"
content = content.replace(target_modals_end, candidate_modals_jsx, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("InstitutionAdminDashboard.jsx updated with candidate UI successfully!")
