import re

path = r"C:\Users\callm\nagriksetu\frontend\src\components\admissions\AdmissionDeskTab.jsx"
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

# 1. Import API_URL if not imported
if "API_URL" not in text:
    text = text.replace(
        "import { apiGet, apiPost } from '../../utils/api.js'",
        "import { apiGet, apiPost, API_URL } from '../../utils/api.js'"
    )

# 2. Add State for Stage 2 Dossier & Documents
old_state = "  // Action Form States inside Modal\n  const [actionType, setActionType] = useState('none')"
new_state = """  // Stage 2 Dossier & Document Verification State
  const [stage2Dossier, setStage2Dossier] = useState(null)
  const [uploadedDocs, setUploadedDocs] = useState([])
  const [verifyingDocId, setVerifyingDocId] = useState(null)
  const [docNotesMap, setDocNotesMap] = useState({})

  // Action Form States inside Modal
  const [actionType, setActionType] = useState('none')"""

text = text.replace(old_state, new_state)

# 3. Update handleInspect to load stage 2 data
old_inspect = """    try {
      setLoadingHistory(true)
      const histData = await apiGet(`/school/admissions/${app.application_id}/history`)
      setHistory(Array.isArray(histData) ? histData : histData?.history || [])
    } catch (err) {
      setHistory([])
    } finally {
      setLoadingHistory(false)
    }"""

new_inspect = """    try {
      setLoadingHistory(true)
      const [histData, stage2Data] = await Promise.all([
        apiGet(`/school/admissions/${app.application_id}/history`).catch(() => []),
        apiGet(`/admissions/applications/${app.application_id}/stage2-eligibility`).catch(() => null)
      ])
      setHistory(Array.isArray(histData) ? histData : histData?.history || [])
      setStage2Dossier(stage2Data)
      setUploadedDocs(stage2Data?.uploaded_documents || [])
    } catch (err) {
      setHistory([])
      setStage2Dossier(null)
      setUploadedDocs([])
    } finally {
      setLoadingHistory(false)
    }"""

text = text.replace(old_inspect, new_inspect)

# 4. Add handleVerifyDocument helper
verify_doc_func = """  // Verify or Reject a single document
  const handleVerifyDocument = async (docId, newStatus) => {
    if (!activeApp) return
    const notes = (docNotesMap[docId] || '').trim()
    if ((newStatus === 'rejected' || newStatus === 'reupload_requested') && (!notes || notes.length < 3)) {
      alert('Please provide verification notes explaining the issue with this document (minimum 3 characters).')
      return
    }
    setVerifyingDocId(docId)
    setActionError(null)
    try {
      await apiPost(`/school/admissions/${activeApp.application_id}/documents/${docId}/verify`, {
        verification_status: newStatus,
        verification_notes: notes || (newStatus === 'verified' ? 'Document verified and authentic.' : null)
      })
      // Refresh documents
      const docsRes = await apiGet(`/admissions/applications/${activeApp.application_id}/documents`)
      setUploadedDocs(Array.isArray(docsRes) ? docsRes : [])
      setSuccess(`Document updated to ${newStatus}.`)
    } catch (err) {
      setActionError(err.message || 'Failed to update document verification.')
    } finally {
      setVerifyingDocId(null)
    }
  }

  // Handle Staff Actions"""

text = text.replace("  // Handle Staff Actions", verify_doc_func)

# 5. Add actionType === 'complete_stage2' inside handleExecuteAction
old_action_complete = """      } else if (actionType === 'reject') {
        if (!rejectionReason.trim() || rejectionReason.trim().length < 5) {
          throw new Error('Please specify an official rejection reason (minimum 5 characters).')
        }
        await apiPost(`/school/admissions/${activeApp.application_id}/reject`, {
          rejection_reason: rejectionReason.trim(),
          rejection_explanation: rejectionExplanation.trim() || null,
          institution_contact_phone: institutionPhone.trim() || null
        })
        setSuccess(`Application ${activeApp.application_id} marked as Rejected with official notice.`)
      }"""

