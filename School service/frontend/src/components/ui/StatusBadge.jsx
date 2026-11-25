/** StatusBadge — shows request/enrollment status with colour coding */
export default function StatusBadge({ status }) {
  const map = {
    active:       'success',
    approved:     'success',
    completed:    'success',
    verified:     'success',
    corrected:    'success',
    accepted:     'success',
    paid:         'success',
    pending:      'pending',
    submitted:    'pending',
    under_review: 'warning',
    needs_review: 'warning',
    clarification_requested: 'warning',
    clarification_required:  'warning',
    resubmitted:  'info',
    rejected:     'error',
    withdrawn:    'error',
    cancelled:    'neutral',
    transferred:  'info',
    inactive:     'neutral',
    not_applied:  'neutral',
    closed:       'neutral',
  }

  const variant = map[status?.toLowerCase()] ?? 'neutral'
  const label   = (status ?? 'Unknown').replace(/_/g, ' ')

  return <span className={`badge badge--${variant}`}>{label}</span>
}
