/** LoadingSpinner — accessible loading indicator */
export default function LoadingSpinner({ size = 'default', label = 'Loading…' }) {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <span className={`spinner${size === 'sm' ? ' spinner--sm' : ''}`} aria-hidden="true" />
      <span className="visually-hidden">{label}</span>
    </div>
  )
}

// Inline loading for buttons/rows
export function InlineSpinner() {
  return (
    <span
      className="spinner spinner--sm"
      style={{ display: 'inline-block', verticalAlign: 'middle' }}
      role="status"
      aria-label="Loading"
    />
  )
}
