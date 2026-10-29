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

          {/* Official Government Footer */}
          <footer className="bg-slate-900 text-slate-300 border-t-4 border-t-saffron-500 pt-8 pb-6 px-4 sm:px-6 lg:px-8 text-xs">
            <div className="max-w-7xl mx-auto space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pb-6 border-b border-slate-800">
                <div className="md:col-span-2 space-y-2">
                  <div className="flex items-center gap-2.5">
                    <div className="w-8 h-8 rounded-full bg-primary-800 border border-saffron-500 flex items-center justify-center font-black text-white text-xs">
                      NS
                    </div>
                    <div>
                      <span className="font-bold text-white text-base block leading-tight">NagrikSetu | नागरिक सेतु</span>
                      <span className="text-[11px] text-slate-400">National Citizen & Administrative Governance Portal</span>
                    </div>
                  </div>
                  <p className="text-slate-400 text-xs leading-relaxed max-w-md pt-1">
                    An official digital public infrastructure initiative designed for transparent citizen registration, household administration, and accessible public services.
                  </p>
                </div>
                <div>
                  <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-2.5">Accessibility & Standards</h4>
                  <ul className="space-y-1.5 text-slate-400">
                    <li>• WCAG 2.2 Level AA Compliant</li>
                    <li>• GIGW Government Guidelines</li>
                    <li>• Bilingual Interface Support</li>
                    <li>• Screen Reader Accessible</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-bold text-white uppercase tracking-wider text-[11px] mb-2.5">Official Assistance</h4>
                  <ul className="space-y-1.5 text-slate-400">
                    <li>• Citizen Toll-Free Helpline: 1800-11-2026</li>
                    <li>• Support: support@nagriksetu.gov.in</li>
                    <li>• WhatsApp Bot Services Enabled</li>
                  </ul>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-slate-400 text-[11px]">
                <p>© 2026 NagrikSetu (नागरिक सेतु). Content Owned and Maintained by Department of Administrative & Citizen Affairs.</p>
                <div className="flex items-center gap-3">
                  <span className="text-emerald-400 font-semibold">● Portal Operational</span>
                  <span>•</span>
                  <span>PostgreSQL 16 & FastAPI</span>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default App;
