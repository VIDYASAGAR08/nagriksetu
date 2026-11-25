with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace the handlers block
start_handler = "  // Centralised Student ID Child Lookup\n  async function handleCentralisedStudentLookup"
end_handler = "  // View Child Academic Records"

start_idx = text.find(start_handler)
end_idx = text.find(end_handler)

if start_idx != -1 and end_idx != -1:
    new_handlers = """  // Centralised Student ID Child Lookup (Module 1 - Step 1)
  async function handleCentralisedStudentLookup(e) {
    if (e) e.preventDefault()
    const target = linkStudentIdInput.trim()
    if (!target) {
      setLookupChildError('Please enter a valid centralised Student ID.')
      return
    }
    setIsLookingUpId(true)
    setLookupChildError('')
    setLookupChildResult(null)
    setSubmitLinkingSuccess(null)

    try {
      const res = await apiGet(`/parent/lookup-by-student-id?student_id=${encodeURIComponent(target)}`, token)
      setLookupChildResult(res)
    } catch (err) {
      setLookupChildResult(null)
      setLookupChildError(err.message || `No student record found matching Student ID '${target}'.`)
    } finally {
      setIsLookingUpId(false)
    }
  }

  // Submit Linking Request for Institution Review (Module 1 - Step 2 & 3)
  async function handleSubmitLinkingRequest() {
    if (!lookupChildResult?.student_id) return
    setIsSubmittingLink(true)
    setSubmitLinkingSuccess(null)
    setLookupChildError('')
    try {
      const payload = {
        student_ref: lookupChildResult.student_id,
        student_id: lookupChildResult.student_id,
        school_id: lookupChildResult.institution_id,
        permanent_student_id: lookupChildResult.permanent_student_id,
        relationship_type: linkRelationship,
      }
      const res = await apiPost('/parent/linking-requests', payload, token)
      setSubmitLinkingSuccess(res.message || `Your request has been submitted successfully to ${lookupChildResult.institution_name}. The institution will review and notify you of its decision.`)
      // Refresh requests list
      const reqData = await apiGet('/parent/linking-requests', token).catch(() => [])
      setRequests(Array.isArray(reqData) ? reqData : [])
    } catch (err) {
      setLookupChildError(err.message || 'Failed to submit linking request. Check for pending duplicates.')
    } finally {
      setIsSubmittingLink(false)
    }
  }

  // Parent response to institution clarification (Module 3)
  async function handleRespondClarification(requestId) {
    const text = (clarificationResponses[requestId] || '').trim()
    if (!text) {
      setClarificationFeedback(prev => ({ ...prev, [requestId]: { type: 'error', message: 'Please enter your clarification response before submitting.' } }))
      return
    }
    setSubmittingClarificationId(requestId)
    setClarificationFeedback(prev => ({ ...prev, [requestId]: null }))
    try {
      const res = await apiPost(`/parent/linking-requests/${requestId}/respond-clarification`, {
        response_notes: text
      }, token)
      setClarificationFeedback(prev => ({ ...prev, [requestId]: { type: 'success', message: res.message || 'Clarification submitted. Waiting for institution review.' } }))
      // Refresh requests list
      const reqData = await apiGet('/parent/linking-requests', token).catch(() => [])
      setRequests(Array.isArray(reqData) ? reqData : [])
    } catch (err) {
      setClarificationFeedback(prev => ({ ...prev, [requestId]: { type: 'error', message: err.message || 'Failed to submit clarification.' } }))
    } finally {
      setSubmittingClarificationId(null)
    }
  }

  function handleResetLookup() {
    setLookupChildResult(null)
    setSubmitLinkingSuccess(null)
    setLookupChildError('')
  }

"""
    text = text[:start_idx] + new_handlers + text[end_idx:]
    print("Replaced handlers successfully.")
else:
    print(f"Error finding handler markers: {start_idx}, {end_idx}")

# 2. Replace activeTab === 'history' block
history_marker = "        {activeTab === 'history' && ("
admissions_marker = "        {/* TAB 4: Admission Applications */}"

hist_start = text.find(history_marker)
adm_start = text.find(admissions_marker)

