import { useState } from 'react'
import { useLocation, useSearchParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'

export default function SelectWorkspacePage() {
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { selectWorkspace } = useAuth()

  const tempToken = location.state?.temp_token || searchParams.get('temp_token') || 'demo_token'
  let workspaces = location.state?.workspaces || []
  if (workspaces.length === 0 && searchParams.get('demo') === '1') {
    workspaces = [
      { institution_id: 'SCH001', school_name: 'Government Model Higher Primary School', school_type: 'Primary School', role_id: 'school_admin', role_name: 'Institution Administrator' },
      { institution_id: 'SCH011', school_name: 'Tumakuru Model School', school_type: 'High School', role_id: 'school_admin', role_name: 'Institution Administrator' }
    ]
  }

  const [loadingInstId, setLoadingInstId] = useState(null)
  const [error, setError] = useState('')

  async function handleSelect(institutionId) {
    try {
      setLoadingInstId(institutionId)
      setError('')
      const me = await selectWorkspace(tempToken, institutionId)
      if (me.role === 'school_admin' || me.role === 'school_staff') {
        navigate('/staff')
      } else if (me.role === 'platform_admin') {
        navigate('/admin')
      } else {
        navigate('/')
      }
    } catch (err) {
      setError(err.message || 'Failed to initialize institution workspace session.')
      setLoadingInstId(null)
    }
  }

  if (!tempToken || workspaces.length === 0) {
    return (
      <div style={{ minHeight: 'calc(100vh - 250px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: '#f4f5f7' }}>
        <div className="card" style={{ maxWidth: '480px', width: '100%', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', textAlign: 'center' }}>
          <Alert type="warning" title="Session Missing or Expired">
            No active multi-institution workspace session was detected. Please log in with your credentials to choose your workspace.
          </Alert>
          <div style={{ marginTop: '1.5rem' }}>
            <Link to="/login" className="btn btn--primary" style={{ textDecoration: 'none' }}>
              Return to Sign In
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div style={{ minHeight: 'calc(100vh - 250px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem', background: '#f4f5f7' }}>
      <div className="card" style={{ maxWidth: '580px', width: '100%', padding: '2rem', border: '1px solid #d0d5dd', borderRadius: '8px', background: '#ffffff', boxShadow: '0 4px 6px rgba(0,0,0,0.05)' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <div style={{ display: 'inline-block', background: '#1a3a6b', color: '#ffffff', fontWeight: 700, padding: '0.35rem 0.75rem', borderRadius: '4px', fontSize: '0.8125rem', marginBottom: '0.75rem' }}>
            MULTI-INSTITUTION WORKSPACE SELECTOR
          </div>
          <h1 style={{ fontSize: '1.6rem', color: '#1a3a6b', margin: '0 0 0.5rem 0' }}>Select Active Institution</h1>
          <p style={{ color: '#4b5563', fontSize: '0.875rem', margin: 0 }}>
            Your account is authorized across multiple educational institutions. Choose a workspace for this session:
          </p>
        </div>

        {error && <Alert type="error" title="Workspace Error" className="mb-4">{error}</Alert>}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1rem' }}>
          {workspaces.map((ws) => {
            const isProcessing = loadingInstId === ws.institution_id
            return (
              <div
                key={ws.institution_id}
                style={{
                  padding: '1.25rem',
                  border: '1px solid #cbd5e1',
                  borderRadius: '6px',
                  background: '#f8fafc',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '1rem',
                  transition: 'all 0.2s ease',
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem' }}>
                    <span style={{ fontWeight: 700, color: '#1a3a6b', fontSize: '1rem' }}>
                      {ws.school_name || ws.institution_id}
                    </span>
                    <span className="badge badge--neutral" style={{ fontSize: '0.75rem', background: '#e2e8f0', color: '#334155', padding: '0.15rem 0.4rem', borderRadius: '4px' }}>
                      {ws.institution_id}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8125rem', color: '#64748b' }}>
                    Type: <strong style={{ color: '#334155' }}>{ws.school_type || 'Institution'}</strong> · Role:{' '}
                    <strong style={{ color: '#1a3a6b' }}>{ws.role_name || ws.role_id}</strong>
                  </div>
                </div>

                <button
                  type="button"
                  disabled={loadingInstId !== null}
                  onClick={() => handleSelect(ws.institution_id)}
                  className="btn btn--primary btn--sm"
                  style={{ minWidth: '130px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.4rem' }}
                >
                  {isProcessing ? <LoadingSpinner size="sm" /> : 'Enter Desk →'}
                </button>
              </div>
            )
          })}
        </div>

        <div style={{ textAlign: 'center', marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid #e2e8f0' }}>
          <Link to="/login" style={{ fontSize: '0.875rem', color: '#64748b', textDecoration: 'none' }}>
            ← Cancel and return to sign in
          </Link>
        </div>
      </div>
    </div>
  )
}
