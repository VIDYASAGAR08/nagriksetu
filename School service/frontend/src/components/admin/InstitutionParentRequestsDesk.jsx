import React, { useState, useEffect, useCallback } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'
import StatusBadge from '../ui/StatusBadge.jsx'

export default function InstitutionParentRequestsDesk({ token, institutionId }) {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  // Selected request for review modal
  const [selectedRequest, setSelectedRequest] = useState(null)
  const [reviewAction, setReviewAction] = useState('none') // 'approve' | 'reject' | 'clarify'
  const [remarks, setRemarks] = useState('')
  const [submittingReview, setSubmittingReview] = useState(false)
  const [reviewFeedback, setReviewFeedback] = useState(null)

  const loadRequests = useCallback(async () => {
    if (!token || !institutionId) return
    try {
      setLoading(true)
      setError('')
      const data = await apiGet(`/institution/${institutionId}/parent-requests`, token)
      setRequests(Array.isArray(data) ? data : (data.requests || []))
    } catch (err) {
      setError(err.message || 'Failed to retrieve parent update requests.')
    } finally {
      setLoading(false)
    }
  }, [token, institutionId])

  useEffect(() => {
    loadRequests()
  }, [loadRequests])

  async function handleExecuteReview() {
    if (!selectedRequest || reviewAction === 'none') return
    if ((reviewAction === 'reject' || reviewAction === 'clarify') && !remarks.trim()) {
      setReviewFeedback({ type: 'error', message: 'Please provide a clear justification or instruction for this action.' })
      return
    }

    try {
      setSubmittingReview(true)
      setReviewFeedback(null)

      await apiPost(
        `/institution/${institutionId}/parent-requests/${selectedRequest.request_id}/review`,
        {
          action: reviewAction,
          remarks: remarks.trim()
        },
        token
      )

      setReviewFeedback({
        type: 'success',
        message: `Parent request has been successfully ${reviewAction === 'approve' ? 'approved and student record updated' : reviewAction === 'reject' ? 'rejected' : 'flagged for clarification'}.`
      })

      // Reload list after a brief delay
      setTimeout(() => {
        loadRequests()
        setSelectedRequest(null)
        setReviewAction('none')
        setRemarks('')
        setReviewFeedback(null)
      }, 1500)
    } catch (err) {
      setReviewFeedback({
        type: 'error',
        message: err.message || 'Failed to complete review action on request.'
      })
    } finally {
      setSubmittingReview(false)
    }
  }

  const filteredRequests = requests.filter(r => {
    if (statusFilter === 'all') return true
    return (r.status || '').toLowerCase() === statusFilter.toLowerCase()
  })

  return (
    <div className="institution-parent-requests-desk">
      {/* Header */}
      <div style={{
        background: '#FFFFFF',
        borderRadius: '12px',
        border: '1px solid #E2E8F0',
        padding: '1.5rem',
        marginBottom: '1.5rem',
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
              👨‍👩‍👧 Parent Governance
            </span>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Parent Data Update & Correction Requests
            </h2>
          </div>
          <p style={{ margin: '0.35rem 0 0 0', color: '#667085', fontSize: '0.88rem' }}>
            Review, verify supporting documentation, and approve demographic updates submitted by authenticated parents.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            style={{
              padding: '0.5rem 0.85rem',
              borderRadius: '6px',
              border: '1px solid #CBD5E1',
              fontSize: '0.85rem',
              background: '#FFFFFF',
              fontWeight: 600
            }}
          >
            <option value="all">All Request Statuses ({requests.length})</option>
            <option value="pending">Pending Review</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="clarification_requested">Clarification Requested</option>
          </select>

          <button
            onClick={loadRequests}
            style={{
              padding: '0.5rem 0.85rem',
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
      </div>

      {error && (
        <Alert type="error" title="Review Desk Error" style={{ marginBottom: '1rem' }}>
          {error}
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
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <LoadingSpinner message="Loading submitted parent update requests..." />
          </div>
        ) : filteredRequests.length === 0 ? (
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
                  <th style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRequests.map((r, idx) => (
                  <tr
                    key={r.request_id || idx}
                    style={{
                      borderBottom: '1px solid #F2F4F7',
                      background: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA'
                    }}
                  >
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#155EEF' }}>
                      {r.request_id}
                    </td>

                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 700, color: '#102B46' }}>{r.student_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#667085', fontFamily: 'monospace' }}>
                        {r.permanent_student_id} {r.standard ? `· Std ${r.standard}-${r.section || 'A'}` : ''}
                      </div>
                    </td>

                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 600, color: '#344054' }}>{r.parent_name || 'Verified Guardian'}</div>
                      <div style={{ fontSize: '0.75rem', color: '#667085' }}>{r.parent_phone || r.parent_email || '—'}</div>
                    </td>

                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{
                        background: '#EFF4FF',
                        color: '#155EEF',
                        padding: '0.2rem 0.5rem',
                        borderRadius: '4px',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        textTransform: 'uppercase'
                      }}>
                        {r.field_name || r.update_type || 'Demographics'}
                      </span>
                    </td>

                    <td style={{ padding: '0.75rem 1rem', color: '#102B46', fontWeight: 600 }}>
                      <div style={{ textDecoration: 'line-through', color: '#98A2B3', fontSize: '0.78rem' }}>
                        {r.old_value || 'Previous Value'}
                      </div>
                      <div style={{ color: '#027A48', fontWeight: 700 }}>
                        {r.new_value || r.requested_value}
                      </div>
                    </td>

                    <td style={{ padding: '0.75rem 1rem', color: '#475467', fontSize: '0.8rem' }}>
                      {r.created_at ? r.created_at.slice(0, 10) : 'Recent'}
                    </td>

                    <td style={{ padding: '0.75rem 1rem' }}>
                      <StatusBadge status={r.status || 'pending'} />
                    </td>

                    <td style={{ padding: '0.75rem 1rem', textAlign: 'center' }}>
                      <button
                        onClick={() => {
                          setSelectedRequest(r)
                          setReviewAction('none')
                          setRemarks('')
                          setReviewFeedback(null)
                        }}
                        style={{
                          padding: '0.35rem 0.75rem',
                          background: '#EFF4FF',
                          color: '#155EEF',
                          border: '1px solid #B2DDFF',
                          borderRadius: '6px',
                          fontWeight: 700,
                          fontSize: '0.78rem',
                          cursor: 'pointer'
                        }}
                      >
                        ⚖️ Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Modal */}
      {selectedRequest && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(16,43,70,0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1.5rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            width: '100%',
            maxWidth: '680px',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)',
            overflow: 'hidden'
          }}>
            {/* Header */}
            <div style={{
              background: '#102B46',
              color: '#FFFFFF',
              padding: '1.25rem 1.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#98A2B3', textTransform: 'uppercase', fontWeight: 700 }}>
                  Institutional Review & Approval Desk
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, margin: '0.2rem 0 0 0', color: '#FFFFFF' }}>
                  Parent Update Request: #{selectedRequest.request_id}
                </h3>
              </div>
              <button
                onClick={() => setSelectedRequest(null)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#FFFFFF',
                  fontSize: '1.2rem',
                  cursor: 'pointer'
                }}
              >
                ✕
              </button>
            </div>

            {/* Body */}
            <div style={{ padding: '1.5rem', overflowY: 'auto', flex: 1 }}>
              {reviewFeedback && (
                <Alert type={reviewFeedback.type} title={reviewFeedback.type === 'success' ? 'Review Recorded' : 'Action Blocked'} style={{ marginBottom: '1.25rem' }}>
                  {reviewFeedback.message}
                </Alert>
              )}

              {/* Summary Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                <div style={{ background: '#F8FAFC', padding: '1rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                  <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Student Information</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                    {selectedRequest.student_name}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.15rem', fontFamily: 'monospace' }}>
                    {selectedRequest.permanent_student_id}
                  </div>
                </div>

                <div style={{ background: '#F8FAFC', padding: '1rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
                  <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Parent / Guardian</div>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#102B46', marginTop: '0.2rem' }}>
                    {selectedRequest.parent_name || 'Verified Guardian'}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.15rem' }}>
                    {selectedRequest.parent_phone || selectedRequest.parent_email || '—'}
                  </div>
                </div>
              </div>

              {/* Comparison Box */}
              <div style={{ background: '#EFF4FF', border: '1px solid #B2DDFF', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', marginBottom: '0.5rem' }}>
                  Requested Field: {selectedRequest.field_name || selectedRequest.update_type}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div>
                    <div style={{ fontSize: '0.72rem', color: '#475467', fontWeight: 600 }}>Current Database Value:</div>
                    <div style={{ fontSize: '0.92rem', fontWeight: 600, color: '#667085', marginTop: '0.2rem' }}>
                      {selectedRequest.old_value || 'None recorded'}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '0.72rem', color: '#027A48', fontWeight: 700 }}>Requested New Value:</div>
                    <div style={{ fontSize: '1rem', fontWeight: 800, color: '#027A48', marginTop: '0.2rem' }}>
                      {selectedRequest.new_value || selectedRequest.requested_value}
                    </div>
                  </div>
                </div>
                {selectedRequest.reason && (
                  <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px dashed #B2DDFF', fontSize: '0.82rem', color: '#344054' }}>
                    <strong>Reason given:</strong> "{selectedRequest.reason}"
                  </div>
                )}
              </div>

              {/* Review Actions */}
              <div style={{ marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#102B46', marginBottom: '0.5rem' }}>
                  Select Institutional Determination:
                </div>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                  <button
                    onClick={() => setReviewAction('approve')}
                    style={{
                      flex: 1,
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: reviewAction === 'approve' ? '2px solid #12B76A' : '1px solid #D0D5DD',
                      background: reviewAction === 'approve' ? '#ECFDF3' : '#FFFFFF',
                      color: reviewAction === 'approve' ? '#027A48' : '#344054',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    ✓ Approve & Update
                  </button>

                  <button
                    onClick={() => setReviewAction('clarify')}
                    style={{
                      flex: 1,
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: reviewAction === 'clarify' ? '2px solid #7A5AF8' : '1px solid #D0D5DD',
                      background: reviewAction === 'clarify' ? '#F4F3FF' : '#FFFFFF',
                      color: reviewAction === 'clarify' ? '#5925DC' : '#344054',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    💬 Request Clarification
                  </button>

                  <button
                    onClick={() => setReviewAction('reject')}
                    style={{
                      flex: 1,
                      padding: '0.65rem',
                      borderRadius: '8px',
                      border: reviewAction === 'reject' ? '2px solid #F04438' : '1px solid #D0D5DD',
                      background: reviewAction === 'reject' ? '#FEF3F2' : '#FFFFFF',
                      color: reviewAction === 'reject' ? '#B42318' : '#344054',
                      fontWeight: 700,
                      cursor: 'pointer'
                    }}
                  >
                    ✕ Reject Request
                  </button>
                </div>
              </div>

              {/* Remarks textarea */}
              {reviewAction !== 'none' && (
                <div>
                  <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    {reviewAction === 'approve' ? 'Approval Audit Remarks (Optional):' : 'Detailed Justification / Feedback for Parent (Mandatory):'}
                  </label>
                  <textarea
                    rows={3}
                    value={remarks}
                    onChange={e => setRemarks(e.target.value)}
                    placeholder={
                      reviewAction === 'approve'
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

            {/* Footer */}
            <div style={{
              padding: '1rem 1.5rem',
              background: '#F8FAFC',
              borderTop: '1px solid #E2E8F0',
              display: 'flex',
              justifyContent: 'flex-end',
              gap: '0.75rem'
            }}>
              <button
                onClick={() => setSelectedRequest(null)}
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
                onClick={handleExecuteReview}
                disabled={reviewAction === 'none' || submittingReview}
                style={{
                  padding: '0.55rem 1.5rem',
                  borderRadius: '6px',
                  border: 'none',
                  background: reviewAction === 'approve' ? '#12B76A' : reviewAction === 'reject' ? '#F04438' : '#155EEF',
                  color: '#FFFFFF',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  cursor: reviewAction === 'none' || submittingReview ? 'not-allowed' : 'pointer'
                }}
              >
                {submittingReview ? 'Submitting...' : 'Confirm Determination'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