if hist_start != -1 and adm_start != -1:
    new_history = """        {activeTab === 'history' && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#1a3a6b', fontWeight: 700 }}>
                  My Child Linking Requests
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', color: '#64748B', fontSize: '0.85rem' }}>
                  Track the verification status of student-linking requests submitted to educational institutions.
                </p>
              </div>
              <button onClick={() => switchTab('link-child')} className="btn btn--primary btn--sm" style={{ fontWeight: 600 }}>
                + Submit New Linking Request
              </button>
            </div>

            {loading ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
              </div>
            ) : requests.length === 0 ? (
              <div className="card" style={{ padding: '3rem', textAlign: 'center', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📂</div>
                <h3 style={{ color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>No Linking Requests Submitted</h3>
                <p style={{ color: '#4b5563', margin: '0 0 1rem 0' }}>You have not submitted any child linking requests yet.</p>
                <button onClick={() => switchTab('link-child')} className="btn btn--primary">
                  Link My Child Now →
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {requests.map(r => {
                  const status = (r.request_status || r.status || '').toLowerCase()
                  const isApproved = status === 'approved'
                  const isRejected = status === 'rejected'
                  const isClarify = status === 'clarification_required'
                  const isPendingReview = status === 'pending_review'
                  const isPending = status === 'pending'

                  return (
                    <div
                      key={r.request_id}
                      className="card"
                      style={{
                        padding: '1.25rem 1.5rem',
                        border: isApproved ? '1px solid #A7F3D0' : isRejected ? '1px solid #FCA5A5' : isClarify ? '1px solid #FCD34D' : isPendingReview ? '1px solid #BAE6FD' : '1px solid #E2E8F0',
                        borderRadius: '10px',
                        background: '#FFFFFF',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '0.85rem' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                            <h4 style={{ margin: 0, fontSize: '1.15rem', color: '#102B46', fontWeight: 700 }}>
                              {r.student_name || r.student_ref}
                            </h4>
                            <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.85rem', background: '#EFF8FF', color: '#175CD3', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                              ID: {r.student_id || r.student_ref}
                            </span>
                            {r.permanent_student_id && (
                              <span style={{ fontFamily: 'monospace', fontSize: '0.78rem', color: '#64748B' }}>
                                PSID: {r.permanent_student_id}
                              </span>
                            )}
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#475467', marginTop: '0.25rem' }}>
                            🏛️ <strong>{r.institution_name || r.school_name || r.school_id}</strong> · {r.institution_type || 'Accredited Institution'}
                            {r.class_or_standard && ` · ${r.class_or_standard}`}
                            {r.program_or_stream && ` · ${r.program_or_stream}`}
                          </div>
                        </div>

                        <div>
                          {isApproved && (
                            <span style={{ background: '#ECFDF5', color: '#027A48', border: '1px solid #A7F3D0', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ✓ VERIFIED & APPROVED
                            </span>
                          )}
                          {isRejected && (
                            <span style={{ background: '#FEF2F2', color: '#B42318', border: '1px solid #FCA5A5', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ✕ REJECTED
                            </span>
                          )}
                          {isClarify && (
                            <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FCD34D', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ⚠️ CLARIFICATION REQUIRED
                            </span>
                          )}
                          {isPendingReview && (
                            <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              ⏳ PENDING REVIEW
                            </span>
                          )}
                          {isPending && (
                            <span style={{ background: '#F2F4F7', color: '#344054', border: '1px solid #D0D5DD', padding: '0.35rem 0.75rem', borderRadius: '16px', fontWeight: 700, fontSize: '0.825rem' }}>
                              🕒 PENDING APPROVAL
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Request details row */}
                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', background: '#F8FAFC', padding: '0.75rem 1rem', borderRadius: '6px', fontSize: '0.825rem', marginBottom: '0.85rem' }}>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Relationship Claimed:</span>
                          <strong>{r.relationship || r.relationship_type || 'Parent'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Request Submitted:</span>
                          <strong>{r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recent'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Decision / Review Date:</span>
                          <strong>{r.decision_date || r.reviewed_at ? new Date(r.decision_date || r.reviewed_at).toLocaleDateString() : 'Awaiting Review'}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748B', display: 'block' }}>Request Reference ID:</span>
                          <span style={{ fontFamily: 'monospace' }}>{r.request_id.slice(0, 8)}...</span>
                        </div>
                      </div>

                      {/* Status-specific banners and interactions */}
                      {isApproved && (
                        <div style={{ background: '#ECFDF5', border: '1px solid #D1FADF', borderRadius: '6px', padding: '0.85rem 1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                          <div>
                            <span style={{ color: '#027A48', fontWeight: 600, fontSize: '0.85rem' }}>
                              ✓ Approved by Institution Administrator. Your child's academic dashboard and official records are verified and active.
                            </span>
                            {r.reviewer_comment && (
                              <div style={{ fontSize: '0.8rem', color: '#065F46', marginTop: '0.2rem' }}>
                                Remarks: "{r.reviewer_comment}"
                              </div>
                            )}
                          </div>
                          <button
                            type="button"
                            onClick={() => switchTab('children')}
                            className="btn btn--primary btn--sm"
                            style={{ fontWeight: 600 }}
                          >
                            Open Child Academic Dashboard →
                          </button>
                        </div>
                      )}

                      {isRejected && (
                        <div style={{ background: '#FEF2F2', border: '1px solid #FEE4E2', borderRadius: '6px', padding: '0.85rem 1rem' }}>
                          <div style={{ color: '#B42318', fontWeight: 700, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                            ✕ Linking Request Not Approved by {r.institution_name || r.school_name || 'Institution'}
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#991B1B', lineHeight: 1.5 }}>
                            <strong>Rejection Reason:</strong> {r.rejection_reason || 'Verification requirements not satisfied.'}
                          </div>
                          {r.reviewer_comment && r.reviewer_comment !== r.rejection_reason && (
                            <div style={{ fontSize: '0.825rem', color: '#7F1D1D', marginTop: '0.25rem' }}>
                              <strong>Administrator Remarks:</strong> {r.reviewer_comment}
                            </div>
                          )}
                          <div style={{ fontSize: '0.78rem', color: '#B42318', marginTop: '0.4rem' }}>
                            ⚠️ Access to this student's records remains restricted. If you believe this is an error, please contact the institution office directly.
                          </div>
                        </div>
                      )}

                      {isClarify && (
                        <div style={{ background: '#FFFAEB', border: '1px solid #FEF0C7', borderRadius: '6px', padding: '1rem' }}>
                          <div style={{ color: '#B54708', fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.35rem' }}>
                            ⚠️ Institution Requests Clarification
                          </div>
                          <div style={{ fontSize: '0.85rem', color: '#7A2E0E', marginBottom: '0.85rem', background: '#FFFFFF', padding: '0.65rem 0.85rem', borderRadius: '6px', border: '1px solid #FEDF89' }}>
                            <strong>Institution Remarks / Instructions:</strong> {r.reviewer_comment || 'Please provide additional documentation confirming your relationship.'}
                          </div>

                          {clarificationFeedback[r.request_id] && (
                            <div style={{ marginBottom: '0.75rem', padding: '0.5rem 0.75rem', borderRadius: '6px', fontSize: '0.85rem', background: clarificationFeedback[r.request_id].type === 'success' ? '#ECFDF5' : '#FEF2F2', color: clarificationFeedback[r.request_id].type === 'success' ? '#027A48' : '#B42318' }}>
                              {clarificationFeedback[r.request_id].message}
                            </div>
                          )}

                          <div>
                            <label style={{ display: 'block', fontWeight: 600, color: '#475467', fontSize: '0.825rem', marginBottom: '0.35rem' }}>
                              Your Clarification Response / Documentation Details:
                            </label>
                            <textarea
                              rows={3}
                              value={clarificationResponses[r.request_id] || ''}
                              onChange={(e) => setClarificationResponses(prev => ({ ...prev, [r.request_id]: e.target.value }))}
                              placeholder="Enter your response, explanation, or document reference numbers requested by the institution..."
                              style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.85rem', fontFamily: 'inherit', resize: 'vertical', boxSizing: 'border-box' }}
                              disabled={submittingClarificationId === r.request_id}
                            />
                            <button
                              type="button"
                              onClick={() => handleRespondClarification(r.request_id)}
                              disabled={submittingClarificationId === r.request_id || !(clarificationResponses[r.request_id] || '').trim()}
                              className="btn btn--primary btn--sm"
                              style={{ marginTop: '0.5rem', fontWeight: 700 }}
                            >
                              {submittingClarificationId === r.request_id ? 'Submitting Clarification...' : 'Submit Response to Institution →'}
                            </button>
                          </div>
                        </div>
                      )}

                      {isPendingReview && (
                        <div style={{ background: '#EFF8FF', border: '1px solid #B2DDFF', borderRadius: '6px', padding: '0.85rem 1rem' }}>
                          <div style={{ color: '#175CD3', fontWeight: 700, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                            ⏳ Clarification Under Institution Review
                          </div>
                          {r.parent_response && (
                            <div style={{ fontSize: '0.85rem', color: '#1E40AF', marginTop: '0.25rem', background: '#FFFFFF', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #D1E9FF' }}>
                              <strong>Your Submitted Response:</strong> "{r.parent_response}"
                            </div>
                          )}
                          <div style={{ fontSize: '0.78rem', color: '#475467', marginTop: '0.35rem' }}>
                            The institution has received your response and is re-evaluating your linking request.
                          </div>
                        </div>
                      )}

                      {isPending && (
                        <div style={{ background: '#F8FAFC', border: '1px solid #EAECF0', borderRadius: '6px', padding: '0.75rem 1rem', color: '#475467', fontSize: '0.85rem' }}>
                          🕒 <strong>Awaiting Institution Review:</strong> Your request is queued for administrative verification at {r.institution_name || r.school_name || 'the institution'}. You will receive a notification once decided.
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )}\n\n"""
    text = text[:hist_start] + new_history + text[adm_start:]
    print("Replaced activeTab history successfully.")
else:
    print(f"Error finding history markers: {hist_start}, {adm_start}")

with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("ParentDashboard.jsx completely updated.")
