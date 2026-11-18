import os

dashboard_file = r"C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx"
desk_file = r"C:\Users\callm\nagriksetu\frontend\src\components\admissions\AdmissionDeskTab.jsx"

# --- 1. UPDATE StaffDashboard.jsx ---
with open(dashboard_file, "r", encoding="utf-8") as f:
    dash_code = f.read()

# Add permissions state and fetch
target_dash_state = """  const isSchoolAdmin = user?.role === 'school_admin'
  const [activeTab, setActiveTab] = useState(() => window.location.search.includes('tab=admissions') ? 'admissions' : (isSchoolAdmin ? 'admin-overview' : 'queue')) // 'admin-overview' | 'queue' | 'students'"""

replacement_dash_state = """  const isSchoolAdmin = user?.role === 'school_admin'
  const [effectiveRole, setEffectiveRole] = useState(user?.role || 'school_staff')
  const [permissions, setPermissions] = useState({
    can_view_applications: isSchoolAdmin,
    can_review_details: isSchoolAdmin,
    can_request_clarification: isSchoolAdmin,
    can_recommend_decision: isSchoolAdmin,
    can_approve_stage1: isSchoolAdmin,
    can_view_history: isSchoolAdmin,
    can_manage_academics: isSchoolAdmin,
    can_manage_students: isSchoolAdmin,
  })
  const [activeTab, setActiveTab] = useState(() => {
    if (window.location.search.includes('tab=admissions')) return 'admissions'
    if (isSchoolAdmin) return 'admin-overview'
    return 'queue'
  })"""

assert target_dash_state in dash_code, "target_dash_state not found"
dash_code = dash_code.replace(target_dash_state, replacement_dash_state, 1)

# Add fetch permissions useEffect
target_dash_effect = """  // Fetch school admin metrics if school admin
  useEffect(() => {"""

replacement_dash_effect = """  // Phase 11B: Fetch staff permissions and effective role
  useEffect(() => {
    async function fetchPermissions() {
      if (!token) return
      try {
        const data = await apiGet('/school/staff/me/permissions', token)
        if (data) {
          const r = data.role_id || user?.role || 'school_staff'
          setEffectiveRole(r)
          if (data.permissions) {
            setPermissions(data.permissions)
            // Auto switch to appropriate default tab based on role
            if (r === 'admissions_officer') {
              setActiveTab('admissions')
            } else if (r === 'student_records_officer') {
              setActiveTab('students')
            } else if (r === 'academic_admin') {
              setActiveTab('program-distribution')
            }
          }
        }
      } catch (err) {
        // Fallback gracefully
      }
    }
    fetchPermissions()
  }, [token, user])

  // Fetch school admin metrics if school admin
  useEffect(() => {"""

assert target_dash_effect in dash_code, "target_dash_effect not found"
dash_code = dash_code.replace(target_dash_effect, replacement_dash_effect, 1)

# Update staff header & buttons
target_dash_header = """            <div style={{ display: 'inline-block', background: isSchoolAdmin ? '#fef3c7' : '#dbeafe', color: isSchoolAdmin ? '#b45309' : '#1d4ed8', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
              {isSchoolAdmin ? 'SCHOOL ADMINISTRATOR (PRINCIPAL / HEADMASTER)' : 'SCHOOL VERIFICATION & TEACHING STAFF'}
            </div>
            <h1 style={{ fontSize: '1.75rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
              {isSchoolAdmin ? 'School Administrator Desk' : 'School Verification Desk'}
            </h1>
            <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
              User: <strong>{user?.full_name || user?.email}</strong> · Assigned School ID: <strong style={{ color: '#1a3a6b' }}>{assignedSchoolId}</strong>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            {isSchoolAdmin && (
              <button
                onClick={() => setActiveTab('admin-overview')}
                className={`btn btn--sm ${activeTab === 'admin-overview' ? 'btn--accent' : 'btn--ghost'}`}
              >
                School Overview
              </button>
            )}
            <button
              onClick={() => { setActiveTab('queue'); loadRequests(); }}
              className={`btn btn--sm ${activeTab === 'queue' ? 'btn--primary' : 'btn--ghost'}`}
            >
              Linking Requests ({requests.length})
            </button>
            <button
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
            )}
            <button
              onClick={() => setActiveTab('admissions')}
              className={`btn btn--sm ${activeTab === 'admissions' ? 'btn--primary' : 'btn--ghost'}`}
            >
              📋 Admission Desk
            </button>
            <button
              onClick={() => setActiveTab('program-distribution')}
              className={`btn btn--sm ${activeTab === 'program-distribution' ? 'btn--accent' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              📊 Programme Distribution
            </button>
          </div>"""

