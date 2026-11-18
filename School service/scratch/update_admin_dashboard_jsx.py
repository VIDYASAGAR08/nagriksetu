import os

file_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Target around line 700
target_top = """        {/* =================================================================
            ADMISSION APPLICATION MANAGEMENT SECTION
            ================================================================= */}
        <div style={{"""

replacement_top = """        {/* =================================================================
            PRIMARY SECTION TABS: APPLICATIONS vs STAFF MANAGEMENT
            ================================================================= */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '2px solid #E2E8F0', paddingBottom: '0.25rem' }}>
          <button
            onClick={() => setMainTab('applications')}
            style={{
              padding: '0.75rem 1.4rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              border: 'none',
              background: 'none',
              borderBottom: mainTab === 'applications' ? '3px solid #155EEF' : '3px solid transparent',
              color: mainTab === 'applications' ? '#155EEF' : '#667085',
              cursor: 'pointer',
              marginBottom: '-0.35rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease'
            }}
          >
            📋 Admission Applications
            <span style={{
              background: mainTab === 'applications' ? '#EFF4FF' : '#F2F4F7',
              color: mainTab === 'applications' ? '#155EEF' : '#475467',
              padding: '0.15rem 0.55rem',
              borderRadius: '10px',
              fontSize: '0.75rem',
              fontWeight: 700
            }}>
              {overview?.total_applications ?? applications.length}
            </span>
          </button>

          <button
            onClick={() => setMainTab('staff')}
            style={{
              padding: '0.75rem 1.4rem',
              fontSize: '0.95rem',
              fontWeight: 700,
              border: 'none',
              background: 'none',
              borderBottom: mainTab === 'staff' ? '3px solid #155EEF' : '3px solid transparent',
              color: mainTab === 'staff' ? '#155EEF' : '#667085',
              cursor: 'pointer',
              marginBottom: '-0.35rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: 'all 0.2s ease'
            }}
          >
            👥 Staff Management & Permissions
            <span style={{
              background: mainTab === 'staff' ? '#EFF4FF' : '#F2F4F7',
              color: mainTab === 'staff' ? '#155EEF' : '#475467',
              padding: '0.15rem 0.55rem',
              borderRadius: '10px',
              fontSize: '0.75rem',
              fontWeight: 700
            }}>
              {staffList.length}
            </span>
          </button>
        </div>

        {resetFeedback && (
          <div style={{ marginBottom: '1.25rem' }}>
            <Alert
              type={resetFeedback.type || 'info'}
              title={resetFeedback.title || 'Notification'}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ wordBreak: 'break-all' }}>{resetFeedback.message}</span>
                <button
                  onClick={() => setResetFeedback(null)}
                  style={{
                    background: 'none',
                    border: 'none',
                    fontWeight: 700,
                    cursor: 'pointer',
                    color: 'inherit',
                    marginLeft: '1rem',
                    fontSize: '1rem'
                  }}
                >
                  ✕
                </button>
              </div>
            </Alert>
          </div>
        )}

        {/* =================================================================
            TAB 1: ADMISSION APPLICATION MANAGEMENT SECTION
            ================================================================= */}
        {mainTab === 'applications' && (
        <div style={{"""

# 2. Target around line 908
target_mid = """              </table>
            </div>
          )}
        </div>

        {/* =================================================================
            APPLICATION DETAIL & REVIEW MODAL
            ================================================================= */}"""

