import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiFetch } from '../../utils/api.js'

export default function NotificationBellDropdown() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [isOpen, setIsOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(false)
  const [filter, setFilter] = useState('all') // 'all' | 'unread'
  const dropdownRef = useRef(null)

  async function fetchUnreadCount() {
    try {
      const data = await apiFetch('/notifications/unread-count')
      if (data && typeof data.unread_count === 'number') {
        setUnreadCount(data.unread_count)
      }
    } catch (e) {
      // silent network catch
    }
  }

  async function fetchRecentNotifications() {
    setLoading(true)
    try {
      const unreadParam = filter === 'unread' ? '&unread_only=true' : ''
      const data = await apiFetch(`/notifications?limit=8&include_meta=true${unreadParam}`)
      if (data) {
        setNotifications(data.items || [])
        if (typeof data.unread_count === 'number') {
          setUnreadCount(data.unread_count)
        }
      }
    } catch (e) {
      console.error('Failed to load notifications:', e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUnreadCount()
    const timer = setInterval(fetchUnreadCount, 30000)
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    if (isOpen) {
      fetchRecentNotifications()
    }
  }, [isOpen, filter])

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  async function handleMarkAsRead(notifId, e) {
    if (e) e.stopPropagation()
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

  function handleActionClick(notif) {
    if (!notif.is_read) {
      handleMarkAsRead(notif.notification_id)
    }
    setIsOpen(false)
    if (notif.action_url) {
      navigate(notif.action_url)
    } else {
      navigate('/notifications')
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

  function formatTimeAgo(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    const now = new Date()
    const diffMs = now - d
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    if (diffDays < 7) return `${diffDays}d ago`
    return d.toLocaleDateString()
  }

  return (
    <div className="notification-bell-container" ref={dropdownRef} style={{ position: 'relative' }}>
      {/* Bell Button */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Open notifications menu"
        style={{
          background: isOpen ? '#E0EAFF' : '#F1F6FC',
          border: '1px solid #D0D5DD',
          borderRadius: '50%',
          width: '38px',
          height: '38px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          position: 'relative',
          padding: 0,
          color: '#102B46',
          transition: 'all 0.2s ease'
        }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
          <path d="M13.73 21a2 2 0 0 1-3.46 0" />
        </svg>

        {unreadCount > 0 && (
          <span
            style={{
              position: 'absolute',
              top: '-3px',
              right: '-3px',
              background: '#D92D20',
              color: '#ffffff',
              borderRadius: '10px',
              padding: '1px 5px',
              fontSize: '11px',
              fontWeight: 700,
              minWidth: '18px',
              height: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 4px rgba(0,0,0,0.15)'
            }}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            right: 0,
            top: '46px',
            width: '360px',
            maxWidth: '90vw',
            background: '#ffffff',
            borderRadius: '12px',
            boxShadow: '0 10px 25px -5px rgba(16, 43, 70, 0.2), 0 8px 10px -6px rgba(16, 43, 70, 0.1)',
            border: '1px solid #E4E7EC',
            zIndex: 1000,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '12px 16px',
              background: '#102B46',
              color: '#ffffff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 700, fontSize: '0.95rem' }}>Notifications</span>
              {unreadCount > 0 && (
                <span
                  style={{
                    background: '#155EEF',
                    color: '#ffffff',
                    fontSize: '11px',
                    fontWeight: 600,
                    padding: '2px 7px',
                    borderRadius: '12px'
                  }}
                >
                  {unreadCount} new
                </span>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {unreadCount > 0 && (
                <button
                  type="button"
                  onClick={handleMarkAllAsRead}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#BAE6FD',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    textDecoration: 'underline'
                  }}
                >
                  Mark all read
                </button>
              )}
            </div>
          </div>

          {/* Subheader Filters */}
          <div
            style={{
              padding: '8px 12px',
              background: '#F8F9FC',
              borderBottom: '1px solid #EAECF0',
              display: 'flex',
              gap: '6px'
            }}
          >
            <button
              type="button"
              onClick={() => setFilter('all')}
              style={{
                background: filter === 'all' ? '#102B46' : '#FFFFFF',
                color: filter === 'all' ? '#FFFFFF' : '#475467',
                border: '1px solid',
                borderColor: filter === 'all' ? '#102B46' : '#D0D5DD',
                padding: '3px 10px',
                borderRadius: '14px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              All
            </button>
            <button
              type="button"
              onClick={() => setFilter('unread')}
              style={{
                background: filter === 'unread' ? '#102B46' : '#FFFFFF',
                color: filter === 'unread' ? '#FFFFFF' : '#475467',
                border: '1px solid',
                borderColor: filter === 'unread' ? '#102B46' : '#D0D5DD',
                padding: '3px 10px',
                borderRadius: '14px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Unread only ({unreadCount})
            </button>
          </div>

          {/* Notifications List */}
          <div style={{ maxHeight: '380px', overflowY: 'auto' }}>
            {loading ? (
              <div style={{ padding: '24px', textAlign: 'center', color: '#667085', fontSize: '0.875rem' }}>
                Loading updates...
              </div>
            ) : notifications.length === 0 ? (
              <div style={{ padding: '32px 16px', textAlign: 'center', color: '#667085' }}>
                <div style={{ fontSize: '1.5rem', marginBottom: '8px' }}>📭</div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#344054' }}>No notifications found</div>
                <div style={{ fontSize: '0.8rem', color: '#98A2B3', marginTop: '2px' }}>
                  {filter === 'unread' ? 'You have read all your alerts.' : 'No alerts have been recorded yet.'}
                </div>
              </div>
            ) : (
              notifications.map(n => {
                const catStyle = getCategoryColor(n.category)
                return (
                  <div
                    key={n.notification_id}
                    onClick={() => handleActionClick(n)}
                    style={{
                      padding: '12px 14px',
                      borderBottom: '1px solid #F2F4F7',
                      background: n.is_read ? '#FFFFFF' : '#F9FBFE',
                      cursor: 'pointer',
                      transition: 'background 0.15s ease',
                      display: 'flex',
                      gap: '10px'
                    }}
                    onMouseEnter={e => (e.currentTarget.style.background = '#F0F4FA')}
                    onMouseLeave={e => (e.currentTarget.style.background = n.is_read ? '#FFFFFF' : '#F9FBFE')}
                  >
                    {/* Read dot */}
                    <div style={{ paddingTop: '6px' }}>
                      <div
                        style={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          background: n.is_read ? 'transparent' : '#155EEF',
                          border: n.is_read ? '1px solid #D0D5DD' : 'none'
                        }}
                      />
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                        <span
                          style={{
                            background: catStyle.bg,
                            color: catStyle.text,
                            border: `1px solid ${catStyle.border}`,
                            fontSize: '10px',
                            fontWeight: 700,
                            padding: '1px 6px',
                            borderRadius: '4px',
                            textTransform: 'uppercase'
                          }}
                        >
                          {n.category || 'General'}
                        </span>
                        <span style={{ fontSize: '11px', color: '#98A2B3' }}>
                          {formatTimeAgo(n.created_at)}
                        </span>
                      </div>

                      <div
                        style={{
                          fontWeight: n.is_read ? 600 : 700,
                          fontSize: '0.85rem',
                          color: '#102B46',
                          marginBottom: '3px',
                          lineHeight: 1.3
                        }}
                      >
                        {n.title}
                      </div>

                      <div
                        style={{
                          fontSize: '0.78rem',
                          color: '#475467',
                          lineHeight: 1.35,
                          whiteSpace: 'normal',
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden'
                        }}
                      >
                        {n.message}
                      </div>

                      {n.priority === 'high' && (
                        <div style={{ marginTop: '4px' }}>
                          <span style={{ background: '#FEF3F2', color: '#B42318', fontSize: '10px', fontWeight: 600, padding: '1px 4px', borderRadius: '3px' }}>
                            Priority: High
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })
            )}
          </div>

          {/* Footer */}
          <div
            style={{
              padding: '10px 14px',
              background: '#F8F9FC',
              borderTop: '1px solid #EAECF0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <button
              type="button"
              onClick={() => {
                setIsOpen(false)
                navigate('/notifications')
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#155EEF',
                fontSize: '12px',
                fontWeight: 700,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              View All Notifications &rarr;
            </button>

            <span style={{ fontSize: '11px', color: '#98A2B3' }}>
              Press ESC to close
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
