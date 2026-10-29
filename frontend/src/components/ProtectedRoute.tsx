import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRole?: 'citizen' | 'admin';
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRole,
}) => {
  const { user, isLoading, isAuthenticated } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center p-6" role="status">
        <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
        <span className="text-sm font-medium text-slate-600">Verifying authorized access...</span>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    // If attempting to access admin route, send to admin login
    const targetLogin = allowedRole === 'admin' ? '/admin/login' : '/login';
    return <Navigate to={targetLogin} state={{ from: location }} replace />;
  }

  if (allowedRole && user.role !== allowedRole) {
    // Role mismatch: redirect to their respective authorized home
    const redirectUrl = user.role === 'admin' ? '/admin/dashboard' : '/citizen/dashboard';
    return <Navigate to={redirectUrl} replace />;
  }

  return <>{children}</>;
};
