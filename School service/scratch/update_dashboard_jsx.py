p = 'C:/Users/callm/nagriksetu/frontend/src/pages/admin/InstitutionAdminDashboard.jsx'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update handleOpenApplication to use appId fallback
old_open_app = """  async function handleOpenApplication(app) {
    setSelectedApp(app)
    setActionTab('none')
    setActionNotes('')
    setRejectionReason('')
    setRejectionExplanation('')
    setClarificationMessage('')
    setConfirmApprove(false)
    setActionFeedback(null)

    // Load full detail and history
    try {
      setLoadingHistory(true)
      setHistoryError('')
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${app.application_id}`, token).catch(() => app),
        apiGet(`/school/admissions/${app.application_id}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
    } catch (err) {
      setHistoryError(err.message || 'Could not load application audit trail.')
    } finally {
      setLoadingHistory(false)
    }
  }"""

new_open_app = """  async function handleOpenApplication(app) {
    const appId = app.application_id || app.id || app.application_reference
    setSelectedApp(app)
    setActionTab('none')
    setActionNotes('')
    setRejectionReason('')
    setRejectionExplanation('')
    setClarificationMessage('')
    setConfirmApprove(false)
    setActionFeedback(null)

    // Load full detail and history
    try {
      setLoadingHistory(true)
      setHistoryError('')
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token).catch(() => app),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
    } catch (err) {
      setHistoryError(err.message || 'Could not load application audit trail.')
    } finally {
      setLoadingHistory(false)
    }
  }"""

# 2. Update Overview Live Feed
old_overview_feed = """            {/* Live Applications Action Items Feed */}
            <div style={{ background: '#FFFFFF', borderRadius: '10px', border: '1px solid #E2E8F0', padding: '1.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
                    🚨 Stage 1 Admission Applications Awaiting Determination
                  </h3>
                  <p style={{ margin: '0.2rem 0 0 0', color: '#667085', fontSize: '0.82rem' }}>
                    Applications requiring immediate academic administrator review.
                  </p>
                </div>
                <button
                  onClick={() => setMainTab('applications')}
                  style={{
                    background: '#EFF4FF',
                    color: '#155EEF',
                    border: '1px solid #B2DDFF',
                    borderRadius: '6px',
                    padding: '0.4rem 0.8rem',
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  View All ({applications.length}) →
                </button>
              </div>

              {applications.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#667085' }}>
                  No pending applications requiring immediate action.
                </div>
              ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', textAlign: 'left' }}>
                      <th style={{ padding: '0.5rem 0.75rem' }}>Application ID</th>
                      <th style={{ padding: '0.5rem 0.75rem' }}>Student Name</th>
                      <th style={{ padding: '0.5rem 0.75rem' }}>Standard / Program</th>
                      <th style={{ padding: '0.5rem 0.75rem' }}>Status</th>
                      <th style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {applications.slice(0, 5).map(app => (
                      <tr key={app.id || app.application_reference} style={{ borderBottom: '1px solid #F2F4F7' }}>
                        <td style={{ padding: '0.5rem 0.75rem', fontFamily: 'monospace', fontWeight: 700, color: '#155EEF' }}>
                          {app.application_reference || app.id}
                        </td>
                        <td style={{ padding: '0.5rem 0.75rem', fontWeight: 700, color: '#102B46' }}>
                          {app.student_name}
                        </td>
                        <td style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>
                          {app.standard ? `Standard ${app.standard}` : (app.program_name || 'Standard 8')}
                        </td>
                        <td style={{ padding: '0.5rem 0.75rem' }}>
                          <StatusBadge status={app.status} />
                        </td>
                        <td style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                          <button
                            onClick={() => {
                              setSelectedApp(app)
                              loadAppHistory(app.id)
                            }}
                            style={{
                              padding: '0.35rem 0.75rem',
                              background: '#155EEF',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              fontSize: '0.78rem',
                              fontWeight: 700,
                              cursor: 'pointer'
                            }}
                          >
                            Review →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>"""

new_overview_feed = """            {/* Live Applications Action Items Feed */}
            {(() => {
              const pendingStage1Apps = applications.filter(a => ['submitted', 'under_review', 'action_required', 'clarification_requested'].includes(a.status))
              const displayCount = overview?.pending_admission_reviews ?? pendingStage1Apps.length
              return (
                <div style={{ background: '#FFFFFF', borderRadius: '10px', border: '1px solid #E2E8F0', padding: '1.25rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
                        🚨 Stage 1 Admission Applications Awaiting Determination
                      </h3>
                      <p style={{ margin: '0.2rem 0 0 0', color: '#667085', fontSize: '0.82rem' }}>
                        Applications requiring immediate academic administrator review.
                      </p>
                    </div>
                    <button
                      onClick={() => setMainTab('applications')}
                      style={{
                        background: '#EFF4FF',
                        color: '#155EEF',
                        border: '1px solid #B2DDFF',
                        borderRadius: '6px',
                        padding: '0.4rem 0.8rem',
                        fontSize: '0.82rem',
                        fontWeight: 700,
                        cursor: 'pointer'
                      }}
                    >
                      View All ({displayCount}) →
                    </button>
                  </div>

                  {pendingStage1Apps.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: '#667085' }}>
                      No pending applications requiring immediate action.
                    </div>
                  ) : (
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', textAlign: 'left' }}>
                          <th style={{ padding: '0.5rem 0.75rem' }}>Application ID</th>
                          <th style={{ padding: '0.5rem 0.75rem' }}>Student Name</th>
                          <th style={{ padding: '0.5rem 0.75rem' }}>Standard / Program</th>
                          <th style={{ padding: '0.5rem 0.75rem' }}>Status</th>
                          <th style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {pendingStage1Apps.slice(0, 5).map(app => (
                          <tr key={app.id || app.application_reference || app.application_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                            <td style={{ padding: '0.5rem 0.75rem', fontFamily: 'monospace', fontWeight: 700, color: '#155EEF' }}>
                              {app.application_reference || app.application_id || app.id}
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem', fontWeight: 700, color: '#102B46' }}>
                              {app.student_name || app.applicant_name}
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem', color: '#475467' }}>
                              {app.standard ? `Standard ${app.standard}` : (app.requested_standard ? `Standard ${app.requested_standard}` : (app.program_name || 'Standard 8'))}
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem' }}>
                              <StatusBadge status={app.status} />
                            </td>
                            <td style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                              <button
                                onClick={() => handleOpenApplication(app)}
                                style={{
                                  padding: '0.35rem 0.75rem',
                                  background: '#155EEF',
                                  color: '#FFFFFF',
                                  border: 'none',
                                  borderRadius: '6px',
                                  fontSize: '0.78rem',
                                  fontWeight: 700,
                                  cursor: 'pointer'
                                }}
                              >
                                Review →
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              )
            })()}"""

# Normalize CRLF/LF
for old_s, new_s in [(old_open_app, new_open_app), (old_overview_feed, new_overview_feed)]:
    old_crlf = old_s.replace('\n', '\r\n')
    new_crlf = new_s.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf, 1)
        print('Replaced CRLF block')
    elif old_s in text:
        text = text.replace(old_s, new_s, 1)
        print('Replaced LF block')
    else:
        print('FAILED to find block:', old_s[:60])

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
