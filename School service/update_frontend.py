import re

# -------------------------------------------------------------
# 1. Update ParentDashboard.jsx
# -------------------------------------------------------------
with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'r', encoding='utf-8') as f:
    parent_jsx = f.read()

# Add new states
old_state_marker = "  const [verificationError, setVerificationError] = useState('')"
new_states = """  const [verificationError, setVerificationError] = useState('')
  const [submitLinkingSuccess, setSubmitLinkingSuccess] = useState(null)
  const [clarificationResponses, setClarificationResponses] = useState({})
  const [submittingClarificationId, setSubmittingClarificationId] = useState(null)
  const [clarificationFeedback, setClarificationFeedback] = useState({})"""

if old_state_marker in parent_jsx:
    parent_jsx = parent_jsx.replace(old_state_marker, new_states, 1)
    print("Added new state variables to ParentDashboard.jsx")
else:
    print("WARNING: old_state_marker not found in ParentDashboard.jsx")

# Replace lookup and verification handlers
old_handlers = """  // Centralised Student ID Child Lookup
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
    setLinkingCodeIssued(false)
    setVerificationCodeInput('')
    setVerificationError('')

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

  // Request Institution-Issued Verification Code
  async function handleRequestLinkingCode() {
    if (!lookupChildResult?.student_id) return
    setIsRequestingCode(true)
    setVerificationError('')
    try {
      await apiPost('/parent/request-linking-code', {
        student_id: lookupChildResult.student_id,
        relationship_type: linkRelationship
      }, token)
      setLinkingCodeIssued(true)
      setVerificationCodeInput('')
      setResendCooldown(30)
    } catch (err) {
      setVerificationError(err.message || 'Failed to request institution verification code.')
    } finally {
      setIsRequestingCode(false)
    }
  }

  // Verify Code and Link Child
  async function handleVerifyAndLinkChild(e) {
    if (e) e.preventDefault()
    const code = verificationCodeInput.trim()
    if (!code) {
      setVerificationError('Please enter the 6-digit verification code.')
      return
    }
    setIsSubmittingLink(true)
    setVerificationError('')
    try {
      const payload = {
        student_id: lookupChildResult.student_id,
        verification_code: code,
        relationship_type: linkRelationship
      }
      const res = await apiPost('/parent/verify-and-link-child', payload, token)
      setSuccess(res.message || `Successfully verified and linked ${lookupChildResult.student_full_name} to your parent account!`)
      
      // Reset form
      setLookupChildResult(null)
      setLinkStudentIdInput('')
      setLinkingCodeIssued(false)
      setVerificationCodeInput('')
      setResendCooldown(0)
      
      // Reload children and switch tab
      await loadData()
      switchTab('children')
    } catch (err) {
      setVerificationError(err.message || 'Verification failed. Please check the code and try again.')
    } finally {
      setIsSubmittingLink(false)
    }
  }

  function handleResetLookup() {
    setLookupChildResult(null)
    setLinkingCodeIssued(false)
    setVerificationCodeInput('')
    setLookupChildError('')
  }"""

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
  }"""

if old_handlers in parent_jsx:
    parent_jsx = parent_jsx.replace(old_handlers, new_handlers, 1)
    print("Replaced linking handlers in ParentDashboard.jsx")
else:
    print("WARNING: old_handlers not found in ParentDashboard.jsx")

# Replace Tab 2: Link Your Child JSX
old_tab_pattern = r'\{\/\* Tab: Link Your Child Using Centralised Student ID \*\/\}[\s\S]*?(?=\{\/\* Tab 2: New Linking Request Form)'
new_tab_jsx = """{/* Tab: Link My Child Using Centralised Student ID */}
        {activeTab === 'link-child' && (
          <div className="card" style={{ maxWidth: '850px', margin: '0 auto', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', boxShadow: '0 2px 6px rgba(0,0,0,0.04)' }}>
            <div style={{ marginBottom: '1.75rem', borderBottom: '1px solid #e8eaed', paddingBottom: '1rem' }}>
              <div style={{ display: 'inline-block', background: '#EFF4FF', color: '#155EEF', fontWeight: 700, padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.35rem', textTransform: 'uppercase' }}>
                Centralised Student Verification
              </div>
              <h2 style={{ fontSize: '1.45rem', color: '#1a3a6b', margin: '0 0 0.35rem 0', fontWeight: 700 }}>
                Link My Child
              </h2>
              <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0, lineHeight: 1.5 }}>
                Enter your child's exact centralised Student ID. The system retrieves official enrollment details directly from the live institution database. Upon your confirmation, a formal verification request is submitted to the educational institution for review and approval.
              </p>
            </div>

            {/* STEP 1: Enter Student ID */}
            <div style={{ marginBottom: '1.5rem', padding: '1.25rem', border: '1px solid #E2E8F0', borderRadius: '8px', background: '#F8FAFC' }}>
              <form onSubmit={handleCentralisedStudentLookup}>
                <label style={{ display: 'block', fontWeight: 600, color: '#1e293b', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
                  Student ID <span style={{ color: '#b91c1c' }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <input
                    type="text"
                    value={linkStudentIdInput}
                    onChange={(e) => {
                      setLinkStudentIdInput(e.target.value.toUpperCase())
                      setLookupChildError('')
                      setSubmitLinkingSuccess(null)
                    }}
                    placeholder="e.g. BSDS260001, PCMB260001, COL03001, 20260001"
                    style={{ flex: 1, minWidth: '240px', padding: '0.7rem 0.9rem', fontSize: '1rem', fontWeight: 600, fontFamily: 'monospace', border: '1px solid #cbd5e1', borderRadius: '6px', letterSpacing: '0.5px' }}
                    disabled={isLookingUpId}
                  />
                  <button
                    type="submit"
                    className="btn btn--primary"
                    disabled={isLookingUpId || !linkStudentIdInput.trim()}
                    style={{ minWidth: '150px', fontWeight: 600 }}
                  >
                    {isLookingUpId ? 'Searching...' : 'Search Student 🔍'}
                  </button>
                  {lookupChildResult && (
                    <button
                      type="button"
                      onClick={handleResetLookup}
                      className="btn btn--secondary"
                      style={{ fontSize: '0.85rem' }}
                    >
                      Reset
                    </button>
                  )}
                </div>
                <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#64748b' }}>
                  💡 Supported IDs across all institutions: Schools (<code>20260001</code>), PU Colleges (<code>PCMB260001</code>, <code>PCMC260001</code>, <code>HEBA260001</code>), Degree & Engineering (<code>BSDS260001</code>, <code>BCA260001</code>, <code>COL03001</code>).
                </div>
              </form>
            </div>

            {/* Error during lookup */}
            {lookupChildError && (
              <Alert type="error" title="Lookup Unsuccessful" className="mb-4">
                {lookupChildError}
              </Alert>
            )}

            {/* Success message on submission */}
            {submitLinkingSuccess && (
              <div style={{ background: '#ECFDF5', border: '1px solid #A7F3D0', borderRadius: '8px', padding: '1.25rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', color: '#065F46', fontWeight: 700, fontSize: '1rem', marginBottom: '0.35rem' }}>
                  <span>✓</span> Request Submitted Successfully
                </div>
                <p style={{ color: '#047857', fontSize: '0.9rem', margin: '0 0 1rem 0', lineHeight: 1.5 }}>
                  {submitLinkingSuccess}
                </p>
                <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                  <button
                    type="button"
                    onClick={() => switchTab('history')}
                    className="btn btn--primary btn--sm"
                    style={{ fontWeight: 600 }}
                  >
                    Track in "My Child Linking Requests" →
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setLookupChildResult(null)
                      setSubmitLinkingSuccess(null)
                      setLinkStudentIdInput('')
                    }}
                    className="btn btn--secondary btn--sm"
                  >
                    Link Another Child
                  </button>
                </div>
              </div>
            )}

            {/* STEP 2: Display Student Details & Confirmation Card */}
            {lookupChildResult && !submitLinkingSuccess && (
              <div style={{ border: '1px solid #B9E6FE', borderRadius: '8px', background: '#F0F9FF', padding: '1.5rem', marginBottom: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem', borderBottom: '1px solid #BAE6FD', paddingBottom: '0.75rem' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0284C7', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Step 2: Review Official Student Details
                    </span>
                    <h3 style={{ fontSize: '1.25rem', color: '#0C4A6E', margin: '0.2rem 0 0 0', fontWeight: 700 }}>
                      {lookupChildResult.student_full_name}
                    </h3>
                  </div>
                  <span className="badge badge--primary" style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.9rem', padding: '0.3rem 0.6rem' }}>
                    {lookupChildResult.student_id}
                  </span>
                </div>

                <p style={{ color: '#0369A1', fontSize: '0.875rem', marginBottom: '1rem' }}>
                  The following details were retrieved directly from the live institution database:
                </p>

                {/* Database details grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', background: '#FFFFFF', padding: '1.25rem', borderRadius: '6px', border: '1px solid #E0F2FE', marginBottom: '1.25rem' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Student Full Name:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.95rem' }}>{lookupChildResult.student_full_name}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Student ID:</span>
                    <strong style={{ color: '#155EEF', fontFamily: 'monospace', fontSize: '0.95rem' }}>{lookupChildResult.student_id}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Permanent Student ID (PSID):</span>
                    <strong style={{ color: '#334155', fontFamily: 'monospace', fontSize: '0.9rem' }}>{lookupChildResult.permanent_student_id}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Institution Name:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.9rem' }}>{lookupChildResult.institution_name}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Institution ID:</span>
                    <strong style={{ color: '#475569', fontFamily: 'monospace', fontSize: '0.85rem' }}>{lookupChildResult.institution_id}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Institution Type:</span>
                    <span style={{ color: '#334155', fontWeight: 600, fontSize: '0.85rem' }}>{lookupChildResult.institution_type || lookupChildResult.category || 'Accredited Institution'}</span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Class / Standard:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>
                      {lookupChildResult.class_or_standard || `Standard ${lookupChildResult.standard}`}
                    </strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Section:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>Section {lookupChildResult.section || 'A'}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Programme / Stream:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.program_or_stream || 'General Academic'}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Academic Year:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.academic_year || '2026-2027'}</strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, display: 'block' }}>Semester:</span>
                    <strong style={{ color: '#0F172A', fontSize: '0.875rem' }}>{lookupChildResult.semester ? `Semester ${lookupChildResult.semester}` : 'Not Applicable'}</strong>
                  </div>
                </div>

                {/* Already linked check */}
                {lookupChildResult.is_already_linked ? (
                  <div style={{ background: '#FEF3C7', border: '1px solid #FCD34D', borderRadius: '6px', padding: '1rem', color: '#92400E', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <strong>✓ Already Verified:</strong> This child is already verified and linked to your parent account.
                    </div>
                    <button
                      type="button"
                      onClick={() => switchTab('children')}
                      className="btn btn--primary btn--sm"
                    >
                      View on Dashboard →
                    </button>
                  </div>
                ) : (
                  /* Relationship Selection & Actions */
                  <div style={{ borderTop: '1px solid #BAE6FD', paddingTop: '1.25rem' }}>
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontWeight: 600, color: '#0C4A6E', marginBottom: '0.4rem', fontSize: '0.875rem' }}>
                        Select Your Relationship to {lookupChildResult.student_full_name} <span style={{ color: '#b91c1c' }}>*</span>:
                      </label>
                      <select
                        value={linkRelationship}
                        onChange={(e) => setLinkRelationship(e.target.value)}
                        style={{ maxWidth: '280px', padding: '0.6rem 0.85rem', border: '1px solid #94A3B8', borderRadius: '6px', fontWeight: 600, fontSize: '0.9rem', background: '#FFFFFF' }}
                      >
                        <option value="Mother">Mother</option>
                        <option value="Father">Father</option>
                        <option value="Legal Guardian">Legal Guardian</option>
                        <option value="Other Guardian">Other Guardian</option>
                      </select>
                    </div>

                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
                      <button
                        type="button"
                        onClick={handleSubmitLinkingRequest}
                        className="btn btn--primary"
                        disabled={isSubmittingLink}
                        style={{ fontWeight: 700 }}
                      >
                        {isSubmittingLink ? 'Submitting to Institution...' : 'Confirm & Submit for Verification →'}
                      </button>
                      <button
                        type="button"
                        onClick={handleResetLookup}
                        className="btn btn--secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        """

match_tab = re.search(old_tab_pattern, parent_jsx)
if match_tab:
    parent_jsx = parent_jsx[:match_tab.start()] + new_tab_jsx + parent_jsx[match_tab.end():]
    print("Replaced Tab link-child JSX successfully.")
else:
    print("WARNING: old_tab_pattern not found in ParentDashboard.jsx")

# Replace Tab 3: Request History JSX
old_history_pattern = r'\{\/\* TAB 3: Linking Requests History \*\/\}[\s\S]*?(?=\{\/\* TAB 4: Admission Applications \*\/})'
new_history_jsx = """{/* TAB 3: My Child Linking Requests */}
        {activeTab === 'history' && (
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
        )}
        """

match_hist = re.search(old_history_pattern, parent_jsx)
if match_hist:
    parent_jsx = parent_jsx[:match_hist.start()] + new_history_jsx + parent_jsx[match_hist.end():]
    print("Replaced Tab 3 Request History JSX successfully.")
else:
    print("WARNING: old_history_pattern not found in ParentDashboard.jsx")

# Also rename the tab navigation label
parent_jsx = parent_jsx.replace("Request History ({requests.length})", "My Child Linking Requests ({requests.length})")
parent_jsx = parent_jsx.replace("🔗 Link Your Child", "🔗 Link My Child")
parent_jsx = parent_jsx.replace("+ Link Your Child", "+ Link My Child")

with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\parent\ParentDashboard.jsx', 'w', encoding='utf-8') as f:
    f.write(parent_jsx)

print("ParentDashboard.jsx updated successfully.")
