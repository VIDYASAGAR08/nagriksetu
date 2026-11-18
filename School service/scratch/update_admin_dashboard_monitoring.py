import os

admin_file = r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\AdminDashboard.jsx"
with open(admin_file, "r", encoding="utf-8") as f:
    admin_code = f.read()

# 1. Add state for staff monitoring
target_state = """  // Institution Admins state
  const [admins, setAdmins] = useState([])"""

replacement_state = """  // Staff Monitoring state
  const [staffMonitoring, setStaffMonitoring] = useState(null)
  const [loadingMonitoring, setLoadingMonitoring] = useState(false)
  const [monitoringCategory, setMonitoringCategory] = useState('all')

  // Institution Admins state
  const [admins, setAdmins] = useState([])"""

assert target_state in admin_code, "target_state not found"
admin_code = admin_code.replace(target_state, replacement_state, 1)

# 2. Add loadStaffMonitoring
target_func = """  async function loadAdmins() {"""

replacement_func = """  async function loadStaffMonitoring() {
    if (!token || !isPlatformAdmin) return
    try {
      setLoadingMonitoring(true)
      const data = await apiGet('/admin/staff-monitoring', token)
      setStaffMonitoring(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch statewide staff monitoring data.')
    } finally {
      setLoadingMonitoring(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'staff-monitoring') {
      loadStaffMonitoring()
    }
  }, [activeTab])

  async function loadAdmins() {"""

assert target_func in admin_code, "target_func not found"
admin_code = admin_code.replace(target_func, replacement_func, 1)

# 3. Add Tab button
target_btn = """          {isPlatformAdmin && (
            <button
              onClick={() => setActiveTab('admins')}
              className={`btn btn--sm ${activeTab === 'admins' ? 'btn--primary' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              👥 Institution Administrators
            </button>
          )}"""

replacement_btn = """          {isPlatformAdmin && (
            <button
              onClick={() => setActiveTab('admins')}
              className={`btn btn--sm ${activeTab === 'admins' ? 'btn--primary' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              👥 Institution Administrators
            </button>
          )}
          {isPlatformAdmin && (
            <button
              onClick={() => setActiveTab('staff-monitoring')}
              className={`btn btn--sm ${activeTab === 'staff-monitoring' ? 'btn--primary' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              📊 Statewide Staff Governance & Monitoring
            </button>
          )}"""

assert target_btn in admin_code, "target_btn not found"
admin_code = admin_code.replace(target_btn, replacement_btn, 1)

# 4. Add Tab view content at the end before closing tags
target_view = """      </div>
    </div>
  )
}"""

