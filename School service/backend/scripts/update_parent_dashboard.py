import re

path = r"C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx"
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Normalize CRLF to LF
text = text.replace('\r\n', '\n')

# 1. Add Stage2AdmissionModal import
if "import Stage2AdmissionModal" not in text:
    text = text.replace(
        "import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'\n",
        "import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'\nimport Stage2AdmissionModal from '../../components/admissions/Stage2AdmissionModal.jsx'\n"
    )

# 2. Add state
if "const [selectedStage2AppId, setSelectedStage2AppId] = useState(null)" not in text:
    text = text.replace(
        "  const [replySubmittingId, setReplySubmittingId] = useState(null)\n",
        "  const [replySubmittingId, setReplySubmittingId] = useState(null)\n  const [selectedStage2AppId, setSelectedStage2AppId] = useState(null)\n"
    )

# 3. Status Badges in Tab 4
old_badges = """                      <div>
                        {app.status === 'submitted' && <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>Submitted (Pending Review)</span>}
                        {app.status === 'under_review' && <span style={{ background: '#F8F9FC', color: '#3E4784', border: '1px solid #D5D9EB', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>Under Review</span>}
                        {app.status === 'action_required' && <span style={{ background: '#FFFAEB', color: '#B54708', border: '1px solid #FEDF89', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>⚠️ Clarification Needed</span>}
                        {app.status === 'approved' && <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✓ Stage 1 Approved</span>}
                        {app.status === 'rejected' && <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✕ Not Approved</span>}
                      </div>"""

new_badges = """                      <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                        {app.status === 'submitted' && <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>Submitted (Pending Review)</span>}
                        {app.status === 'under_review' && <span style={{ background: '#F8F9FC', color: '#3E4784', border: '1px solid #D5D9EB', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>Under Review</span>}
                        {app.status === 'action_required' && <span style={{ background: '#FFFAEB', color: '#B54708', border: '1px solid #FEDF89', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>⚠️ Clarification Needed</span>}
                        {app.status === 'approved' && <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✓ Stage 1 Approved</span>}
                        {app.status === 'stage2_submitted' && <span style={{ background: '#F0F9FF', color: '#026AA2', border: '1px solid #B9E6FE', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>📋 Stage 2 Submitted</span>}
                        {app.status === 'documents_uploaded' && <span style={{ background: '#EEF4FF', color: '#3538CD', border: '1px solid #C7D7FE', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>📁 Documents Uploaded</span>}
                        {(app.status === 'detailed_review_completed' || app.status === 'documents_verified') && <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✓ Stage 2 Verified</span>}
                        {(app.status === 'final_admission_confirmed' || app.status === 'enrolled') && <span style={{ background: '#FDF4FF', color: '#C11574', border: '1px solid #FCCEEE', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>🎓 Enrolled</span>}
                        {app.status === 'rejected' && <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.35rem 0.8rem', borderRadius: '20px', fontSize: '0.825rem', fontWeight: 700 }}>✕ Not Approved</span>}
                      </div>"""

text = text.replace(old_badges, new_badges)

# 4. Update Banners
old_approved_banner = """                    {/* Approved Banner */}
                    {app.status === 'approved' && (
                      <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1rem', marginTop: '1rem', color: '#027A48', fontSize: '0.875rem' }}>
                        🎉 <strong>Preliminary Eligibility Confirmed:</strong> Your Stage 1 application has been approved by the institution review desk. You are eligible for Stage 2 official dossier submission and certificate verification.
                      </div>
                    )}"""

new_approved_banner = """                    {/* Approved Banner - Actionable for Stage 2 */}
                    {app.status === 'approved' && (
                      <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#027A48', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                              🎉 Preliminary Eligibility Confirmed: Stage 1 Approved!
                            </div>
                            <p style={{ margin: 0, color: '#05603A', fontSize: '0.85rem' }}>
                              Your Stage 1 preliminary application has been approved. Please complete Stage 2 to provide student demographics, previous schooling history, and upload required certificates for verification.
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setSelectedStage2AppId(app.application_id)}
                            style={{ background: '#027A48', color: '#ffffff', border: 'none', padding: '0.6rem 1.25rem', borderRadius: '8px', fontWeight: 700, cursor: 'pointer', fontSize: '0.875rem', whiteSpace: 'nowrap' }}
                          >
                            Complete Stage 2 Dossier & Uploads →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Stage 2 Submitted / Documents Uploaded Banner */}
                    {(app.status === 'stage2_submitted' || app.status === 'documents_uploaded') && (
                      <div style={{ background: '#F0F9FF', border: '1px solid #B9E6FE', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#026AA2', fontSize: '0.875rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                          <div>
                            <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                              📋 Stage 2 Dossier & Documents Under Review
                            </div>
                            <p style={{ margin: 0, color: '#026AA2', fontSize: '0.85rem' }}>
                              Your detailed demographics and uploaded documents are currently being verified by the admissions desk staff. You can view or add more certificates if requested.
                            </p>
                          </div>
                          <button
                            type="button"
                            onClick={() => setSelectedStage2AppId(app.application_id)}
                            style={{ background: '#026AA2', color: '#ffffff', border: 'none', padding: '0.55rem 1.1rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem', whiteSpace: 'nowrap' }}
                          >
                            Manage Documents & Dossier →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Stage 2 Verified Banner */}
                    {(app.status === 'detailed_review_completed' || app.status === 'documents_verified') && (
                      <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1.25rem', marginTop: '1rem', color: '#027A48', fontSize: '0.875rem' }}>
                        <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                          ✓ Documents & Stage 2 Dossier Verified
                        </div>
                        <p style={{ margin: 0, color: '#05603A', fontSize: '0.85rem' }}>
                          All required institutional certificates have been verified by the admissions desk. Awaiting final seat allotment and student enrolment.
                        </p>
                      </div>
                    )}

                    {/* Final Admission Confirmed Banner */}
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

text = text.replace(old_approved_banner, new_approved_banner)

# 5. Insert Modal at the end of component
modal_snippet = """        {/* Modal: Stage 2 Admission Dossier & Document Upload */}
        <Stage2AdmissionModal
          applicationId={selectedStage2AppId}
          isOpen={Boolean(selectedStage2AppId)}
          onClose={() => setSelectedStage2AppId(null)}
          onSuccess={() => {
            setSelectedStage2AppId(null)
            loadAdmissionApps()
          }}
        />
      </div>
    </div>
  )
}"""

if "<Stage2AdmissionModal" not in text:
    text = text.replace(
        "      </div>\n    </div>\n  )\n}",
        modal_snippet
    )

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("ParentDashboard.jsx successfully updated.")