replacement_dash_header = """            <div style={{ display: 'inline-block', background: isSchoolAdmin ? '#fef3c7' : effectiveRole === 'admissions_officer' ? '#dbeafe' : effectiveRole === 'academic_admin' ? '#fce7f3' : effectiveRole === 'student_records_officer' ? '#dcfce7' : '#f1f5f9', color: isSchoolAdmin ? '#b45309' : effectiveRole === 'admissions_officer' ? '#1d4ed8' : effectiveRole === 'academic_admin' ? '#9d174d' : effectiveRole === 'student_records_officer' ? '#15803d' : '#334155', fontWeight: 700, padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem' }}>
              {isSchoolAdmin ? 'INSTITUTION ADMINISTRATOR' :
               effectiveRole === 'admissions_officer' ? 'INSTITUTION ADMISSIONS OFFICER' :
               effectiveRole === 'academic_admin' ? 'ACADEMIC ADMINISTRATOR' :
               effectiveRole === 'student_records_officer' ? 'STUDENT RECORDS OFFICER' :
               'GENERAL STAFF MEMBER'}
            </div>
            <h1 style={{ fontSize: '1.75rem', color: '#1a3a6b', margin: '0 0 0.25rem 0' }}>
              {isSchoolAdmin ? 'Institution Administrator Desk' :
               effectiveRole === 'admissions_officer' ? 'Admissions Management Desk' :
               effectiveRole === 'academic_admin' ? 'Academic Administration Desk' :
               effectiveRole === 'student_records_officer' ? 'Student Records Desk' :
               'Staff Verification Desk'}
            </h1>
            <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
              User: <strong>{user?.full_name || user?.email}</strong> · Assigned Institution ID: <strong style={{ color: '#1a3a6b' }}>{assignedSchoolId}</strong> · Role: <strong style={{ textTransform: 'capitalize' }}>{effectiveRole.replace('_', ' ')}</strong>
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {isSchoolAdmin && (
              <button
                onClick={() => setActiveTab('admin-overview')}
                className={`btn btn--sm ${activeTab === 'admin-overview' ? 'btn--accent' : 'btn--ghost'}`}
              >
                School Overview
              </button>
            )}
            {(isSchoolAdmin || permissions.can_manage_students || effectiveRole === 'school_staff') && (
              <button
                onClick={() => { setActiveTab('queue'); loadRequests(); }}
                className={`btn btn--sm ${activeTab === 'queue' ? 'btn--primary' : 'btn--ghost'}`}
              >
                Linking Requests ({requests.length})
              </button>
            )}
            {(isSchoolAdmin || permissions.can_manage_students) && (
              <button
                onClick={() => setActiveTab('students')}
                className={`btn btn--sm ${activeTab === 'students' ? 'btn--primary' : 'btn--ghost'}`}
              >
                Student Roster (Filtered)
              </button>
            )}
            {isSchoolAdmin && (
              <button
                onClick={() => { setActiveTab('staff-mgmt'); loadStaffList(); }}
                className={`btn btn--sm ${activeTab === 'staff-mgmt' ? 'btn--accent' : 'btn--ghost'}`}
              >
                👥 Staff Management
              </button>
            )}
            {(isSchoolAdmin || permissions.can_view_applications) && (
              <button
                onClick={() => setActiveTab('admissions')}
                className={`btn btn--sm ${activeTab === 'admissions' ? 'btn--primary' : 'btn--ghost'}`}
              >
                📋 Admission Desk
              </button>
            )}
            {(isSchoolAdmin || permissions.can_manage_academics) && (
              <button
                onClick={() => setActiveTab('program-distribution')}
                className={`btn btn--sm ${activeTab === 'program-distribution' ? 'btn--accent' : 'btn--ghost'}`}
                style={{ fontWeight: 600 }}
              >
                📊 Programme Distribution
              </button>
            )}
          </div>"""

