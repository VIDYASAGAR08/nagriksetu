import { useState, useEffect } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'

const STATUS_CONFIG = {
  SUBMITTED: { label: 'New / Submitted', color: '#155EEF', bg: '#EFF4FF', icon: '📝' },
  UNDER_REVIEW: { label: 'Under Review', color: '#B54708', bg: '#FEF0C7', icon: '🔍' },
  CLARIFICATION_REQUIRED: { label: 'Clarification Required', color: '#C01048', bg: '#FFE4E8', icon: '⚠️' },
  RESUBMITTED: { label: 'Clarification Received', color: '#7A5AF8', bg: '#F4F3FF', icon: '🔄' },
  ACCEPTED: { label: 'Accepted', color: '#027A48', bg: '#ECFDF3', icon: '✅' },
  CORRECTION_PENDING: { label: 'Correction Pending', color: '#E31B23', bg: '#FEF3F2', icon: '⏳' },
  CORRECTED: { label: 'Record Corrected', color: '#039855', bg: '#D1FADF', icon: '🎉' },
  VERIFICATION_PENDING: { label: 'Verification Pending', color: '#0E7090', bg: '#ECFEFF', icon: '📋' },
  VERIFIED: { label: 'Verified', color: '#027A48', bg: '#ECFDF3', icon: '🛡️' },
  REJECTED: { label: 'Rejected', color: '#B42318', bg: '#FEF3F2', icon: '❌' },
  CLOSED: { label: 'Closed', color: '#475467', bg: '#F2F4F7', icon: '🔒' }
}

