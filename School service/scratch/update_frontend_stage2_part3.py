dashboard_path = 'C:/Users/callm/nagriksetu/frontend/src/pages/admin/InstitutionAdminDashboard.jsx'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Locate the Action Panel inside Review Modal
old_action_panel = """                {/* =================================================================
                    ADMINISTRATOR ACTION PANEL (STAGE 1 vs STAGE 2 DIFFERENTIATED)
                    ================================================================= */}
                <div style={{
                  background: '#FFFFFF',
                  border: '1px solid #D0D5DD',
                  borderRadius: '8px',
                  padding: '1.25rem',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <h4 style={{ margin: 0, color: '#102B46', fontSize: '0.95rem', fontWeight: 700 }}>
                      ⚡ Administrator Evaluation Decisions
                    </h4>

                    {/* Action Selector Buttons */}
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button
                        type="button"
                        onClick={() => setActionTab('approve')}
                        style={{
                          background: actionTab === 'approve' ? '#12B76A' : '#F2F4F7',
                          color: actionTab === 'approve' ? '#FFFFFF' : '#344054',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '0.4rem 0.75rem',
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                      >
                        ✓ Approve Stage 1
                      </button>

                      <button
                        type="button"
                        onClick={() => setActionTab('clarify')}
                        style={{
                          background: actionTab === 'clarify' ? '#7A5AF8' : '#F2F4F7',
                          color: actionTab === 'clarify' ? '#FFFFFF' : '#344054',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '0.4rem 0.75rem',
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                      >
                        💬 Request Clarification
                      </button>

                      <button
                        type="button"
                        onClick={() => setActionTab('reject')}
                        style={{
                          background: actionTab === 'reject' ? '#F04438' : '#F2F4F7',
                          color: actionTab === 'reject' ? '#FFFFFF' : '#344054',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '0.4rem 0.75rem',
                          fontSize: '0.8rem',
                          fontWeight: 700,
                          cursor: 'pointer'
                        }}
                      >
                        ✕ Reject Application
                      </button>
                    </div>
                  </div>"""

new_action_panel = """                {/* =================================================================
                    ADMINISTRATOR ACTION PANEL (STAGE 1 vs STAGE 2 DIFFERENTIATED)
                    ================================================================= */}
                {(() => {
                  const isStage2 = ['approved', 'stage2_submitted', 'documents_uploaded', 'detailed_review_completed', 'stage2_correction_requested'].includes(selectedApp.status)
                  const isReviewComplete = selectedApp.status === 'detailed_review_completed'
                  
                  return (
                    <div style={{
                      background: '#FFFFFF',
                      border: '1px solid #D0D5DD',
                      borderRadius: '8px',
                      padding: '1.25rem',
                      marginBottom: '1.5rem'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                        <div>
                          <h4 style={{ margin: 0, color: '#102B46', fontSize: '0.95rem', fontWeight: 700 }}>
                            ⚡ Administrator Evaluation Decisions
                          </h4>
                          <div style={{ fontSize: '0.75rem', color: '#667085', marginTop: '0.15rem' }}>
                            {isStage2 ? (
                              isReviewComplete 
                                ? 'Stage 2 detailed review is completed. Eligible for final seat allotment.'
                                : 'Stage 2 Detailed Review: Verify documents and complete institutional evaluation.'
                            ) : (
                              'Stage 1 Preliminary Review: Verify applicant age and residency to unlock Stage 2.'
                            )}
                          </div>
                        </div>

                        {/* Action Selector Buttons */}
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                          {!isStage2 ? (
                            /* STAGE 1 ACTIONS */
                            <button
                              type="button"
                              onClick={() => setActionTab('approve')}
                              style={{
                                background: actionTab === 'approve' ? '#12B76A' : '#F2F4F7',
                                color: actionTab === 'approve' ? '#FFFFFF' : '#344054',
                                border: 'none',
                                borderRadius: '6px',
                                padding: '0.4rem 0.75rem',
                                fontSize: '0.8rem',
                                fontWeight: 700,
                                cursor: 'pointer'
                              }}
                            >
                              ✓ Approve Stage 1
                            </button>
                          ) : (
                            /* STAGE 2 ACTIONS — NEVER RE-SHOW STAGE 1 APPROVAL */
                            <>
                              {!isReviewComplete && (
                                <>
                                  <button
                                    type="button"
                                    onClick={() => setActionTab('stage2_complete')}
                                    style={{
                                      background: actionTab === 'stage2_complete' ? '#12B76A' : '#ECFDF3',
                                      color: actionTab === 'stage2_complete' ? '#FFFFFF' : '#027A48',
                                      border: '1px solid #A6F4C5',
                                      borderRadius: '6px',
                                      padding: '0.4rem 0.75rem',
                                      fontSize: '0.8rem',
                                      fontWeight: 700,
                                      cursor: 'pointer'
                                    }}
                                  >
                                    ✓ Complete Stage 2 Review
                                  </button>

                                  <button
                                    type="button"
                                    onClick={() => setActionTab('stage2_correction')}
                                    style={{
                                      background: actionTab === 'stage2_correction' ? '#F79009' : '#FEF0C7',
                                      color: actionTab === 'stage2_correction' ? '#FFFFFF' : '#B54708',
                                      border: '1px solid #FEDF89',
                                      borderRadius: '6px',
                                      padding: '0.4rem 0.75rem',
                                      fontSize: '0.8rem',
                                      fontWeight: 700,
                                      cursor: 'pointer'
                                    }}
                                  >
                                    📝 Request Correction
                                  </button>
                                </>
                              )}
                            </>
                          )}

                          <button
                            type="button"
                            onClick={() => setActionTab('clarify')}
                            style={{
                              background: actionTab === 'clarify' ? '#7A5AF8' : '#F2F4F7',
                              color: actionTab === 'clarify' ? '#FFFFFF' : '#344054',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.4rem 0.75rem',
                              fontSize: '0.8rem',
                              fontWeight: 700,
                              cursor: 'pointer'
                            }}
                          >
                            💬 Clarification Inquiry
                          </button>

                          <button
                            type="button"
                            onClick={() => setActionTab('reject')}
                            style={{
                              background: actionTab === 'reject' ? '#F04438' : '#F2F4F7',
                              color: actionTab === 'reject' ? '#FFFFFF' : '#344054',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.4rem 0.75rem',
                              fontSize: '0.8rem',
                              fontWeight: 700,
                              cursor: 'pointer'
                            }}
                          >
                            ✕ Reject Application
                          </button>
                        </div>
                      </div>

                      {/* When Stage 2 Detailed Review is already completed */}
                      {isReviewComplete && (
                        <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1rem', color: '#027A48' }}>
                          <div style={{ fontWeight: 700, fontSize: '0.95rem', marginBottom: '0.25rem' }}>
                            ✓ Stage 2 Detailed Review Completed & Verified
                          </div>
                          <p style={{ margin: 0, fontSize: '0.825rem', color: '#05603A' }}>
                            All supporting documents and academic credentials have been verified. The applicant is qualified for final institutional seat allotment and formal enrolment.
                          </p>
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedApp(null)
                              setMainTab('students')
                            }}
                            style={{ marginTop: '0.75rem', background: '#12B76A', color: '#FFFFFF', border: 'none', borderRadius: '6px', padding: '0.45rem 0.9rem', fontWeight: 700, fontSize: '0.8rem', cursor: 'pointer' }}
                          >
                            Open Student Management / Seat Allotment Desk →
                          </button>
                        </div>
                      )}"""

