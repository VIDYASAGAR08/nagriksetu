import { useState } from 'react'

/**
 * PasswordInput — Secure password input field with show/hide toggle.
 * Provides accessible eye toggle, preserves existing styles and validation attributes.
 */
export default function PasswordInput({
  id,
  name,
  value,
  onChange,
  placeholder = 'Enter password',
  required = false,
  minLength,
  maxLength,
  disabled = false,
  autoComplete,
  className = 'input',
  style = {},
  containerStyle = {},
  ...restProps
}) {
  const [showPassword, setShowPassword] = useState(false)

  // Merge container style to keep layout predictable
  const resolvedContainerStyle = {
    position: 'relative',
    display: 'block',
    width: '100%',
    boxSizing: 'border-box',
    ...containerStyle,
  }

  // Merge input styles: ensure right padding leaves room for the eye icon
  const resolvedInputStyle = {
    boxSizing: 'border-box',
    ...style,
    paddingRight: '2.5rem',
  }

  return (
    <div className="password-input-wrapper" style={resolvedContainerStyle}>
      <input
        type={showPassword ? 'text' : 'password'}
        id={id}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        minLength={minLength}
        maxLength={maxLength}
        disabled={disabled}
        autoComplete={autoComplete}
        className={className}
        style={resolvedInputStyle}
        {...restProps}
      />
      <button
        type="button"
        tabIndex={0}
        onClick={() => setShowPassword(prev => !prev)}
        aria-label={showPassword ? 'Hide password' : 'Show password'}
        title={showPassword ? 'Hide password' : 'Show password'}
        style={{
          position: 'absolute',
          right: '0.625rem',
          top: '50%',
          transform: 'translateY(-50%)',
          background: 'none',
          border: 'none',
          padding: '0.25rem',
          margin: 0,
          cursor: 'pointer',
          color: '#64748B',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '4px',
          lineHeight: 1,
          transition: 'color 0.15s ease, opacity 0.15s ease',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.color = '#102B46' }}
        onMouseLeave={(e) => { e.currentTarget.style.color = '#64748B' }}
      >
        {showPassword ? (
          /* Eye-Off Icon (Hide password) */
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
            <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
            <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
            <line x1="2" y1="2" x2="22" y2="22" />
          </svg>
        ) : (
          /* Eye Icon (Show password) */
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
            <circle cx="12" cy="12" r="3" />
          </svg>
        )}
      </button>
    </div>
  )
}