monitoring_jsx = """
        {/* TAB 4: STATEWIDE STAFF GOVERNANCE & MONITORING */}
        {activeTab === 'staff-monitoring' && isPlatformAdmin && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.25rem 0' }}>
                  Statewide Staff Governance & Lifecycle Monitoring
                </h2>
                <p style={{ color: '#667085', fontSize: '0.85rem', margin: 0 }}>
                  Central visibility across all 30 institutions: invitations, candidate applications, approvals, permissions, and suspensions.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                <select
                  value={monitoringCategory}
                  onChange={(e) => setMonitoringCategory(e.target.value)}
                  style={{ padding: '0.5rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.825rem', background: '#FFFFFF', color: '#102B46' }}
                >
                  <option value="all">All Institution Categories (30)</option>
                  <option value="Schools (K-10)">Schools (K-10) [15]</option>
                  <option value="PU Colleges (11-12)">PU Colleges (11-12) [5]</option>
                  <option value="Degree Colleges">Degree Colleges [5]</option>
                  <option value="Universities">Universities [5]</option>
                </select>

                <button
                  onClick={loadStaffMonitoring}
                  className="btn btn--secondary btn--sm"
                >
                  ↻ Refresh
                </button>
              </div>
            </div>

            {/* KPI Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: '#FFFFFF', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#102B46' }}>30</div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Monitored Institutions</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Zero cross-tenant bleed</div>
              </div>

              <div style={{ background: '#FFFFFF', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#155EEF' }}>
                  {loadingMonitoring ? '...' : staffMonitoring?.summary?.total_candidate_applications ?? 0}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Candidate Applications</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Three-level onboarding</div>
              </div>

              <div style={{ background: '#FFFFFF', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#12B76A' }}>
                  {loadingMonitoring ? '...' : staffMonitoring?.summary?.active_roster_staff ?? 0}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Active Roster Staff</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Authorized personnel</div>
              </div>

              <div style={{ background: '#FFFFFF', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.85rem', fontWeight: 800, color: '#F04438' }}>
                  {loadingMonitoring ? '...' : staffMonitoring?.summary?.suspended_staff ?? 0}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Suspended Accounts</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Login revoking active</div>
              </div>
            </div>

            {/* Candidate Applications Ledger */}
            <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden', marginBottom: '1.5rem' }}>
              <div style={{ padding: '0.85rem 1.25rem', background: '#F8F9FA', borderBottom: '1px solid #EAECF0', fontWeight: 700, color: '#102B46', fontSize: '0.9rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>Staff Candidate Applications Dossiers</span>
                <span style={{ fontSize: '0.75rem', color: '#667085' }}>{staffMonitoring?.applications?.length || 0} Records</span>
              </div>

              {loadingMonitoring ? (
                <div style={{ padding: '2rem', textAlign: 'center' }}><LoadingSpinner /></div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.825rem', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ background: '#F8F9FA', borderBottom: '1px solid #EAECF0', color: '#475467' }}>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Application ID</th>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Institution</th>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Candidate</th>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Role</th>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Status</th>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Reviewer</th>
                        <th style={{ padding: '0.65rem 0.85rem' }}>Updated</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(staffMonitoring?.applications || [])
                        .filter(app => monitoringCategory === 'all' || app.category === monitoringCategory)
                        .map((app) => (
                          <tr key={app.application_id} style={{ borderBottom: '1px solid #EAECF0' }}>
                            <td style={{ padding: '0.65rem 0.85rem', fontFamily: 'monospace', fontWeight: 700, color: '#102B46' }}>
                              {app.application_id}
                            </td>
                            <td style={{ padding: '0.65rem 0.85rem' }}>
                              <div style={{ fontWeight: 600, color: '#102B46' }}>{app.institution_name}</div>
                              <div style={{ fontSize: '0.72rem', color: '#667085' }}>{app.institution_id} · {app.category}</div>
                            </td>
                            <td style={{ padding: '0.65rem 0.85rem' }}>
                              <div style={{ fontWeight: 600 }}>{app.candidate_name}</div>
                              <div style={{ fontSize: '0.72rem', color: '#667085' }}>{app.candidate_email}</div>
                            </td>
                            <td style={{ padding: '0.65rem 0.85rem', textTransform: 'capitalize' }}>
                              {app.role_id?.replace('_', ' ')}
                            </td>
                            <td style={{ padding: '0.65rem 0.85rem' }}>
                              <span style={{
                                padding: '0.15rem 0.45rem',
                                borderRadius: '4px',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                background: app.status === 'activated' ? '#ECFDF3' : app.status === 'approved' ? '#EFF8FF' : app.status === 'declined' ? '#FEF3F2' : '#FFFAEB',
                                color: app.status === 'activated' ? '#027A48' : app.status === 'approved' ? '#175CD3' : app.status === 'declined' ? '#B42318' : '#B54708'
                              }}>
                                {app.status?.replace('_', ' ')}
                              </span>
                            </td>
                            <td style={{ padding: '0.65rem 0.85rem', color: '#475467' }}>
                              {app.reviewed_by || app.created_by || '-'}
                            </td>
                            <td style={{ padding: '0.65rem 0.85rem', color: '#667085', fontSize: '0.75rem' }}>
                              {app.updated_at ? new Date(app.updated_at).toLocaleString() : '-'}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Append-Only Statewide Staff Audit Ledger */}
            <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '8px', overflow: 'hidden' }}>
              <div style={{ padding: '0.85rem 1.25rem', background: '#F8F9FA', borderBottom: '1px solid #EAECF0', fontWeight: 700, color: '#102B46', fontSize: '0.9rem', display: 'flex', justifyContent: 'space-between' }}>
                <span>Statewide Append-Only Staff Governance Audit Trail</span>
                <span style={{ fontSize: '0.75rem', color: '#12B76A', fontWeight: 700 }}>● IMMUTABLE LEDGER</span>
              </div>

              {loadingMonitoring ? (
                <div style={{ padding: '2rem', textAlign: 'center' }}><LoadingSpinner /></div>
              ) : (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', textAlign: 'left' }}>
                    <thead>
                      <tr style={{ background: '#F8F9FA', borderBottom: '1px solid #EAECF0', color: '#475467' }}>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Timestamp</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Action</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Institution</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Actor</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Target Entity</th>
                        <th style={{ padding: '0.6rem 0.75rem' }}>Metadata Details</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(staffMonitoring?.audit_events || [])
                        .filter(evt => monitoringCategory === 'all' || evt.category === monitoringCategory)
                        .map((evt) => (
                          <tr key={evt.audit_id} style={{ borderBottom: '1px solid #EAECF0' }}>
                            <td style={{ padding: '0.6rem 0.75rem', color: '#667085', whiteSpace: 'nowrap' }}>
                              {evt.timestamp ? new Date(evt.timestamp).toLocaleString() : 'N/A'}
                            </td>
                            <td style={{ padding: '0.6rem 0.75rem' }}>
                              <span style={{ background: '#EFF4FF', color: '#155EEF', padding: '0.15rem 0.45rem', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700 }}>
                                {evt.action}
                              </span>
                            </td>
                            <td style={{ padding: '0.6rem 0.75rem' }}>
                              <div style={{ fontWeight: 600, color: '#102B46' }}>{evt.institution_name || evt.institution_id}</div>
                              <div style={{ fontSize: '0.7rem', color: '#667085' }}>{evt.institution_id}</div>
                            </td>
                            <td style={{ padding: '0.6rem 0.75rem' }}>
                              <div style={{ fontWeight: 600 }}>{evt.actor_name}</div>
                              <div style={{ fontSize: '0.7rem', color: '#667085' }}>Role: {evt.actor_role}</div>
                            </td>
                            <td style={{ padding: '0.6rem 0.75rem', fontFamily: 'monospace', color: '#344054' }}>
                              {evt.entity_id || '-'}
                            </td>
                            <td style={{ padding: '0.6rem 0.75rem', color: '#475467', fontSize: '0.75rem' }}>
                              {JSON.stringify(evt.metadata)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}"""

assert target_view in admin_code, "target_view not found"
admin_code = admin_code.replace(target_view, monitoring_jsx, 1)

with open(admin_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(admin_code)

print("AdminDashboard.jsx updated successfully!")
