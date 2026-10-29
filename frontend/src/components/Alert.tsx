import React from 'react';
import { AlertCircle, CheckCircle, Info, X } from 'lucide-react';

interface AlertProps {
  type: 'error' | 'success' | 'info';
  message: string;
  onClose?: () => void;
  className?: string;
}

export const Alert: React.FC<AlertProps> = ({ type, message, onClose, className = '' }) => {
  const configs = {
    error: {
      bg: 'bg-rose-50 border-rose-200 text-rose-900',
      icon: <AlertCircle className="w-5 h-5 text-rose-600 flex-shrink-0" aria-hidden="true" />,
      label: 'Error message:',
    },
    success: {
      bg: 'bg-emerald-50 border-emerald-200 text-emerald-900',
      icon: <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" aria-hidden="true" />,
      label: 'Success notification:',
    },
    info: {
      bg: 'bg-primary-50 border-primary-200 text-primary-900',
      icon: <Info className="w-5 h-5 text-primary-600 flex-shrink-0" aria-hidden="true" />,
      label: 'Information:',
    },
  };

  const config = configs[type];

  return (
    <div
      role={type === 'error' ? 'alert' : 'status'}
      aria-live={type === 'error' ? 'assertive' : 'polite'}
      className={`p-4 rounded-lg border flex items-start justify-between gap-3 ${config.bg} ${className}`}
    >
      <div className="flex items-start gap-3">
        {config.icon}
        <div>
          <span className="sr-only">{config.label}</span>
          <p className="text-sm font-medium">{message}</p>
        </div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          type="button"
          aria-label="Dismiss alert"
          className="text-slate-500 hover:text-slate-800 p-1 rounded hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-primary-500"
        >
          <X className="w-4 h-4" aria-hidden="true" />
        </button>
      )}
    </div>
  );
};
