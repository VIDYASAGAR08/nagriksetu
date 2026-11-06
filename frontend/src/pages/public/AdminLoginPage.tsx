import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Alert } from '../../components/Alert';
import { BiometricAuthModal } from '../../components/BiometricAuthModal';
import { ShieldCheck, Mail, Lock, Eye, EyeOff, KeyRound, Fingerprint } from 'lucide-react';

export const AdminLoginPage: React.FC = () => {
  const { login, loginWithSession } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isBiometricOpen, setIsBiometricOpen] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email.trim() || !password) {
      setErrorMessage('Administrator credentials are required.');
      return;
    }

    setIsSubmitting(true);
    try {
      const user = await login(email.trim().toLowerCase(), password);
      if (user.role !== 'admin') {
        throw new Error('Access denied. This account does not possess administrative privileges.');
      }
      navigate('/admin/dashboard');
    } catch (err: any) {
      setErrorMessage(err.message || 'Administrator authentication failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const fillDemoAdmin = () => {
    setEmail('admin@civicportal.gov');
    setPassword('AdminPass123!@#');
  };

  const fillScopedAdmin = () => {
    setEmail('admin.bengaluru@nagriksetu.gov.in');
    setPassword('AdminPass123!@#');
  };

  return (
    <div id="main-content" className="min-h-[75vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-slate-900/5">
      <div className="max-w-md w-full bg-white p-8 rounded-2xl border-2 border-slate-800 shadow-2xl">
        <div className="text-center mb-6">
          <div className="w-14 h-14 bg-slate-900 text-white rounded-2xl mx-auto flex items-center justify-center font-bold mb-3 shadow-md">
            <ShieldCheck className="w-8 h-8 text-amber-400" />
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Administrative Portal</h1>
          <p className="text-sm text-slate-600 mt-1">
            Restricted access for authorized municipal administrators
          </p>
        </div>

        {errorMessage && (
          <Alert
            type="error"
            message={errorMessage}
            onClose={() => setErrorMessage(null)}
            className="mb-6"
          />
        )}

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div>
            <label htmlFor="admin-email" className="block text-sm font-semibold text-slate-800 mb-1.5">
              Admin Identifier / Email <span className="text-rose-600" aria-hidden="true">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Mail className="w-5 h-5" aria-hidden="true" />
              </div>
              <input
                id="admin-email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@civicportal.gov"
                className="w-full pl-10 pr-3 py-2.5 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm font-mono"
              />
            </div>
          </div>

          <div>
            <label htmlFor="admin-password" className="block text-sm font-semibold text-slate-800 mb-1.5">
              Master Admin Password <span className="text-rose-600" aria-hidden="true">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                <Lock className="w-5 h-5" aria-hidden="true" />
              </div>
              <input
                id="admin-password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full pl-10 pr-10 py-2.5 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm font-mono"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 px-4 rounded-xl text-white font-bold bg-slate-900 hover:bg-black focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-900 shadow-lg transition-all flex items-center justify-center gap-2 min-h-[46px] disabled:opacity-70"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Verifying Security Clearance...</span>
              </>
            ) : (
              <>
                <KeyRound className="w-4 h-4 text-amber-400" />
                <span>Sign In as Administrator</span>
              </>
            )}
          </button>

          {/* Biometric Clearance Option */}
          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-white px-2 text-slate-400 font-medium">High Security Clearance</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              if (!email.trim()) {
                setEmail('admin@civicportal.gov');
              }
              setIsBiometricOpen(true);
            }}
            className="w-full py-2.5 px-4 rounded-xl font-bold border-2 border-slate-900 bg-slate-50 hover:bg-slate-100 text-slate-900 transition flex items-center justify-center gap-2 text-sm shadow-xs"
          >
            <Fingerprint className="w-4 h-4 text-amber-500" />
            <span>Biometric Administrator Clearance (Touch ID / Face ID)</span>
          </button>
        </form>

        <BiometricAuthModal
          isOpen={isBiometricOpen}
          onClose={() => setIsBiometricOpen(false)}
          email={email || 'admin@civicportal.gov'}
          title="Administrative Biometric Clearance"
          roleHint="admin"
          onSuccess={async (res) => {
            await loginWithSession(res.access_token, res.user);
            navigate('/admin/dashboard');
          }}
        />

        <div className="mt-5 pt-4 border-t border-slate-100 flex flex-col gap-2 text-xs">
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={fillDemoAdmin}
              className="text-amber-700 hover:text-amber-900 font-semibold underline focus:outline-none"
            >
              Fill National Admin (All Areas)
            </button>
            <button
              type="button"
              onClick={fillScopedAdmin}
              className="text-emerald-700 hover:text-emerald-900 font-semibold underline focus:outline-none"
            >
              Fill Scoped Admin (Bengaluru)
            </button>
          </div>
          <div className="text-right pt-1">
            <Link to="/login" className="text-slate-500 hover:text-slate-800">
              Citizen Login &rarr;
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
