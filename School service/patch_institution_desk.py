with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Locate subtab 2 start
subtab2_marker = "{/* SUB-TAB 2: DATA CORRECTION REQUESTS */}"
subtab2_idx = text.find(subtab2_marker)

# Locate modal 1 and 2 start
modal1_marker = "{/* MODAL 1: OFFICIAL VERIFICATION CODE ISSUED"
modal1_idx = text.find(modal1_marker)

# Locate update review modal start
update_modal_marker = "{/* MODAL 3: REVIEW UPDATE REQUEST */}"
update_modal_idx = text.find(update_modal_marker)

print(f"subtab2_idx: {subtab2_idx}, modal1_idx: {modal1_idx}, update_modal_idx: {update_modal_idx}")

# We will construct the top half (from import to before subtab2), then keep subtab2, then add the new modals (approve, clarify, reject), then keep update review modal to the end.

top_half = """import React, { useState, useEffect, useCallback } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'
import StatusBadge from '../ui/StatusBadge.jsx'

export default function InstitutionParentRequestsDesk({ token, institutionId }) {
  // Desk Sub-tab: 'linking' (Parent / Guardian Verification Requests) | 'updates' (Data Correction Requests)
  const [deskTab, setDeskTab] = useState('linking')

  // --- 1. Parent Linking Requests State ---
  const [linkingRequests, setLinkingRequests] = useState([])
  const [loadingLinking, setLoadingLinking] = useState(true)
  const [linkingError, setLinkingError] = useState('')
  const [linkingStatusFilter, setLinkingStatusFilter] = useState('all')

  // Linking Review Modals State
  const [selectedLinkingRequest, setSelectedLinkingRequest] = useState(null)
  const [submittingLinkingReview, setSubmittingLinkingReview] = useState(false)
  const [linkingFeedback, setLinkingFeedback] = useState(null)

  // Actions Modals
  const [showApproveModal, setShowApproveModal] = useState(false)
  const [approveRemarks, setApproveRemarks] = useState('')

  const [showClarifyModal, setShowClarifyModal] = useState(false)
  const [clarifyRemarks, setClarifyRemarks] = useState('')

  const [showRejectModal, setShowRejectModal] = useState(false)
  const [rejectReason, setRejectReason] = useState('Identity and relationship documents could not be verified')
  const [rejectRemarks, setRejectRemarks] = useState('')

  // --- 2. Data Correction Requests State ---
  const [updateRequests, setUpdateRequests] = useState([])
  const [loadingUpdates, setLoadingUpdates] = useState(false)
  const [updateError, setUpdateError] = useState('')
  const [updateStatusFilter, setUpdateStatusFilter] = useState('all')

  // Update Review Modal
  const [selectedUpdateRequest, setSelectedUpdateRequest] = useState(null)
  const [updateReviewAction, setUpdateReviewAction] = useState('none')
  const [updateRemarks, setUpdateRemarks] = useState('')
  const [submittingUpdateReview, setSubmittingUpdateReview] = useState(false)
  const [updateReviewFeedback, setUpdateReviewFeedback] = useState(null)

  // Fetch Linking Requests
  const loadLinkingRequests = useCallback(async () => {
    if (!token || !institutionId) return
    try {
      setLoadingLinking(true)
      setLinkingError('')
      const data = await apiGet(`/institution/${institutionId}/linking-requests?status_filter=${linkingStatusFilter}`, token)
      setLinkingRequests(Array.isArray(data) ? data : (data.requests || []))
    } catch (err) {
      setLinkingError(err.message || 'Failed to retrieve parent linking requests.')
    } finally {
      setLoadingLinking(false)
    }
  }, [token, institutionId, linkingStatusFilter])

  // Fetch Update Requests
  const loadUpdateRequests = useCallback(async () => {
    if (!token || !institutionId) return
    try {
      setLoadingUpdates(true)
      setUpdateError('')
      const data = await apiGet(`/institution/${institutionId}/parent-requests`, token)
      setUpdateRequests(Array.isArray(data) ? data : (data.requests || []))
    } catch (err) {
      setUpdateError(err.message || 'Failed to retrieve parent data correction requests.')
    } finally {
      setLoadingUpdates(false)
    }
  }, [token, institutionId])

  useEffect(() => {
    if (deskTab === 'linking') {
      loadLinkingRequests()
    } else {
      loadUpdateRequests()
    }
  }, [deskTab, loadLinkingRequests, loadUpdateRequests])

  // --- Three Linking Review Actions ---
  // 1. ACCEPT (Approve)
  async function handleConfirmApprove() {
    if (!selectedLinkingRequest) return
    try {
      setSubmittingLinkingReview(true)
      setLinkingFeedback(null)
      const res = await apiPost(
        `/school/linking-requests/${selectedLinkingRequest.request_id}/review`,
        {
          action: 'approve',
          decision: 'approved',
          remarks: approveRemarks.trim() || 'Approved by institution administrator upon verification of parent credentials.',
          review_comment: approveRemarks.trim() || 'Approved by institution administrator upon verification of parent credentials.',
          permanent_student_id: selectedLinkingRequest.permanent_student_id,
          confirm_student_match: true
        },
        token
      )
      setLinkingFeedback({
        type: 'success',
        message: res.message || `Successfully approved linking request for ${selectedLinkingRequest.parent_name || 'Parent'}. Student records are now accessible.`
      })
      setShowApproveModal(false)
      setSelectedLinkingRequest(null)
      setApproveRemarks('')
      await loadLinkingRequests()
    } catch (err) {
      setLinkingFeedback({
        type: 'error',
        message: err.message || 'Failed to approve linking request.'
      })
    } finally {
      setSubmittingLinkingReview(false)
    }
  }

  // 2. REJECT
  async function handleConfirmReject() {
    if (!selectedLinkingRequest) return
    const finalReason = rejectReason.trim()
    const finalRemarks = rejectRemarks.trim() || finalReason
    if (!finalReason) {
      setLinkingFeedback({
        type: 'error',
        message: 'Rejection reason is required.'
      })
      return
    }
    try {
      setSubmittingLinkingReview(true)
      setLinkingFeedback(null)
      const res = await apiPost(
        `/school/linking-requests/${selectedLinkingRequest.request_id}/review`,
        {
          action: 'reject',
          decision: 'rejected',
          rejection_reason: finalReason,
          remarks: finalRemarks,
          review_comment: finalRemarks
        },
        token
      )
      setLinkingFeedback({
        type: 'success',
        message: res.message || `Linking request rejected. Student records remain protected.`
      })
      setShowRejectModal(false)
      setSelectedLinkingRequest(null)
      setRejectRemarks('')
      await loadLinkingRequests()
    } catch (err) {
      setLinkingFeedback({
        type: 'error',
        message: err.message || 'Failed to reject linking request.'
      })
    } finally {
      setSubmittingLinkingReview(false)
    }
  }

  // 3. REQUEST CLARIFICATION
  async function handleConfirmClarify() {
    if (!selectedLinkingRequest) return
    const remarks = clarifyRemarks.trim()
    if (!remarks) {
      setLinkingFeedback({
        type: 'error',
        message: 'Please provide instructions or remarks for the parent.'
      })
      return
    }
    try {
      setSubmittingLinkingReview(true)
      setLinkingFeedback(null)
      const res = await apiPost(
        `/school/linking-requests/${selectedLinkingRequest.request_id}/review`,
        {
          action: 'clarify',
          decision: 'clarification_required',
          remarks: remarks,
          review_comment: remarks
        },
        token
      )
      setLinkingFeedback({
        type: 'success',
        message: res.message || `Clarification requested. Parent has been notified.`
      })
      setShowClarifyModal(false)
      setSelectedLinkingRequest(null)
      setClarifyRemarks('')
      await loadLinkingRequests()
    } catch (err) {
      setLinkingFeedback({
        type: 'error',
        message: err.message || 'Failed to request clarification.'
      })
    } finally {
      setSubmittingLinkingReview(false)
    }
  }

  // --- Data Correction Actions ---
  async function handleExecuteUpdateReview() {
    if (!selectedUpdateRequest || updateReviewAction === 'none') return
    if ((updateReviewAction === 'reject' || updateReviewAction === 'clarify') && !updateRemarks.trim()) {
      setUpdateReviewFeedback({ type: 'error', message: 'Please provide a clear justification or instruction for this action.' })
      return
    }

    try {
      setSubmittingUpdateReview(true)
      setUpdateReviewFeedback(null)

      await apiPost(
        `/institution/${institutionId}/parent-requests/${selectedUpdateRequest.request_id}/review`,
        {
          action: updateReviewAction,
          remarks: updateRemarks.trim()
        },
        token
      )

      setUpdateReviewFeedback({
        type: 'success',
        message: `Parent request has been successfully ${updateReviewAction === 'approve' ? 'approved and student record updated' : updateReviewAction === 'reject' ? 'rejected' : 'flagged for clarification'}.`
      })

      setTimeout(() => {
        loadUpdateRequests()
        setSelectedUpdateRequest(null)
        setUpdateReviewAction('none')
        setUpdateRemarks('')
        setUpdateReviewFeedback(null)
      }, 1500)
    } catch (err) {
      setUpdateReviewFeedback({
        type: 'error',
        message: err.message || 'Failed to complete review action on request.'
      })
    } finally {
      setSubmittingUpdateReview(false)
    }
  }

  const filteredUpdates = updateRequests.filter(r => {
    if (updateStatusFilter === 'all') return true
    return (r.status || '').toLowerCase() === updateStatusFilter.toLowerCase()
  })

  const pendingLinkingCount = linkingRequests.filter(r => ['pending', 'pending_review', 'clarification_required'].includes((r.request_status || r.status || '').toLowerCase())).length
  const pendingUpdatesCount = updateRequests.filter(r => (r.status || r.request_status) === 'pending').length

  return (
    <div className="institution-parent-requests-desk">
      {/* Header Banner */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        padding: '1.5rem',
        marginBottom: '1.25rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span style={{
              background: '#FDF2FA',
              color: '#C11574',
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              👨‍👩‍👧 Parent Governance Desk
            </span>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Parent Authorization & Governance
            </h2>
          </div>
          <p style={{ margin: '0.35rem 0 0 0', color: '#667085', fontSize: '0.88rem' }}>
            Review parent child-linking requests, evaluate relationship verification proofs, and manage student record updates.
          </p>
        </div>

        {/* Tab switchers */}
        <div style={{ display: 'flex', gap: '0.5rem', background: '#F1F5F9', padding: '0.25rem', borderRadius: '8px' }}>
          <button
            onClick={() => setDeskTab('linking')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: 'none',
              fontWeight: 700,
              fontSize: '0.875rem',
              cursor: 'pointer',
              background: deskTab === 'linking' ? '#FFFFFF' : 'transparent',
              color: deskTab === 'linking' ? '#155EEF' : '#64748B',
              boxShadow: deskTab === 'linking' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <span>🔗 Parent / Guardian Verification Requests</span>
            {pendingLinkingCount > 0 && (
              <span style={{ background: '#FEE4E2', color: '#B42318', fontSize: '0.75rem', padding: '0.1rem 0.45rem', borderRadius: '10px' }}>
                {pendingLinkingCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setDeskTab('updates')}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              border: 'none',
              fontWeight: 700,
              fontSize: '0.875rem',
              cursor: 'pointer',
              background: deskTab === 'updates' ? '#FFFFFF' : 'transparent',
              color: deskTab === 'updates' ? '#155EEF' : '#64748B',
              boxShadow: deskTab === 'updates' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <span>📝 Data Correction Requests</span>
            {pendingUpdatesCount > 0 && (
              <span style={{ background: '#FEF0C7', color: '#B54708', fontSize: '0.75rem', padding: '0.1rem 0.45rem', borderRadius: '10px' }}>
                {pendingUpdatesCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* SUB-TAB 1: PARENT / GUARDIAN VERIFICATION REQUESTS */}
      {deskTab === 'linking' && (
        <div>
          {/* Controls bar */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: '8px',
            border: '1px solid #E2E8F0',
            padding: '1rem 1.25rem',
            marginBottom: '1rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '0.75rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#475467' }}>Filter Status:</span>
              <select
                value={linkingStatusFilter}
                onChange={e => setLinkingStatusFilter(e.target.value)}
                style={{
                  padding: '0.45rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  background: '#FFFFFF'
                }}
              >
                <option value="all">All Statuses ({linkingRequests.length})</option>
                <option value="pending">Pending Initial Review</option>
                <option value="pending_review">Pending Review (Clarification Responded)</option>
                <option value="clarification_required">Clarification Required</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            <button
              onClick={loadLinkingRequests}
              disabled={loadingLinking}
              style={{
                padding: '0.45rem 0.85rem',
                borderRadius: '6px',
                border: '1px solid #D0D5DD',
                background: '#FFFFFF',
                color: '#344054',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              ↻ Refresh Requests
            </button>
          </div>

          {linkingFeedback && (
            <Alert
              type={linkingFeedback.type}
              title={linkingFeedback.type === 'success' ? 'Action Completed' : 'Action Failed'}
              style={{ marginBottom: '1rem' }}
            >
              {linkingFeedback.message}
            </Alert>
          )}

          {linkingError && (
            <Alert type="error" title="Error Loading Requests" style={{ marginBottom: '1rem' }}>
              {linkingError}
            </Alert>
          )}

          {/* Table */}
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            border: '1px solid #E2E8F0',
            overflow: 'hidden',
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
          }}>
            {loadingLinking ? (
              <div style={{ padding: '3rem', textAlign: 'center' }}>
                <LoadingSpinner message="Loading verification requests..." />
              </div>
            ) : linkingRequests.length === 0 ? (
              <div style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📭</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  No Parent Verification Requests
                </h3>
                <p style={{ color: '#667085', fontSize: '0.88rem', margin: 0 }}>
                  There are currently no verification requests matching the selected filter.
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
                  <thead>
                    <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', fontWeight: 700, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Request ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Requesting Parent</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Parent Account ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Relationship</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Student Name & ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Class / Stream</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Submitted At</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Administrative Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {linkingRequests.map(r => {
                      const rawStatus = (r.request_status || r.status || '').toLowerCase()
                      const isReviewable = ['pending', 'pending_review', 'clarification_required'].includes(rawStatus)

                      return (
                        <tr key={r.request_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                          <td style={{ padding: '0.85rem 1rem', fontFamily: 'monospace', fontSize: '0.78rem', color: '#64748B' }}>
                            {r.request_id.slice(0, 8)}...
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ fontWeight: 700, color: '#102B46' }}>{r.parent_name || 'Parent Guardian'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.parent_email || ''}</div>
                            {r.parent_phone && <div style={{ fontSize: '0.75rem', color: '#64748B' }}>📞 {r.parent_phone}</div>}
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <span style={{ fontFamily: 'monospace', fontSize: '0.78rem', background: '#F1F5F9', padding: '0.2rem 0.5rem', borderRadius: '4px', color: '#334155' }}>
                              {r.parent_user_id}
                            </span>
                          </td>
                          <td style={{ padding: '0.85rem 1rem', fontWeight: 600, color: '#344054' }}>
                            {r.relationship_type || 'Parent'}
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ fontWeight: 700, color: '#155EEF' }}>{r.student_name || 'Enrolled Student'}</div>
                            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center', marginTop: '0.2rem', flexWrap: 'wrap' }}>
                              <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.78rem', background: '#EFF8FF', color: '#175CD3', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                                ID: {r.student_id || r.student_ref}
                              </span>
                              {r.permanent_student_id && (
                                <span style={{ fontFamily: 'monospace', fontSize: '0.72rem', color: '#64748B' }}>
                                  PSID: {r.permanent_student_id}
                                </span>
                              )}
                            </div>
                          </td>
                          <td style={{ padding: '0.85rem 1rem', fontSize: '0.8rem', color: '#334155' }}>
                            <div>{r.class_or_standard || (r.standard ? `Std ${r.standard}` : 'N/A')} {r.section ? `(${r.section})` : ''}</div>
                            <div style={{ fontSize: '0.74rem', color: '#64748B' }}>{r.program_or_stream || 'General Academic'}</div>
                          </td>
                          <td style={{ padding: '0.85rem 1rem', color: '#64748B', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                            {r.created_at ? new Date(r.created_at).toLocaleString() : 'Recent'}
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            {rawStatus === 'approved' && (
                              <span style={{ background: '#ECFDF5', color: '#027A48', border: '1px solid #A7F3D0', padding: '0.25rem 0.55rem', borderRadius: '12px', fontWeight: 700, fontSize: '0.75rem' }}>
                                APPROVED
                              </span>
                            )}
                            {rawStatus === 'rejected' && (
                              <span style={{ background: '#FEF2F2', color: '#B42318', border: '1px solid #FCA5A5', padding: '0.25rem 0.55rem', borderRadius: '12px', fontWeight: 700, fontSize: '0.75rem' }}>
                                REJECTED
                              </span>
                            )}
                            {rawStatus === 'clarification_required' && (
                              <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FCD34D', padding: '0.25rem 0.55rem', borderRadius: '12px', fontWeight: 700, fontSize: '0.75rem' }}>
                                CLARIFICATION_REQUIRED
                              </span>
                            )}
                            {rawStatus === 'pending_review' && (
                              <span style={{ background: '#EFF8FF', color: '#175CD3', border: '1px solid #B2DDFF', padding: '0.25rem 0.55rem', borderRadius: '12px', fontWeight: 700, fontSize: '0.75rem' }}>
                                PENDING_REVIEW
                              </span>
                            )}
                            {rawStatus === 'pending' && (
                              <span style={{ background: '#F2F4F7', color: '#344054', border: '1px solid #D0D5DD', padding: '0.25rem 0.55rem', borderRadius: '12px', fontWeight: 700, fontSize: '0.75rem' }}>
                                PENDING
                              </span>
                            )}

                            {/* Show parent response note if pending_review */}
                            {rawStatus === 'pending_review' && r.parent_response && (
                              <div style={{ marginTop: '0.35rem', background: '#F0F9FF', border: '1px solid #BAE6FD', padding: '0.35rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', color: '#0369A1' }}>
                                <strong>Parent Response:</strong> "{r.parent_response}"
                              </div>
                            )}

                            {/* Show clarification requested if clarification_required */}
                            {rawStatus === 'clarification_required' && r.reviewer_comment && (
                              <div style={{ marginTop: '0.35rem', background: '#FFFAEB', border: '1px solid #FEDF89', padding: '0.35rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', color: '#B54708' }}>
                                <strong>Requested:</strong> "{r.reviewer_comment}"
                              </div>
                            )}

                            {/* Show rejection reason if rejected */}
                            {rawStatus === 'rejected' && r.rejection_reason && (
                              <div style={{ marginTop: '0.35rem', background: '#FEF2F2', border: '1px solid #FECDCA', padding: '0.35rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', color: '#B42318' }}>
                                <strong>Reason:</strong> {r.rejection_reason}
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>
                            {isReviewable ? (
                              <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                                <button
                                  onClick={() => {
                                    setSelectedLinkingRequest(r)
                                    setApproveRemarks('')
                                    setShowApproveModal(true)
                                  }}
                                  disabled={submittingLinkingReview}
                                  className="btn btn--sm"
                                  style={{
                                    background: '#12B76A',
                                    color: '#FFFFFF',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    padding: '0.35rem 0.65rem',
                                    fontSize: '0.78rem',
                                    cursor: 'pointer'
                                  }}
                                  title="Approve linking request"
                                >
                                  ✓ Accept
                                </button>

                                <button
                                  onClick={() => {
                                    setSelectedLinkingRequest(r)
                                    setClarifyRemarks('')
                                    setShowClarifyModal(true)
                                  }}
                                  disabled={submittingLinkingReview}
                                  className="btn btn--sm"
                                  style={{
                                    background: '#F79009',
                                    color: '#FFFFFF',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    padding: '0.35rem 0.65rem',
                                    fontSize: '0.78rem',
                                    cursor: 'pointer'
                                  }}
                                  title="Request additional verification documents or details from parent"
                                >
                                  💬 Clarify
                                </button>

                                <button
                                  onClick={() => {
                                    setSelectedLinkingRequest(r)
                                    setRejectReason('Student identity / relationship verification mismatch')
                                    setRejectRemarks('')
                                    setShowRejectModal(true)
                                  }}
                                  disabled={submittingLinkingReview}
                                  className="btn btn--sm"
                                  style={{
                                    background: '#FFFFFF',
                                    color: '#B42318',
                                    border: '1px solid #FDA29B',
                                    borderRadius: '6px',
                                    fontWeight: 600,
                                    padding: '0.35rem 0.65rem',
                                    fontSize: '0.78rem',
                                    cursor: 'pointer'
                                  }}
                                  title="Reject linking request"
                                >
                                  ✕ Reject
                                </button>
                              </div>
                            ) : (
                              <span style={{ fontSize: '0.8rem', color: '#64748B' }}>
                                {r.reviewed_at ? `Decided: ${new Date(r.reviewed_at).toLocaleDateString()}` : 'Completed'}
                              </span>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
"""

