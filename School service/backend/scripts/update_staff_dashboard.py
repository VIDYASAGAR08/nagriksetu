import re

file_path = "C:/Users/callm/nagriksetu/frontend/src/pages/staff/StaffDashboard.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add staff management state
state_target = "  const assignedSchoolId = user?.school_id || 'SCH001'"
state_replacement = """  // Staff Management state (for school_admin)
  const [staffList, setStaffList] = useState([])
  const [loadingStaff, setLoadingStaff] = useState(false)
  const [showInviteStaffModal, setShowInviteStaffModal] = useState(false)
  const [staffFullName, setStaffFullName] = useState('')
  const [staffEmail, setStaffEmail] = useState('')
  const [staffPhone, setStaffPhone] = useState('')
  const [staffRole, setStaffRole] = useState('school_staff')
  const [submittingStaffInvite, setSubmittingStaffInvite] = useState(false)
  const [staffInviteResult, setStaffInviteResult] = useState(null)
  const [staffInviteError, setStaffInviteError] = useState('')

  const assignedSchoolId = user?.school_id || 'SCH001'

  async function loadStaffList() {
    if (!token || !isSchoolAdmin) return
    try {
      setLoadingStaff(true)
      const data = await apiGet('/school/admin/staff', token)
      setStaffList(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to load school staff roster.')
    } finally {
      setLoadingStaff(false)
    }
  }

  async function handleStaffInviteSubmit(e) {
    e.preventDefault()
    if (!staffFullName.trim() || !staffEmail.trim()) {
      setStaffInviteError('Please fill in required fields.')
      return
    }

    try {
      setSubmittingStaffInvite(true)
      setStaffInviteError('')
      const payload = {
        full_name: staffFullName.trim(),
        email: staffEmail.trim(),
        phone: staffPhone.trim() || undefined,
        institution_id: assignedSchoolId,
        role_id: staffRole
      }
      const res = await apiPost('/school/admin/staff/invite', payload, token)
      setStaffInviteResult(res)
      setSuccess(`Staff invitation issued for ${res.email}!`)
      loadStaffList()
    } catch (err) {
      setStaffInviteError(err.message || 'Failed to issue staff invitation.')
    } finally {
      setSubmittingStaffInvite(false)
    }
  }"""

if state_target in content:
    content = content.replace(state_target, state_replacement, 1)
    print("State replacement succeeded")
else:
    print("State target not found!")

# 2. Add Tab button
tab_btn_target = """            <button
              onClick={() => setActiveTab('students')}
              className={`btn btn--sm ${activeTab === 'students' ? 'btn--primary' : 'btn--ghost'}`}
            >
              Student Roster (Filtered)
            </button>"""

tab_btn_replacement = """            <button
              onClick={() => setActiveTab('students')}
              className={`btn btn--sm ${activeTab === 'students' ? 'btn--primary' : 'btn--ghost'}`}
            >
              Student Roster (Filtered)
            </button>
            {isSchoolAdmin && (
              <button
                onClick={() => { setActiveTab('staff-mgmt'); loadStaffList(); }}
                className={`btn btn--sm ${activeTab === 'staff-mgmt' ? 'btn--accent' : 'btn--ghost'}`}
              >
                👥 Staff Management
              </button>
            )}"""

if tab_btn_target in content:
    content = content.replace(tab_btn_target, tab_btn_replacement, 1)
    print("Tab button replacement succeeded")
else:
    print("Tab button target not found!")

# 3. Clean duplicate onClick on line ~347 if present
dup_onclick = """            <button
              onClick={() => setActiveTab('admissions')}
              onClick={() => setActiveTab('admissions')}"""
if dup_onclick in content:
    content = content.replace(dup_onclick, """            <button
              onClick={() => setActiveTab('admissions')}""", 1)
    print("Fixed duplicate onClick")