# Replace Action Panel
if old_action_panel in text:
    text = text.replace(old_action_panel, new_action_panel, 1)
    print("Replaced old_action_panel LF successfully!")
else:
    old_crlf = old_action_panel.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_action_panel.replace('\n', '\r\n'), 1)
        print("Replaced old_action_panel CRLF successfully!")
    else:
        print("FAILED to find old_action_panel!")

# Now add the stage 2 form handlers right before closing the action panel
old_form_anchor = """                  {actionTab === 'clarify' && ("""

new_form_anchor = """                  {/* Stage 2 Complete Review Form */}
                  {actionTab === 'stage2_complete' && (
                    <form onSubmit={(e) => { e.preventDefault(); handleStage2ReviewSubmit('detailed_review_completed') }} style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', borderRadius: '8px', padding: '1rem', marginBottom: '0.75rem' }}>
                      <div style={{ fontWeight: 700, color: '#027A48', marginBottom: '0.4rem', fontSize: '0.9rem' }}>
                        Complete Stage 2 Detailed Review
                      </div>
                      <p style={{ margin: '0 0 0.65rem 0', fontSize: '0.825rem', color: '#05603A' }}>
                        Confirm that all demographic information, marks card records, and uploaded certificates have been verified and satisfy institutional criteria.
                      </p>

                      {selectedApp.pending_documents_count > 0 && (
                        <div style={{ marginBottom: '0.75rem', background: '#FEF0C7', border: '1px solid #FEDF89', borderRadius: '6px', padding: '0.5rem 0.75rem', color: '#B54708', fontSize: '0.8rem', fontWeight: 600 }}>
                          ⚠️ Note: {selectedApp.pending_documents_count} document(s) are still pending individual verification.
                        </div>
                      )}

                      <div style={{ marginBottom: '0.75rem' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#05603A', marginBottom: '0.3rem' }}>
                          Review Assessment Notes (Optional)
                        </label>
                        <textarea
                          rows={2}
                          placeholder="e.g. Verified previous marks percentage (76.0%) and all statutory certificates. Ready for final admission."
                          value={stage2ReviewNotes}
                          onChange={(e) => setStage2ReviewNotes(e.target.value)}
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #A6F4C5', fontSize: '0.85rem', boxSizing: 'border-box' }}
                        />
                      </div>

                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          type="submit"
                          disabled={submittingAction}
                          style={{
                            background: '#12B76A',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.5rem 1rem',
                            fontWeight: 700,
                            fontSize: '0.85rem',
                            cursor: 'pointer'
                          }}
                        >
                          {submittingAction ? 'Processing...' : 'Confirm Stage 2 Review Completed'}
                        </button>
                        <button type="button" onClick={() => setActionTab('none')} className="btn btn--secondary btn--sm">
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}

                  {/* Stage 2 Request Correction Form */}
                  {actionTab === 'stage2_correction' && (
                    <form onSubmit={(e) => { e.preventDefault(); handleStage2ReviewSubmit('stage2_correction_requested') }} style={{ background: '#FEF0C7', border: '1px solid #FEDF89', borderRadius: '8px', padding: '1rem', marginBottom: '0.75rem' }}>
                      <div style={{ fontWeight: 700, color: '#B54708', marginBottom: '0.4rem', fontSize: '0.9rem' }}>
                        Request Stage 2 Correction from Parent
                      </div>
                      <p style={{ margin: '0 0 0.65rem 0', fontSize: '0.825rem', color: '#7A2E0E' }}>
                        Specify the demographic or academic information that requires correction by the parent. The application status will reflect Stage 2 Correction Requested.
                      </p>

                      <div style={{ marginBottom: '0.75rem' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#7A2E0E', marginBottom: '0.3rem' }}>
                          Correction Instructions <span style={{ color: '#F04438' }}>*</span>
                        </label>
                        <textarea
                          rows={3}
                          required
                          placeholder="e.g. Previous marks percentage does not match the uploaded marks card. Please update with exact score."
                          value={stage2ReviewNotes}
                          onChange={(e) => setStage2ReviewNotes(e.target.value)}
                          style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #FEDF89', fontSize: '0.85rem', boxSizing: 'border-box' }}
                        />
                      </div>

                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button
                          type="submit"
                          disabled={submittingAction || !stage2ReviewNotes.trim()}
                          style={{
                            background: '#F79009',
                            color: '#FFFFFF',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '0.5rem 1rem',
                            fontWeight: 700,
                            fontSize: '0.85rem',
                            cursor: 'pointer'
                          }}
                        >
                          {submittingAction ? 'Processing...' : 'Send Correction Request'}
                        </button>
                        <button type="button" onClick={() => setActionTab('none')} className="btn btn--secondary btn--sm">
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}

                  {actionTab === 'clarify' && ("""

