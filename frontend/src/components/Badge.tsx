import React from 'react';

interface BadgeProps {
  status: string;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ status, className = '' }) => {
  const normalized = status.toLowerCase().replace(/_/g, ' ');

  let colorClasses = 'bg-slate-100 text-slate-800 border-slate-300';
  let indicator = '●';

  if (['active', 'approved'].includes(status.toLowerCase())) {
    colorClasses = 'bg-emerald-50 text-emerald-800 border-emerald-300';
    indicator = '✓';
  } else if (['pending_review', 'pending'].includes(status.toLowerCase())) {
    colorClasses = 'bg-amber-50 text-amber-800 border-amber-300';
    indicator = '⏳';
  } else if (['archived', 'suspended', 'inactive'].includes(status.toLowerCase())) {
    colorClasses = 'bg-rose-50 text-rose-800 border-rose-300';
    indicator = '✕';
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClasses} ${className}`}
      aria-label={`Status: ${normalized}`}
    >
      <span aria-hidden="true" className="font-bold text-[10px]">{indicator}</span>
      <span className="capitalize">{normalized}</span>
    </span>
  );
};
