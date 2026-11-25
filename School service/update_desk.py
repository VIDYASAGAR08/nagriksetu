import os

content = '''import React, { useState, useEffect, useCallback } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'
import StatusBadge from '../ui/StatusBadge.jsx'

export default function InstitutionParentRequestsDesk({ token, institutionId }) {
  // Desk Sub-tab: 'linking' (Parent Linking Requests) | 'updates' (Data Correction Requests)
  const [deskTab, setDeskTab] = useState('linking')

  // --- 1. Parent Linking Requests State ---
  const [linkingRequests, setLinkingRequests] = useState([])
  const [loadingLinking, setLoadingLinking] = useState(true)
  const [linkingError, setLinkingError] = useState('')
  const [linkingStatusFilter, setLinkingStatusFilter] = useState('all')

  // Linking Review / Issue Code Modal State
  const [selectedLinkingRequest, setSelectedLinkingRequest] = useState(null)
  const [issuedCodeData, setIssuedCodeData] = useState(null)
  const [issuingCode, setIssuingCode] = useState(false)
  const [submittingLinkingReview, setSubmittingLinkingReview] = useState(false)
  const [linkingFeedback, setLinkingFeedback] = useState(null)
  const [linkingRejectRemarks, setLinkingRejectRemarks] = useState('')
  const [showRejectModal, setShowRejectModal] = useState(false)

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

  // --- Linking Actions ---
  // A. Quick Approve Link
  async function handleApproveLinking(req) {
    if (!req) return
    try {
      setSubmittingLinkingReview(true)
      setLinkingFeedback(null)
      await apiPost(
        `/school/linking-requests/${req.request_id}/review`,
        {
          decision: 'approved',
          review_comment: 'Approved by institution administrator upon verification of parent credentials.',
          permanent_student_id: req.permanent_student_id,
          confirm_student_match: true
        },
        token
      )
      setLinkingFeedback({
        type: 'success',
        message: `Successfully approved linking request for ${req.parent_name || 'Parent'} and student ${req.student_name || req.student_id}. Student records are now accessible.`
      })
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

  // B. Issue Official 6-digit Verification Code
  async function handleIssueCode(req) {
    if (!req) return
    try {
      setIssuingCode(true)
      setIssuedCodeData(null)
      setLinkingFeedback(null)
      const res = await apiPost(`/school/linking-requests/${req.request_id}/issue-code`, {}, token)
      setIssuedCodeData({
        ...res,
        request: req
      })
    } catch (err) {
      setLinkingFeedback({
        type: 'error',
        message: err.message || 'Failed to generate institution verification code.'
      })
    } finally {
      setIssuingCode(false)
    }
  }

  // C. Reject Linking Request
  async function handleRejectLinking() {
    if (!selectedLinkingRequest) return
    const reason = linkingRejectRemarks.trim() || 'Institution verification requirements not satisfied.'
    try {
      setSubmittingLinkingReview(true)
      await apiPost(
        `/school/linking-requests/${selectedLinkingRequest.request_id}/review`,
        {
          decision: 'rejected',
          review_comment: reason,
          confirm_student_match: false
        },
        token
      )
      setLinkingFeedback({
        type: 'success',
        message: `Linking request rejected. Student records remain protected.`
      })
      setShowRejectModal(false)
      setSelectedLinkingRequest(null)
      setLinkingRejectRemarks('')
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

  const pendingLinkingCount = linkingRequests.filter(r => (r.request_status || r.status) === 'pending').length
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
            Review parent child-linking requests, generate secure authorization verification codes, and process record correction requests.
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
            <span>🔗 Parent Linking Requests</span>
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

      {/* SUB-TAB 1: PARENT LINKING REQUESTS */}
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
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#475467' }}>Filter by Status:</span>
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
                <option value="pending">Pending ({pendingLinkingCount})</option>
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
                <LoadingSpinner message="Loading institution linking requests..." />
              </div>
            ) : linkingRequests.length === 0 ? (
              <div style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📭</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  No Parent Linking Requests
                </h3>
                <p style={{ color: '#667085', fontSize: '0.88rem', margin: 0 }}>
                  There are currently no child-linking requests matching the selected filter.
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
                      <th style={{ padding: '0.75rem 1rem' }}>Student Name & ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Relationship</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Submitted At</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Administrative Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {linkingRequests.map(r => {
                      const isPending = (r.request_status || r.status) === 'pending'
                      return (
                        <tr key={r.request_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                          <td style={{ padding: '0.85rem 1rem', fontFamily: 'monospace', fontSize: '0.78rem', color: '#64748B' }}>
                            {r.request_id.slice(0, 8)}...
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ fontWeight: 700, color: '#102B46' }}>{r.parent_name || 'Parent Guardian'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.parent_email || r.parent_phone || 'No direct contact'}</div>
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <span style={{ fontFamily: 'monospace', fontSize: '0.78rem', background: '#F1F5F9', padding: '0.2rem 0.5rem', borderRadius: '4px', color: '#334155' }}>
                              {r.parent_user_id}
                            </span>
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <div style={{ fontWeight: 700, color: '#155EEF' }}>{r.student_name || 'Enrolled Student'}</div>
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.2rem' }}>
                              <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.78rem', background: '#EFF8FF', color: '#175CD3', padding: '0.1rem 0.4rem', borderRadius: '4px' }}>
                                ID: {r.student_id || r.student_ref}
                              </span>
                              {r.permanent_student_id && (
                                <span style={{ fontSize: '0.72rem', color: '#64748B' }}>
                                  PSID: {r.permanent_student_id}
                                </span>
                              )}
                            </div>
                          </td>
                          <td style={{ padding: '0.85rem 1rem', fontWeight: 600, color: '#344054' }}>
                            {r.relationship_type || 'Parent'}
                          </td>
                          <td style={{ padding: '0.85rem 1rem', color: '#64748B', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                            {r.created_at ? new Date(r.created_at).toLocaleString() : 'Recent'}
                          </td>
                          <td style={{ padding: '0.85rem 1rem' }}>
                            <StatusBadge status={r.request_status || r.status} />
                          </td>
                          <td style={{ padding: '0.85rem 1rem', textAlign: 'center' }}>
                            {isPending ? (
                              <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                                <button
                                  onClick={() => handleApproveLinking(r)}
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
                                  title="Immediately approve and link parent to child records"
                                >
                                  ✓ Approve & Link
                                </button>
                                <button
                                  onClick={() => handleIssueCode(r)}
                                  disabled={issuingCode}
                                  className="btn btn--sm"
                                  style={{
                                    background: '#155EEF',
                                    color: '#FFFFFF',
                                    border: 'none',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    padding: '0.35rem 0.65rem',
                                    fontSize: '0.78rem',
                                    cursor: 'pointer'
                                  }}
                                  title="Issue official 6-digit verification code for parent"
                                >
                                  🔑 Issue Code
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedLinkingRequest(r)
                                    setShowRejectModal(true)
                                  }}
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
                                >
                                  ✕ Reject
                                </button>
                              </div>
                            ) : (
                              <span style={{ fontSize: '0.8rem', color: '#64748B' }}>
                                {r.reviewed_at ? `Reviewed: ${new Date(r.reviewed_at).toLocaleDateString()}` : 'Completed'}
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

      {/* SUB-TAB 2: DATA CORRECTION REQUESTS */}
      {deskTab === 'updates' && (
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
              <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#475467' }}>Filter by Status:</span>
              <select
                value={updateStatusFilter}
                onChange={e => setUpdateStatusFilter(e.target.value)}
                style={{
                  padding: '0.45rem 0.75rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  background: '#FFFFFF'
                }}
              >
                <option value="all">All Request Statuses ({updateRequests.length})</option>
                <option value="pending">Pending Review ({pendingUpdatesCount})</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
                <option value="clarification_requested">Clarification Requested</option>
              </select>
            </div>

            <button
              onClick={loadUpdateRequests}
              disabled={loadingUpdates}
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
              ↻ Refresh
            </button>
          </div>

          {updateError && (
            <Alert type="error" title="Review Desk Error" style={{ marginBottom: '1rem' }}>
              {updateError}
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
            {loadingUpdates ? (
              <div style={{ padding: '3rem', textAlign: 'center' }}>
                <LoadingSpinner message="Loading submitted parent update requests..." />
              </div>
            ) : filteredUpdates.length === 0 ? (
              <div style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>📭</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                  No Requests in Current Filter
                </h3>
                <p style={{ color: '#667085', fontSize: '0.88rem', margin: 0 }}>
                  No parent update requests currently match the selected status filter.
                </p>
              </div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
                  <thead>
                    <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', fontWeight: 700, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Request ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Student Profile</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Parent / Contact</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Field Requested</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Requested Value</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Submitted At</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                      <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredUpdates.map(r => (
                      <tr key={r.request_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                        <td style={{ padding: '0.85rem 1rem', fontFamily: 'monospace', fontSize: '0.78rem', color: '#64748B' }}>
                          {r.request_id.slice(0, 8)}...
                        </td>
                        <td style={{ padding: '0.85rem 1rem' }}>
                          <div style={{ fontWeight: 700, color: '#102B46' }}>{r.student_name || 'Enrolled Student'}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>PSID: {r.permanent_student_id}</div>
                        </td>
                        <td style={{ padding: '0.85rem 1rem' }}>
                          <div style={{ fontWeight: 600, color: '#344054' }}>{r.parent_name || 'Parent Guardian'}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.parent_phone || r.parent_email || '—'}</div>
                        </td>
                        <td style={{ padding: '0.85rem 1rem' }}>
                          <span style={{
                            background: '#EFF8FF',
                            color: '#175CD3',
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            fontWeight: 600,
                            fontSize: '0.78rem',
                            textTransform: 'capitalize'
                          }}>
                            {r.field_name?.replace(/_/g, ' ')}
                          </span>
                        </td>
                        <td style={{ padding: '0.85rem 1rem', fontFamily: 'monospace', fontWeight: 600, color: '#027A48' }}>
                          {r.requested_value || '—'}
                        </td>
                        <td style={{ padding: '0.85rem 1rem', color: '#64748B', fontSize: '0.8rem', whiteSpace: 'nowrap' }}>
                          {r.created_at ? new Date(r.created_at).toLocaleDateString() : 'Recent'}
                        </td>
                        <td style={{ padding: '0.85rem 1rem' }}>
                          <StatusBadge status={r.status} />
                        </td>
                        <td style={{ padding: '0.85rem 1rem', textAlign: 'right' }}>
                          <button
                            onClick={() => {
                              setSelectedUpdateRequest(r)
                              setUpdateReviewAction('none')
                              setUpdateRemarks('')
                              setUpdateReviewFeedback(null)
                            }}
                            style={{
                              padding: '0.35rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #D0D5DD',
                              background: '#FFFFFF',
                              color: '#155EEF',
                              fontWeight: 700,
                              fontSize: '0.8rem',
                              cursor: 'pointer'
                            }}
                          >
                            Inspect & Review →
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MODAL 1: OFFICIAL VERIFICATION CODE ISSUED (FOR ADMINISTRATOR DISPATCH) */}
      {issuedCodeData && (
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
            maxWidth: '520px',
            width: '100%',
            overflow: 'hidden',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <div style={{ background: '#0F172A', color: '#FFFFFF', padding: '1.25rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase', color: '#38BDF8' }}>
                  Official Institution Authorization
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.2rem', color: '#FFFFFF' }}>
                  🔑 Parent Verification Code Generated
                </h3>
              </div>
              <button
                onClick={() => setIssuedCodeData(null)}
                style={{ background: 'none', border: 'none', color: '#94A3B8', fontSize: '1.4rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              <div style={{ textAlign: 'center', marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '0.5rem' }}>
                  Official 6-Digit Verification Code:
                </div>
                <div style={{
                  background: '#F0FDF4',
                  border: '2px dashed #16A34A',
                  borderRadius: '8px',
                  padding: '1rem',
                  display: 'inline-block',
                  minWidth: '220px'
                }}>
                  <span style={{
                    fontSize: '2.2rem',
                    fontWeight: 900,
                    fontFamily: 'monospace',
                    letterSpacing: '8px',
                    color: '#15803D'
                  }}>
                    {issuedCodeData.verification_code}
                  </span>
                </div>
                <div style={{ fontSize: '0.775rem', color: '#16A34A', marginTop: '0.4rem', fontWeight: 600 }}>
                  ⏱️ Valid for 15 minutes · Single-use authorization
                </div>
              </div>

              {/* Instructions Box */}
              <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem', fontSize: '0.84rem', color: '#334155', lineHeight: 1.5 }}>
                <div style={{ fontWeight: 700, color: '#0F172A', marginBottom: '0.35rem' }}>
                  Administrative Dispatch Instructions:
                </div>
                <ul style={{ margin: 0, paddingLeft: '1.2rem' }}>
                  <li>Provide this code directly to <strong>{issuedCodeData.request?.parent_name || 'the requesting parent'}</strong> (Parent Account: <code>{issuedCodeData.request?.parent_user_id}</code>).</li>
                  <li>Convey this code only after verifying the parent's identity via institution office, verified phone, or authorized dispatch.</li>
                  <li>The parent will enter this code in their Parent Portal under "Link Your Child" to complete authorization.</li>
                </ul>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText(issuedCodeData.verification_code)
                    alert('Verification code copied to clipboard!')
                  }}
                  style={{
                    padding: '0.6rem 1.25rem',
                    borderRadius: '6px',
                    border: '1px solid #CBD5E1',
                    background: '#FFFFFF',
                    color: '#1E293B',
                    fontWeight: 700,
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  📋 Copy Code
                </button>
                <button
                  onClick={() => setIssuedCodeData(null)}
                  style={{
                    padding: '0.6rem 1.5rem',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#155EEF',
                    color: '#FFFFFF',
                    fontWeight: 700,
                    fontSize: '0.85rem',
                    cursor: 'pointer'
                  }}
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: REJECT LINKING REQUEST */}
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
            maxWidth: '480px',
            width: '100%',
            overflow: 'hidden',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #E2E8F0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#991B1B', fontWeight: 800 }}>
                Reject Parent Linking Request
              </h3>
              <button
                onClick={() => {
                  setShowRejectModal(false)
                  setSelectedLinkingRequest(null)
                }}
                style={{ background: 'none', border: 'none', color: '#64748B', fontSize: '1.3rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              <p style={{ margin: '0 0 1rem 0', fontSize: '0.88rem', color: '#475467' }}>
                Are you sure you want to reject the linking request from <strong>{selectedLinkingRequest.parent_name || 'Parent'}</strong> for student <strong>{selectedLinkingRequest.student_name} ({selectedLinkingRequest.student_id})</strong>?
              </p>

              <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                Rejection Justification:
              </label>
              <textarea
                rows={3}
                value={linkingRejectRemarks}
                onChange={e => setLinkingRejectRemarks(e.target.value)}
                placeholder="e.g. Identity documents could not be verified by the school administration."
                style={{
                  width: '100%',
                  padding: '0.65rem',
                  borderRadius: '6px',
                  border: '1px solid #CBD5E1',
                  fontSize: '0.85rem',
                  marginBottom: '1rem'
                }}
              />

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button
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
                  onClick={handleRejectLinking}
                  disabled={submittingLinkingReview}
                  style={{
                    padding: '0.55rem 1.5rem',
                    borderRadius: '6px',
                    border: 'none',
                    background: '#D92D20',
                    color: '#FFFFFF',
                    fontWeight: 700,
                    cursor: submittingLinkingReview ? 'not-allowed' : 'pointer'
                  }}
                >
                  {submittingLinkingReview ? 'Rejecting...' : 'Confirm Rejection'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: DATA CORRECTION REVIEW MODAL */}
      {selectedUpdateRequest && (
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
            maxWidth: '650px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
          }}>
            <div style={{
              padding: '1.25rem 1.5rem',
              borderBottom: '1px solid #E2E8F0',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '1px', textTransform: 'uppercase', color: '#155EEF' }}>
                  Demographic Update Review
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.25rem', color: '#102B46' }}>
                  Review Parent Correction Request
                </h3>
              </div>
              <button
                onClick={() => setSelectedUpdateRequest(null)}
                style={{ background: 'none', border: 'none', color: '#64748B', fontSize: '1.3rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              {updateReviewFeedback && (
                <Alert type={updateReviewFeedback.type} style={{ marginBottom: '1rem' }}>
                  {updateReviewFeedback.message}
                </Alert>
              )}

              <div style={{ background: '#F8FAFC', border: '1px solid #E2E8F0', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', fontSize: '0.85rem' }}>
                  <div>Student: <strong>{selectedUpdateRequest.student_name}</strong></div>
                  <div>PSID: <strong style={{ fontFamily: 'monospace' }}>{selectedUpdateRequest.permanent_student_id}</strong></div>
                  <div>Parent: <strong>{selectedUpdateRequest.parent_name}</strong></div>
                  <div>Field: <strong style={{ color: '#155EEF' }}>{selectedUpdateRequest.field_name}</strong></div>
                  <div>Current Value: <strong style={{ color: '#64748B' }}>{selectedUpdateRequest.current_value || '—'}</strong></div>
                  <div>Requested: <strong style={{ color: '#027A48' }}>{selectedUpdateRequest.requested_value}</strong></div>
                </div>
              </div>

              {/* Review Actions */}
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#102B46', marginBottom: '0.5rem' }}>
                  Select Determination:
                </div>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={() => setUpdateReviewAction('approve')}
                    style={{
                      flex: 1,
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: updateReviewAction === 'approve' ? '2px solid #12B76A' : '1px solid #D0D5DD',
                      background: updateReviewAction === 'approve' ? '#ECFDF3' : '#FFFFFF',
                      color: updateReviewAction === 'approve' ? '#027A48' : '#344054',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    ✓ Approve
                  </button>
                  <button
                    onClick={() => setUpdateReviewAction('clarify')}
                    style={{
                      flex: 1,
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: updateReviewAction === 'clarify' ? '2px solid #7A5AF8' : '1px solid #D0D5DD',
                      background: updateReviewAction === 'clarify' ? '#F4F3FF' : '#FFFFFF',
                      color: updateReviewAction === 'clarify' ? '#5925DC' : '#344054',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    💬 Clarify
                  </button>
                  <button
                    onClick={() => setUpdateReviewAction('reject')}
                    style={{
                      flex: 1,
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: updateReviewAction === 'reject' ? '2px solid #F04438' : '1px solid #D0D5DD',
                      background: updateReviewAction === 'reject' ? '#FEF3F2' : '#FFFFFF',
                      color: updateReviewAction === 'reject' ? '#B42318' : '#344054',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    ✕ Reject
                  </button>
                </div>
              </div>

              {updateReviewAction !== 'none' && (
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    {updateReviewAction === 'approve' ? 'Approval Audit Remarks (Optional):' : 'Detailed Justification / Feedback for Parent (Mandatory):'}
                  </label>
                  <textarea
                    rows={3}
                    value={updateRemarks}
                    onChange={e => setUpdateRemarks(e.target.value)}
                    placeholder={
                      updateReviewAction === 'approve'
                        ? 'e.g. Verified against submitted birth certificate record.'
                        : 'e.g. Scanned proof unclear. Please upload a gazetted officer attested affidavit.'
                    }
                    style={{
                      width: '100%',
                      padding: '0.65rem',
                      borderRadius: '6px',
                      border: '1px solid #CBD5E1',
                      fontSize: '0.85rem'
                    }}
                  />
                </div>
              )}
            </div>

            <div style={{
              padding: '1rem 1.5rem',
              background: '#F8FAFC',
              borderTop: '1px solid #E2E8F0',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => setSelectedUpdateRequest(null)}
                style={{
                  padding: '0.55rem 1.25rem',
                  borderRadius: '6px',
                  border: '1px solid #D0D5DD',
                  background: '#FFFFFF',
                  color: '#344054',
                  fontWeight: 600,
                  fontSize: '0.85rem',
                  cursor: 'pointer'
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleExecuteUpdateReview}
                disabled={updateReviewAction === 'none' || submittingUpdateReview}
                style={{
                  padding: '0.55rem 1.5rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: updateReviewAction === 'approve' ? '#12B76A' : updateReviewAction === 'reject' ? '#F04438' : '#155EEF',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  cursor: updateReviewAction === 'none' || submittingUpdateReview ? 'not-allowed' : 'pointer'
                }}
              >
                {submittingUpdateReview ? 'Submitting...' : 'Confirm Determination'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
'''

with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("InstitutionParentRequestsDesk.jsx updated successfully!")
