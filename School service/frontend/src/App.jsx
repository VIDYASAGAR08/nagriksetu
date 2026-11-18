import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext.jsx'
import GovHeader from './components/layout/GovHeader.jsx'
import Footer from './components/layout/Footer.jsx'
// Pages
import HomePage from './pages/public/HomePage.jsx'
import LandingRoute from './components/routing/LandingRoute.jsx'
import SchoolDirectoryPage from './pages/public/SchoolDirectoryPage.jsx'
import SchoolDetailsPage from './pages/public/SchoolDetailsPage.jsx'
import LoginPage from './pages/auth/LoginPage.jsx'
import SelectInstitutionPage from './pages/auth/SelectInstitutionPage.jsx'
import RegisterPage from './pages/auth/RegisterPage.jsx'
import SelectWorkspacePage from './pages/auth/SelectWorkspacePage.jsx'
import AcceptInvitationPage from './pages/auth/AcceptInvitationPage.jsx'
import StaffCandidateApplicationPage from './pages/auth/StaffCandidateApplicationPage.jsx'
import StaffCandidateActivationPage from './pages/auth/StaffCandidateActivationPage.jsx'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage.jsx'
import ResetPasswordPage from './pages/auth/ResetPasswordPage.jsx'
import SetupPasswordPage from './pages/auth/SetupPasswordPage.jsx'
import ParentDashboard from './pages/parent/ParentDashboard.jsx'
import StudentDashboard from './pages/student/StudentDashboard.jsx'
import StaffDashboard from './pages/staff/StaffDashboard.jsx'
import AdminDashboard from './pages/admin/AdminDashboard.jsx'
import InstitutionAdminDashboard from './pages/admin/InstitutionAdminDashboard.jsx'
import NotificationCenterPage from './pages/notifications/NotificationCenterPage.jsx'
import InfoPage from './pages/public/InfoPage.jsx'

import './App.css'

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app-shell" style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', background: '#f4f5f7' }}>
          <GovHeader />
          <main style={{ flex: '1 0 auto' }}>
            <Routes>
              <Route path="/" element={<LandingRoute />} />
              <Route path="/schools" element={<SchoolDirectoryPage />} />
              <Route path="/schools/:schoolId" element={<SchoolDetailsPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/select-institution" element={<SelectInstitutionPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/select-workspace" element={<SelectWorkspacePage />} />
              <Route path="/accept-invitation" element={<AcceptInvitationPage />} />
              <Route path="/staff-application" element={<StaffCandidateApplicationPage />} />
              <Route path="/staff-activation" element={<StaffCandidateActivationPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route path="/setup-password" element={<SetupPasswordPage />} />
              <Route path="/parent" element={<ParentDashboard />} />
              <Route path="/student" element={<StudentDashboard />} />
              <Route path="/staff" element={<StaffDashboard />} />
              <Route path="/institution-admin" element={<InstitutionAdminDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/notifications" element={<NotificationCenterPage />} />
              <Route path="/ocr-demo" element={<Navigate to="/schools" replace />} />
              <Route path="/about" element={<InfoPage />} />
              <Route path="/help" element={<InfoPage />} />
              <Route path="/contact" element={<InfoPage />} />
              <Route path="/privacy" element={<InfoPage />} />
              <Route path="/terms" element={<InfoPage />} />
              <Route path="/accessibility" element={<InfoPage />} />
              <Route path="/sitemap" element={<InfoPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  )
}
