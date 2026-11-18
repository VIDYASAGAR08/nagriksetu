import sys

fe_path = r'C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx'
with open(fe_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. State variables
old_state = """  // Stage 2 & Document Review State inside Review Modal
  const [previewDoc, setPreviewDoc] = useState(null)
  const [docActionModal, setDocActionModal] = useState(null) // { doc, actionType: 'verified' | 'reupload_requested' | 'rejected', notes: '' }
  const [submittingDocAction, setSubmittingDocAction] = useState(false)
  const [stage2ReviewNotes, setStage2ReviewNotes] = useState('')"""

new_state = """  // Stage 2 & Document Review State inside Review Modal
  const [previewDoc, setPreviewDoc] = useState(null)
  const [previewZoom, setPreviewZoom] = useState(100)
  const [confirmAcceptDoc, setConfirmAcceptDoc] = useState(null)
  const [acceptDocNotes, setAcceptDocNotes] = useState('Document verified and found authentic by institution administrator.')
  const [confirmRejectDoc, setConfirmRejectDoc] = useState(null) // { doc, reason: '' }
  const [submittingDocAction, setSubmittingDocAction] = useState(false)
  const [stage2ReviewNotes, setStage2ReviewNotes] = useState('')"""

assert old_state in code, "old_state not found"
code = code.replace(old_state, new_state, 1)

# 2. Handlers
old_handlers = """  // Handle Quick Verify Document
  async function handleQuickVerifyDoc(doc) {
    if (!selectedApp || !token) return
    const appId = selectedApp.application_id || selectedApp.id
    try {
      await apiPost(`/school/admissions/${appId}/documents/${doc.document_id}/verify`, {
        verification_status: 'verified',
        verification_notes: 'Document verified and found authentic by institution administrator.'
      }, token)
      setActionFeedback({ type: 'success', message: `Document '${doc.file_name}' (${doc.document_type}) verified successfully.` })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to verify document.' })
    }
  }

  // Handle Document Verification Action Submit (Verify / Reupload / Reject)
  async function handleVerifyDocSubmit(e) {
    e.preventDefault()
    if (!docActionModal || !selectedApp || !token) return
    const { doc, actionType, notes } = docActionModal
    if ((actionType === 'reupload_requested' || actionType === 'rejected') && !notes.trim()) {
      setActionFeedback({ type: 'error', message: 'A specific reason/explanation is mandatory when rejecting or requesting document re-upload.' })
      return
    }
    const appId = selectedApp.application_id || selectedApp.id
    try {
      setSubmittingDocAction(true)
      await apiPost(`/school/admissions/${appId}/documents/${doc.document_id}/verify`, {
        verification_status: actionType,
        verification_notes: notes.trim() || undefined
      }, token)
      
      const label = actionType === 'verified' ? 'Verified' : (actionType === 'reupload_requested' ? 'Replacement Requested' : 'Rejected')
      setActionFeedback({ type: 'success', message: `Document '${doc.file_name}' marked as ${label}.` })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
      setDocActionModal(null)
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to update document verification status.' })
    } finally {
      setSubmittingDocAction(false)
    }
  }"""

new_handlers = """  // Handle Accept Document (Opens confirmation modal or processes confirmed acceptance)
  async function handleAcceptDocConfirm(e) {
    if (e && e.preventDefault) e.preventDefault()
    if (!confirmAcceptDoc || !selectedApp || !token) return
    const appId = selectedApp.application_id || selectedApp.id
    try {
      setSubmittingDocAction(true)
      await apiPost(`/school/admissions/${appId}/documents/${confirmAcceptDoc.document_id}/verify`, {
        verification_status: 'verified',
        verification_notes: acceptDocNotes?.trim() || 'Document verified and found authentic by institution administrator.'
      }, token)
      setActionFeedback({ type: 'success', message: 'Document successfully verified.' })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
      setConfirmAcceptDoc(null)
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to verify document.' })
    } finally {
      setSubmittingDocAction(false)
    }
  }

  // Handle Reject Document (Submits mandatory rejection reason)
  async function handleRejectDocConfirm(e) {
    if (e && e.preventDefault) e.preventDefault()
    if (!confirmRejectDoc || !selectedApp || !token) return
    const { doc, reason } = confirmRejectDoc
    if (!reason || !reason.trim()) {
      setActionFeedback({ type: 'error', message: 'A specific rejection reason is mandatory when rejecting an uploaded document.' })
      return
    }
    const appId = selectedApp.application_id || selectedApp.id
    try {
      setSubmittingDocAction(true)
      await apiPost(`/school/admissions/${appId}/documents/${doc.document_id}/verify`, {
        verification_status: 'rejected',
        verification_notes: reason.trim()
      }, token)
      setActionFeedback({ type: 'success', message: `Document '${doc.file_name}' marked as Rejected. Notification dispatched to parent.` })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
      setConfirmRejectDoc(null)
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to reject document.' })
    } finally {
      setSubmittingDocAction(false)
    }
  }"""

assert old_handlers in code, "old_handlers not found"
code = code.replace(old_handlers, new_handlers, 1)

# 3. Documents Table rows & Action buttons
old_table_section = """                  {/* Documents List */}
                  {selectedApp.documents && selectedApp.documents.length > 0 ? (
                    <div style={{ border: '1px solid #EAECF0', borderRadius: '6px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.825rem', textAlign: 'left' }}>
                        <thead>
                          <tr style={{ background: '#F8F9FA', borderBottom: '1px solid #EAECF0', color: '#475467' }}>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Certificate / Document</th>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Original Filename & Size</th>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Uploaded Date</th>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                            <th style={{ padding: '0.6rem 0.75rem', textAlign: 'right' }}>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedApp.documents.map((doc) => {
                            const typeLabels = {
                              birth_certificate: 'Birth Certificate',
                              transfer_certificate: 'Transfer Certificate (TC)',
                              previous_marks_card: 'Previous Marks Card / Report',
                              passport_photo: 'Passport Photograph',
                              caste_certificate: 'Caste / Category Certificate',
                              income_certificate: 'Income Certificate',
                              aadhaar_card: 'Aadhaar Card / ID Proof',
                              conduct_certificate: 'Conduct Certificate'
                            }
                            const typeLabel = typeLabels[doc.document_type] || doc.document_type.replace(/_/g, ' ')
                            const sizeKb = doc.file_size_bytes ? (doc.file_size_bytes / 1024).toFixed(1) + ' KB' : 'N/A'

                            return (
                              <tr key={doc.document_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                                <td style={{ padding: '0.6rem 0.75rem' }}>
                                  <div style={{ fontWeight: 700, color: '#102B46' }}>{typeLabel}</div>
                                  <div style={{ fontSize: '0.72rem', color: '#667085', fontFamily: 'monospace' }}>{doc.document_type}</div>
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem', color: '#344054' }}>
                                  <div style={{ fontWeight: 600 }}>{doc.file_name}</div>
                                  <div style={{ fontSize: '0.72rem', color: '#98A2B3' }}>{sizeKb} • {doc.mime_type || 'binary'}</div>
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem', color: '#667085', fontSize: '0.78rem' }}>
                                  {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'N/A'}
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem' }}>
                                  {doc.verification_status === 'verified' && (
                                    <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      ✓ Verified
                                    </span>
                                  )}
                                  {doc.verification_status === 'pending' && (
                                    <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FEDF89', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      ⏳ Pending Review
                                    </span>
                                  )}
                                  {doc.verification_status === 'reupload_requested' && (
                                    <span style={{ background: '#F9F5FF', color: '#6941C6', border: '1px solid #D6BBFB', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      🔄 Replacement Requested
                                    </span>
                                  )}
                                  {doc.verification_status === 'rejected' && (
                                    <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      ✕ Rejected
                                    </span>
                                  )}
                                  {doc.verification_notes && (
                                    <div style={{ fontSize: '0.72rem', color: '#475467', fontStyle: 'italic', marginTop: '0.25rem' }}>
                                      "{doc.verification_notes}"
                                    </div>
                                  )}
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem', textAlign: 'right' }}>
                                  <div style={{ display: 'inline-flex', gap: '0.35rem', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                                    {/* Preview Button */}
                                    <button
                                      type="button"
                                      onClick={() => setPreviewDoc(doc)}
                                      title="Preview Document"
                                      style={{
                                        background: '#EFF4FF',
                                        color: '#155EEF',
                                        border: '1px solid #B2DDFF',
                                        borderRadius: '4px',
                                        padding: '0.25rem 0.5rem',
                                        fontSize: '0.72rem',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                      }}
                                    >
                                      👁️ Preview
                                    </button>

                                    {/* Download Button */}
                                    <a
                                      href={`${doc.download_url}?token=${token}`}
                                      target="_blank"
                                      rel="noreferrer"
                                      download={doc.file_name}
                                      title="Download Document"
                                      style={{
                                        background: '#F8F9FA',
                                        color: '#344054',
                                        border: '1px solid #D0D5DD',
                                        borderRadius: '4px',
                                        padding: '0.25rem 0.5rem',
                                        fontSize: '0.72rem',
                                        fontWeight: 600,
                                        textDecoration: 'none',
                                        display: 'inline-block'
                                      }}
                                    >
                                      ⬇️ Download
                                    </a>

                                    {/* Verify Button */}
                                    {doc.verification_status !== 'verified' && (
                                      <button
                                        type="button"
                                        onClick={() => handleQuickVerifyDoc(doc)}
                                        title="Mark Verified"
                                        style={{
                                          background: '#ECFDF3',
                                          color: '#027A48',
                                          border: '1px solid #A6F4C5',
                                          borderRadius: '4px',
                                          padding: '0.25rem 0.5rem',
                                          fontSize: '0.72rem',
                                          fontWeight: 700,
                                          cursor: 'pointer'
                                        }}
                                      >
                                        ✓ Verify
                                      </button>
                                    )}

                                    {/* Request Replacement */}
                                    <button
                                      type="button"
                                      onClick={() => setDocActionModal({ doc, actionType: 'reupload_requested', notes: '' })}
                                      title="Request Replacement Document"
                                      style={{
                                        background: '#F9F5FF',
                                        color: '#6941C6',
                                        border: '1px solid #D6BBFB',
                                        borderRadius: '4px',
                                        padding: '0.25rem 0.5rem',
                                        fontSize: '0.72rem',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                      }}
                                    >
                                      🔄 Replace
                                    </button>

                                    {/* Reject Document */}
                                    {doc.verification_status !== 'rejected' && (
                                      <button
                                        type="button"
                                        onClick={() => setDocActionModal({ doc, actionType: 'rejected', notes: '' })}
                                        title="Reject Document"
                                        style={{
                                          background: '#FEF3F2',
                                          color: '#B42318',
                                          border: '1px solid #FECDCA',
                                          borderRadius: '4px',
                                          padding: '0.25rem 0.5rem',
                                          fontSize: '0.72rem',
                                          fontWeight: 600,
                                          cursor: 'pointer'
                                        }}
                                      >
                                        ✕ Reject
                                      </button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : ("""

new_table_section = """                  {/* Documents List */}
                  {selectedApp.documents && selectedApp.documents.length > 0 ? (
                    <div style={{ border: '1px solid #EAECF0', borderRadius: '6px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.825rem', textAlign: 'left' }}>
                        <thead>
                          <tr style={{ background: '#F8F9FA', borderBottom: '1px solid #EAECF0', color: '#475467' }}>
                            <th style={{ padding: '0.65rem 0.75rem', width: '24%' }}>Certificate / Document</th>
                            <th style={{ padding: '0.65rem 0.75rem', width: '22%' }}>Original Filename & Size</th>
                            <th style={{ padding: '0.65rem 0.75rem', width: '14%' }}>Uploaded Date</th>
                            <th style={{ padding: '0.65rem 0.75rem', width: '40%' }}>Status & Verification Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedApp.documents.map((doc) => {
                            const typeLabels = {
                              birth_certificate: 'Birth Certificate',
                              transfer_certificate: 'Transfer Certificate (TC)',
                              previous_marks_card: 'Previous Marks Card / Report',
                              passport_photo: 'Passport Photograph',
                              caste_certificate: 'Caste / Category Certificate',
                              income_certificate: 'Income Certificate',
                              aadhaar_card: 'Aadhaar Card / ID Proof',
                              conduct_certificate: 'Conduct Certificate'
                            }
                            const typeLabel = typeLabels[doc.document_type] || doc.document_type.replace(/_/g, ' ')
                            const sizeKb = doc.file_size_bytes ? (doc.file_size_bytes / 1024).toFixed(1) + ' KB' : 'N/A'

                            return (
                              <tr key={doc.document_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                                <td style={{ padding: '0.65rem 0.75rem' }}>
                                  <div style={{ fontWeight: 700, color: '#102B46', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                                    <span>{typeLabel}</span>
                                    {doc.version && doc.version > 1 && (
                                      <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.1rem 0.35rem', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 700 }}>
                                        v{doc.version}
                                      </span>
                                    )}
                                  </div>
                                  <div style={{ fontSize: '0.72rem', color: '#667085', fontFamily: 'monospace' }}>{doc.document_type}</div>
                                </td>

                                <td style={{ padding: '0.65rem 0.75rem', color: '#344054' }}>
                                  <div style={{ fontWeight: 600, wordBreak: 'break-all' }}>{doc.file_name}</div>
                                  <div style={{ fontSize: '0.72rem', color: '#98A2B3' }}>{sizeKb} • {doc.mime_type || 'binary'}</div>
                                </td>

                                <td style={{ padding: '0.65rem 0.75rem', color: '#667085', fontSize: '0.78rem' }}>
                                  {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'N/A'}
                                </td>

                                <td style={{ padding: '0.65rem 0.75rem' }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                                    {/* Status Badge */}
                                    {doc.verification_status === 'verified' && (
                                      <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.22rem 0.6rem', borderRadius: '12px', fontSize: '0.74rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                        ✓ Verified
                                      </span>
                                    )}
                                    {doc.verification_status === 'pending' && (
                                      <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FEDF89', padding: '0.22rem 0.6rem', borderRadius: '12px', fontSize: '0.74rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                        ⏳ Pending Review
                                      </span>
                                    )}
                                    {doc.verification_status === 'reupload_requested' && (
                                      <span style={{ background: '#F9F5FF', color: '#6941C6', border: '1px solid #D6BBFB', padding: '0.22rem 0.6rem', borderRadius: '12px', fontSize: '0.74rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                        🔄 Replacement Requested
                                      </span>
                                    )}
                                    {doc.verification_status === 'rejected' && (
                                      <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.22rem 0.6rem', borderRadius: '12px', fontSize: '0.74rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                                        ✕ Rejected
                                      </span>
                                    )}

                                    {/* Three Action Buttons Placed Immediately Beside Status */}
                                    <div style={{ display: 'inline-flex', gap: '0.35rem', alignItems: 'center', flexWrap: 'wrap' }}>
                                      {/* 1. View Button (neutral / blue) */}
                                      <button
                                        type="button"
                                        onClick={() => {
                                          setPreviewZoom(100);
                                          setPreviewDoc(doc);
                                        }}
                                        title="View document preview"
                                        style={{
                                          background: '#EFF4FF',
                                          color: '#155EEF',
                                          border: '1px solid #B2DDFF',
                                          borderRadius: '5px',
                                          padding: '0.25rem 0.6rem',
                                          fontSize: '0.74rem',
                                          fontWeight: 600,
                                          cursor: 'pointer',
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          gap: '0.25rem',
                                          transition: 'all 0.15s ease'
                                        }}
                                      >
                                        👁️ View
                                      </button>

                                      {/* 2. Accept Button (green) */}
                                      <button
                                        type="button"
                                        disabled={doc.verification_status === 'verified'}
                                        onClick={() => {
                                          setAcceptDocNotes('Document verified and found authentic by institution administrator.');
                                          setConfirmAcceptDoc(doc);
                                        }}
                                        title={doc.verification_status === 'verified' ? 'Document is already verified' : 'Accept and verify this document'}
                                        style={{
                                          background: doc.verification_status === 'verified' ? '#F4F5F7' : '#ECFDF3',
                                          color: doc.verification_status === 'verified' ? '#98A2B3' : '#027A48',
                                          border: `1px solid ${doc.verification_status === 'verified' ? '#D0D5DD' : '#A6F4C5'}`,
                                          borderRadius: '5px',
                                          padding: '0.25rem 0.6rem',
                                          fontSize: '0.74rem',
                                          fontWeight: 700,
                                          cursor: doc.verification_status === 'verified' ? 'not-allowed' : 'pointer',
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          gap: '0.25rem',
                                          opacity: doc.verification_status === 'verified' ? 0.6 : 1,
                                          transition: 'all 0.15s ease'
                                        }}
                                      >
                                        ✓ Accept
                                      </button>

                                      {/* 3. Reject Button (red) */}
                                      <button
                                        type="button"
                                        disabled={doc.verification_status === 'rejected'}
                                        onClick={() => setConfirmRejectDoc({ doc, reason: '' })}
                                        title={doc.verification_status === 'rejected' ? 'Document is already rejected' : 'Reject this document with mandatory reason'}
                                        style={{
                                          background: doc.verification_status === 'rejected' ? '#F4F5F7' : '#FEF3F2',
                                          color: doc.verification_status === 'rejected' ? '#98A2B3' : '#B42318',
                                          border: `1px solid ${doc.verification_status === 'rejected' ? '#D0D5DD' : '#FECDCA'}`,
                                          borderRadius: '5px',
                                          padding: '0.25rem 0.6rem',
                                          fontSize: '0.74rem',
                                          fontWeight: 700,
                                          cursor: doc.verification_status === 'rejected' ? 'not-allowed' : 'pointer',
                                          display: 'inline-flex',
                                          alignItems: 'center',
                                          gap: '0.25rem',
                                          opacity: doc.verification_status === 'rejected' ? 0.6 : 1,
                                          transition: 'all 0.15s ease'
                                        }}
                                      >
                                        ✕ Reject
                                      </button>
                                    </div>
                                  </div>

                                  {/* Verification Details / Audit Line */}
                                  {doc.verification_status === 'verified' && (
                                    <div style={{ fontSize: '0.72rem', color: '#027A48', marginTop: '0.25rem', fontWeight: 600 }}>
                                      ✓ Verified by {doc.verified_by_name || 'Administrator'} {doc.verified_at ? `on ${new Date(doc.verified_at).toLocaleDateString()}` : ''}
                                    </div>
                                  )}
                                  {doc.verification_status === 'rejected' && doc.verification_notes && (
                                    <div style={{ fontSize: '0.72rem', color: '#B42318', marginTop: '0.25rem', background: '#FFF5F5', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid #FECDCA' }}>
                                      <strong>Rejection Reason:</strong> "{doc.verification_notes}"
                                    </div>
                                  )}
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : ("""

assert old_table_section in code, "old_table_section not found"
code = code.replace(old_table_section, new_table_section, 1)

# 4. Modals at bottom (Preview Modal with Zoom, Accept Modal, Reject Modal)
old_modals = """              {/* Floating Document Action Modal (Re-upload Request / Rejection) */}
              {docActionModal && (
                <div style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(0,0,0,0.5)',
                  zIndex: 10001,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '1rem'
                }}>
                  <div style={{ background: '#FFFFFF', borderRadius: '8px', maxWidth: '480px', width: '100%', padding: '1.5rem', boxShadow: '0 10px 25px rgba(0,0,0,0.2)' }}>
                    <h3 style={{ margin: '0 0 0.5rem 0', color: docActionModal.actionType === 'rejected' ? '#B42318' : '#6941C6', fontSize: '1.1rem' }}>
                      {docActionModal.actionType === 'rejected' ? '✕ Reject Document' : '🔄 Request Replacement Document'}
                    </h3>
                    <p style={{ margin: '0 0 0.85rem 0', fontSize: '0.85rem', color: '#475467' }}>
                      Document: <strong>{docActionModal.doc.file_name}</strong> ({docActionModal.doc.document_type})
                    </p>

                    <form onSubmit={handleVerifyDocSubmit}>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                          Reason / Instructions for Parent <span style={{ color: '#F04438' }}>*</span>
                        </label>
                        <textarea
                          rows={3}
                          required
                          placeholder={docActionModal.actionType === 'rejected' ? 'e.g. Document image is illegible or not a recognized institutional certificate.' : 'e.g. Please re-upload a clear, uncropped color scan of the original certificate.'}
                          value={docActionModal.notes}
                          onChange={(e) => setDocActionModal(prev => ({ ...prev, notes: e.target.value }))}
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', boxSizing: 'border-box' }}
                        />
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                        <button
                          type="button"
                          onClick={() => setDocActionModal(null)}
                          className="btn btn--secondary btn--sm"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={submittingDocAction || !docActionModal.notes.trim()}
                          style={{
                            background: docActionModal.actionType === 'rejected' ? '#F04438' : '#7A5AF8',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.45rem 0.9rem',
                            fontWeight: 700,
                            fontSize: '0.825rem',
                            cursor: 'pointer'
                          }}
                        >
                          {submittingDocAction ? 'Submitting...' : (docActionModal.actionType === 'rejected' ? 'Confirm Rejection' : 'Send Re-upload Request')}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

              {/* Floating Document Preview Modal */}
              {previewDoc && (
                <div style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(0,0,0,0.7)',
                  zIndex: 10002,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '1.5rem',
                  backdropFilter: 'blur(2px)'
                }}>
                  <div style={{ background: '#FFFFFF', borderRadius: '10px', maxWidth: '800px', width: '100%', maxHeight: '90vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 20px 40px rgba(0,0,0,0.3)' }}>
                    <div style={{ background: '#102B46', color: '#FFFFFF', padding: '1rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#98A2B3', textTransform: 'uppercase', fontWeight: 700 }}>
                          Document Inspection
                        </div>
                        <div style={{ fontSize: '1rem', fontWeight: 700, marginTop: '0.15rem' }}>
                          {previewDoc.file_name} ({previewDoc.document_type})
                        </div>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <a
                          href={`${previewDoc.download_url}?token=${token}`}
                          target="_blank"
                          rel="noreferrer"
                          download={previewDoc.file_name}
                          style={{
                            background: '#EFF4FF',
                            color: '#155EEF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.35rem 0.75rem',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            textDecoration: 'none',
                            display: 'inline-flex',
                            alignItems: 'center'
                          }}
                        >
                          ⬇️ Download Original
                        </a>
                        <button
                          onClick={() => setPreviewDoc(null)}
                          style={{ background: 'rgba(255,255,255,0.2)', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.35rem 0.65rem', cursor: 'pointer', fontWeight: 700 }}
                        >
                          ✕
                        </button>
                      </div>
                    </div>

                    <div style={{ padding: '1.25rem', flex: 1, overflowY: 'auto', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#F8F9FA' }}>
                      {previewDoc.mime_type && previewDoc.mime_type.startsWith('image/') ? (
                        <img
                          src={`${previewDoc.download_url}?token=${token}`}
                          alt={previewDoc.file_name}
                          style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                        />
                      ) : (
                        <iframe
                          src={`${previewDoc.download_url}?token=${token}`}
                          title={previewDoc.file_name}
                          style={{ width: '100%', height: '70vh', border: 'none', borderRadius: '6px' }}
                        />
                      )}
                    </div>
                  </div>
                </div>
              )}"""

new_modals = """              {/* MODAL 1: ACCEPT CONFIRMATION MODAL */}
              {confirmAcceptDoc && (
                <div style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(16, 43, 70, 0.65)',
                  zIndex: 10002,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '1rem',
                  backdropFilter: 'blur(3px)'
                }}>
                  <div style={{ background: '#FFFFFF', borderRadius: '10px', maxWidth: '520px', width: '100%', padding: '1.5rem', boxShadow: '0 20px 40px rgba(0,0,0,0.25)', border: '1px solid #A6F4C5' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                      <span style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#ECFDF3', color: '#027A48', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: 800 }}>
                        ✓
                      </span>
                      <div>
                        <h3 style={{ margin: 0, color: '#102B46', fontSize: '1.15rem', fontWeight: 700 }}>
                          Confirm Document Verification
                        </h3>
                        <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.15rem' }}>
                          Accept and mark supporting certificate as authentic
                        </div>
                      </div>
                    </div>

                    <div style={{ background: '#F8F9FA', borderRadius: '6px', padding: '0.85rem 1rem', marginBottom: '1.1rem', border: '1px solid #EAECF0', fontSize: '0.825rem' }}>
                      <div style={{ marginBottom: '0.35rem' }}>
                        <span style={{ color: '#667085' }}>Document: </span>
                        <strong style={{ color: '#102B46' }}>{confirmAcceptDoc.file_name}</strong>
                      </div>
                      <div style={{ marginBottom: '0.35rem' }}>
                        <span style={{ color: '#667085' }}>Category: </span>
                        <strong style={{ color: '#102B46' }}>{confirmAcceptDoc.document_type?.replace(/_/g, ' ')?.toUpperCase()}</strong>
                      </div>
                      <div>
                        <span style={{ color: '#667085' }}>Applicant: </span>
                        <strong style={{ color: '#155EEF' }}>{selectedApp.applicant_name}</strong> ({selectedApp.application_id})
                      </div>
                    </div>

                    <p style={{ fontSize: '0.85rem', color: '#344054', lineHeight: 1.4, margin: '0 0 1rem 0' }}>
                      Are you sure you want to accept and verify this document? This will record your administrator signature, institution ID, and verification timestamp in the permanent application audit trail.
                    </p>

                    <form onSubmit={handleAcceptDocConfirm}>
                      <div style={{ marginBottom: '1.25rem' }}>
                        <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                          Verification Notes (Optional)
                        </label>
                        <input
                          type="text"
                          value={acceptDocNotes}
                          onChange={(e) => setAcceptDocNotes(e.target.value)}
                          placeholder="e.g. Verified against original board record"
                          style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.825rem', boxSizing: 'border-box' }}
                        />
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                        <button
                          type="button"
                          onClick={() => setConfirmAcceptDoc(null)}
                          className="btn btn--secondary btn--sm"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={submittingDocAction}
                          style={{
                            background: '#027A48',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.5rem 1.15rem',
                            fontWeight: 700,
                            fontSize: '0.85rem',
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}
                        >
                          {submittingDocAction ? 'Verifying...' : '✓ Confirm Accept'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

              {/* MODAL 2: REJECT MODAL (MANDATORY REASON) */}
              {confirmRejectDoc && (
                <div style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(16, 43, 70, 0.65)',
                  zIndex: 10002,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '1rem',
                  backdropFilter: 'blur(3px)'
                }}>
                  <div style={{ background: '#FFFFFF', borderRadius: '10px', maxWidth: '520px', width: '100%', padding: '1.5rem', boxShadow: '0 20px 40px rgba(0,0,0,0.25)', border: '1px solid #FECDCA' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
                      <span style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#FEF3F2', color: '#B42318', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem', fontWeight: 800 }}>
                        ✕
                      </span>
                      <div>
                        <h3 style={{ margin: 0, color: '#B42318', fontSize: '1.15rem', fontWeight: 700 }}>
                          Reject Uploaded Document
                        </h3>
                        <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.15rem' }}>
                          Document status will update to REJECTED and notify parent
                        </div>
                      </div>
                    </div>

                    <div style={{ background: '#F8F9FA', borderRadius: '6px', padding: '0.85rem 1rem', marginBottom: '1.1rem', border: '1px solid #EAECF0', fontSize: '0.825rem' }}>
                      <div style={{ marginBottom: '0.35rem' }}>
                        <span style={{ color: '#667085' }}>Document: </span>
                        <strong style={{ color: '#102B46' }}>{confirmRejectDoc.doc.file_name}</strong>
                      </div>
                      <div>
                        <span style={{ color: '#667085' }}>Category: </span>
                        <strong style={{ color: '#102B46' }}>{confirmRejectDoc.doc.document_type?.replace(/_/g, ' ')?.toUpperCase()}</strong>
                      </div>
                    </div>

                    <div style={{ background: '#FFFAEB', border: '1px solid #FEDF89', borderRadius: '6px', padding: '0.75rem 0.9rem', marginBottom: '1.1rem', fontSize: '0.8rem', color: '#B54708', lineHeight: 1.4 }}>
                      ⚠️ The applicant's parent will receive an immediate in-app notification detailing this rejection and will be authorized to upload a replacement document.
                    </div>

                    <form onSubmit={handleRejectDocConfirm}>
                      <div style={{ marginBottom: '1.25rem' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                          Rejection Reason <span style={{ color: '#D92D20' }}>*</span>
                        </label>
                        <textarea
                          rows={3}
                          required
                          value={confirmRejectDoc.reason}
                          onChange={(e) => setConfirmRejectDoc(prev => ({ ...prev, reason: e.target.value }))}
                          placeholder="State the exact reason (e.g. Document is blurry/illegible, missing official seal, incomplete marks statement, or wrong certificate uploaded)..."
                          style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.825rem', boxSizing: 'border-box' }}
                        />
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                        <button
                          type="button"
                          onClick={() => setConfirmRejectDoc(null)}
                          className="btn btn--secondary btn--sm"
                        >
                          Cancel
                        </button>
                        <button
                          type="submit"
                          disabled={submittingDocAction || !confirmRejectDoc.reason.trim()}
                          style={{
                            background: '#B42318',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.5rem 1.15rem',
                            fontWeight: 700,
                            fontSize: '0.85rem',
                            cursor: (!confirmRejectDoc.reason.trim() || submittingDocAction) ? 'not-allowed' : 'pointer',
                            opacity: (!confirmRejectDoc.reason.trim() || submittingDocAction) ? 0.6 : 1,
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem'
                          }}
                        >
                          {submittingDocAction ? 'Submitting...' : '✕ Confirm Rejection'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

              {/* MODAL 3: ENHANCED DOCUMENT PREVIEW MODAL WITH ZOOM */}
              {previewDoc && (
                <div style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(16, 43, 70, 0.75)',
                  zIndex: 10003,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '1.5rem',
                  backdropFilter: 'blur(3px)'
                }}>
                  <div style={{ background: '#FFFFFF', borderRadius: '10px', maxWidth: '850px', width: '100%', maxHeight: '92vh', display: 'flex', flexDirection: 'column', overflow: 'hidden', boxShadow: '0 25px 50px rgba(0,0,0,0.35)', border: '1px solid #D0D5DD' }}>
                    {/* Header */}
                    <div style={{ background: '#102B46', color: '#FFFFFF', padding: '0.9rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                      <div>
                        <div style={{ fontSize: '0.72rem', color: '#98A2B3', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
                          {previewDoc.document_type?.replace(/_/g, ' ')?.toUpperCase()} • PREVIEW
                        </div>
                        <div style={{ fontSize: '0.95rem', fontWeight: 700, marginTop: '0.15rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span>{previewDoc.file_name}</span>
                          {previewDoc.file_size_bytes && (
                            <span style={{ fontSize: '0.75rem', color: '#CBD5E1', fontWeight: 400 }}>
                              ({(previewDoc.file_size_bytes / 1024).toFixed(1)} KB)
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Controls: Zoom, Download, Close */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {/* Zoom Controls */}
                        <div style={{ display: 'inline-flex', alignItems: 'center', background: 'rgba(255,255,255,0.12)', borderRadius: '6px', padding: '0.15rem 0.35rem', border: '1px solid rgba(255,255,255,0.2)' }}>
                          <button
                            type="button"
                            onClick={() => setPreviewZoom(z => Math.max(50, z - 25))}
                            title="Zoom Out"
                            style={{ background: 'transparent', color: '#FFFFFF', border: 'none', padding: '0.2rem 0.4rem', cursor: 'pointer', fontWeight: 700, fontSize: '0.85rem' }}
                          >
                            −
                          </button>
                          <span style={{ fontSize: '0.72rem', color: '#FFFFFF', padding: '0 0.4rem', fontWeight: 600, minWidth: '45px', textAlign: 'center' }}>
                            {previewZoom}%
                          </span>
                          <button
                            type="button"
                            onClick={() => setPreviewZoom(z => Math.min(250, z + 25))}
                            title="Zoom In"
                            style={{ background: 'transparent', color: '#FFFFFF', border: 'none', padding: '0.2rem 0.4rem', cursor: 'pointer', fontWeight: 700, fontSize: '0.85rem' }}
                          >
                            +
                          </button>
                          <button
                            type="button"
                            onClick={() => setPreviewZoom(100)}
                            title="Reset Zoom (100%)"
                            style={{ background: 'rgba(255,255,255,0.15)', color: '#FFFFFF', border: 'none', borderRadius: '4px', padding: '0.15rem 0.35rem', marginLeft: '0.2rem', cursor: 'pointer', fontSize: '0.68rem', fontWeight: 600 }}
                          >
                            Reset
                          </button>
                        </div>

                        {/* Download Original Button */}
                        <a
                          href={`${previewDoc.download_url}?token=${token}`}
                          target="_blank"
                          rel="noreferrer"
                          download={previewDoc.file_name}
                          style={{
                            background: '#EFF4FF',
                            color: '#155EEF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.35rem 0.75rem',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            textDecoration: 'none',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.3rem'
                          }}
                        >
                          ⬇️ Download
                        </a>

                        {/* Close Modal Button */}
                        <button
                          onClick={() => setPreviewDoc(null)}
                          style={{ background: 'rgba(255,255,255,0.2)', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.35rem 0.65rem', cursor: 'pointer', fontWeight: 700 }}
                          title="Close preview"
                        >
                          ✕
                        </button>
                      </div>
                    </div>

                    {/* Preview Content Area */}
                    <div style={{ padding: '1.25rem', flex: 1, overflow: 'auto', display: 'flex', justifyContent: 'center', alignItems: 'center', background: '#F8F9FA' }}>
                      {previewDoc.mime_type && previewDoc.mime_type.startsWith('image/') ? (
                        <div style={{ overflow: 'auto', maxHeight: '72vh', width: '100%', display: 'flex', justifyContent: 'center' }}>
                          <img
                            src={`${previewDoc.download_url}?token=${token}`}
                            alt={previewDoc.file_name}
                            style={{
                              transform: `scale(${previewZoom / 100})`,
                              transformOrigin: 'top center',
                              transition: 'transform 0.15s ease',
                              maxWidth: '100%',
                              objectFit: 'contain',
                              borderRadius: '6px',
                              boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
                            }}
                          />
                        </div>
                      ) : (
                        <iframe
                          src={`${previewDoc.download_url}?token=${token}`}
                          title={previewDoc.file_name}
                          style={{ width: '100%', height: '70vh', border: 'none', borderRadius: '6px', background: '#FFFFFF' }}
                        />
                      )}
                    </div>

                    {/* Preview Modal Footer with Status & Fast Verification Actions */}
                    <div style={{ padding: '0.75rem 1.25rem', background: '#FFFFFF', borderTop: '1px solid #EAECF0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span style={{ fontSize: '0.78rem', color: '#667085' }}>Current Status:</span>
                        {previewDoc.verification_status === 'verified' && (
                          <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.15rem 0.5rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                            ✓ Verified
                          </span>
                        )}
                        {previewDoc.verification_status === 'pending' && (
                          <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FEDF89', padding: '0.15rem 0.5rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                            ⏳ Pending Review
                          </span>
                        )}
                        {previewDoc.verification_status === 'rejected' && (
                          <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.15rem 0.5rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                            ✕ Rejected
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        {previewDoc.verification_status !== 'verified' && (
                          <button
                            type="button"
                            onClick={() => {
                              const doc = previewDoc;
                              setPreviewDoc(null);
                              setAcceptDocNotes('Document verified and found authentic by institution administrator.');
                              setConfirmAcceptDoc(doc);
                            }}
                            style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', borderRadius: '5px', padding: '0.3rem 0.75rem', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}
                          >
                            ✓ Accept Document
                          </button>
                        )}
                        {previewDoc.verification_status !== 'rejected' && (
                          <button
                            type="button"
                            onClick={() => {
                              const doc = previewDoc;
                              setPreviewDoc(null);
                              setConfirmRejectDoc({ doc, reason: '' });
                            }}
                            style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', borderRadius: '5px', padding: '0.3rem 0.75rem', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}
                          >
                            ✕ Reject Document
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}"""

assert old_modals in code, "old_modals not found"
code = code.replace(old_modals, new_modals, 1)

with open(fe_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("SUCCESS: InstitutionAdminDashboard.jsx successfully patched!")