export default function InstitutionRequestsDesk({ institutionId, institutionName, token }) {
  const [requests, setRequests] = useState([])
  const [summary, setSummary] = useState({})
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [feedback, setFeedback] = useState(null)

  // Investigation Modal
  const [selectedReq, setSelectedReq] = useState(null)
  const [loadingDetails, setLoadingDetails] = useState(false)
  const [detailsData, setDetailsData] = useState(null)

  // Action Modals State
  const [actionType, setActionType] = useState(null) // 'REJECT' | 'CLARIFY' | 'REMARK' | 'CORRECT' | 'ESCALATE'
  const [actionReason, setActionReason] = useState('')
  const [actionNotes, setActionNotes] = useState('')
  const [actionClarificationPrompt, setActionClarificationPrompt] = useState('')
  const [actionVisibility, setActionVisibility] = useState('internal_only') // 'internal_only' | 'requester_visible'
  const [actionCorrectedValue, setActionCorrectedValue] = useState('')
  const [submittingAction, setSubmittingAction] = useState(false)

  // Load Requests
  const loadRequests = async () => {
    if (!institutionId) return
    try {
      setLoading(true)
      const data = await apiGet(`/institution/${institutionId}/requests`, token)
      setRequests(data.requests || [])
      setSummary(data.summary || {})
    } catch (err) {
      console.error('Failed to load institution requests:', err)
      setFeedback({ type: 'error', message: err.message || 'Failed to load requests' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadRequests()
  }, [institutionId])

  // Open Details Modal
  const openDetails = async (reqId) => {
    try {
      setSelectedReq(reqId)
      setLoadingDetails(true)
      setDetailsData(null)
      setActionType(null)
      const data = await apiGet(`/requests/${reqId}`, token)
      setDetailsData(data)
      setActionCorrectedValue(data.request?.requested_value || '')
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to fetch details' })
    } finally {
      setLoadingDetails(false)
    }
  }

  // Handle Accept
  const handleAccept = async () => {
    try {
      setSubmittingAction(true)
      await apiPost(`/institution/${institutionId}/requests/${selectedReq}/accept`, {
        notes: 'Request accepted by institution administrator.'
      }, token)
      setFeedback({ type: 'success', message: 'Request accepted successfully.' })
      await openDetails(selectedReq)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to accept request' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Reject
  const handleReject = async (e) => {
    e.preventDefault()
    if (!actionReason.trim()) {
      alert('Mandatory rejection reason is required.')
      return
    }
    try {
      setSubmittingAction(true)
      await apiPost(`/institution/${institutionId}/requests/${selectedReq}/reject`, {
        rejection_reason: actionReason.trim(),
        remarks: actionNotes.trim() || null
      }, token)
      setActionType(null)
      setActionReason('')
      setActionNotes('')
      setFeedback({ type: 'success', message: 'Request rejected with official recorded reason.' })
      await openDetails(selectedReq)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to reject request' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Request Clarification
  const handleClarification = async (e) => {
    e.preventDefault()
    if (!actionClarificationPrompt.trim()) {
      alert('Please state clearly what clarification or evidence is required.')
      return
    }
    try {
      setSubmittingAction(true)
      await apiPost(`/institution/${institutionId}/requests/${selectedReq}/request-clarification`, {
        clarification_prompt: actionClarificationPrompt.trim()
      }, token)
      setActionType(null)
      setActionClarificationPrompt('')
      setFeedback({ type: 'success', message: 'Clarification requested from requester.' })
      await openDetails(selectedReq)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to request clarification' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Add Remark
  const handleAddRemark = async (e) => {
    e.preventDefault()
    if (!actionNotes.trim()) return
    try {
      setSubmittingAction(true)
      await apiPost(`/institution/${institutionId}/requests/${selectedReq}/remarks`, {
        message: actionNotes.trim(),
        visibility: actionVisibility
      }, token)
      setActionType(null)
      setActionNotes('')
      setFeedback({ type: 'success', message: `Remark saved (${actionVisibility === 'internal_only' ? 'Internal Only' : 'Visible to Requester'}).` })
      await openDetails(selectedReq)
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to add remark' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Execute Correction
  const handleExecuteCorrection = async (e) => {
    e.preventDefault()
    if (!actionCorrectedValue.trim()) {
      alert('Corrected value is required.')
      return
    }
    if (!actionNotes.trim()) {
      alert('Mandatory justification notes are required for database record correction.')
      return
    }
    try {
      setSubmittingAction(true)
      const res = await apiPost(`/institution/${institutionId}/requests/${selectedReq}/execute-correction`, {
        target_module: detailsData.request.target_module,
        target_record_id: detailsData.request.target_record_id,
        field_name: detailsData.request.field_name,
        proposed_new_value: actionCorrectedValue.trim(),
        confirmation_remarks: actionNotes.trim()
      }, token)

      setActionType(null)
      setActionCorrectedValue('')
      setActionNotes('')
      setFeedback({
        type: 'success',
        message: `Database Record Successfully Corrected & Verified! (Updated: ${res.field_name} in ${res.target_table} to "${res.corrected_value}")`
      })
      await openDetails(selectedReq)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Database update failed.' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Escalate
  const handleEscalate = async (e) => {
    e.preventDefault()
    if (!actionNotes.trim()) {
      alert('Escalation reason is required.')
      return
    }
    try {
      setSubmittingAction(true)
      await apiPost(`/institution/${institutionId}/requests/${selectedReq}/escalate`, {
        escalation_reason: actionNotes.trim()
      }, token)
      setActionType(null)
      setActionNotes('')
      setFeedback({ type: 'success', message: 'Request escalated to Platform Authority.' })
      await openDetails(selectedReq)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to escalate' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Close
  const handleClose = async () => {
    if (!window.confirm('Are you sure you want to officially close this request?')) return
    try {
      setSubmittingAction(true)
      await apiPost(`/institution/${institutionId}/requests/${selectedReq}/close`, {
        closing_remarks: 'Completed and closed by institution administrator.'
      }, token)
      setFeedback({ type: 'success', message: 'Request marked as CLOSED.' })
      await openDetails(selectedReq)
      await loadRequests()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to close request' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Filter requests
  const filteredRequests = requests.filter(r => {
    if (statusFilter !== 'ALL' && r.status !== statusFilter) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchTrack = r.tracking_number?.toLowerCase().includes(q)
      const matchReq = r.requester_name?.toLowerCase().includes(q)
      const matchSub = r.subject?.toLowerCase().includes(q)
      const matchTarget = r.target_student_name?.toLowerCase().includes(q) || r.target_student_id?.toLowerCase().includes(q)
      if (!matchTrack && !matchReq && !matchSub && !matchTarget) return false
    }
    return true
  })

  return (
    <div style={{ padding: '0.5rem 0' }}>
      {/* Header and KPI Summary */}
      <div style={{
        background: '#ffffff',
        padding: '1.25rem 1.5rem',
        borderRadius: '10px',
        border: '1px solid #E2E8F0',
        marginBottom: '1.5rem',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <h2 style={{ margin: 0, fontSize: '1.35rem', color: '#102B46', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span>🛡️</span> Requests, Grievances & Record Correction Desk
            </h2>
            <p style={{ margin: '0.25rem 0 0 0', color: '#64748B', fontSize: '0.875rem' }}>
              Investigate grievances, review requests, issue clarifications, and execute authorized transactional record corrections.
            </p>
          </div>
          <button
            onClick={loadRequests}
            className="btn btn--secondary btn--sm"
            style={{ fontWeight: 600 }}
          >
            🔄 Refresh Desk
          </button>
        </div>

        {/* KPI Summary Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
          <div style={{ background: '#F8FAFC', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>TOTAL RECEIVED</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46' }}>{summary.total || 0}</div>
          </div>
          <div style={{ background: '#EFF4FF', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #B2DDFF' }}>
            <div style={{ fontSize: '0.75rem', color: '#155EEF', fontWeight: 600 }}>NEW SUBMISSIONS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#155EEF' }}>{summary.submitted || 0}</div>
          </div>
          <div style={{ background: '#FEF0C7', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #FDD384' }}>
            <div style={{ fontSize: '0.75rem', color: '#B54708', fontWeight: 600 }}>UNDER REVIEW</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#B54708' }}>{summary.under_review || 0}</div>
          </div>
          <div style={{ background: '#FFE4E8', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #FDA29B' }}>
            <div style={{ fontSize: '0.75rem', color: '#C01048', fontWeight: 600 }}>NEEDS CLARIFICATION</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#C01048' }}>{summary.clarification_required || 0}</div>
          </div>
          <div style={{ background: '#ECFDF3', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #A6F4C5' }}>
            <div style={{ fontSize: '0.75rem', color: '#027A48', fontWeight: 600 }}>CORRECTED & RESOLVED</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#027A48' }}>{summary.corrected || 0}</div>
          </div>
          <div style={{ background: '#FEF3F2', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #FECDCA' }}>
            <div style={{ fontSize: '0.75rem', color: '#B42318', fontWeight: 600 }}>REJECTED</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#B42318' }}>{summary.rejected || 0}</div>
          </div>
        </div>
      </div>

      {feedback && (
        <div style={{ marginBottom: '1.25rem' }}>
          <Alert type={feedback.type}>{feedback.message}</Alert>
        </div>
      )}

      {/* Filter Tabs & Search */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
          {[
            { id: 'ALL', label: 'All' },
            { id: 'SUBMITTED', label: 'New' },
            { id: 'UNDER_REVIEW', label: 'Under Review' },
            { id: 'CLARIFICATION_REQUIRED', label: 'Clarification Needed' },
            { id: 'RESUBMITTED', label: 'Clarified' },
            { id: 'CORRECTION_PENDING', label: 'Correction Pending' },
            { id: 'CORRECTED', label: 'Corrected' },
            { id: 'REJECTED', label: 'Rejected' },
            { id: 'CLOSED', label: 'Closed' }
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setStatusFilter(f.id)}
              style={{
                padding: '0.35rem 0.75rem',
                borderRadius: '16px',
                fontSize: '0.8rem',
                fontWeight: statusFilter === f.id ? 700 : 500,
                border: '1px solid',
                borderColor: statusFilter === f.id ? '#155EEF' : '#D0D5DD',
                background: statusFilter === f.id ? '#EFF4FF' : '#FFFFFF',
                color: statusFilter === f.id ? '#155EEF' : '#475467',
                cursor: 'pointer'
              }}
            >
              {f.label}
            </button>
          ))}
        </div>

        <input
          type="text"
          placeholder="Filter by Tracking ID, Citizen, Student..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            padding: '0.45rem 0.85rem',
            borderRadius: '6px',
            border: '1px solid #D0D5DD',
            fontSize: '0.85rem',
            width: '280px'
          }}
        />
      </div>

      {/* Requests Table */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <LoadingSpinner />
        </div>
      ) : filteredRequests.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', background: '#FFFFFF', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🗂️</div>
          <h3 style={{ margin: 0, color: '#102B46' }}>No Requests Matching Criteria</h3>
          <p style={{ color: '#64748B', margin: '0.5rem 0 0 0', fontSize: '0.875rem' }}>
            There are currently no active requests under this filter.
          </p>
        </div>
      ) : (
        <div style={{ background: '#FFFFFF', borderRadius: '10px', border: '1px solid #E2E8F0', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
            <thead>
              <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467', fontWeight: 600 }}>
                <th style={{ padding: '0.75rem 1rem' }}>Tracking ID</th>
                <th style={{ padding: '0.75rem 1rem' }}>Requester</th>
                <th style={{ padding: '0.75rem 1rem' }}>Category & Subject</th>
                <th style={{ padding: '0.75rem 1rem' }}>Target Person / Student</th>
                <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                <th style={{ padding: '0.75rem 1rem' }}>Priority</th>
                <th style={{ padding: '0.75rem 1rem' }}>Date</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredRequests.map(r => {
                const statusMeta = STATUS_CONFIG[r.status] || { label: r.status, color: '#475467', bg: '#F2F4F7', icon: '📄' }
                return (
                  <tr key={r.request_id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                    <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#0F172A' }}>
                      {r.tracking_number}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 600, color: '#102B46' }}>{r.requester_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.requester_role}</div>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 600, color: '#1E293B' }}>{r.subject}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.category?.replace(/_/g, ' ')}</div>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      {r.target_student_name ? (
                        <div>
                          <div style={{ fontWeight: 600, color: '#102B46' }}>{r.target_student_name}</div>
                          <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.target_student_id}</div>
                        </div>
                      ) : (
                        <span style={{ color: '#94A3B8' }}>Self / Institution</span>
                      )}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{
                        padding: '0.2rem 0.6rem',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: 700,
                        background: statusMeta.bg,
                        color: statusMeta.color,
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem'
                      }}>
                        {statusMeta.icon} {statusMeta.label}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        color: r.priority === 'URGENT' ? '#D92D20' : (r.priority === 'HIGH' ? '#B54708' : '#475467')
                      }}>
                        {r.priority}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontSize: '0.78rem', color: '#64748B' }}>
                      {new Date(r.created_at).toLocaleDateString()}
                    </td>
                    <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                      <button
                        onClick={() => openDetails(r.request_id)}
                        className="btn btn--sm"
                        style={{
                          background: '#155EEF',
                          color: '#FFFFFF',
                          border: 'none',
                          padding: '0.35rem 0.75rem',
                          borderRadius: '6px',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        Investigate & Action →
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* INVESTIGATION & ACTION MODAL */}
      {selectedReq && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(16, 24, 40, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          padding: '1rem'
        }}>
          <div style={{
            background: '#FFFFFF',
            borderRadius: '12px',
            maxWidth: '850px',
            width: '100%',
            maxHeight: '92vh',
            overflowY: 'auto',
            padding: '2rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.75rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase' }}>
                  Official Grievance & Record Correction Investigation
                </span>
                <h3 style={{ margin: '0.15rem 0 0 0', fontSize: '1.3rem', color: '#102B46', fontWeight: 700 }}>
                  {detailsData?.request?.tracking_number || selectedReq}
                </h3>
              </div>
              <button
                type="button"
                onClick={() => { setSelectedReq(null); setActionType(null); }}
                style={{ background: 'none', border: 'none', fontSize: '1.5rem', cursor: 'pointer', color: '#94A3B8' }}
              >
                ✕
              </button>
            </div>

            {loadingDetails || !detailsData ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <LoadingSpinner />
                <p style={{ marginTop: '0.5rem', color: '#64748B' }}>Loading case file and audit trails...</p>
              </div>
            ) : (
              <div>
                {/* Status Bar */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  background: STATUS_CONFIG[detailsData.request.status]?.bg || '#F8FAFC',
                  border: `1px solid ${STATUS_CONFIG[detailsData.request.status]?.color || '#CBD5E1'}`,
                  borderRadius: '8px',
                  padding: '0.85rem 1.25rem',
                  marginBottom: '1.25rem'
                }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#475467', fontWeight: 600 }}>STATUS: </span>
                    <strong style={{ fontSize: '1rem', color: STATUS_CONFIG[detailsData.request.status]?.color }}>
                      {STATUS_CONFIG[detailsData.request.status]?.icon} {STATUS_CONFIG[detailsData.request.status]?.label}
                    </strong>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.75rem', color: '#475467', fontWeight: 600 }}>ROUTING: </span>
                    <strong style={{ fontSize: '0.875rem', color: '#102B46' }}>
                      {detailsData.request.assigned_institution_id}
                    </strong>
                  </div>
                </div>

                {/* Main Case Summary */}
                <div style={{ background: '#F8FAFC', padding: '1rem', borderRadius: '8px', border: '1px solid #E2E8F0', marginBottom: '1.25rem' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.85rem' }}>
                    <div><strong>Requester:</strong> {detailsData.request.requester_name} ({detailsData.request.requester_role})</div>
                    <div><strong>Contact:</strong> {detailsData.request.requester_email || detailsData.request.requester_phone || 'On file'}</div>
                    <div><strong>Category:</strong> {detailsData.request.category?.replace(/_/g, ' ')}</div>
                    <div><strong>Priority:</strong> {detailsData.request.priority}</div>
                    {detailsData.request.target_student_name && (
                      <div style={{ gridColumn: 'span 2' }}>
                        <strong>Target Student:</strong> {detailsData.request.target_student_name} (ID: <code>{detailsData.request.target_student_id}</code> | PSID: <code>{detailsData.request.permanent_student_id}</code>)
                      </div>
                    )}
                  </div>
                  <div style={{ marginTop: '0.75rem', borderTop: '1px solid #E2E8F0', paddingTop: '0.5rem' }}>
                    <strong>Subject:</strong> {detailsData.request.subject}
                    <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.875rem', color: '#334155', lineHeight: 1.4 }}>
                      {detailsData.request.description}
                    </p>
                  </div>
                </div>

                {/* Target Record & Field Preview */}
                {detailsData.request.target_module && detailsData.request.field_name && (
                  <div style={{
                    background: '#F0F9FF',
                    border: '1px solid #B9E6FE',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1.25rem'
                  }}>
                    <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#026AA2', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                      Database Target Record Specification
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', fontSize: '0.825rem' }}>
                      <div>Target Table: <code>{detailsData.request.target_module}</code></div>
                      <div>Target Field: <code>{detailsData.request.field_name}</code></div>
                      <div>Record Key: <code>{detailsData.request.target_record_id}</code></div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '0.75rem', background: '#FFFFFF', padding: '0.75rem', borderRadius: '6px' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: '#64748B', display: 'block' }}>Current Value in Database:</span>
                        <strong style={{ color: '#B42318' }}>{detailsData.request.current_value || 'None / Not Set'}</strong>
                      </div>
                      <div>
                        <span style={{ fontSize: '0.75rem', color: '#64748B', display: 'block' }}>Requested Correction:</span>
                        <strong style={{ color: '#027A48' }}>{detailsData.request.requested_value || 'None Specified'}</strong>
                      </div>
                    </div>
                  </div>
                )}

                {/* Verification / Rejection / Clarification Status Notes */}
                {detailsData.request.rejection_reason && (
                  <div style={{ background: '#FEF3F2', border: '1px solid #FDA29B', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', color: '#B42318', fontSize: '0.85rem' }}>
                    <strong>Official Rejection Reason:</strong> {detailsData.request.rejection_reason}
                  </div>
                )}

                {detailsData.request.clarification_prompt && (
                  <div style={{ background: '#FFF8F0', border: '1px solid #FEDF89', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', color: '#B54708', fontSize: '0.85rem' }}>
                    <strong>Clarification Prompt Issued:</strong> {detailsData.request.clarification_prompt}
                  </div>
                )}

                {/* Action Bar Buttons */}
                <div style={{
                  display: 'flex',
                  gap: '0.5rem',
                  flexWrap: 'wrap',
                  background: '#FFFFFF',
                  padding: '1rem',
                  border: '1px solid #D0D5DD',
                  borderRadius: '8px',
                  marginBottom: '1.25rem'
                }}>
                  <button
                    onClick={handleAccept}
                    disabled={submittingAction || ['ACCEPTED', 'CORRECTED', 'CLOSED'].includes(detailsData.request.status)}
                    style={{ background: '#027A48', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    ✓ Accept Request
                  </button>

                  <button
                    onClick={() => { setActionType('CORRECT'); setActionNotes(''); }}
                    disabled={submittingAction || detailsData.request.status === 'CORRECTED'}
                    style={{ background: '#155EEF', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    🛠️ Execute Live Correction
                  </button>

                  <button
                    onClick={() => { setActionType('CLARIFY'); setActionClarificationPrompt(''); }}
                    disabled={submittingAction || ['CORRECTED', 'CLOSED', 'REJECTED'].includes(detailsData.request.status)}
                    style={{ background: '#B54708', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    ❓ Request Clarification
                  </button>

                  <button
                    onClick={() => { setActionType('REJECT'); setActionReason(''); setActionNotes(''); }}
                    disabled={submittingAction || ['CORRECTED', 'CLOSED', 'REJECTED'].includes(detailsData.request.status)}
                    style={{ background: '#D92D20', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    ✕ Reject Request
                  </button>

                  <button
                    onClick={() => { setActionType('REMARK'); setActionNotes(''); }}
                    style={{ background: '#475467', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    💬 Add Remark
                  </button>

                  <button
                    onClick={() => { setActionType('ESCALATE'); setActionNotes(''); }}
                    disabled={detailsData.request.is_escalated}
                    style={{ background: '#7A5AF8', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    🚀 Escalate to Platform
                  </button>

                  <button
                    onClick={handleClose}
                    disabled={detailsData.request.status === 'CLOSED'}
                    style={{ background: '#344054', color: '#FFFFFF', padding: '0.45rem 0.85rem', borderRadius: '6px', border: 'none', fontWeight: 600, cursor: 'pointer', fontSize: '0.825rem' }}
                  >
                    🔒 Close Request
                  </button>
                </div>

                {/* ACTION SUB-FORMS */}
                {actionType === 'CORRECT' && (
                  <div style={{ background: '#EFF8FF', border: '2px solid #2E90FA', padding: '1.25rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#175CD3' }}>
                      Authorised Live Record Correction Engine
                    </h4>
                    <p style={{ margin: '0 0 1rem 0', fontSize: '0.825rem', color: '#1E40AF' }}>
                      Executing this will immediately apply a transactional database update to <code>{detailsData.request.target_module}</code>. All changes are permanently recorded in the audit trail.
                    </p>
                    <form onSubmit={handleExecuteCorrection}>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
                          Target Field: <code>{detailsData.request.field_name}</code>
                        </label>
                        <input
                          type="text"
                          required
                          value={actionCorrectedValue}
                          onChange={(e) => setActionCorrectedValue(e.target.value)}
                          placeholder="Corrected value to write to database"
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #94A3B8', fontSize: '0.9rem' }}
                        />
                      </div>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
                          Official Correction Justification / Audit Notes <span style={{ color: '#D92D20' }}>*</span>
                        </label>
                        <textarea
                          required
                          rows={2}
                          value={actionNotes}
                          onChange={(e) => setActionNotes(e.target.value)}
                          placeholder="e.g., Verified register; attendance rectified from Absent to Present."
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #94A3B8', fontSize: '0.85rem' }}
                        />
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                        <button type="button" onClick={() => setActionType(null)} className="btn btn--secondary btn--sm">Cancel</button>
                        <button type="submit" disabled={submittingAction} className="btn btn--primary btn--sm" style={{ background: '#155EEF', color: '#FFFFFF' }}>
                          {submittingAction ? 'Writing to Database...' : 'Commit Live Record Correction →'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {actionType === 'REJECT' && (
                  <div style={{ background: '#FEF3F2', border: '2px solid #F97066', padding: '1.25rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#B42318' }}>
                      Reject Request (Mandatory Reason Required)
                    </h4>
                    <p style={{ margin: '0 0 1rem 0', fontSize: '0.825rem', color: '#7A271A' }}>
                      The requester will be immediately notified and provided with the official explanation below.
                    </p>
                    <form onSubmit={handleReject}>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
                          Mandatory Rejection Reason <span style={{ color: '#D92D20' }}>*</span>
                        </label>
                        <input
                          type="text"
                          required
                          value={actionReason}
                          onChange={(e) => setActionReason(e.target.value)}
                          placeholder="e.g., CCTV verification confirms absence on requested date."
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #FDA29B', fontSize: '0.9rem' }}
                        />
                      </div>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
                          Additional Explanatory Remarks (Optional)
                        </label>
                        <textarea
                          rows={2}
                          value={actionNotes}
                          onChange={(e) => setActionNotes(e.target.value)}
                          placeholder="Advice or guidance for the requester..."
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #FDA29B', fontSize: '0.85rem' }}
                        />
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                        <button type="button" onClick={() => setActionType(null)} className="btn btn--secondary btn--sm">Cancel</button>
                        <button type="submit" disabled={submittingAction} className="btn btn--danger btn--sm">
                          {submittingAction ? 'Rejecting...' : 'Confirm Rejection'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {actionType === 'CLARIFY' && (
                  <div style={{ background: '#FFF8F0', border: '2px solid #FD853A', padding: '1.25rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#B54708' }}>
                      Request Additional Clarification or Evidence
                    </h4>
                    <form onSubmit={handleClarification}>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
                          Clarification Prompt <span style={{ color: '#D92D20' }}>*</span>
                        </label>
                        <textarea
                          required
                          rows={3}
                          value={actionClarificationPrompt}
                          onChange={(e) => setActionClarificationPrompt(e.target.value)}
                          placeholder="State specifically what evidence or details the requester must provide..."
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #FEDF89', fontSize: '0.875rem' }}
                        />
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                        <button type="button" onClick={() => setActionType(null)} className="btn btn--secondary btn--sm">Cancel</button>
                        <button type="submit" disabled={submittingAction} className="btn btn--sm" style={{ background: '#B54708', color: '#FFFFFF' }}>
                          {submittingAction ? 'Sending...' : 'Send Clarification Prompt'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {actionType === 'REMARK' && (
                  <div style={{ background: '#F8FAFC', border: '1px solid #CBD5E1', padding: '1.25rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#1E293B' }}>Add Official Remark</h4>
                    <form onSubmit={handleAddRemark}>
                      <div style={{ marginBottom: '0.75rem' }}>
                        <textarea
                          required
                          rows={3}
                          value={actionNotes}
                          onChange={(e) => setActionNotes(e.target.value)}
                          placeholder="Enter administrative case notes or communication..."
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                        />
                      </div>
                      <div style={{ marginBottom: '1rem', display: 'flex', gap: '1.5rem', fontSize: '0.85rem' }}>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
                          <input
                            type="radio"
                            name="visibility"
                            checked={actionVisibility === 'internal_only'}
                            onChange={() => setActionVisibility('internal_only')}
                          />
                          <span><strong>🔒 Internal Only</strong> (Confidential to institution staff)</span>
                        </label>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', cursor: 'pointer' }}>
                          <input
                            type="radio"
                            name="visibility"
                            checked={actionVisibility === 'requester_visible'}
                            onChange={() => setActionVisibility('requester_visible')}
                          />
                          <span><strong>👁️ Requester Visible</strong> (Visible on citizen dashboard)</span>
                        </label>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                        <button type="button" onClick={() => setActionType(null)} className="btn btn--secondary btn--sm">Cancel</button>
                        <button type="submit" disabled={submittingAction} className="btn btn--primary btn--sm">Save Remark</button>
                      </div>
                    </form>
                  </div>
                )}

                {actionType === 'ESCALATE' && (
                  <div style={{ background: '#F4F3FF', border: '2px solid #7A5AF8', padding: '1.25rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
                    <h4 style={{ margin: '0 0 0.5rem 0', color: '#5925DC' }}>Escalate Case to Platform Administrator</h4>
                    <form onSubmit={handleEscalate}>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.25rem' }}>
                          Escalation Reason <span style={{ color: '#D92D20' }}>*</span>
                        </label>
                        <textarea
                          required
                          rows={2}
                          value={actionNotes}
                          onChange={(e) => setActionNotes(e.target.value)}
                          placeholder="State why platform intervention is required..."
                          style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D6BBFB', fontSize: '0.85rem' }}
                        />
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                        <button type="button" onClick={() => setActionType(null)} className="btn btn--secondary btn--sm">Cancel</button>
                        <button type="submit" disabled={submittingAction} className="btn btn--sm" style={{ background: '#7A5AF8', color: '#FFFFFF' }}>
                          Escalate Now
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {/* Remarks & Investigation Log */}
                <div style={{ marginBottom: '1.5rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: '#102B46', fontSize: '0.95rem', borderBottom: '1px solid #E2E8F0', paddingBottom: '0.35rem' }}>
                    Investigation Remarks & Case Notes
                  </h4>
                  {detailsData.remarks?.length === 0 ? (
                    <p style={{ fontSize: '0.825rem', color: '#64748B', fontStyle: 'italic' }}>No remarks recorded yet.</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {detailsData.remarks?.map((rem, idx) => (
                        <div
                          key={idx}
                          style={{
                            background: rem.visibility === 'internal_only' ? '#F8F9FC' : '#FFFFFF',
                            border: '1px solid',
                            borderColor: rem.visibility === 'internal_only' ? '#D0D5DD' : '#94A3B8',
                            borderRadius: '6px',
                            padding: '0.75rem'
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '0.25rem' }}>
                            <span><strong>{rem.author_name}</strong> ({rem.author_role})</span>
                            <span style={{
                              fontWeight: 700,
                              color: rem.visibility === 'internal_only' ? '#B42318' : '#027A48'
                            }}>
                              {rem.visibility === 'internal_only' ? '🔒 Internal Only' : '👁️ Requester Visible'}
                            </span>
                          </div>
                          <p style={{ margin: 0, fontSize: '0.85rem', color: '#1E293B' }}>{rem.message || rem.remark_text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div style={{ textAlign: 'right', borderTop: '1px solid #E2E8F0', paddingTop: '1rem' }}>
                  <button onClick={() => { setSelectedReq(null); setActionType(null); }} className="btn btn--secondary">
                    Close Case File
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
