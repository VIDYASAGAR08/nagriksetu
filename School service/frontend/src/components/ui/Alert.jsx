/** Alert — information notice box */
export default function Alert({ type = 'info', title, children, className = '' }) {
  const icons = { info: 'ℹ', success: '✓', warning: '⚠', error: '✕' }
  return (
    <div className={`alert alert--${type} ${className}`} role="alert">
      <span className="alert__icon" aria-hidden="true">{icons[type]}</span>
      <div className="alert__body">
        {title && <div className="alert__title">{title}</div>}
        <div className="alert__desc">{children}</div>
      </div>
    </div>
  )
}
