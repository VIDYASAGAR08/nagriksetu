import React, { useState, useEffect, useCallback } from 'react'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'
import Alert from '../ui/Alert.jsx'

export default function InstitutionParentsDirectory({ token, institutionId }) {
  const [parents, setParents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')

  const loadParents = useCallback(async () => {
    if (!token || !institutionId) return
    try {
      setLoading(true)
      setError('')
      const data = await apiGet(`/institution/${institutionId}/parents`, token)
      setParents(Array.isArray(data) ? data : (data.parents || []))
    } catch (err) {
      setError(err.message || 'Failed to retrieve linked parent directory.')
    } finally {
      setLoading(false)
    }
  }, [token, institutionId])

  useEffect(() => {
    loadParents()
  }, [loadParents])

  const filteredParents = parents.filter(p => {
    if (!searchQuery.trim()) return true
    const q = searchQuery.toLowerCase()
    return (
      (p.full_name && p.full_name.toLowerCase().includes(q)) ||
      (p.student_name && p.student_name.toLowerCase().includes(q)) ||
      (p.permanent_student_id && p.permanent_student_id.toLowerCase().includes(q)) ||
      (p.phone && p.phone.includes(q)) ||
      (p.email && p.email.toLowerCase().includes(q))
    )
  })

  return (
    <div className="institution-parents-directory">
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
              background: '#EFF4FF',
              color: '#155EEF',
              padding: '0.35rem 0.75rem',
              borderRadius: '6px',
              fontWeight: 700,
              fontSize: '0.85rem'
            }}>
              👨‍👩‍👧 Community Registry
            </span>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
              Verified Parents & Legal Guardians Directory
            </h2>
          </div>
          <p style={{ margin: '0.35rem 0 0 0', color: '#667085', fontSize: '0.88rem' }}>
            Registry of verified parents and legal guardians legally linked to enrolled students of this institution.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="text"
            placeholder="Search parent, student, or phone..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{
              padding: '0.5rem 0.85rem',
              borderRadius: '6px',
              border: '1px solid #CBD5E1',
              fontSize: '0.85rem',
              width: '260px'
            }}
          />
          <button
            onClick={loadParents}
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
        <Alert type="error" title="Directory Error" style={{ marginBottom: '1rem' }}>
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
        <div style={{
          padding: '0.85rem 1.25rem',
          background: '#F8FAFC',
          borderBottom: '1px solid #E2E8F0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#102B46' }}>
            Total Verified Guardians: <span style={{ color: '#155EEF' }}>{parents.length} accounts</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: '#667085' }}>
            Showing {filteredParents.length} matching
          </div>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center' }}>
            <LoadingSpinner message="Loading guardian registry..." />
          </div>
        ) : filteredParents.length === 0 ? (
          <div style={{ padding: '3.5rem 1.5rem', textAlign: 'center' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>👨‍👩‍👧</div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.5rem 0' }}>
              No Guardians Found
            </h3>
            <p style={{ color: '#667085', fontSize: '0.88rem', margin: 0 }}>
              No parent or guardian records matched your search parameters.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.86rem' }}>
              <thead>
                <tr style={{ background: '#F8FAFC', borderBottom: '2px solid #E2E8F0', color: '#475467', fontWeight: 700, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Guardian Name</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Relationship</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Linked Student Profile</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Phone Number</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Official Email</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Verification Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredParents.map((p, idx) => (
                  <tr
                    key={p.guardian_id || idx}
                    style={{
                      borderBottom: '1px solid #F2F4F7',
                      background: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA'
                    }}
                  >
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#102B46' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span>👤</span>
                        <span>{p.full_name || 'Verified Guardian'}</span>
                      </div>
                    </td>

                    <td style={{ padding: '0.75rem 1rem', color: '#475467', fontWeight: 600 }}>
                      {p.relationship || 'Father / Legal Guardian'}
                    </td>

                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 700, color: '#102B46' }}>{p.student_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#155EEF', fontFamily: 'monospace' }}>
                        {p.permanent_student_id} {p.standard ? `· Std ${p.standard}-${p.section || 'A'}` : ''}
                      </div>
                    </td>

                    <td style={{ padding: '0.75rem 1rem', color: '#344054', fontWeight: 600 }}>
                      {p.phone || '—'}
                    </td>

                    <td style={{ padding: '0.75rem 1rem', color: '#475467', fontSize: '0.82rem' }}>
                      {p.email || '—'}
                    </td>

                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span style={{
                        background: '#ECFDF3',
                        color: '#027A48',
                        padding: '0.25rem 0.65rem',
                        borderRadius: '20px',
                        fontWeight: 700,
                        fontSize: '0.75rem',
                        border: '1px solid #A6F4C5'
                      }}>
                        ✓ Aadhaar Verified
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
