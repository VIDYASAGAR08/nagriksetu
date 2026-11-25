import { useState, useEffect } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'

export default function PlatformRequestOversightDesk({ token }) {
  const [oversightData, setOversightData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [institutionFilter, setInstitutionFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [feedback, setFeedback] = useState(null)

  // Forward Modal State
  const [selectedForwardReq, setSelectedForwardReq] = useState(null)
  const [targetInstId, setTargetInstId] = useState('')
  const [forwardReason, setForwardReason] = useState('')
  const [submittingForward, setSubmittingForward] = useState(false)

  const loadOversight = async () => {
    try {
      setLoading(true)
      const data = await apiGet('/admin/requests/oversight', token)
      setOversightData(data)
    } catch (err) {
      console.error('Failed to load oversight data:', err)
      setFeedback({ type: 'error', message: err.message || 'Failed to load platform request oversight' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadOversight()
  }, [])

  const handleForwardSubmit = async (e) => {
    e.preventDefault()
    if (!targetInstId.trim() || !forwardReason.trim()) {
      alert('Target institution ID and forwarding reason are required.')
      return
    }
    try {
      setSubmittingForward(true)
      await apiPost(`/admin/requests/${selectedForwardReq}/forward`, {
        target_institution_id: targetInstId.trim(),
        forward_remarks: forwardReason.trim()
      }, token)
      setSelectedForwardReq(null)
      setTargetInstId('')
      setForwardReason('')
      setFeedback({ type: 'success', message: 'Request successfully forwarded to designated institution.' })
      await loadOversight()
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Failed to forward request' })
    } finally {
      setSubmittingForward(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem' }}>
        <LoadingSpinner />
        <p style={{ marginTop: '0.5rem', color: '#64748B' }}>Loading platform request oversight data...</p>
      </div>
    )
  }

  const kpis = oversightData?.kpis || {}
  const instBreakdown = oversightData?.institution_breakdown || []
  const requests = oversightData?.requests || []

  // Filter requests
  const filteredRequests = requests.filter(r => {
    if (statusFilter !== 'ALL' && r.status !== statusFilter) return false
    if (institutionFilter !== 'ALL' && r.assigned_institution_id !== institutionFilter) return false
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      const matchTrack = r.tracking_number?.toLowerCase().includes(q)
      const matchReq = r.requester_name?.toLowerCase().includes(q)
      const matchSub = r.subject?.toLowerCase().includes(q)
      const matchInst = r.assigned_institution_name?.toLowerCase().includes(q) || r.assigned_institution_id?.toLowerCase().includes(q)
      if (!matchTrack && !matchReq && !matchSub && !matchInst) return false
    }
    return true
  })

  return (
    <div style={{ padding: '0.5rem 0' }}>
      {/* Top Banner */}
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
              <span>🏛️</span> State-Wide Request, Grievance & SLA Oversight
            </h2>
            <p style={{ margin: '0.25rem 0 0 0', color: '#64748B', fontSize: '0.875rem' }}>
              Central administrative oversight of all citizen requests, institutional grievances, escalations, and record corrections.
            </p>
          </div>
          <button onClick={loadOversight} className="btn btn--secondary btn--sm" style={{ fontWeight: 600 }}>
            🔄 Refresh Oversight
          </button>
        </div>

        {/* Global KPIs */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '0.75rem' }}>
          <div style={{ background: '#F8FAFC', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #E2E8F0' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600 }}>TOTAL SYSTEM REQUESTS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46' }}>{kpis.total || 0}</div>
          </div>
          <div style={{ background: '#EFF4FF', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #B2DDFF' }}>
            <div style={{ fontSize: '0.75rem', color: '#155EEF', fontWeight: 600 }}>OPEN / IN-PROGRESS</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#155EEF' }}>{kpis.open || 0}</div>
          </div>
          <div style={{ background: '#F4F3FF', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #D6BBFB' }}>
            <div style={{ fontSize: '0.75rem', color: '#7A5AF8', fontWeight: 600 }}>ESCALATED TO STATE</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#7A5AF8' }}>{kpis.escalated || 0}</div>
          </div>
          <div style={{ background: '#ECFDF3', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #A6F4C5' }}>
            <div style={{ fontSize: '0.75rem', color: '#027A48', fontWeight: 600 }}>RECORDS CORRECTED</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#027A48' }}>{kpis.corrected || 0}</div>
          </div>
          <div style={{ background: '#FEF3F2', padding: '0.75rem 1rem', borderRadius: '8px', border: '1px solid #FECDCA' }}>
            <div style={{ fontSize: '0.75rem', color: '#B42318', fontWeight: 600 }}>SLA RISK / OVERDUE</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#B42318' }}>{kpis.overdue || 0}</div>
          </div>
        </div>
      </div>

      {feedback && (
        <div style={{ marginBottom: '1.25rem' }}>
          <Alert type={feedback.type}>{feedback.message}</Alert>
        </div>
      )}

      {/* Institution Breakdown Table */}
      <div style={{ background: '#FFFFFF', borderRadius: '10px', border: '1px solid #E2E8F0', padding: '1.25rem', marginBottom: '1.5rem' }}>
        <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1.05rem', color: '#102B46', fontWeight: 700 }}>
          Institution Request & SLA Performance Breakdown
        </h3>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.84rem' }}>
            <thead>
              <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467', fontWeight: 600 }}>
                <th style={{ padding: '0.6rem 0.85rem' }}>Institution</th>
                <th style={{ padding: '0.6rem 0.85rem' }}>Total Requests</th>
                <th style={{ padding: '0.6rem 0.85rem' }}>Open</th>
                <th style={{ padding: '0.6rem 0.85rem' }}>Corrected</th>
                <th style={{ padding: '0.6rem 0.85rem' }}>Escalated</th>
                <th style={{ padding: '0.6rem 0.85rem' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {instBreakdown.map((ib, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid #F1F5F9' }}>
                  <td style={{ padding: '0.6rem 0.85rem' }}>
                    <div style={{ fontWeight: 600, color: '#102B46' }}>{ib.institution_name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748B' }}><code>{ib.institution_id}</code></div>
                  </td>
                  <td style={{ padding: '0.6rem 0.85rem', fontWeight: 700 }}>{ib.total_requests}</td>
                  <td style={{ padding: '0.6rem 0.85rem', color: '#155EEF', fontWeight: 700 }}>{ib.open_requests}</td>
                  <td style={{ padding: '0.6rem 0.85rem', color: '#027A48', fontWeight: 700 }}>{ib.corrected_requests}</td>
                  <td style={{ padding: '0.6rem 0.85rem', color: ib.escalated_requests > 0 ? '#D92D20' : '#475467', fontWeight: 700 }}>
                    {ib.escalated_requests}
                  </td>
                  <td style={{ padding: '0.6rem 0.85rem' }}>
                    <button
                      onClick={() => setInstitutionFilter(ib.institution_id)}
                      className="btn btn--sm btn--outline"
                      style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                    >
                      Filter Table ↓
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem' }}
          >
            <option value="ALL">All Statuses</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="UNDER_REVIEW">Under Review</option>
            <option value="CLARIFICATION_REQUIRED">Clarification Required</option>
            <option value="CORRECTED">Record Corrected</option>
            <option value="REJECTED">Rejected</option>
            <option value="CLOSED">Closed</option>
          </select>

          <select
            value={institutionFilter}
            onChange={(e) => setInstitutionFilter(e.target.value)}
            style={{ padding: '0.4rem 0.75rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem' }}
          >
            <option value="ALL">All Institutions</option>
            {instBreakdown.map((ib, idx) => (
              <option key={idx} value={ib.institution_id}>
                {ib.institution_name} ({ib.institution_id})
              </option>
            ))}
          </select>

          {institutionFilter !== 'ALL' && (
            <button onClick={() => setInstitutionFilter('ALL')} className="btn btn--sm btn--secondary" style={{ fontSize: '0.75rem' }}>
              Clear Filter ✕
            </button>
          )}
        </div>

        <input
          type="text"
          placeholder="Search by ID, citizen, institution..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{ padding: '0.45rem 0.85rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem', width: '280px' }}
        />
      </div>

      {/* Requests Table */}
      <div style={{ background: '#FFFFFF', borderRadius: '10px', border: '1px solid #E2E8F0', overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0', color: '#475467', fontWeight: 600 }}>
              <th style={{ padding: '0.75rem 1rem' }}>Tracking ID</th>
              <th style={{ padding: '0.75rem 1rem' }}>Assigned Institution</th>
              <th style={{ padding: '0.75rem 1rem' }}>Requester</th>
              <th style={{ padding: '0.75rem 1rem' }}>Subject & Category</th>
              <th style={{ padding: '0.75rem 1rem' }}>Status</th>
              <th style={{ padding: '0.75rem 1rem' }}>Escalated</th>
              <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredRequests.map(r => (
              <tr key={r.request_id} style={{ borderBottom: '1px solid #F1F5F9' }}>
                <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700 }}>
                  {r.tracking_number}
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <div style={{ fontWeight: 600, color: '#102B46' }}>{r.assigned_institution_name || r.assigned_institution_id}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>Tier: {r.routing_tier}</div>
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <div style={{ fontWeight: 600 }}>{r.requester_name}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.requester_role}</div>
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <div style={{ fontWeight: 600, color: '#1E293B' }}>{r.subject}</div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B' }}>{r.category?.replace(/_/g, ' ')}</div>
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  <span style={{
                    padding: '0.2rem 0.55rem',
                    borderRadius: '12px',
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    background: r.status === 'CORRECTED' ? '#D1FADF' : (r.status === 'REJECTED' ? '#FEF3F2' : '#EFF4FF'),
                    color: r.status === 'CORRECTED' ? '#039855' : (r.status === 'REJECTED' ? '#B42318' : '#155EEF')
                  }}>
                    {r.status}
                  </span>
                </td>
                <td style={{ padding: '0.75rem 1rem' }}>
                  {r.is_escalated ? (
                    <span style={{ background: '#FEE4E2', color: '#D92D20', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700 }}>
                      ESCALATED
                    </span>
                  ) : (
                    <span style={{ color: '#94A3B8' }}>No</span>
                  )}
                </td>
                <td style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>
                  <button
                    onClick={() => { setSelectedForwardReq(r.request_id); setTargetInstId(''); setForwardReason(''); }}
                    className="btn btn--sm btn--outline"
                    style={{ fontSize: '0.78rem' }}
                  >
                    Forward / Re-route
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* FORWARD MODAL */}
      {selectedForwardReq && (
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
            maxWidth: '500px',
            width: '100%',
            padding: '1.75rem',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#102B46' }}>Re-Route / Forward Request</h3>
            <p style={{ margin: '0 0 1.25rem 0', fontSize: '0.85rem', color: '#64748B' }}>
              Assign this case to another accredited educational institution.
            </p>

            <form onSubmit={handleForwardSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.35rem' }}>
                  Target Institution ID <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., SCH002 or COL001"
                  value={targetInstId}
                  onChange={(e) => setTargetInstId(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD' }}
                />
              </div>

              <div style={{ marginBottom: '1.25rem' }}>
                <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#1E293B', marginBottom: '0.35rem' }}>
                  Forwarding Justification <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <textarea
                  required
                  rows={3}
                  placeholder="Explain why this request is being reassigned..."
                  value={forwardReason}
                  onChange={(e) => setForwardReason(e.target.value)}
                  style={{ width: '100%', padding: '0.55rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.85rem' }}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
                <button type="button" onClick={() => setSelectedForwardReq(null)} className="btn btn--secondary">
                  Cancel
                </button>
                <button type="submit" disabled={submittingForward} className="btn btn--primary">
                  {submittingForward ? 'Forwarding...' : 'Forward Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
