import React from 'react'

export default function InstitutionCompareDrawer({
  selectedList = [],
  onRemove,
  onClear,
  onOpenModal
}) {
  if (selectedList.length === 0) return null

  const canCompare = selectedList.length >= 2

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        background: '#102B46',
        color: '#FFFFFF',
        boxShadow: '0 -4px 20px rgba(0,0,0,0.25)',
        padding: '0.85rem 1.5rem',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
        borderTop: '3px solid #155EEF'
      }}
    >
      {/* Left: Summary & pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{ fontSize: '1.25rem' }}>⚖️</span>
          <div>
            <div style={{ fontSize: '0.9rem', fontWeight: 700 }}>
              Institution Comparison Tray
            </div>
            <div style={{ fontSize: '0.75rem', color: '#98A2B3' }}>
              {selectedList.length} of 10 selected (minimum 2 to compare)
            </div>
          </div>
        </div>

        {/* Selected School Chips */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', maxWidth: '650px' }}>
          {selectedList.map((inst) => (
            <div
              key={inst.school_id}
              style={{
                background: 'rgba(255, 255, 255, 0.12)',
                border: '1px solid rgba(255, 255, 255, 0.25)',
                borderRadius: '20px',
                padding: '0.25rem 0.65rem',
                fontSize: '0.78rem',
                fontWeight: 600,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                color: '#FFFFFF'
              }}
            >
              <span style={{ maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {inst.school_name}
              </span>
              <button
                onClick={() => onRemove(inst.school_id)}
                title="Remove from comparison"
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#CBD5E1',
                  cursor: 'pointer',
                  padding: 0,
                  fontSize: '0.9rem',
                  lineHeight: 1
                }}
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Right: Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <button
          onClick={onClear}
          style={{
            background: 'transparent',
            border: '1px solid rgba(255,255,255,0.3)',
            color: '#FFFFFF',
            borderRadius: '6px',
            padding: '0.5rem 0.85rem',
            fontSize: '0.825rem',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          Clear All
        </button>

        <button
          onClick={onOpenModal}
          disabled={!canCompare}
          style={{
            background: canCompare ? '#155EEF' : '#475467',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '6px',
            padding: '0.5rem 1.25rem',
            fontSize: '0.85rem',
            fontWeight: 700,
            cursor: canCompare ? 'pointer' : 'not-allowed',
            opacity: canCompare ? 1 : 0.6,
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem'
          }}
        >
          <span>Compare Institutions</span>
          <span>({selectedList.length})</span>
          <span>→</span>
        </button>
      </div>
    </div>
  )
}