if old_form_anchor in text:
    text = text.replace(old_form_anchor, new_form_anchor, 1)
    print("Replaced old_form_anchor LF successfully!")
else:
    old_form_crlf = old_form_anchor.replace('\n', '\r\n')
    if old_form_crlf in text:
        text = text.replace(old_form_crlf, new_form_anchor.replace('\n', '\r\n'), 1)
        print("Replaced old_form_anchor CRLF successfully!")
    else:
        print("FAILED to find old_form_anchor!")

# Also close the isStage2 IIFE around line 3646
old_panel_close = """                  )}
                </div>

                {/* =================================================================
                    APPLICATION HISTORY / AUDIT TRAIL"""

new_panel_close = """                  )}
                    </div>
                  )
                })()}

                {/* =================================================================
                    APPLICATION HISTORY / AUDIT TRAIL"""

if old_panel_close in text:
    text = text.replace(old_panel_close, new_panel_close, 1)
    print("Replaced old_panel_close LF successfully!")
else:
    old_panel_close_crlf = old_panel_close.replace('\n', '\r\n')
    if old_panel_close_crlf in text:
        text = text.replace(old_panel_close_crlf, new_panel_close.replace('\n', '\r\n'), 1)
        print("Replaced old_panel_close CRLF successfully!")
    else:
        print("FAILED to find old_panel_close!")

# Append floating document modals right before `{/* Modal Footer */}`
old_modal_footer = """              {/* Modal Footer */}"""

new_modals_and_footer = """              {/* Floating Document Action Modal (Re-upload Request / Rejection) */}
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
              )}

              {/* Modal Footer */}"""

if old_modal_footer in text:
    text = text.replace(old_modal_footer, new_modals_and_footer, 1)
    print("Replaced old_modal_footer LF successfully!")
else:
    old_modal_footer_crlf = old_modal_footer.replace('\n', '\r\n')
    if old_modal_footer_crlf in text:
        text = text.replace(old_modal_footer_crlf, new_modals_and_footer.replace('\n', '\r\n'), 1)
        print("Replaced old_modal_footer CRLF successfully!")
    else:
        print("FAILED to find old_modal_footer!")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved stage 3 of frontend update.")