new_action_complete = """      } else if (actionType === 'reject') {
        if (!rejectionReason.trim() || rejectionReason.trim().length < 5) {
          throw new Error('Please specify an official rejection reason (minimum 5 characters).')
        }
        await apiPost(`/school/admissions/${activeApp.application_id}/reject`, {
          rejection_reason: rejectionReason.trim(),
          rejection_explanation: rejectionExplanation.trim() || null,
          institution_contact_phone: institutionPhone.trim() || null
        })
        setSuccess(`Application ${activeApp.application_id} marked as Rejected with official notice.`)
      } else if (actionType === 'complete_stage2') {
        await apiPost(`/school/admissions/${activeApp.application_id}/stage2-review`, {
          decision: 'detailed_review_completed',
          review_notes: actionNotes.trim() || 'All Stage 2 documents and academic records verified.'
        })
        setSuccess(`Stage 2 review completed for ${activeApp.application_id}. Application marked as verified.`)
      }"""

text = text.replace(old_action_complete, new_action_complete)

# 6. Update renderStatusBadge
old_badge_cases = """      case 'approved':
        return <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Approved</span>
      case 'rejected':
        return <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Rejected</span>
      default:
        return <span style={{ background: '#F1F5F9', color: '#475569', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{status}</span>
    }"""

new_badge_cases = """      case 'approved':
        return <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Stage 1 Approved</span>
      case 'stage2_submitted':
        return <span style={{ background: '#F0F9FF', color: '#026AA2', border: '1px solid #B9E6FE', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Stage 2 Submitted</span>
      case 'documents_uploaded':
        return <span style={{ background: '#EEF4FF', color: '#3538CD', border: '1px solid #C7D7FE', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Docs Uploaded</span>
      case 'detailed_review_completed':
      case 'documents_verified':
        return <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Stage 2 Verified</span>
      case 'final_admission_confirmed':
      case 'enrolled':
        return <span style={{ background: '#FDF4FF', color: '#C11574', border: '1px solid #FCCEEE', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>🎓 Enrolled</span>
      case 'rejected':
        return <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>Rejected</span>
      default:
        return <span style={{ background: '#F1F5F9', color: '#475569', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>{status}</span>
    }"""

text = text.replace(old_badge_cases, new_badge_cases)

# 7. Add Stage 2 Dossier & Document Inspection Panel into Modal before Action Controls
target_before_actions = "              {/* Action Buttons Toolbar */}"

