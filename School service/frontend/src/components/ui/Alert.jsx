/** Alert — information notice box */
import React from 'react'

export default function Alert({ type = 'info', title, children, className = '' }) {
  const icons = { info: 'ℹ', success: '✓', warning: '⚠', error: '✕' }
  const renderContent = () => {
    if (children && typeof children === 'object' && !React.isValidElement(children)) {
      return children.detail || children.message || children.msg || JSON.stringify(children)
    }
    return children
  }
  return (
    <div className={`alert alert--${type} ${className}`} role="alert">
      <span className="alert__icon" aria-hidden="true">{icons[type]}</span>
      <div className="alert__body">
        {title && <div className="alert__title">{title}</div>}
        <div className="alert__desc">{renderContent()}</div>
      </div>
    </div>
  )
}