replacement_mid = """              </table>
            </div>
          )}
        </div>
        )}

        {/* =================================================================
            TAB 2: STAFF MANAGEMENT & ROLE-BASED PERMISSIONS
            ================================================================= */}
        {mainTab === 'staff' && (
          <div style={{
            background: '#FFFFFF',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '1.5rem',
            boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
          }}>
            {/* Staff Section Header */}
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
            </div>

            {/* Staff KPI Summary Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#102B46' }}>
                  {loadingStaff ? '...' : staffList.length}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Total Staff Roster</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Assigned to {institutionId}</div>
              </div>

              <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#12B76A' }}>
                  {loadingStaff ? '...' : staffList.filter(s => s.status === 'active' && s.is_active).length}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Active Accounts</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Operational access</div>
              </div>

              <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F79009' }}>
                  {loadingStaff ? '...' : staffList.filter(s => s.invitation_status === 'pending').length}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Pending Invitations</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Token valid 72 hrs</div>
              </div>

              <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '10px', padding: '1rem', textAlign: 'center' }}>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#F04438' }}>
                  {loadingStaff ? '...' : staffList.filter(s => s.status === 'suspended' || !s.is_active).length}
                </div>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475467', marginTop: '0.2rem' }}>Suspended Accounts</div>
                <div style={{ fontSize: '0.7rem', color: '#98A2B3' }}>Login revoking active</div>
              </div>
            </div>

            {/* Staff Search and Filters */}
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.75rem',
              alignItems: 'center',
              padding: '1rem',
              background: '#F8F9FA',
              borderRadius: '8px',
              marginBottom: '1.25rem'
            }}>
              <div style={{ flex: '1 1 260px' }}>
                <input
                  type="text"
                  placeholder="Search staff by name or email address..."
                  value={staffSearch}
                  onChange={(e) => setStaffSearch(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.55rem 0.8rem',
                    border: '1px solid #D0D5DD',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    boxSizing: 'border-box'
                  }}
                />
              </div>

              <select
                value={staffRoleFilter}
                onChange={(e) => setStaffRoleFilter(e.target.value)}
                style={{
                  padding: '0.55rem 0.8rem',
                  border: '1px solid #D0D5DD',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  color: '#102B46',
                  background: '#FFFFFF'
                }}
              >
                <option value="all">All Roles</option>
                <option value="admissions_officer">Admissions Officer</option>
                <option value="academic_admin">Academic Administrator</option>
                <option value="student_records_officer">Student Records Officer</option>
                <option value="school_staff">General Staff Member</option>
              </select>

              <select
                value={staffStatusFilter}
                onChange={(e) => setStaffStatusFilter(e.target.value)}
                style={{
                  padding: '0.55rem 0.8rem',
                  border: '1px solid #D0D5DD',
                  borderRadius: '6px',
                  fontSize: '0.85rem',
                  color: '#102B46',
                  background: '#FFFFFF'
                }}
              >
                <option value="all">All Statuses</option>
                <option value="active">Active Accounts</option>
                <option value="pending">Pending Invitations</option>
                <option value="suspended">Suspended Accounts</option>
              </select>

              {(staffSearch || staffRoleFilter !== 'all' || staffStatusFilter !== 'all') && (
                <button
                  onClick={() => {
                    setStaffSearch('')
                    setStaffRoleFilter('all')
                    setStaffStatusFilter('all')
                  }}
                  style={{
                    padding: '0.55rem 0.85rem',
                    background: '#FFFFFF',
                    border: '1px solid #D0D5DD',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    color: '#667085',
                    cursor: 'pointer'
                  }}
                >
                  Reset Filters
                </button>
              )}
            </div>

            {staffError && <Alert type="error" title="Staff Management Notice" style={{ marginBottom: '1.25rem' }}>{staffError}</Alert>}

            {/* Staff Table */}
            {loadingStaff ? (
              <div style={{ textAlign: 'center', padding: '3.5rem 0' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.75rem', color: '#667085', fontSize: '0.9rem' }}>Retrieving institution staff records...</p>
              </div>
            ) : filteredStaff.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '3rem 1rem', background: '#F8F9FA', borderRadius: '8px' }}>
                <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>👥</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.35rem 0' }}>No Staff Members Found</h3>
                <p style={{ color: '#667085', fontSize: '0.85rem', margin: '0 0 1rem 0' }}>
                  {staffSearch || staffRoleFilter !== 'all' || staffStatusFilter !== 'all'
                    ? 'No staff members match the selected search criteria.'
                    : 'No staff members have been invited for this institution yet.'}
                </p>
                <button
                  onClick={() => {
                    setShowInviteModal(true)
                    setInviteResult(null)
                    setInviteError('')
                  }}
                  className="btn btn--primary btn--sm"
                >
                  ➕ Invite First Staff Member
                </button>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#F8F9FA', borderBottom: '2px solid #EAECF0', color: '#475467', fontWeight: 700 }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Staff Member</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Assigned Role</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Account Status</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Invitation Status</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Key Permissions</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Last Login</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredStaff.map((staff) => {
                      const isSuspended = staff.status === 'suspended' || !staff.is_active
                      const perms = staff.permissions || {}
                      return (
                        <tr key={staff.user_id} style={{ borderBottom: '1px solid #EAECF0' }}>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ fontWeight: 700, color: '#102B46' }}>{staff.full_name || 'Staff User'}</div>
                            <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.15rem' }}>{staff.email}</div>
                            {staff.phone && <div style={{ fontSize: '0.72rem', color: '#98A2B3' }}>📞 {staff.phone}</div>}
                          </td>

                          <td style={{ padding: '0.85rem 1rem' }}>
                            <span style={{
                              display: 'inline-block',
                              padding: '0.25rem 0.6rem',
                              borderRadius: '6px',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              background: staff.role_id === 'admissions_officer' ? '#EFF4FF' :
                                          staff.role_id === 'academic_admin' ? '#FDF2FA' :
                                          staff.role_id === 'student_records_officer' ? '#ECFDF3' : '#F2F4F7',
                              color: staff.role_id === 'admissions_officer' ? '#155EEF' :
                                     staff.role_id === 'academic_admin' ? '#C11574' :
                                     staff.role_id === 'student_records_officer' ? '#027A48' : '#344054'
                            }}>
                              {staff.role_id === 'admissions_officer' ? 'Admissions Officer' :
                               staff.role_id === 'academic_admin' ? 'Academic Administrator' :
                               staff.role_id === 'student_records_officer' ? 'Student Records Officer' : 'General Staff'}
                            </span>
                          </td>

                          <td style={{ padding: '0.85rem 1rem' }}>
                            <span style={{
                              padding: '0.2rem 0.55rem',
                              borderRadius: '12px',
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              background: isSuspended ? '#FEF3F2' : '#ECFDF3',
                              color: isSuspended ? '#B42318' : '#027A48',
                              border: `1px solid ${isSuspended ? '#FECDCA' : '#A6F4C5'}`
                            }}>
                              {isSuspended ? 'SUSPENDED' : 'ACTIVE'}
                            </span>
                          </td>

                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', flexWrap: 'wrap' }}>
                              <span style={{
                                padding: '0.2rem 0.5rem',
                                borderRadius: '12px',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                                background: staff.invitation_status === 'accepted' ? '#EFF8FF' :
                                            staff.invitation_status === 'pending' ? '#FFFAEB' : '#F8F9FA',
                                color: staff.invitation_status === 'accepted' ? '#175CD3' :
                                       staff.invitation_status === 'pending' ? '#B54708' : '#475467'
                              }}>
                                {staff.invitation_status?.toUpperCase() || 'ACCEPTED'}
                              </span>

                              {staff.invitation_status === 'pending' && (
                                <button
                                  onClick={() => handleResendInvitation(staff.user_id)}
                                  title="Issue new 72-hour cryptographic token"
                                  style={{
                                    background: '#FFFFFF',
                                    border: '1px solid #D0D5DD',
                                    borderRadius: '4px',
                                    padding: '0.2rem 0.45rem',
                                    fontSize: '0.7rem',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                    color: '#155EEF'
                                  }}
                                >
                                  🔄 Resend Token
                                </button>
                              )}
                            </div>
                          </td>

                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.25rem' }}>
                              {perms.can_view_applications && (
                                <span style={{ background: '#EFF4FF', color: '#155EEF', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 600 }}>
                                  View Apps
                                </span>
                              )}
                              {perms.can_recommend_decision && (
                                <span style={{ background: '#F0F9FF', color: '#026AA2', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 600 }}>
                                  Recommend
                                </span>
                              )}
                              {perms.can_approve_stage1 ? (
                                <span style={{ background: '#FEF08A', color: '#854D0E', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 800 }}>
                                  ⭐ Approve Stage 1
                                </span>
                              ) : null}
                              {perms.can_manage_academics && (
                                <span style={{ background: '#FDF2FA', color: '#C11574', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 600 }}>
                                  Academics
                                </span>
                              )}
                              {perms.can_manage_students && (
                                <span style={{ background: '#ECFDF3', color: '#027A48', fontSize: '0.7rem', padding: '0.1rem 0.4rem', borderRadius: '4px', fontWeight: 600 }}>
                                  Students
                                </span>
                              )}
                            </div>
                          </td>

                          <td style={{ padding: '0.85rem 1rem', color: '#667085', fontSize: '0.78rem' }}>
                            {staff.last_login ? new Date(staff.last_login).toLocaleDateString() : 'Never'}
                          </td>

                          <td style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>
                            <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                              <button
                                onClick={() => handleOpenStaffModal(staff)}
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
                                ⚙️ Permissions
                              </button>

                              <button
                                onClick={() => handleToggleSuspendStaff(staff)}
                                style={{
                                  background: isSuspended ? '#ECFDF3' : '#FEF3F2',
                                  color: isSuspended ? '#027A48' : '#B42318',
                                  border: `1px solid ${isSuspended ? '#A6F4C5' : '#FECDCA'}`,
                                  borderRadius: '4px',
                                  padding: '0.35rem 0.65rem',
                                  fontSize: '0.75rem',
                                  fontWeight: 700,
                                  cursor: 'pointer'
                                }}
                              >
                                {isSuspended ? 'Reactivate' : 'Suspend'}
                              </button>

                              <button
                                onClick={() => handleAdminResetPassword(staff.user_id)}
                                title="Issue password reset link"
                                style={{
                                  background: '#F8F9FA',
                                  color: '#344054',
                                  border: '1px solid #D0D5DD',
                                  borderRadius: '4px',
                                  padding: '0.35rem 0.55rem',
                                  fontSize: '0.75rem',
                                  fontWeight: 600,
                                  cursor: 'pointer'
                                }}
                              >
                                🔑 Reset
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* =================================================================
            APPLICATION DETAIL & REVIEW MODAL
            ================================================================= */}"""