# 4. Add Tab content & modal before closing tag
closing_block_target = "{/* Tab 1: Linking Requests Queue */}"
staff_tab_content = """{/* Tab: Staff Management (School Admin only) */}
        {activeTab === 'staff-mgmt' && isSchoolAdmin && (
          <div>
            <div className="card" style={{ padding: '1.25rem', border: '1px solid #d0d5dd', borderRadius: '8px', marginBottom: '1.5rem', background: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h2 style={{ fontSize: '1.25rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
                  Institutional Staff Directory & Invitations
                </h2>
                <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
                  Manage authorized educators, verification officers and staff assigned to school <strong>{assignedSchoolId}</strong>.
                </p>
              </div>

              <button
                type="button"
                onClick={() => {
                  setStaffFullName('');
                  setStaffEmail('');
                  setStaffPhone('');
                  setStaffRole('school_staff');
                  setStaffInviteResult(null);
                  setStaffInviteError('');
                  setShowInviteStaffModal(true);
                }}
                className="btn btn--primary"
                style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                + Invite Staff Member
              </button>
            </div>

            {loadingStaff ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#6b7280' }}>Loading school staff roster...</p>
              </div>
            ) : (
              <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '1px solid #e2e8f0', color: '#475569' }}>
                        <th style={{ padding: '0.75rem 1rem' }}>Staff Member</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Assigned School</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Role</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                        <th style={{ padding: '0.75rem 1rem' }}>Last Login</th>
                      </tr>
                    </thead>
                    <tbody>
                      {staffList.length === 0 ? (
                        <tr>
                          <td colSpan={5} style={{ padding: '2rem', textAlign: 'center', color: '#6b7280' }}>
                            No staff records found for this school.
                          </td>
                        </tr>
                      ) : (
                        staffList.map((st) => (
                          <tr key={st.user_id} style={{ borderBottom: '1px solid #e8eaed' }}>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 600, color: '#1a3a6b' }}>{st.full_name}</div>
                              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>{st.email}</div>
                              {st.phone && <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Tel: {st.phone}</div>}
                            </td>
                            <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#1a3a6b' }}>
                              {assignedSchoolId}
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span className="badge badge--info" style={{ fontSize: '0.75rem' }}>
                                {st.role_name || st.role_id || st.role}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span className={`badge ${st.status === 'active' ? 'badge--success' : 'badge--warning'}`} style={{ fontSize: '0.75rem' }}>
                                {(st.status || 'active').toUpperCase()}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem', fontSize: '0.8125rem', color: '#64748b' }}>
                              {st.last_login ? new Date(st.last_login).toLocaleString() : 'Never'}
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Invite Staff Modal */}
        {showInviteStaffModal && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0,0,0,0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: '1rem',
            }}
          >
            <div
              className="card"
              style={{
                maxWidth: '520px',
                width: '100%',
                background: '#ffffff',
                borderRadius: '8px',
                padding: '2rem',
                maxHeight: '90vh',
                overflowY: 'auto',
                boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 style={{ fontSize: '1.35rem', color: '#1a3a6b', margin: 0 }}>
                  {staffInviteResult ? 'Staff Invitation Issued' : 'Invite Staff Member'}
                </h3>
                <button
                  type="button"
                  onClick={() => setShowInviteStaffModal(false)}
                  style={{ background: 'none', border: 'none', fontSize: '1.25rem', cursor: 'pointer', color: '#6b7280' }}
                >
                  ✕
                </button>
              </div>

              {staffInviteResult ? (
                <div>
                  <Alert type="success" title="Invitation Created" className="mb-4">
                    Invitation link generated for <strong>{staffInviteResult.email}</strong> at school <strong>{assignedSchoolId}</strong>.
                  </Alert>

                  <div style={{ background: '#f8fafc', padding: '1.25rem', borderRadius: '6px', border: '1px solid #cbd5e1', marginBottom: '1.5rem' }}>
                    <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.4rem' }}>
                      Activation Link:
                    </div>
                    <input
                      type="text"
                      readOnly
                      value={staffInviteResult.invitation_link || `http://localhost:5173/#/accept-invitation?token=${staffInviteResult.invitation_token}`}
                      style={{ width: '100%', padding: '0.5rem', fontSize: '0.8125rem', fontFamily: 'monospace', background: '#ffffff', border: '1px solid #cbd5e1', borderRadius: '4px', marginBottom: '0.75rem' }}
                      onClick={e => e.target.select()}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard?.writeText(staffInviteResult.invitation_link || `http://localhost:5173/#/accept-invitation?token=${staffInviteResult.invitation_token}`)
                        setSuccess('Staff invitation link copied to clipboard!')
                      }}
                      className="btn btn--accent"
                    >
                      Copy Link
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowInviteStaffModal(false)}
                      className="btn btn--primary"
                    >
                      Done
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleStaffInviteSubmit}>
                  {staffInviteError && <Alert type="error" title="Error" className="mb-4">{staffInviteError}</Alert>}

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Staff Member Name *
                    </label>
                    <input
                      type="text"
                      required
                      className="input"
                      placeholder="e.g. Anand Murthy"
                      value={staffFullName}
                      onChange={e => setStaffFullName(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Email Address *
                    </label>
                    <input
                      type="email"
                      required
                      className="input"
                      placeholder="e.g. anand@school.edu.in"
                      value={staffEmail}
                      onChange={e => setStaffEmail(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Contact Mobile (Optional)
                    </label>
                    <input
                      type="text"
                      className="input"
                      placeholder="e.g. 9845098765"
                      value={staffPhone}
                      onChange={e => setStaffPhone(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Target Institution
                    </label>
                    <input
                      type="text"
                      disabled
                      value={`${assignedSchoolId} (Locked to your school)`}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px', background: '#f1f5f9', color: '#64748b' }}
                    />
                  </div>

                  <div style={{ marginBottom: '1.5rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#1a3a6b', marginBottom: '0.35rem' }}>
                      Role within School *
                    </label>
                    <select
                      className="input"
                      value={staffRole}
                      onChange={e => setStaffRole(e.target.value)}
                      style={{ width: '100%', padding: '0.625rem 0.75rem', border: '1px solid #d0d5dd', borderRadius: '4px' }}
                    >
                      <option value="school_staff">School Staff / Teacher</option>
                      <option value="admissions_officer">Admissions Desk Officer</option>
                      <option value="academic_admin">Academic Coordinator</option>
                      <option value="student_records_officer">Student Records Officer</option>
                    </select>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <button
                      type="button"
                      onClick={() => setShowInviteStaffModal(false)}
                      className="btn btn--ghost"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={submittingStaffInvite}
                      className="btn btn--primary"
                      style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                      {submittingStaffInvite ? <LoadingSpinner size="sm" /> : 'Send Staff Invitation →'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        )}

        {/* Tab 1: Linking Requests Queue */}"""

if closing_block_target in content:
    content = content.replace(closing_block_target, staff_tab_content, 1)
    print("Staff tab content replacement succeeded")
else:
    print("Closing block target not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated StaffDashboard.jsx successfully!")