# Now build the new modals for Approve, Clarify, and Reject
new_linking_modals = """      {/* MODAL 1: ACCEPT / APPROVE LINKING REQUEST */}
      {showApproveModal && selectedLinkingRequest && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '100%',
            overflow: 'hidden',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <div style={{ background: '#065F46', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase', color: '#A7F3D0' }}>
                  Institution Authorization
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: '#FFFFFF' }}>
                  ✓ Accept & Approve Linking Request
                </h3>
              </div>
              <button
                onClick={() => {
                  setShowApproveModal(false)
                  setSelectedLinkingRequest(null)
                }}
                style={{ background: 'none', border: 'none', color: '#A7F3D0', fontSize: '1.4rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.88rem', color: '#334155', lineHeight: 1.5 }}>
                Approving this request will verify parent <strong>{selectedLinkingRequest.parent_name || 'Parent'}</strong> ({selectedLinkingRequest.relationship_type}) and grant authorized access to academic records for student <strong>{selectedLinkingRequest.student_name}</strong> (Student ID: <code>{selectedLinkingRequest.student_id}</code>).
              </p>

              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Administrator Remarks (Optional):
              </label>
              <textarea
                rows={3}
                value={approveRemarks}
                onChange={e => setApproveRemarks(e.target.value)}
                placeholder="e.g. Identity and parentage verified against official admission enrollment register."
                style={{
                  width: '100%',
                  padding: '0.65rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  marginBottom: '1.25rem',
                  boxSizing: 'border-box'
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowApproveModal(false)
                    setSelectedLinkingRequest(null)
                  }}
                  style={{
                    padding: '0.55rem 1.25rem',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    background: '#FFFFFF',
                    color: '#344054',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmApprove}
                  disabled={submittingLinkingReview}
                  style={{
                    padding: '0.55rem 1.5rem',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#12B76A',
                    color: '#FFFFFF',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  {submittingLinkingReview ? 'Approving...' : 'Confirm & Approve Access ✓'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: REQUEST CLARIFICATION */}
      {showClarifyModal && selectedLinkingRequest && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '100%',
            overflow: 'hidden',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <div style={{ background: '#B54708', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase', color: '#FEF0C7' }}>
                  Action Required From Parent
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: '#FFFFFF' }}>
                  💬 Request Clarification / Documentation
                </h3>
              </div>
              <button
                onClick={() => {
                  setShowClarifyModal(false)
                  setSelectedLinkingRequest(null)
                }}
                style={{ background: 'none', border: 'none', color: '#FEF0C7', fontSize: '1.4rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.88rem', color: '#334155', lineHeight: 1.5 }}>
                Request additional evidence or information from <strong>{selectedLinkingRequest.parent_name || 'Parent'}</strong> regarding student <strong>{selectedLinkingRequest.student_name}</strong>. The parent will be notified to submit a response.
              </p>

              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Clarification Instructions / Remarks <span style={{ color: '#b91c1c' }}>*</span>:
              </label>
              <textarea
                rows={4}
                value={clarifyRemarks}
                onChange={e => setClarifyRemarks(e.target.value)}
                placeholder="e.g. Please provide a scanned copy of the birth certificate or official guardianship order confirming parentage."
                style={{
                  width: '100%',
                  padding: '0.65rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  marginBottom: '1.25rem',
                  boxSizing: 'border-box'
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowClarifyModal(false)
                    setSelectedLinkingRequest(null)
                  }}
                  style={{
                    padding: '0.55rem 1.25rem',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    background: '#FFFFFF',
                    color: '#344054',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmClarify}
                  disabled={submittingLinkingReview || !clarifyRemarks.trim()}
                  style={{
                    padding: '0.55rem 1.5rem',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#F79009',
                    color: '#FFFFFF',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  {submittingLinkingReview ? 'Sending Request...' : 'Send Clarification Request →'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: REJECT LINKING REQUEST */}
      {showRejectModal && selectedLinkingRequest && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.75)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            maxWidth: '500px',
            width: '100%',
            overflow: 'hidden',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <div style={{ background: '#991B1B', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase', color: '#FCA5A5' }}>
                  Security & Access Control
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: '#FFFFFF' }}>
                  ✕ Reject Parent Linking Request
                </h3>
              </div>
              <button
                onClick={() => {
                  setShowRejectModal(false)
                  setSelectedLinkingRequest(null)
                }}
                style={{ background: 'none', border: 'none', color: '#FCA5A5', fontSize: '1.4rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.88rem', color: '#334155', lineHeight: 1.5 }}>
                Rejecting this request will keep student academic records private. Parent <strong>{selectedLinkingRequest.parent_name || 'Parent'}</strong> will receive a formal notification with the stated reason.
              </p>

              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Rejection Reason <span style={{ color: '#b91c1c' }}>*</span>:
              </label>
              <select
                value={rejectReason}
                onChange={e => setRejectReason(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.6rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  marginBottom: '1rem',
                  background: '#FFFFFF',
                  boxSizing: 'border-box'
                }}
              >
                <option value="Identity and relationship documents could not be verified">Identity and relationship documents could not be verified</option>
                <option value="Student reference ID does not belong to active enrollments in this institution">Student reference ID does not belong to active enrollments in this institution</option>
                <option value="Conflicting guardian record exists in official register">Conflicting guardian record exists in official register</option>
                <option value="Requested clarification was incomplete or unsatisfactory">Requested clarification was incomplete or unsatisfactory</option>
                <option value="Administrative policy or legal custody restriction">Administrative policy or legal custody restriction</option>
              </select>

              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Additional Remarks / Details:
              </label>
              <textarea
                rows={3}
                value={rejectRemarks}
                onChange={e => setRejectRemarks(e.target.value)}
                placeholder="Provide specific notes explaining the rejection to the parent..."
                style={{
                  width: '100%',
                  padding: '0.65rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  marginBottom: '1.25rem',
                  boxSizing: 'border-box'
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  type="button"
                  onClick={() => {
                    setShowRejectModal(false)
                    setSelectedLinkingRequest(null)
                  }}
                  style={{
                    padding: '0.55rem 1.25rem',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    background: '#FFFFFF',
                    color: '#344054',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleConfirmReject}
                  disabled={submittingLinkingReview}
                  style={{
                    padding: '0.55rem 1.5rem',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#B42318',
                    color: '#FFFFFF',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  {submittingLinkingReview ? 'Rejecting...' : 'Confirm Rejection ✕'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
"""

subtab2_content = text[subtab2_idx:modal1_idx]
update_modal_content = text[update_modal_idx:]

new_full_component = top_half + subtab2_content + new_linking_modals + update_modal_content

with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'w', encoding='utf-8') as f:
    f.write(new_full_component)

print("InstitutionParentRequestsDesk.jsx completely rewritten and updated.")
