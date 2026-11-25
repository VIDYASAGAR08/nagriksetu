import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import NagrikSetuAiChat from './NagrikSetuAiChat.jsx'

export default function AiAssistanceWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const location = useLocation()

  // Don't show floating widget if user is already on the dedicated /ai-assistance page
  if (location.pathname === '/ai-assistance') {
    return null
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 9999,
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      {/* Floating Chat Modal */}
      {isOpen && (
        <div style={{
          position: 'absolute',
          bottom: '68px',
          right: '0',
          width: '420px',
          maxWidth: '92vw',
          zIndex: 10000,
          animation: 'fadeInUp 0.2s ease-out'
        }}>
          {/* Top toolbar over widget */}
          <div style={{
            display: 'flex',
            justifyContent: 'flex-end',
            marginBottom: '6px'
          }}>
            <Link
              to="/ai-assistance"
              onClick={() => setIsOpen(false)}
              style={{
                backgroundColor: '#ffffff',
                color: '#0B2545',
                padding: '4px 10px',
                borderRadius: '4px',
                fontSize: '11px',
                fontWeight: '600',
                textDecoration: 'none',
                boxShadow: '0 2px 6px rgba(0,0,0,0.1)',
                border: '1px solid #cbd5e1'
              }}
            >
              ⤢ Open Full Page
            </Link>
          </div>

          <NagrikSetuAiChat isFullPage={false} onClose={() => setIsOpen(false)} />
        </div>
      )}

      {/* Floating Trigger Button */}
      <button
        onClick={() => setIsOpen(prev => !prev)}
        title="Open NagrikSetu AI Assistance"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          backgroundColor: '#0B2545',
          color: '#ffffff',
          border: '2px solid #134074',
          borderRadius: '30px',
          padding: '12px 20px',
          boxShadow: '0 6px 20px rgba(11,37,69,0.3)',
          cursor: 'pointer',
          fontWeight: '700',
          fontSize: '14px',
          letterSpacing: '0.2px',
          transition: 'all 0.2s ease'
        }}
        onMouseOver={e => {
          e.currentTarget.style.backgroundColor = '#134074'
          e.currentTarget.style.transform = 'translateY(-2px)'
        }}
        onMouseOut={e => {
          e.currentTarget.style.backgroundColor = '#0B2545'
          e.currentTarget.style.transform = 'translateY(0)'
        }}
      >
        <span style={{ fontSize: '18px' }}>💬</span>
        <span>NagrikSetu AI</span>
        <span style={{
          backgroundColor: '#10b981',
          color: '#ffffff',
          fontSize: '9px',
          fontWeight: '800',
          padding: '2px 6px',
          borderRadius: '8px',
          textTransform: 'uppercase'
        }}>
          Live
        </span>
      </button>
    </div>
  )
}