# 3. Target around line 1406
target_bottom = """        {selectedApp && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(16, 43, 70, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
            zIndex: 9999,
            backdropFilter: 'blur(3px)'
          }}>"""

replacement_bottom = """        {/* =================================================================
            INVITE STAFF MODAL
            ================================================================= */}
        {showInviteModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(16, 43, 70, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
            zIndex: 9999,
            backdropFilter: 'blur(3px)'
          }}>
            <div style={{
              background: '#FFFFFF',
              borderRadius: '12px',
              maxWidth: '650px',
              width: '100%',
              maxHeight: '92vh',
              overflowY: 'auto',
              boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
            }}>
              <div style={{
                background: '#102B46',
                color: '#FFFFFF',
                padding: '1.25rem 1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTopLeftRadius: '12px',
                borderTopRightRadius: '12px'
              }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#98A2B3', textTransform: 'uppercase', fontWeight: 700 }}>
                    Staff Onboarding Portal
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, marginTop: '0.2rem' }}>
                    Invite Staff Member to {institutionId}
                  </div>
                </div>
                <button
                  onClick={() => setShowInviteModal(false)}
                  style={{ background: 'none', border: 'none', color: '#FFFFFF', fontSize: '1.2rem', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              <div style={{ padding: '1.5rem' }}>
                {inviteError && <Alert type="error" title="Invitation Error" style={{ marginBottom: '1.25rem' }}>{inviteError}</Alert>}

                {inviteResult ? (
                  <div>
                    <Alert type="success" title="Invitation Generated Successfully!" style={{ marginBottom: '1.25rem' }}>
                      Single-use cryptographic invitation issued for <strong>{inviteResult.email}</strong>. Token expires in 72 hours.
                    </Alert>

                    <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', marginBottom: '1.5rem' }}>
                      <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: '#475467', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                        Cryptographic Invitation URL:
                      </label>
                      <input
                        type="text"
                        readOnly
                        value={`${window.location.origin}${inviteResult.invitation_url}`}
                        style={{
                          width: '100%',
                          padding: '0.55rem',
                          borderRadius: '6px',
                          border: '1px solid #D0D5DD',
                          fontFamily: 'monospace',
                          fontSize: '0.8rem',
                          background: '#FFFFFF',
                          marginBottom: '0.75rem'
                        }}
                      />
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText(`${window.location.origin}${inviteResult.invitation_url}`)
                          alert('Invitation link copied to clipboard!')
                        }}
                        className="btn btn--secondary btn--sm"
                      >
                        📋 Copy Invitation Link
                      </button>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => setShowInviteModal(false)}
                        className="btn btn--primary"
                      >
                        Done
                      </button>
                    </div>
                  </div>
                ) : (
                  <form onSubmit={handleInviteStaff}>
                    <div style={{ marginBottom: '1rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                        Full Legal Name *
                      </label>
                      <input
                        type="text"
                        required
                        placeholder="e.g. Ramesh Kulkarni"
                        value={inviteFullName}
                        onChange={(e) => setInviteFullName(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                          Official Work Email *
                        </label>
                        <input
                          type="email"
                          required
                          placeholder="e.g. ramesh@institution.edu"
                          value={inviteEmail}
                          onChange={(e) => setInviteEmail(e.target.value)}
                          style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                        />
                      </div>

                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                          Mobile Phone (Optional)
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. 9876543210"
                          value={invitePhone}
                          onChange={(e) => setInvitePhone(e.target.value)}
                          style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                        />
                      </div>
                    </div>

                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                        Staff Role Assignment *
                      </label>
                      <select
                        value={inviteRole}
                        onChange={(e) => {
                          const r = e.target.value
                          setInviteRole(r)
                          if (r === 'admissions_officer') {
                            setInviteCustomPerms({
                              can_view_applications: true,
                              can_review_details: true,
                              can_request_clarification: true,
                              can_recommend_decision: true,
                              can_approve_stage1: false,
                              can_view_history: true,
                              can_manage_academics: false,
                              can_manage_students: false,
                            })
                          } else if (r === 'academic_admin') {
                            setInviteCustomPerms({
                              can_view_applications: false,
                              can_review_details: false,
                              can_request_clarification: false,
                              can_recommend_decision: false,
                              can_approve_stage1: false,
                              can_view_history: false,
                              can_manage_academics: true,
                              can_manage_students: false,
                            })
                          } else if (r === 'student_records_officer') {
                            setInviteCustomPerms({
                              can_view_applications: false,
                              can_review_details: false,
                              can_request_clarification: false,
                              can_recommend_decision: false,
                              can_approve_stage1: false,
                              can_view_history: false,
                              can_manage_academics: false,
                              can_manage_students: true,
                            })
                          } else {
                            setInviteCustomPerms({
                              can_view_applications: false,
                              can_review_details: false,
                              can_request_clarification: false,
                              can_recommend_decision: false,
                              can_approve_stage1: false,
                              can_view_history: false,
                              can_manage_academics: false,
                              can_manage_students: false,
                            })
                          }
                        }}
                        style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem', background: '#FFFFFF' }}
                      >
                        <option value="admissions_officer">Admissions Officer (Review, Clarify, Recommend)</option>
                        <option value="academic_admin">Academic Administrator (Streams & Programmes)</option>
                        <option value="student_records_officer">Student Records Officer (Roster & Records)</option>
                        <option value="general_staff">General Staff Member (Read-only)</option>
                      </select>
                    </div>

                    <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#344054', marginBottom: '0.6rem' }}>
                        Default Permissions for this Role:
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.8rem' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475467' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_view_applications}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_view_applications: e.target.checked })}
                          />
                          View Applications
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475467' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_review_details}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_review_details: e.target.checked })}
                          />
                          Review Details
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475467' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_request_clarification}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_request_clarification: e.target.checked })}
                          />
                          Request Clarification
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475467' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_recommend_decision}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_recommend_decision: e.target.checked })}
                          />
                          Recommend Decision
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475467' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_manage_academics}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_manage_academics: e.target.checked })}
                          />
                          Manage Academics
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#475467' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_manage_students}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_manage_students: e.target.checked })}
                          />
                          Manage Student Records
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#854D0E', gridColumn: 'span 2', marginTop: '0.25rem' }}>
                          <input
                            type="checkbox"
                            checked={!!inviteCustomPerms.can_approve_stage1}
                            onChange={(e) => setInviteCustomPerms({ ...inviteCustomPerms, can_approve_stage1: e.target.checked })}
                          />
                          ⭐ Explicit Authority: Approve Stage 1 Admissions
                        </label>
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                      <button
                        type="button"
                        onClick={() => setShowInviteModal(false)}
                        className="btn btn--secondary"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={submittingInvite}
                        className="btn btn--primary"
                      >
                        {submittingInvite ? 'Dispatching Invitation...' : 'Dispatch Invitation →'}
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </div>
          </div>
        )}

        {/* =================================================================
            STAFF PERMISSIONS & ACTIVITY PROFILE MODAL
            ================================================================= */}
        {selectedStaff && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(16, 43, 70, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
            zIndex: 9999,
            backdropFilter: 'blur(3px)'
          }}>
            <div style={{
              background: '#FFFFFF',
              borderRadius: '12px',
              maxWidth: '750px',
              width: '100%',
              maxHeight: '92vh',
              overflowY: 'auto',
              boxShadow: '0 20px 40px rgba(0,0,0,0.2)',
              display: 'flex',
              flexDirection: 'column'
            }}>
              {/* Modal Header */}
              <div style={{
                background: '#102B46',
                color: '#FFFFFF',
                padding: '1.25rem 1.5rem',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTopLeftRadius: '12px',
                borderTopRightRadius: '12px'
              }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#98A2B3', textTransform: 'uppercase', fontWeight: 700 }}>
                    Staff Role & Permission Governance
                  </div>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, marginTop: '0.2rem' }}>
                    {selectedStaff.full_name || selectedStaff.email}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#E0EAFF', marginTop: '0.15rem' }}>
                    User ID: {selectedStaff.user_id} · Institution: {institutionId}
                  </div>
                </div>

                <button
                  onClick={() => setSelectedStaff(null)}
                  style={{ background: 'none', border: 'none', color: '#FFFFFF', fontSize: '1.2rem', cursor: 'pointer' }}
                >
                  ✕
                </button>
              </div>

              {/* Subtabs */}
              <div style={{ display: 'flex', background: '#F8F9FA', borderBottom: '1px solid #EAECF0', padding: '0 1.5rem' }}>
                <button
                  onClick={() => setStaffModalTab('permissions')}
                  style={{
                    padding: '0.75rem 1rem',
                    border: 'none',
                    background: 'none',
                    borderBottom: staffModalTab === 'permissions' ? '3px solid #155EEF' : '3px solid transparent',
                    color: staffModalTab === 'permissions' ? '#155EEF' : '#667085',
                    fontWeight: 700,
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  ⚙️ Role & Permission Matrix
                </button>

                <button
                  onClick={() => setStaffModalTab('activity')}
                  style={{
                    padding: '0.75rem 1rem',
                    border: 'none',
                    background: 'none',
                    borderBottom: staffModalTab === 'activity' ? '3px solid #155EEF' : '3px solid transparent',
                    color: staffModalTab === 'activity' ? '#155EEF' : '#667085',
                    fontWeight: 700,
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  📜 Audit Trail & Activity Log ({staffActivity.length})
                </button>
              </div>

              <div style={{ padding: '1.5rem', flex: 1 }}>
                {permsFeedback && (
                  <Alert
                    type={permsFeedback.type}
                    title={permsFeedback.type === 'success' ? 'Update Successful' : 'Action Failed'}
                    style={{ marginBottom: '1.25rem' }}
                  >
                    {permsFeedback.message}
                  </Alert>
                )}

                {staffModalTab === 'permissions' ? (
                  <form onSubmit={handleSavePermissions}>
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                        Assigned Staff Role
                      </label>
                      <select
                        value={editRole}
                        onChange={(e) => handleModalRoleChange(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem', background: '#FFFFFF' }}
                      >
                        <option value="admissions_officer">Admissions Officer</option>
                        <option value="academic_admin">Academic Administrator</option>
                        <option value="student_records_officer">Student Records Officer</option>
                        <option value="school_staff">General Staff Member</option>
                      </select>
                      <span style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.25rem', display: 'block' }}>
                        Selecting a role re-populates recommended default permissions below. You can customize them freely.
                      </span>
                    </div>

                    <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.25rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.75rem' }}>
                        Admission Management Permissions
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_view_applications}
                            onChange={(e) => setEditPerms({ ...editPerms, can_view_applications: e.target.checked })}
                          />
                          <span>View Applications</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_review_details}
                            onChange={(e) => setEditPerms({ ...editPerms, can_review_details: e.target.checked })}
                          />
                          <span>Review Application Details</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_request_clarification}
                            onChange={(e) => setEditPerms({ ...editPerms, can_request_clarification: e.target.checked })}
                          />
                          <span>Request Clarification</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_recommend_decision}
                            onChange={(e) => setEditPerms({ ...editPerms, can_recommend_decision: e.target.checked })}
                          />
                          <span>Recommend Decision</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_view_history}
                            onChange={(e) => setEditPerms({ ...editPerms, can_view_history: e.target.checked })}
                          />
                          <span>View Audit History</span>
                        </label>
                      </div>

                      <div style={{ marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid #E2E8F0' }}>
                        <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', color: '#854D0E', background: '#FEF08A', padding: '0.75rem', borderRadius: '6px' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_approve_stage1}
                            onChange={(e) => setEditPerms({ ...editPerms, can_approve_stage1: e.target.checked })}
                            style={{ marginTop: '0.15rem' }}
                          />
                          <div>
                            <strong style={{ display: 'block', fontSize: '0.85rem' }}>Authorize Binding Stage 1 Approval (can_approve_stage1)</strong>
                            <span style={{ fontSize: '0.75rem' }}>
                              Enables this staff member to approve preliminary admissions directly without administrator sign-off. Restricted by default.
                            </span>
                          </div>
                        </label>
                      </div>
                    </div>

                    <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#102B46', marginBottom: '0.75rem' }}>
                        Academic & Student Record Permissions
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_manage_academics}
                            onChange={(e) => setEditPerms({ ...editPerms, can_manage_academics: e.target.checked })}
                          />
                          <span>Manage Academic Programmes</span>
                        </label>

                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#344054' }}>
                          <input
                            type="checkbox"
                            checked={!!editPerms.can_manage_students}
                            onChange={(e) => setEditPerms({ ...editPerms, can_manage_students: e.target.checked })}
                          />
                          <span>Access Student Directory & Rosters</span>
                        </label>
                      </div>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                      <button
                        type="button"
                        onClick={() => setSelectedStaff(null)}
                        className="btn btn--secondary"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={updatingPerms}
                        className="btn btn--primary"
                      >
                        {updatingPerms ? 'Saving Changes...' : 'Save Permissions'}
                      </button>
                    </div>
                  </form>
                ) : (
                  <div>
                    {loadingActivity ? (
                      <div style={{ textAlign: 'center', padding: '2rem' }}>
                        <LoadingSpinner />
                        <p style={{ marginTop: '0.5rem', color: '#667085', fontSize: '0.85rem' }}>Loading activity audit log...</p>
                      </div>
                    ) : staffActivity.length === 0 ? (
                      <div style={{ textAlign: 'center', padding: '2.5rem', background: '#F8F9FA', borderRadius: '8px' }}>
                        <div style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>📜</div>
                        <div style={{ fontWeight: 700, color: '#102B46' }}>No Recorded Actions</div>
                        <div style={{ fontSize: '0.8rem', color: '#667085', marginTop: '0.2rem' }}>
                          This staff member has not performed any auditable admission or system transitions yet.
                        </div>
                      </div>
                    ) : (
                      <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem' }}>
                          <thead>
                            <tr style={{ background: '#F8F9FA', borderBottom: '2px solid #EAECF0', textAlign: 'left', color: '#475467' }}>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Timestamp</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Action Type</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Target Reference</th>
                              <th style={{ padding: '0.5rem 0.75rem' }}>Details / Note</th>
                            </tr>
                          </thead>
                          <tbody>
                            {staffActivity.map((act, idx) => (
                              <tr key={idx} style={{ borderBottom: '1px solid #EAECF0' }}>
                                <td style={{ padding: '0.55rem 0.75rem', color: '#667085', whiteSpace: 'nowrap' }}>
                                  {act.timestamp ? new Date(act.timestamp).toLocaleString() : 'N/A'}
                                </td>
                                <td style={{ padding: '0.55rem 0.75rem' }}>
                                  <span style={{
                                    padding: '0.15rem 0.45rem',
                                    borderRadius: '4px',
                                    fontSize: '0.72rem',
                                    fontWeight: 700,
                                    background: '#EFF4FF',
                                    color: '#155EEF'
                                  }}>
                                    {act.action_type}
                                  </span>
                                </td>
                                <td style={{ padding: '0.55rem 0.75rem', fontFamily: 'monospace', color: '#102B46' }}>
                                  {act.target_reference || act.target_id || '-'}
                                </td>
                                <td style={{ padding: '0.55rem 0.75rem', color: '#344054' }}>
                                  {act.details || act.note || '-'}
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
            </div>
          </div>
        )}

        {selectedApp && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(16, 43, 70, 0.65)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '1rem',
            zIndex: 9999,
            backdropFilter: 'blur(3px)'
          }}>"""

assert target_top in content, "target_top not found"
content = content.replace(target_top, replacement_top, 1)

assert target_mid in content, "target_mid not found"
content = content.replace(target_mid, replacement_mid, 1)

assert target_bottom in content, "target_bottom not found"
content = content.replace(target_bottom, replacement_bottom, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("InstitutionAdminDashboard.jsx updated successfully!")
