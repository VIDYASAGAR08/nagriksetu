import { useState, useEffect, useRef } from 'react'
import { API_URL, apiFetch } from '../../utils/api.js'

const WELCOME_MESSAGE = {
  id: 'welcome',
  sender: 'assistant',
  text: "Hello! Welcome to NagrikSetu AI Assistance. I can help you with school admissions, school discovery, student information, scholarships, RTE, academic guidance, attendance, school administration and other education-related services. What would you like to know?",
  sources: ['Official Education Directory', 'Statutory Knowledge Base'],
  actions: [
    'Find government schools near me',
    'What are RTE 25% admission rules?',
    'Which scholarships are available in Karnataka?',
    'How do I track student attendance?'
  ],
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function NagrikSetuAiChat({ isFullPage = true, onClose = null }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(() => 'sess_' + Math.random().toString(36).substring(2, 10))
  const [suggestions, setSuggestions] = useState([])
  const [engineStatus, setEngineStatus] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    // Fetch suggestions
    fetch(`${API_URL}/ai/suggestions`)
      .then(res => res.json())
      .then(data => {
        if (data.suggestions) setSuggestions(data.suggestions)
      })
      .catch(() => {
        setSuggestions([
          { label: 'Find schools near me', query: 'Which government schools are available in Bengaluru?' },
          { label: 'RTE 25% Quota', query: 'What are the RTE admission guidelines and income criteria?' },
          { label: 'Check Scholarships', query: 'Which scholarships are available in Karnataka for school students?' },
          { label: 'Compare Schools', query: 'Compare SCH001 and SCH002 by seats and facilities' },
          { label: 'Seat Vacancies', query: 'How many vacant seats are available across schools?' }
        ])
      })

    // Fetch engine status
    fetch(`${API_URL}/ai/status`)
      .then(res => res.json())
      .then(data => setEngineStatus(data))
      .catch(() => {})
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function handleSend(queryText = null) {
    const textToSend = (queryText || inputValue).trim()
    if (!textToSend || loading) return

    const userMsg = {
      id: 'usr_' + Date.now(),
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMsg])
    setInputValue('')
    setLoading(true)

    const token = localStorage.getItem('token')
    const headers = {
      'Content-Type': 'application/json'
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    fetch(`${API_URL}/ai/chat`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message: textToSend,
        session_id: sessionId
      })
    })
      .then(async res => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}))
          throw new Error(errData.detail || `Server error (${res.status})`)
        }
        return res.json()
      })
      .then(data => {
        const aiMsg = {
          id: 'ai_' + Date.now(),
          sender: 'assistant',
          text: data.response || 'No response returned from the AI assistant.',
          sources: data.grounded_sources || [],
          actions: data.suggested_actions || [],
          matched_question: data.matched_question,
          intent: data.intent,
          category: data.category,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        if (data.session_id) {
          setSessionId(data.session_id)
        }
        setMessages(prev => [...prev, aiMsg])
      })
      .catch(err => {
        const errorMsg = {
          id: 'err_' + Date.now(),
          sender: 'assistant',
          text: `⚠️ Unable to complete request: ${err.message}. Please verify your connection or try again.`,
          sources: ['System Error Handler'],
          actions: ['Retry inquiry', 'Find Government Schools'],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setMessages(prev => [...prev, errorMsg])
      })
      .finally(() => {
        setLoading(false)
        setTimeout(() => inputRef.current?.focus(), 100)
      })
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  function handleNewConversation() {
    setMessages([
      {
        ...WELCOME_MESSAGE,
        id: 'welcome_' + Date.now(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ])
    setSessionId('sess_' + Math.random().toString(36).substring(2, 10))
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: isFullPage ? 'calc(100vh - 120px)' : '560px',
      maxHeight: isFullPage ? '820px' : '620px',
      backgroundColor: '#ffffff',
      borderRadius: isFullPage ? '8px' : '12px',
      border: '1px solid #dbe2ea',
      boxShadow: isFullPage ? '0 4px 16px rgba(11,37,69,0.08)' : '0 10px 30px rgba(11,37,69,0.2)',
      overflow: 'hidden',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        backgroundColor: '#0B2545',
        color: '#ffffff',
        padding: '14px 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '2px solid #134074'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: '#134074',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#90e0ef',
            fontWeight: '700',
            fontSize: '16px',
            border: '1px solid #00b4d8'
          }}>
            NS
          </div>
          <div>
            <div style={{ fontSize: '16px', fontWeight: '700', letterSpacing: '0.3px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              NagrikSetu AI Assistance
              <span style={{
                fontSize: '10px',
                padding: '2px 8px',
                borderRadius: '12px',
                backgroundColor: '#10b981',
                color: '#ffffff',
                fontWeight: '600',
                letterSpacing: '0.4px',
                textTransform: 'uppercase'
              }}>
                Universal AI
              </span>
            </div>
            <div style={{ fontSize: '11px', color: '#94a3b8' }}>
              Karnataka School Services • Grounded Knowledge & Verified Database
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleNewConversation}
            title="Start New Conversation"
            style={{
              background: 'transparent',
              border: '1px solid rgba(255,255,255,0.25)',
              color: '#ffffff',
              padding: '6px 12px',
              borderRadius: '4px',
              fontSize: '12px',
              cursor: 'pointer',
              fontWeight: '500',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <span>🔄</span> New Chat
          </button>

          {onClose && (
            <button
              onClick={onClose}
              title="Close chat"
              style={{
                background: 'transparent',
                border: 'none',
                color: '#ffffff',
                fontSize: '20px',
                cursor: 'pointer',
                padding: '4px 8px',
                lineHeight: '1'
              }}
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Engine Status Banner */}
      {engineStatus && (
        <div style={{
          backgroundColor: '#f8fafc',
          padding: '6px 16px',
          borderBottom: '1px solid #e2e8f0',
          fontSize: '11px',
          color: '#475569',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <strong>Active Provider:</strong> {engineStatus.active_provider === 'gemini' ? 'Google Gemini API' : 'NagrikSetu Grounded Knowledge & DB Engine'}
            <span style={{ marginLeft: '12px', color: '#0284c7' }}>
              • <strong>200 Questions Connected</strong>
            </span>
          </div>
          <div style={{ color: '#059669', fontWeight: '600' }}>
            ✓ Verified DB Schema & RBAC Active
          </div>
        </div>
      )}

      {/* Message Area */}
      <div style={{
        flex: 1,
        padding: '16px 20px',
        overflowY: 'auto',
        backgroundColor: '#f8fafc',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.map(msg => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '100%'
            }}
          >
            {/* Sender Label & Timestamp */}
            <div style={{
              fontSize: '11px',
              color: '#64748b',
              marginBottom: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span>{msg.sender === 'user' ? 'You' : 'NagrikSetu Assistant'}</span>
              <span>•</span>
              <span>{msg.timestamp}</span>
              {msg.matched_question && (
                <span style={{
                  backgroundColor: '#e0f2fe',
                  color: '#0369a1',
                  padding: '1px 6px',
                  borderRadius: '4px',
                  fontSize: '10px',
                  fontWeight: '600'
                }}>
                  Ref: {msg.matched_question.code}
                </span>
              )}
            </div>

            {/* Bubble */}
            <div style={{
              maxWidth: '85%',
              padding: '14px 18px',
              borderRadius: msg.sender === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
              backgroundColor: msg.sender === 'user' ? '#0B2545' : '#ffffff',
              color: msg.sender === 'user' ? '#ffffff' : '#1e293b',
              border: msg.sender === 'user' ? 'none' : '1px solid #e2e8f0',
              boxShadow: '0 2px 6px rgba(0,0,0,0.04)',
              fontSize: '14px',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word'
            }}>
              {msg.text}

              {/* Grounded Sources */}
              {msg.sources && msg.sources.length > 0 && (
                <div style={{
                  marginTop: '12px',
                  paddingTop: '8px',
                  borderTop: '1px solid #f1f5f9',
                  fontSize: '11px',
                  color: '#64748b'
                }}>
                  <strong style={{ color: '#0369a1' }}>Data Sources:</strong>{' '}
                  {msg.sources.join(' • ')}
                </div>
              )}
            </div>

            {/* Suggested Follow-up Actions */}
            {msg.actions && msg.actions.length > 0 && (
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '8px',
                marginTop: '8px',
                maxWidth: '85%'
              }}>
                {msg.actions.map((act, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(act)}
                    disabled={loading}
                    style={{
                      backgroundColor: '#e2e8f0',
                      border: '1px solid #cbd5e1',
                      borderRadius: '16px',
                      padding: '4px 12px',
                      fontSize: '12px',
                      color: '#1e293b',
                      cursor: 'pointer',
                      transition: 'background-color 0.2s',
                      textAlign: 'left'
                    }}
                    onMouseOver={e => e.currentTarget.style.backgroundColor = '#cbd5e1'}
                    onMouseOut={e => e.currentTarget.style.backgroundColor = '#e2e8f0'}
                  >
                    💬 {act}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '12px 16px',
            backgroundColor: '#ffffff',
            borderRadius: '12px',
            border: '1px solid #e2e8f0',
            width: 'fit-content'
          }}>
            <div style={{ fontSize: '13px', color: '#64748b', fontStyle: 'italic' }}>
              Consulting NagrikSetu database & verified records...
            </div>
            <div style={{ display: 'flex', gap: '4px' }}>
              <span style={{ animation: 'pulse 1s infinite', fontSize: '14px' }}>●</span>
              <span style={{ animation: 'pulse 1s infinite 0.2s', fontSize: '14px' }}>●</span>
              <span style={{ animation: 'pulse 1s infinite 0.4s', fontSize: '14px' }}>●</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Suggestion Bar (Initial / Persistent) */}
      {suggestions.length > 0 && messages.length <= 2 && (
        <div style={{
          padding: '8px 16px',
          backgroundColor: '#f1f5f9',
          borderTop: '1px solid #e2e8f0',
          display: 'flex',
          gap: '8px',
          overflowX: 'auto',
          whiteSpace: 'nowrap'
        }}>
          <span style={{ fontSize: '11px', color: '#64748b', alignSelf: 'center', fontWeight: '600' }}>
            Suggestions:
          </span>
          {suggestions.map((s, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(s.query)}
              disabled={loading}
              style={{
                backgroundColor: '#ffffff',
                border: '1px solid #cbd5e1',
                borderRadius: '14px',
                padding: '4px 10px',
                fontSize: '11px',
                color: '#0B2545',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              {s.label}
            </button>
          ))}
        </div>
      )}

      {/* Input Area */}
      <div style={{
        padding: '12px 16px',
        backgroundColor: '#ffffff',
        borderTop: '1px solid #e2e8f0',
        display: 'flex',
        gap: '10px',
        alignItems: 'center'
      }}>
        <textarea
          ref={inputRef}
          value={inputValue}
          onChange={e => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask any question about schools, admissions, scholarships, attendance, or administration..."
          rows={1}
          disabled={loading}
          style={{
            flex: 1,
            padding: '10px 14px',
            borderRadius: '6px',
            border: '1px solid #cbd5e1',
            fontSize: '14px',
            outline: 'none',
            resize: 'none',
            fontFamily: 'inherit',
            lineHeight: '1.4',
            boxSizing: 'border-box'
          }}
          onFocus={e => e.target.style.borderColor = '#0B2545'}
          onBlur={e => e.target.style.borderColor = '#cbd5e1'}
        />

        <button
          onClick={() => handleSend()}
          disabled={loading || !inputValue.trim()}
          style={{
            backgroundColor: inputValue.trim() && !loading ? '#0B2545' : '#94a3b8',
            color: '#ffffff',
            border: 'none',
            padding: '10px 18px',
            borderRadius: '6px',
            fontWeight: '600',
            fontSize: '14px',
            cursor: inputValue.trim() && !loading ? 'pointer' : 'not-allowed',
            transition: 'background-color 0.2s',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          Send ↵
        </button>
      </div>
    </div>
  )
}