assert target_dash_header in dash_code, "target_dash_header not found"
dash_code = dash_code.replace(target_dash_header, replacement_dash_header, 1)

# Pass permissions into AdmissionDeskTab
target_dash_tab = """        {activeTab === 'admissions' && (
          <AdmissionDeskTab schoolId={assignedSchoolId} />
        )}"""

replacement_dash_tab = """        {activeTab === 'admissions' && (
          <AdmissionDeskTab
            schoolId={assignedSchoolId}
            permissions={permissions}
            effectiveRole={effectiveRole}
          />
        )}"""

assert target_dash_tab in dash_code, "target_dash_tab not found"
dash_code = dash_code.replace(target_dash_tab, replacement_dash_tab, 1)

with open(dashboard_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(dash_code)
print("StaffDashboard.jsx updated successfully!")

# --- 2. UPDATE AdmissionDeskTab.jsx ---
with open(desk_file, "r", encoding="utf-8") as f:
    desk_code = f.read()

# Update signature
target_desk_sig = """export default function AdmissionDeskTab({ schoolId }) {"""
replacement_desk_sig = """export default function AdmissionDeskTab({ schoolId, permissions = {}, effectiveRole = '' }) {"""

assert target_desk_sig in desk_code, "target_desk_sig not found"
desk_code = desk_code.replace(target_desk_sig, replacement_desk_sig, 1)

# Add recommendationDecision state
target_desk_state = """  // Action Form States inside Modal
  const [actionType, setActionType] = useState('none') // 'none' | 'review' | 'clarify' | 'approve' | 'reject'"""

replacement_desk_state = """  // Action Form States inside Modal
  const [actionType, setActionType] = useState('none') // 'none' | 'review' | 'clarify' | 'approve' | 'reject' | 'recommend'
  const [recommendationDecision, setRecommendationDecision] = useState('recommend_approval')"""

assert target_desk_state in desk_code, "target_desk_state not found"
desk_code = desk_code.replace(target_desk_state, replacement_desk_state, 1)

# Update handleExecuteAction
target_desk_action = """      if (actionType === 'review') {"""

replacement_desk_action = """      if (actionType === 'recommend') {
        if (!actionNotes.trim()) {
          throw new Error('Please provide notes or rationale justifying your recommendation.')
        }
        await apiPost(`/school/admissions/${activeApp.application_id}/recommend`, {
          recommendation: recommendationDecision,
          notes: actionNotes.trim()
        })
        setSuccess(`Official recommendation submitted for ${activeApp.application_id}.`)
      } else if (actionType === 'review') {"""

assert target_desk_action in desk_code, "target_desk_action not found"
desk_code = desk_code.replace(target_desk_action, replacement_desk_action, 1)

# Update toolbar buttons
target_desk_btns = """                  <button
                    onClick={() => { setActionType('approve'); setActionError(null); }}
                    style={{
                      background: actionType === 'approve' ? '#027A48' : '#ECFDF3',
                      color: actionType === 'approve' ? '#ffffff' : '#027A48',
                      border: '1px solid #A6F4C5',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    ✓ Approve Stage 1
                  </button>"""

replacement_desk_btns = """                  {(permissions.can_recommend_decision ?? true) && (
                    <button
                      onClick={() => { setActionType('recommend'); setActionError(null); }}
                      style={{
                        background: actionType === 'recommend' ? '#026AA2' : '#F0F9FF',
                        color: actionType === 'recommend' ? '#ffffff' : '#026AA2',
                        border: '1px solid #B2DDFF',
                        padding: '0.5rem 1rem',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '0.85rem',
                        cursor: 'pointer'
                      }}
                    >
                      👍 Recommend Decision to Admin
                    </button>
                  )}

                  <button
                    onClick={() => { setActionType('approve'); setActionError(null); }}
                    style={{
                      background: actionType === 'approve' ? '#027A48' : '#ECFDF3',
                      color: actionType === 'approve' ? '#ffffff' : '#027A48',
                      border: '1px solid #A6F4C5',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    ✓ Approve Stage 1 {permissions.can_approve_stage1 === false ? '(Admin Authorization Required)' : ''}
                  </button>"""

assert target_desk_btns in desk_code, "target_desk_btns not found"
desk_code = desk_code.replace(target_desk_btns, replacement_desk_btns, 1)

# Add recommend panel and approve guard
target_desk_approve_panel = """              {actionType === 'approve' && (
                <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#027A48', marginBottom: '0.35rem' }}>
                    Stage 1 Approval Note
                  </label>"""

replacement_desk_approve_panel = """              {actionType === 'recommend' && (
                <div style={{ background: '#F0F9FF', border: '1px solid #B2DDFF', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#026AA2', marginBottom: '0.35rem' }}>
                    Official Staff Recommendation *
                  </label>
                  <select
                    value={recommendationDecision}
                    onChange={(e) => setRecommendationDecision(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #B2DDFF', fontSize: '0.85rem', marginBottom: '0.75rem', background: '#FFFFFF' }}
                  >
                    <option value="recommend_approval">Recommend Stage 1 Approval</option>
                    <option value="recommend_rejection">Recommend Application Rejection</option>
                    <option value="request_clarification">Recommend Requesting Parent Clarification</option>
                  </select>

                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#026AA2', marginBottom: '0.35rem' }}>
                    Institutional Rationale & Evaluation Notes * (Mandatory)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Verified eligibility and standard capacity. Recommended for Stage 1 approval."
                    value={actionNotes}
                    onChange={(e) => setActionNotes(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #B2DDFF', fontSize: '0.85rem', marginBottom: '0.75rem' }}
                  />

                  <button
                    onClick={handleExecuteAction}
                    disabled={actionSubmitting}
                    style={{ background: '#026AA2', color: '#ffffff', border: 'none', padding: '0.5rem 1.25rem', borderRadius: '6px', fontWeight: 700, fontSize: '0.85rem', cursor: 'pointer' }}
                  >
                    {actionSubmitting ? 'Submitting...' : 'Submit Recommendation to Administrator'}
                  </button>
                </div>
              )}

              {actionType === 'approve' && (
                <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
                  {permissions.can_approve_stage1 === false && (
                    <div style={{ background: '#FEF3F2', border: '1px solid #FECDCA', color: '#B42318', padding: '0.65rem', borderRadius: '6px', marginBottom: '0.75rem', fontSize: '0.825rem' }}>
                      ⚠️ <strong>Unauthorized:</strong> Your account does not have explicit Stage 1 approval authority (<code>can_approve_stage1</code>). Please use <strong>Recommend Decision to Admin</strong> to forward your recommendation.
                    </div>
                  )}
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#027A48', marginBottom: '0.35rem' }}>
                    Stage 1 Approval Note
                  </label>"""

assert target_desk_approve_panel in desk_code, "target_desk_approve_panel not found"
desk_code = desk_code.replace(target_desk_approve_panel, replacement_desk_approve_panel, 1)

# Guard the approve button inside the panel if can_approve_stage1 is false
target_desk_approve_btn = """                  <button
                    onClick={handleExecuteAction}
                    disabled={actionSubmitting}
                    style={{ background: '#027A48', color: '#ffffff', border: 'none', padding: '0.5rem 1.25rem', borderRadius: '6px', fontWeight: 700, fontSize: '0.85rem', cursor: 'pointer' }}
                  >
                    {actionSubmitting ? 'Processing...' : 'Confirm Stage 1 Approval ✓'}
                  </button>"""

replacement_desk_approve_btn = """                  <button
                    onClick={handleExecuteAction}
                    disabled={actionSubmitting || permissions.can_approve_stage1 === false}
                    style={{
                      background: permissions.can_approve_stage1 === false ? '#98A2B3' : '#027A48',
                      color: '#ffffff',
                      border: 'none',
                      padding: '0.5rem 1.25rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: permissions.can_approve_stage1 === false ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {permissions.can_approve_stage1 === false ? 'Approval Restricted to Admin' : actionSubmitting ? 'Processing...' : 'Confirm Stage 1 Approval ✓'}
                  </button>"""

assert target_desk_approve_btn in desk_code, "target_desk_approve_btn not found"
desk_code = desk_code.replace(target_desk_approve_btn, replacement_desk_approve_btn, 1)

with open(desk_file, "w", encoding="utf-8", newline="\n") as f:
    f.write(desk_code)
print("AdmissionDeskTab.jsx updated successfully!")
