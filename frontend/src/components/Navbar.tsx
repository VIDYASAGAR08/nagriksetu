import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  User as UserIcon,
  MessageSquare,
  LogOut,
  Sliders,
  Type,
  Menu,
  X,
  Users,
  Building,
  FileText,
  QrCode,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, citizenProfile, logout, isAuthenticated, isAdmin, isCitizen, highContrast, largeText, toggleHighContrast, toggleLargeText } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      {/* Accessibility Utility Bar */}
      <div className="bg-slate-900 text-slate-100 text-xs py-1.5 px-4 sm:px-8 flex justify-between items-center border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-primary-400">Official Administrative Service</span>
          <span className="hidden sm:inline text-slate-400">|</span>
          <span className="hidden sm:inline text-slate-400">Government of Public Administration</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={toggleHighContrast}
            type="button"
            aria-pressed={highContrast}
            className="flex items-center gap-1 hover:text-white px-2 py-0.5 rounded border border-slate-700 hover:border-slate-500 focus:outline-none focus:ring-1 focus:ring-primary-400"
          >
            <Sliders className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{highContrast ? 'Standard Contrast' : 'High Contrast'}</span>
          </button>
          <button
            onClick={toggleLargeText}
            type="button"
            aria-pressed={largeText}
            className="flex items-center gap-1 hover:text-white px-2 py-0.5 rounded border border-slate-700 hover:border-slate-500 focus:outline-none focus:ring-1 focus:ring-primary-400"
          >
            <Type className="w-3.5 h-3.5" aria-hidden="true" />
            <span>{largeText ? 'Default Text' : 'Enlarge Text'}</span>
          </button>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16" aria-label="Main Navigation">
        {/* Brand */}
        <Link
          to="/"
          className="flex items-center gap-2.5 font-bold text-lg sm:text-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md p-1"
        >
          <div className="w-9 h-9 rounded-lg bg-primary-700 text-white flex items-center justify-center font-black shadow-sm">
            CA
          </div>
          <div className="flex flex-col">
            <span className="leading-tight">CivicAdmin</span>
            <span className="text-[10px] font-normal text-slate-500 uppercase tracking-wider">Citizen Services</span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <div className="hidden md:flex items-center gap-1">
          {isAuthenticated ? (
            <>
              {isCitizen && (
                <>
                  <Link
                    to="/citizen/dashboard"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/citizen/dashboard')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/citizen/profile"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/citizen/profile')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    My Profile
                  </Link>
                  <Link
                    to="/citizen/household"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/citizen/household')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    My Household
                  </Link>
                  <Link
                    to="/citizen/chat"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/citizen/chat')
                        ? 'bg-primary-50 text-primary-700 font-semibold'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <MessageSquare className="w-4 h-4 text-emerald-600" aria-hidden="true" />
                    <span>Citizen Assistant</span>
                  </Link>
                  <Link
                    to="/whatsapp"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1.5 ${
                      isActive('/whatsapp')
                        ? 'bg-emerald-50 text-emerald-800 font-semibold'
                        : 'text-emerald-700 hover:bg-emerald-50'
                    }`}
                  >
                    <QrCode className="w-4 h-4 text-emerald-600" aria-hidden="true" />
                    <span>WhatsApp Bot</span>
                  </Link>
                </>
              )}

              {isAdmin && (
                <>
                  <Link
                    to="/admin/dashboard"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive('/admin/dashboard')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    Admin Dashboard
                  </Link>
                  <Link
                    to="/admin/citizens"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
                      isActive('/admin/citizens')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <Users className="w-4 h-4" />
                    <span>Citizens</span>
                  </Link>
                  <Link
                    to="/admin/households"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
                      isActive('/admin/households')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <Building className="w-4 h-4" />
                    <span>Households</span>
                  </Link>
                  <Link
                    to="/admin/audit"
                    className={`px-3 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
                      isActive('/admin/audit')
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <FileText className="w-4 h-4" />
                    <span>Audit Trail</span>
                  </Link>
                </>
              )}
            </>
          ) : (
            <>
              <Link
                to="/"
                className={`px-3 py-2 rounded-md text-sm font-medium ${
                  isActive('/') ? 'text-primary-700 font-semibold' : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                Home
              </Link>
              <Link
                to="/whatsapp"
                className={`px-3 py-2 rounded-md text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                  isActive('/whatsapp')
                    ? 'bg-emerald-50 text-emerald-800'
                    : 'text-emerald-700 hover:bg-emerald-50'
                }`}
              >
                <QrCode className="w-4 h-4 text-emerald-600" />
                <span>WhatsApp Bot & QR</span>
              </Link>
              <Link
                to="/login"
                className="px-3 py-2 rounded-md text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                Citizen Sign In
              </Link>
              <Link
                to="/register"
                className="px-3 py-2 rounded-md text-sm font-medium text-primary-700 hover:bg-primary-50 font-semibold"
              >
                Citizen Registration
              </Link>
              <Link
                to="/admin/login"
                className="px-3 py-2 rounded-md text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-300 ml-2 hover:bg-slate-50 flex items-center gap-1"
              >
                <ShieldCheck className="w-4 h-4 text-primary-700" />
                <span>Admin Portal</span>
              </Link>
            </>
          )}
        </div>

        {/* User Badge & Logout */}
        {isAuthenticated && (
          <div className="hidden md:flex items-center gap-3">
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-100 border border-slate-200 text-xs">
              <UserIcon className="w-3.5 h-3.5 text-slate-500" aria-hidden="true" />
              <span className="font-medium text-slate-800">
                {citizenProfile?.full_name || user?.email}
              </span>
              <span className="px-1.5 py-0.2 bg-slate-200 text-slate-700 rounded text-[10px] font-bold uppercase">
                {user?.role}
              </span>
            </div>
            <button
              onClick={handleLogout}
              type="button"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium text-rose-700 hover:bg-rose-50 border border-rose-200 focus:outline-none focus:ring-2 focus:ring-rose-500"
            >
              <LogOut className="w-4 h-4" aria-hidden="true" />
              <span>Sign Out</span>
            </button>
          </div>
        )}

        {/* Mobile Menu Toggle Button */}
        <div className="flex md:hidden items-center">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            type="button"
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle navigation menu"
            className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          {isAuthenticated ? (
            <>
              <div className="p-2 mb-2 bg-slate-100 rounded-lg text-xs">
                <p className="font-semibold text-slate-900">{citizenProfile?.full_name || user?.email}</p>
                <p className="text-slate-500 capitalize">Role: {user?.role}</p>
              </div>

              {isCitizen && (
                <>
                  <Link
                    to="/citizen/dashboard"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/citizen/profile"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    My Profile
                  </Link>
                  <Link
                    to="/citizen/household"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    My Household
                  </Link>
                  <Link
                    to="/citizen/chat"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-emerald-700 hover:bg-emerald-50"
                  >
                    Citizen Assistant
                  </Link>
                </>
              )}

              {isAdmin && (
                <>
                  <Link
                    to="/admin/dashboard"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Admin Dashboard
                  </Link>
                  <Link
                    to="/admin/citizens"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Citizen Management
                  </Link>
                  <Link
                    to="/admin/households"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Household Management
                  </Link>
                  <Link
                    to="/admin/audit"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
                  >
                    Audit Trail
                  </Link>
                </>
              )}

              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  handleLogout();
                }}
                className="w-full text-left px-3 py-2 rounded-md text-base font-medium text-rose-700 hover:bg-rose-50"
              >
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
              >
                Home
              </Link>
              <Link
                to="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
              >
                Citizen Sign In
              </Link>
              <Link
                to="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-primary-700 hover:bg-primary-50"
              >
                Citizen Registration
              </Link>
              <Link
                to="/admin/login"
                onClick={() => setMobileMenuOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-slate-900 border-t border-slate-200 mt-2 pt-2"
              >
                Administrator Portal
              </Link>
            </>
          )}
        </div>
      )}
    </header>
  );
};