dossier_panel = """              {/* STAGE 2 DEMOGRAPHIC & ACADEMIC DOSSIER */}
              {stage2Dossier?.stage2_submission ? (
                <div style={{ background: '#F0F9FF', border: '1px solid #B9E6FE', borderRadius: '10px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                  <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#026AA2', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    📋 Stage 2 Detailed Demographic & Academic Dossier
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Date of Birth</span>
                      <strong>{stage2Dossier.stage2_submission.date_of_birth || 'N/A'}</strong>
                    </div>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Gender / Blood Group</span>
                      <strong style={{ textTransform: 'capitalize' }}>{stage2Dossier.stage2_submission.gender} • {stage2Dossier.stage2_submission.blood_group}</strong>
                    </div>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Emergency Contact</span>
                      <strong>{stage2Dossier.stage2_submission.emergency_contact_name || 'N/A'} ({stage2Dossier.stage2_submission.emergency_contact_phone || 'N/A'})</strong>
                    </div>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Previous Institution</span>
                      <strong>{stage2Dossier.stage2_submission.previous_institution_name || 'N/A'}</strong>
                      <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{stage2Dossier.stage2_submission.previous_institution_location}</div>
                    </div>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Previous Class / Board</span>
                      <strong>{stage2Dossier.stage2_submission.previous_standard_or_degree} • {stage2Dossier.stage2_submission.previous_board}</strong>
                    </div>
                    <div>
                      <span style={{ color: '#64748B', fontSize: '0.75rem', display: 'block' }}>Previous Marks Score</span>
                      <strong style={{ color: '#027A48' }}>{stage2Dossier.stage2_submission.previous_marks_percentage ? `${stage2Dossier.stage2_submission.previous_marks_percentage}%` : 'N/A'}</strong>
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ background: '#F8FAFC', border: '1px dashed #CBD5E1', borderRadius: '10px', padding: '1rem', marginBottom: '1.5rem', fontSize: '0.85rem', color: '#64748B' }}>
                  ℹ️ Stage 2 detailed demographic & previous schooling dossier has not yet been submitted by the parent.
                </div>
              )}

              {/* STAGE 2 SUPPORTING DOCUMENTS & VERIFICATION */}
              <div style={{ background: '#ffffff', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#102B46', fontWeight: 700 }}>
                    📁 Stage 2 Supporting Certificates & Verification ({uploadedDocs.length})
                  </h4>
                  <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
                    Authenticity verification required before final seat allotment
                  </span>
                </div>

                {uploadedDocs.length === 0 ? (
                  <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748B', fontStyle: 'italic' }}>
                    No digital verification certificates uploaded yet for this application.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                    {uploadedDocs.map((doc) => (
                      <div
                        key={doc.document_id}
                        style={{
                          border: '1px solid #E2E8F0',
                          borderRadius: '8px',
                          padding: '0.85rem',
                          background: doc.verification_status === 'verified' ? '#F6FEF9' : doc.verification_status === 'rejected' ? '#FEF3F2' : '#F8FAFC'
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                          <div>
                            <span style={{ fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 700, color: '#475569', background: '#E2E8F0', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                              {doc.document_type?.replace(/_/g, ' ')}
                            </span>
                            <div style={{ fontWeight: 600, color: '#1E293B', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                              📄 {doc.file_name}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#64748B' }}>
                              Size: {(doc.file_size_bytes / 1024).toFixed(1)} KB • Uploaded {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'Recently'}
                            </div>
                          </div>

                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <a
                              href={`${API_URL}/admissions/applications/${activeApp.application_id}/documents/${doc.document_id}/file`}
                              target="_blank"
                              rel="noreferrer"
                              style={{
                                background: '#102B46',
                                color: '#ffffff',
                                textDecoration: 'none',
                                padding: '0.3rem 0.65rem',
                                borderRadius: '4px',
                                fontSize: '0.75rem',
                                fontWeight: 600
                              }}
                            >
                              👁️ View Document
                            </a>
                            <span
                              style={{
                                padding: '0.25rem 0.65rem',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                fontWeight: 700,
                                background: doc.verification_status === 'verified' ? '#ECFDF3' : doc.verification_status === 'rejected' ? '#FEF3F2' : doc.verification_status === 'reupload_requested' ? '#FFFAEB' : '#EFF8FF',
                                color: doc.verification_status === 'verified' ? '#027A48' : doc.verification_status === 'rejected' ? '#B42318' : doc.verification_status === 'reupload_requested' ? '#B54708' : '#175CD3',
                                border: `1px solid ${doc.verification_status === 'verified' ? '#A6F4C5' : doc.verification_status === 'rejected' ? '#FECDCA' : doc.verification_status === 'reupload_requested' ? '#FEDF89' : '#B2DDFF'}`
                              }}
                            >
                              {doc.verification_status?.toUpperCase() || 'PENDING'}
                            </span>
                          </div>
                        </div>

                        {doc.verification_notes && (
                          <div style={{ fontSize: '0.78rem', color: '#475569', background: '#ffffff', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid #E2E8F0', marginBottom: '0.5rem' }}>
                            <strong>Staff Note:</strong> {doc.verification_notes}
                          </div>
                        )}

                        {/* Document Staff Action Controls */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap', borderTop: '1px dashed #CBD5E1', paddingTop: '0.5rem' }}>
                          <input
                            type="text"
                            placeholder="Verification feedback notes (required if rejecting / requesting re-upload)..."
                            value={docNotesMap[doc.document_id] || ''}
                            onChange={(e) => setDocNotesMap({ ...docNotesMap, [doc.document_id]: e.target.value })}
                            style={{ flex: 1, minWidth: '220px', padding: '0.3rem 0.6rem', borderRadius: '4px', border: '1px solid #CBD5E1', fontSize: '0.78rem' }}
                          />
                          <button
                            type="button"
                            disabled={verifyingDocId === doc.document_id}
                            onClick={() => handleVerifyDocument(doc.document_id, 'verified')}
                            style={{ background: '#027A48', color: '#ffffff', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer' }}
                          >
                            ✓ Verify
                          </button>
                          <button
                            type="button"
                            disabled={verifyingDocId === doc.document_id}
                            onClick={() => handleVerifyDocument(doc.document_id, 'reupload_requested')}
                            style={{ background: '#B54708', color: '#ffffff', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
                          >
                            ⚠️ Re-upload
                          </button>
                          <button
                            type="button"
                            disabled={verifyingDocId === doc.document_id}
                            onClick={() => handleVerifyDocument(doc.document_id, 'rejected')}
                            style={{ background: '#B42318', color: '#ffffff', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
                          >
                            ✕ Reject
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Action Buttons Toolbar */}"""

