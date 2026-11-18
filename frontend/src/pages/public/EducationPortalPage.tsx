import React, { useEffect } from 'react';

/**
 * Pure redirect component that automatically forwards the user to the
 * teammate's School & Education Microservice on Port 5174 without rendering
 * any intermediate or extra page.
 */
export const EducationPortalPage: React.FC = () => {
  useEffect(() => {
    window.location.replace('http://localhost:5174/');
  }, []);

  if (typeof window !== 'undefined') {
    window.location.replace('http://localhost:5174/');
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">
      <div className="text-center space-y-4">
        <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold text-slate-300">Redirecting to School Service (Port 5174)...</p>
      </div>
    </div>
  );
};
