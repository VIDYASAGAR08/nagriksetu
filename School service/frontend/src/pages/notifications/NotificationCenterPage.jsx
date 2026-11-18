import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiFetch } from '../../utils/api.js'

export default function NotificationCenterPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [notifications, setNotifications] = useState([])
  const [total, setTotal] = useState(0)
  const [unreadCount, setUnreadCount] = useState(0)
  const [loading, setLoading] = useState(true)

  // Filters
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [page, setPage] = useState(0)
  const pageSize = 15

  // Modals
  const [preferencesOpen, setPreferencesOpen] = useState(false)
  const [channelStatusOpen, setChannelStatusOpen] = useState(false)
  const [channelStatuses, setChannelStatuses] = useState(null)
  const [preferences, setPreferences] = useState({
    academic_updates: 1,
    attendance_alerts: 1,
    examination_alerts: 1,
    admission_updates: 1,
    institution_announcements: 1,
    administrative_alerts: 1,
    email_enabled: 1,
    sms_enabled: 1,
    whatsapp_enabled: 0
  })
  const [savingPrefs, setSavingPrefs] = useState(false)
  const [prefSuccess, setPrefSuccess] = useState('')

  async function loadNotifications() {
    setLoading(true)
    try {
      const catParam = selectedCategory !== 'all' ? `&category=${selectedCategory}` : ''
      const unreadParam = unreadOnly ? '&unread_only=true' : ''
      const offset = page * pageSize

      const data = await apiFetch(`/notifications?limit=${pageSize}&offset=${offset}&include_meta=true${catParam}${unreadParam}`)
      if (data) {
        setNotifications(data.items || [])
        setTotal(data.total || 0)
        setUnreadCount(data.unread_count || 0)
      }
    } catch (e) {
      console.error('Failed to load notifications:', e)
    } finally {
      setLoading(false)
    }
  }

  async function loadPreferences() {
    try {
      const data = await apiFetch('/notifications/preferences')
      if (data) {
        setPreferences(data)
      }
    } catch (e) {
      console.error('Failed to load preferences:', e)
    }
  }

  async function loadChannelStatuses() {
    try {
      const data = await apiFetch('/notifications/channels/status')
      if (data) {
        setChannelStatuses(data)
      }
    } catch (e) {
      console.error('Failed to load channel statuses:', e)
    }
  }

  useEffect(() => {
    loadNotifications()
  }, [selectedCategory, unreadOnly, page])

  useEffect(() => {
    loadPreferences()
    loadChannelStatuses()
  }, [])

  async function handleMarkAsRead(notifId) {
    try {
      await apiFetch(`/notifications/${notifId}/read`, { method: 'POST' })
      setNotifications(prev => prev.map(n => n.notification_id === notifId ? { ...n, is_read: 1 } : n))
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (e) {
      console.error(e)
    }
  }

  async function handleMarkAllAsRead() {
    try {
      await apiFetch('/notifications/read-all', { method: 'POST' })
      setNotifications(prev => prev.map(n => ({ ...n, is_read: 1 })))
      setUnreadCount(0)
    } catch (e) {
      console.error(e)
    }
  }

  async function handleSavePreferences(e) {
    e.preventDefault()
    setSavingPrefs(true)
    setPrefSuccess('')
    try {
      const updated = await apiFetch('/notifications/preferences', {
        method: 'PUT',
        body: JSON.stringify(preferences)
      })
      if (updated) {
        setPreferences(updated)
        setPrefSuccess('Notification preferences saved successfully.')
        setTimeout(() => setPrefSuccess(''), 3500)
      }
    } catch (e) {
      console.error('Save preferences failed:', e)
    } finally {
      setSavingPrefs(false)
    }
  }

  function getCategoryColor(cat) {
    switch (cat?.toLowerCase()) {
      case 'attendance': return { bg: '#FEF3F2', text: '#B42318', border: '#FECDCA' }
      case 'academic': return { bg: '#EFF8FF', text: '#175CD3', border: '#B2DDFF' }
      case 'examination': return { bg: '#F9F5FF', text: '#6941C6', border: '#E9D7FE' }
      case 'announcement': return { bg: '#ECFDF3', text: '#027A48', border: '#A6F4C5' }
      case 'admission': return { bg: '#EEF4FF', text: '#3538CD', border: '#C7D7FE' }
      case 'administrative': return { bg: '#F0F9FF', text: '#026AA2', border: '#B9E6FE' }
      case 'security': return { bg: '#FFF1F3', text: '#C01048', border: '#FCCEEE' }
      default: return { bg: '#F8F9FC', text: '#344054', border: '#D0D5DD' }
    }
  }

  const categories = [
    { id: 'all', label: 'All Categories' },
    { id: 'attendance', label: 'Attendance' },
    { id: 'academic', label: 'Academic & Marks' },
    { id: 'examination', label: 'Examinations' },
    { id: 'announcement', label: 'Announcements' },
    { id: 'admission', label: 'Admissions' },
    { id: 'administrative', label: 'Administrative' },
    { id: 'security', label: 'Security & System' }
  ]

  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="container" style={{ padding: '2rem 1rem', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Breadcrumb */}
      <div style={{ marginBottom: '1rem', fontSize: '0.85rem', color: '#667085' }}>
        <Link to="/" style={{ color: '#155EEF', textDecoration: 'none' }}>Home</Link> &rsaquo;{' '}
        <span style={{ color: '#344054', fontWeight: 600 }}>Notification & Communication Center</span>
      </div>

      {/* Header Banner */}
      <div
        style={{
          background: 'linear-gradient(135deg, #102B46 0%, #155EEF 100%)',
          borderRadius: '12px',
          padding: '1.75rem 2rem',
          color: '#ffffff',
          marginBottom: '1.5rem',
          boxShadow: '0 4px 12px rgba(16, 43, 70, 0.15)',
          display: 'flex',
          flexWrap: 'wrap',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '1rem'
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
            <span style={{ fontSize: '1.8rem' }}>🔔</span>
            <h1 style={{ margin: 0, fontSize: '1.6rem', fontWeight: 800 }}>Notification & Communication Center</h1>
          </div>
          <p style={{ margin: 0, opacity: 0.9, fontSize: '0.95rem' }}>
            Unified real-time alerts, academic evaluations, attendance tracking, and official institutional announcements.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            type="button"
            onClick={() => setChannelStatusOpen(true)}
            style={{
              background: 'rgba(255, 255, 255, 0.15)',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              color: '#ffffff',
              padding: '8px 14px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            📡 Provider Status
          </button>

          <button
            type="button"
            onClick={() => setPreferencesOpen(true)}
            style={{
              background: '#ffffff',
              border: 'none',
              color: '#102B46',
              padding: '8px 16px',
              borderRadius: '8px',
              fontSize: '0.85rem',
              fontWeight: 700,
              cursor: 'pointer',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            ⚙️ Preferences
          </button>
        </div>
      </div>

      {/* KPI Overview Strip */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          marginBottom: '1.5rem'
        }}
      >
        <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '10px', border: '1px solid #EAECF0' }}>
          <div style={{ fontSize: '0.8rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>Total Alerts</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#102B46', marginTop: '4px' }}>{total}</div>
        </div>
        <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '10px', border: '1px solid #EAECF0' }}>
          <div style={{ fontSize: '0.8rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>Unread Alerts</div>
          <div style={{ fontSize: '1.8rem', fontWeight: 800, color: unreadCount > 0 ? '#D92D20' : '#027A48', marginTop: '4px' }}>
            {unreadCount}
          </div>
        </div>
        <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '10px', border: '1px solid #EAECF0' }}>
          <div style={{ fontSize: '0.8rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>Delivery Channels</div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#102B46', marginTop: '8px' }}>
            In-App: <span style={{ color: '#027A48' }}>Active</span> | External: <span style={{ color: '#667085' }}>Audited</span>
          </div>
        </div>
        <div style={{ background: '#ffffff', padding: '1.25rem', borderRadius: '10px', border: '1px solid #EAECF0' }}>
          <div style={{ fontSize: '0.8rem', color: '#667085', fontWeight: 600, textTransform: 'uppercase' }}>Tenant Scope</div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: '#102B46', marginTop: '8px' }}>
            {user?.school_id || 'System User'} ({user?.role?.replace('_', ' ')?.toUpperCase()})
          </div>
        </div>
      </div>

      {/* Filter and Action Bar */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '10px',
          border: '1px solid #EAECF0',
          padding: '1rem 1.25rem',
          marginBottom: '1.5rem'
        }}
      >
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between', gap: '1rem' }}>
          {/* Category Tabs */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {categories.map(cat => (
              <button
                key={cat.id}
                type="button"
                onClick={() => {
                  setSelectedCategory(cat.id)
                  setPage(0)
                }}
                style={{
                  background: selectedCategory === cat.id ? '#102B46' : '#F8F9FC',
                  color: selectedCategory === cat.id ? '#ffffff' : '#475467',
                  border: '1px solid',
                  borderColor: selectedCategory === cat.id ? '#102B46' : '#D0D5DD',
                  padding: '5px 12px',
                  borderRadius: '16px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease'
                }}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* Quick Actions */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: '#344054', cursor: 'pointer', fontWeight: 600 }}>
              <input
                type="checkbox"
                checked={unreadOnly}
                onChange={e => {
                  setUnreadOnly(e.target.checked)
                  setPage(0)
                }}
                style={{ width: '16px', height: '16px', cursor: 'pointer' }}
              />
              Unread only
            </label>

            {unreadCount > 0 && (
              <button
                type="button"
                onClick={handleMarkAllAsRead}
                style={{
                  background: '#EFF8FF',
                  border: '1px solid #B2DDFF',
                  color: '#175CD3',
                  padding: '5px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                ✓ Mark all as read
              </button>
            )}

            <button
              type="button"
              onClick={loadNotifications}
              style={{
                background: '#F8F9FC',
                border: '1px solid #D0D5DD',
                color: '#344054',
                padding: '5px 10px',
                borderRadius: '6px',
                fontSize: '0.82rem',
                cursor: 'pointer'
              }}
              title="Refresh ledger"
            >
              🔄 Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Notifications Ledger */}
      <div
        style={{
          background: '#ffffff',
          borderRadius: '12px',
          border: '1px solid #EAECF0',
          overflow: 'hidden',
          boxShadow: '0 1px 3px rgba(16, 24, 40, 0.05)'
        }}
      >
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: '#667085' }}>
            Loading notification ledger...
          </div>
        ) : notifications.length === 0 ? (
          <div style={{ padding: '4rem 1rem', textAlign: 'center', color: '#667085' }}>
            <div style={{ fontSize: '2.5rem', marginBottom: '12px' }}>📬</div>
            <h3 style={{ margin: '0 0 6px 0', color: '#102B46', fontWeight: 700 }}>No Notifications In This View</h3>
            <p style={{ margin: 0, fontSize: '0.9rem', color: '#98A2B3' }}>
              {unreadOnly ? 'You have cleared all unread notifications.' : 'No alerts match your selected category filter.'}
            </p>
          </div>
        ) : (
          <div>
            {notifications.map((n, idx) => {
              const catStyle = getCategoryColor(n.category)
              return (
                <div
                  key={n.notification_id}
                  style={{
                    padding: '1.25rem 1.5rem',
                    borderBottom: idx === notifications.length - 1 ? 'none' : '1px solid #EAECF0',
                    background: n.is_read ? '#ffffff' : '#F9FBFE',
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '14px',
                    transition: 'background 0.15s ease'
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#F4F7FC')}
                  onMouseLeave={e => (e.currentTarget.style.background = n.is_read ? '#ffffff' : '#F9FBFE')}
                >
                  {/* Read Indicator */}
                  <div style={{ paddingTop: '6px' }}>
                    <div
                      style={{
                        width: '10px',
                        height: '10px',
                        borderRadius: '50%',
                        background: n.is_read ? 'transparent' : '#155EEF',
                        border: n.is_read ? '2px solid #D0D5DD' : 'none'
                      }}
                      title={n.is_read ? 'Read' : 'Unread'}
                    />
                  </div>

                  {/* Body */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                      <span
                        style={{
                          background: catStyle.bg,
                          color: catStyle.text,
                          border: `1px solid ${catStyle.border}`,
                          fontSize: '11px',
                          fontWeight: 700,
                          padding: '2px 8px',
                          borderRadius: '4px',
                          textTransform: 'uppercase'
                        }}
                      >
                        {n.category || 'General'}
                      </span>

                      {n.priority === 'high' && (
                        <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', fontSize: '11px', fontWeight: 700, padding: '2px 6px', borderRadius: '4px' }}>
                          High Priority
                        </span>
                      )}

                      <span style={{ fontSize: '11px', color: '#98A2B3', marginLeft: 'auto' }}>
                        📅 {n.created_at}
                      </span>
                    </div>

                    <div style={{ fontSize: '1rem', fontWeight: n.is_read ? 600 : 800, color: '#102B46', marginBottom: '4px' }}>
                      {n.title}
                    </div>

                    <p style={{ margin: '0 0 10px 0', fontSize: '0.9rem', color: '#475467', lineHeight: 1.5 }}>
                      {n.message}
                    </p>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      {n.action_url && (
                        <button
                          type="button"
                          onClick={() => {
                            if (!n.is_read) handleMarkAsRead(n.notification_id)
                            navigate(n.action_url)
                          }}
                          style={{
                            background: '#102B46',
                            color: '#ffffff',
                            border: 'none',
                            padding: '4px 12px',
                            borderRadius: '6px',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          View Details &rarr;
                        </button>
                      )}

                      {!n.is_read && (
                        <button
                          type="button"
                          onClick={() => handleMarkAsRead(n.notification_id)}
                          style={{
                            background: 'transparent',
                            border: '1px solid #D0D5DD',
                            color: '#475467',
                            padding: '3px 10px',
                            borderRadius: '6px',
                            fontSize: '0.78rem',
                            cursor: 'pointer'
                          }}
                        >
                          Mark as read
                        </button>
                      )}

                      {Boolean(n.is_read) && n.read_at ? (
                        <span style={{ fontSize: '11px', color: '#98A2B3' }}>
                          ✓ Read at {n.read_at}
                        </span>
                      ) : null}
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Pagination Footer */}
        {totalPages > 1 && (
          <div
            style={{
              padding: '12px 1.5rem',
              background: '#F8F9FC',
              borderTop: '1px solid #EAECF0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ fontSize: '0.85rem', color: '#667085' }}>
              Showing Page {page + 1} of {totalPages} ({total} alerts)
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button
                type="button"
                disabled={page === 0}
                onClick={() => setPage(p => Math.max(0, p - 1))}
                style={{
                  background: '#ffffff',
                  border: '1px solid #D0D5DD',
                  padding: '4px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  cursor: page === 0 ? 'not-allowed' : 'pointer',
                  opacity: page === 0 ? 0.5 : 1
                }}
              >
                &larr; Previous
              </button>

              <button
                type="button"
                disabled={page >= totalPages - 1}
                onClick={() => setPage(p => p + 1)}
                style={{
                  background: '#ffffff',
                  border: '1px solid #D0D5DD',
                  padding: '4px 12px',
                  borderRadius: '6px',
                  fontSize: '0.82rem',
                  cursor: page >= totalPages - 1 ? 'not-allowed' : 'pointer',
                  opacity: page >= totalPages - 1 ? 0.5 : 1
                }}
              >
                Next &rarr;
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Preferences Modal */}
      {preferencesOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(16, 43, 70, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1100,
            padding: '1rem'
          }}
        >
          <div
            style={{
              background: '#ffffff',
              borderRadius: '12px',
              maxWidth: '540px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
            }}
          >
            <div
              style={{
                padding: '16px 20px',
                background: '#102B46',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Notification Preferences</h3>
              <button
                type="button"
                onClick={() => setPreferencesOpen(false)}
                style={{ background: 'transparent', border: 'none', color: '#ffffff', fontSize: '1.2rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSavePreferences} style={{ padding: '20px' }}>
              <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: '#475467', lineHeight: 1.4 }}>
                Configure which notification categories and delivery channels you wish to receive.
                Mandatory security alerts and policy updates cannot be disabled.
              </p>

              {prefSuccess && (
                <div style={{ background: '#ECFDF3', border: '1px solid #A6F4C5', color: '#027A48', padding: '10px', borderRadius: '6px', fontSize: '0.85rem', marginBottom: '14px' }}>
                  ✓ {prefSuccess}
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#102B46', borderBottom: '1px solid #EAECF0', paddingBottom: '4px' }}>
                  Category Subscriptions
                </div>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <span>Academic & Evaluation Results</span>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.academic_updates)}
                    onChange={e => setPreferences(p => ({ ...p, academic_updates: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <span>Daily & Subject Attendance Alerts</span>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.attendance_alerts)}
                    onChange={e => setPreferences(p => ({ ...p, attendance_alerts: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <span>Examination Schedules & Timetables</span>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.examination_alerts)}
                    onChange={e => setPreferences(p => ({ ...p, examination_alerts: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <span>Admission Stage & Verification Updates</span>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.admission_updates)}
                    onChange={e => setPreferences(p => ({ ...p, admission_updates: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <span>Official Institution Announcements</span>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.institution_announcements)}
                    onChange={e => setPreferences(p => ({ ...p, institution_announcements: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <span>Administrative & Staff Reminders</span>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.administrative_alerts)}
                    onChange={e => setPreferences(p => ({ ...p, administrative_alerts: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#667085', opacity: 0.8 }}>
                  <span>🔒 Security & Operational Notices (Mandatory)</span>
                  <input type="checkbox" checked disabled style={{ width: '18px', height: '18px' }} />
                </label>

                <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#102B46', borderBottom: '1px solid #EAECF0', paddingBottom: '4px', marginTop: '10px' }}>
                  External Delivery Channels (Optional)
                </div>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <div>
                    <div>Email Dispatch</div>
                    <div style={{ fontSize: '0.75rem', color: '#98A2B3' }}>Sends notification copies to registered email</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.email_enabled)}
                    onChange={e => setPreferences(p => ({ ...p, email_enabled: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <div>
                    <div>SMS Mobile Alerts</div>
                    <div style={{ fontSize: '0.75rem', color: '#98A2B3' }}>Sends urgent text alerts to registered mobile</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.sms_enabled)}
                    onChange={e => setPreferences(p => ({ ...p, sms_enabled: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>

                <label style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.85rem', color: '#344054', cursor: 'pointer' }}>
                  <div>
                    <div>WhatsApp Messaging</div>
                    <div style={{ fontSize: '0.75rem', color: '#98A2B3' }}>Meta WhatsApp Business Cloud channel</div>
                  </div>
                  <input
                    type="checkbox"
                    checked={Boolean(preferences.whatsapp_enabled)}
                    onChange={e => setPreferences(p => ({ ...p, whatsapp_enabled: e.target.checked ? 1 : 0 }))}
                    style={{ width: '18px', height: '18px' }}
                  />
                </label>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  type="button"
                  onClick={() => setPreferencesOpen(false)}
                  style={{
                    background: '#F8F9FC',
                    border: '1px solid #D0D5DD',
                    color: '#344054',
                    padding: '8px 16px',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={savingPrefs}
                  style={{
                    background: '#155EEF',
                    border: 'none',
                    color: '#ffffff',
                    padding: '8px 18px',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    cursor: savingPrefs ? 'wait' : 'pointer'
                  }}
                >
                  {savingPrefs ? 'Saving...' : 'Save Preferences'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Provider Status Modal */}
      {channelStatusOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(16, 43, 70, 0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1100,
            padding: '1rem'
          }}
        >
          <div
            style={{
              background: '#ffffff',
              borderRadius: '12px',
              maxWidth: '560px',
              width: '100%',
              maxHeight: '90vh',
              overflowY: 'auto',
              boxShadow: '0 20px 25px -5px rgba(0,0,0,0.2)'
            }}
          >
            <div
              style={{
                padding: '16px 20px',
                background: '#102B46',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between'
              }}
            >
              <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 700 }}>Communication Channel Status</h3>
              <button
                type="button"
                onClick={() => setChannelStatusOpen(false)}
                style={{ background: 'transparent', border: 'none', color: '#ffffff', fontSize: '1.2rem', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>

            <div style={{ padding: '20px' }}>
              <p style={{ margin: '0 0 16px 0', fontSize: '0.85rem', color: '#475467', lineHeight: 1.4 }}>
                Real-time configuration check for delivery providers. In accordance with platform policy,
                credentials are never fabricated and unconfigured channels report status safely.
              </p>

              {channelStatuses && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {Object.entries(channelStatuses).map(([key, info]) => {
                    const isActive = info.status === 'active'
                    return (
                      <div
                        key={key}
                        style={{
                          padding: '12px 14px',
                          borderRadius: '8px',
                          border: '1px solid',
                          borderColor: isActive ? '#A6F4C5' : '#FEDF89',
                          background: isActive ? '#ECFDF3' : '#FFFAEB',
                          display: 'flex',
                          alignItems: 'flex-start',
                          justifyContent: 'space-between',
                          gap: '10px'
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.9rem', color: '#102B46' }}>
                              {info.provider}
                            </span>
                            <span
                              style={{
                                background: isActive ? '#027A48' : '#B54708',
                                color: '#ffffff',
                                fontSize: '10px',
                                fontWeight: 700,
                                padding: '1px 6px',
                                borderRadius: '4px',
                                textTransform: 'uppercase'
                              }}
                            >
                              {info.status?.replace('_', ' ')}
                            </span>
                          </div>
                          <div style={{ fontSize: '0.8rem', color: '#475467' }}>
                            {info.details}
                          </div>
                        </div>

                        <div style={{ fontSize: '1.2rem' }}>
                          {isActive ? '✅' : '⚠️'}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}

              <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={() => setChannelStatusOpen(false)}
                  style={{
                    background: '#102B46',
                    border: 'none',
                    color: '#ffffff',
                    padding: '8px 18px',
                    borderRadius: '6px',
                    fontSize: '0.85rem',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
