import React from 'react';
import { Link } from 'react-router-dom';
import {
  ShieldCheck,
  Users,
  Home,
  MessageSquare,
  Lock,
  CheckCircle2,
  ArrowRight,
  Accessibility,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div id="main-content" className="py-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <div className="text-center max-w-3xl mx-auto mb-16">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-100 text-primary-800 text-xs font-semibold uppercase tracking-wider mb-4 border border-primary-200">
          <ShieldCheck className="w-4 h-4" />
          <span>Official Public Administration Microservice</span>
        </div>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight leading-tight">
          Accessible, Transparent Citizen & Household Administration
        </h1>
        <p className="mt-4 text-base sm:text-lg text-slate-600 leading-relaxed">
          Welcome to the CivicAdmin public portal. Manage your citizen profile, review registered household
          associations, and interact with the administrative assistant through a secure, accessible platform.
        </p>

        {/* Primary Call to Actions */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/register"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-base font-semibold text-white bg-primary-700 hover:bg-primary-800 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 transition-all min-h-[48px]"
          >
            <span>Register as Citizen</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/login"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-base font-semibold text-slate-800 bg-white border border-slate-300 hover:bg-slate-50 shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 transition-all min-h-[48px]"
          >
            <span>Citizen Sign In</span>
          </Link>
        </div>
      </div>

      {/* Feature Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
        {/* Card 1: Identity & Profiles */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center mb-5">
            <Users className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Citizen Identity & Profiles</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Unique citizen identifiers, multi-language preferences, and authenticated profile self-service with strict
            data ownership.
          </p>
        </div>

        {/* Card 2: Household Records */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center mb-5">
            <Home className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Household Management</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            Privacy-centric household associations. Citizens can view their residential record without exposing private
            co-resident credentials.
          </p>
        </div>

        {/* Card 3: Interactive Assistant */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center mb-5">
            <MessageSquare className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 mb-2">Conversational Assistant</h2>
          <p className="text-sm text-slate-600 leading-relaxed">
            WhatsApp-inspired conversational UI providing fast query resolution for profile details, household data, and
            platform services.
          </p>
        </div>
      </div>

      {/* Accessibility & Standards Commitment */}
      <div className="bg-slate-900 text-white rounded-2xl p-8 mb-12 shadow-md">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-slate-800 text-primary-400">
              <Accessibility className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-lg font-bold">WCAG 2.2 AA Accessibility Commitment</h3>
              <p className="mt-1 text-sm text-slate-300 max-w-2xl leading-relaxed">
                Built with semantic HTML, high contrast mode, keyboard focus navigation, screen-reader live alerts, and
                enlarged typography options for public inclusivity.
              </p>
            </div>
          </div>
          <div className="flex-shrink-0 flex items-center gap-2 text-xs font-medium text-slate-300 bg-slate-800/80 px-4 py-2 rounded-lg border border-slate-700">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Fully Keyboard Navigable</span>
          </div>
        </div>
      </div>

      {/* University Demonstration Quick-Access Banner */}
      <div className="border border-primary-200 bg-primary-50/70 rounded-2xl p-6 text-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-primary-900 flex items-center gap-2">
              <Lock className="w-4 h-4 text-primary-700" />
              <span>University Demonstration Guide & Seed Credentials</span>
            </h3>
            <p className="text-sm text-slate-700 mt-1">
              Test accounts have been pre-seeded for examination:
            </p>
            <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
              <div className="bg-white p-2 rounded border border-primary-200">
                <strong>Citizen Demo:</strong> aarav.sharma@example.com / CitizenPass123!@
              </div>
              <div className="bg-white p-2 rounded border border-primary-200">
                <strong>Admin Demo:</strong> admin@civicportal.gov / AdminPass123!@#
              </div>
            </div>
          </div>
          <Link
            to="/admin/login"
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-semibold text-primary-900 bg-primary-200 hover:bg-primary-300 transition-colors flex-shrink-0"
          >
            <span>Administrator Portal &rarr;</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
