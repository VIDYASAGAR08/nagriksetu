import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { ProtectedRoute } from './components/ProtectedRoute';

// Public Pages
import { LandingPage } from './pages/public/LandingPage';
import { LoginPage } from './pages/public/LoginPage';
import { RegisterPage } from './pages/public/RegisterPage';
import { AdminLoginPage } from './pages/public/AdminLoginPage';
import { WhatsAppBotPage } from './pages/public/WhatsAppBotPage';

// Citizen Pages
import { CitizenDashboard } from './pages/citizen/CitizenDashboard';
import { CitizenProfilePage } from './pages/citizen/CitizenProfilePage';
import { CitizenHouseholdPage } from './pages/citizen/CitizenHouseholdPage';
import { CitizenChatPage } from './pages/citizen/CitizenChatPage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { CitizenManagementPage } from './pages/admin/CitizenManagementPage';
import { HouseholdManagementPage } from './pages/admin/HouseholdManagementPage';
import { AuditLogPage } from './pages/admin/AuditLogPage';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
          <Navbar />
          <main className="flex-1">
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/admin/login" element={<AdminLoginPage />} />
              <Route path="/whatsapp" element={<WhatsAppBotPage />} />

              {/* Citizen Protected Routes */}
              <Route
                path="/citizen/dashboard"
                element={
                  <ProtectedRoute allowedRole="citizen">
                    <CitizenDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/citizen/profile"
                element={
                  <ProtectedRoute allowedRole="citizen">
                    <CitizenProfilePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/citizen/household"
                element={
                  <ProtectedRoute allowedRole="citizen">
                    <CitizenHouseholdPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/citizen/chat"
                element={
                  <ProtectedRoute allowedRole="citizen">
                    <CitizenChatPage />
                  </ProtectedRoute>
                }
              />

              {/* Admin Protected Routes */}
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute allowedRole="admin">
                    <AdminDashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/citizens"
                element={
                  <ProtectedRoute allowedRole="admin">
                    <CitizenManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/households"
                element={
                  <ProtectedRoute allowedRole="admin">
                    <HouseholdManagementPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/audit"
                element={
                  <ProtectedRoute allowedRole="admin">
                    <AuditLogPage />
                  </ProtectedRoute>
                }
              />

              {/* Fallback */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          {/* Accessible Footer */}
          <footer className="bg-white border-t border-slate-200 py-6 px-4 text-center text-xs text-slate-500">
            <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
              <p>© 2026 CivicAdmin Administrative Service Microservice. All rights reserved.</p>
              <div className="flex items-center gap-4 text-slate-600">
                <span>Phase 1 Demonstration</span>
                <span>•</span>
                <span>WCAG 2.2 AA Accessible</span>
                <span>•</span>
                <span>PostgreSQL 16 & FastAPI</span>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
