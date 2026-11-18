/** StatusBadge — shows request/enrollment status with colour coding */
export default function StatusBadge({ status }) {
  const map = {
    active:       'success',
    approved:     'success',
    completed:    'success',
    verified:     'success',
    paid:         'success',
    pending:      'pending',
    under_review: 'warning',
    needs_review: 'warning',
    rejected:     'error',
    withdrawn:    'error',
    cancelled:    'neutral',
    transferred:  'info',
    inactive:     'neutral',
    not_applied:  'neutral',
  }

  const variant = map[status?.toLowerCase()] ?? 'neutral'
  const label   = (status ?? 'Unknown').replace(/_/g, ' ')

  return <span className={`badge badge--${variant}`}>{label}</span>
}
