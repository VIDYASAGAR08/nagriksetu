import React from 'react'

export default function SeatBadge({ availableSeats, totalCapacity }) {
  if (availableSeats === undefined || availableSeats === null) {
    return (
      <span style={{
        fontSize: '0.72rem',
        fontWeight: 600,
        background: '#F2F4F7',
        color: '#475467',
        padding: '0.2rem 0.5rem',
        borderRadius: '4px',
        border: '1px solid #D0D5DD',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.25rem'
      }}>
        <span>⚪</span>
        <span>Seats on Request</span>
      </span>
    )
  }

  const isFull = availableSeats <= 0
  const isLimited = availableSeats > 0 && availableSeats <= 10

  const bg = isFull ? '#FEF3F2' : isLimited ? '#FFFAEB' : '#ECFDF3'
  const color = isFull ? '#B42318' : isLimited ? '#B54708' : '#027A48'
  const border = isFull ? '#FECDCA' : isLimited ? '#FEDF89' : '#A6F4C5'
  const icon = isFull ? '🔴' : isLimited ? '🟡' : '🟢'
  const label = isFull ? 'Seats Full' : isLimited ? `${availableSeats} Seats Left` : `${availableSeats} Seats Open`

  return (
    <span style={{
      fontSize: '0.72rem',
      fontWeight: 700,
      background: bg,
      color: color,
      border: `1px solid ${border}`,
      padding: '0.2rem 0.55rem',
      borderRadius: '4px',
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.3rem'
    }}>
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  )
}