text = text.replace(target_before_actions, dossier_panel)

# 8. Add "Complete Stage 2 Review" button to Action Controls
old_buttons_block = """                  <button
                    onClick={() => { setActionType('reject'); setActionError(null); }}
                    style={{
                      background: actionType === 'reject' ? '#B42318' : '#FEF3F2',
                      color: actionType === 'reject' ? '#ffffff' : '#B42318',
                      border: '1px solid #FECDCA',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 600,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    ✕ Reject Application
                  </button>"""

new_buttons_block = """                  <button
                    onClick={() => { setActionType('reject'); setActionError(null); }}
                    style={{
                      background: actionType === 'reject' ? '#B42318' : '#FEF3F2',
                      color: actionType === 'reject' ? '#ffffff' : '#B42318',
                      border: '1px solid #FECDCA',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 600,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    ✕ Reject Application
                  </button>

                  <button
                    onClick={() => { setActionType('complete_stage2'); setActionError(null); }}
                    style={{
                      background: actionType === 'complete_stage2' ? '#0E7090' : '#ECFEFF',
                      color: actionType === 'complete_stage2' ? '#ffffff' : '#0E7090',
                      border: '1px solid #A5F3FC',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    📋 Complete Stage 2 Review
                  </button>"""

text = text.replace(old_buttons_block, new_buttons_block)

# 9. Add action panel for complete_stage2
complete_stage2_panel = """              {actionType === 'complete_stage2' && (
                <div style={{ background: '#ECFEFF', border: '1px solid #A5F3FC', borderRadius: '8px', padding: '1rem', marginBottom: '1rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#0E7090', marginBottom: '0.35rem' }}>
                    Stage 2 Verification Review Notes
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Verified date of birth, previous schooling marks, and mandatory transfer certificate."
                    value={actionNotes}
                    onChange={(e) => setActionNotes(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #A5F3FC', fontSize: '0.85rem', marginBottom: '0.75rem' }}
                  />
                  <div style={{ fontSize: '0.8rem', color: '#0E7090', marginBottom: '0.75rem' }}>
                    🛡️ This confirms all required Stage 2 documents are verified. The applicant will be queued for Phase 6 Final Admission Confirmation & Student Enrolment.
                  </div>
                  <button
                    onClick={handleExecuteAction}
                    disabled={actionSubmitting}
                    style={{ background: '#0E7090', color: '#ffffff', border: 'none', padding: '0.5rem 1.25rem', borderRadius: '6px', fontWeight: 700, fontSize: '0.85rem', cursor: 'pointer' }}
                  >
                    {actionSubmitting ? 'Finalizing Review...' : 'Confirm: Complete Stage 2 Review ✓'}
                  </button>
                </div>
              )}"""

target_after_reject_panel = "              {actionType === 'reject' && ("
# find end of reject panel
pos_reject = text.find(target_after_reject_panel)
pos_end_reject = text.find("</div>\n              )}", pos_reject) + len("</div>\n              )}")
text = text[:pos_end_reject] + "\n\n" + complete_stage2_panel + text[pos_end_reject:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

print("AdmissionDeskTab.jsx successfully upgraded with Stage 2 dossier & document verification.")
