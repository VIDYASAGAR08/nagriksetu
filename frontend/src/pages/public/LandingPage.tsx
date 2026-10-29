import React from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Home,
  Lock,
  CheckCircle2,
  ArrowRight,
  Accessibility,
  QrCode,
  Award,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div id="main-content" className="py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12">
      {/* Official Government Hero Banner */}
      <div className="relative rounded-3xl bg-gradient-to-b from-primary-900 via-primary-800 to-primary-950 text-white p-8 sm:p-14 overflow-hidden shadow-xl border border-slate-700">
        {/* Subtle Decorative Background Motif */}
        <div className="absolute -top-24 -right-24 w-96 h-96 rounded-full bg-saffron-500/10 blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 rounded-full bg-govgreen-500/10 blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl mx-auto text-center space-y-5">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/10 backdrop-blur-md text-saffron-300 text-xs font-bold uppercase tracking-wider border border-white/15">
            <Award className="w-3.5 h-3.5 text-saffron-400" />
            <span>भारत सरकार अधिकृत | National Digital Governance Initiative</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            नागरिक सेतु — <span className="text-saffron-400">NagrikSetu</span>
          </h1>
          <p className="text-lg sm:text-xl font-medium text-slate-200">
            Unified Public Administration & Citizen Services Platform
          </p>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl mx-auto">
            Welcome to the official NagrikSetu portal. Complete citizen registration, verify household residency
            records, track municipal review status, or access automated services directly on WhatsApp.
          </p>

          {/* Primary Action Buttons */}
          <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3.5">
            <Link
              to="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-base font-bold text-white bg-saffron-600 hover:bg-saffron-500 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-saffron-400 transition-all min-h-[48px]"
            >
              <span>Citizen Registration (पंजीकरण)</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/whatsapp"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-base font-bold text-slate-950 bg-[#25D366] hover:bg-[#20bd5a] shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#25D366] transition-all min-h-[48px]"
            >
              <QrCode className="w-5 h-5 text-slate-950" />
              <span>WhatsApp Bot & QR Code</span>
            </Link>

            <Link
              to="/login"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl text-base font-semibold text-white bg-white/10 hover:bg-white/20 border border-white/20 backdrop-blur-xs shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-300 transition-all min-h-[48px]"
            >
              <span>Citizen Sign In</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Official Government 4 Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Citizen Identity */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition-shadow">
          <div className="w-12 h-12 rounded-xl bg-primary-100 text-primary-800 flex items-center justify-center mb-4 border border-primary-200">
            <Users className="w-6 h-6 text-primary-800" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 mb-1.5">Official Citizen Registry</h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Unique government citizen identifiers (`CIT-XXXXXXXX`), multilingual interface preferences, and verified status
            tracking with Argon2 security.
          </p>
        </div>

        {/* Card 2: Household Records */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition-shadow">
          <div className="w-12 h-12 rounded-xl bg-govgreen-100 text-govgreen-800 flex items-center justify-center mb-4 border border-govgreen-200">
            <Home className="w-6 h-6 text-govgreen-800" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 mb-1.5">Household & Dwelling Management</h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Privacy-first household association. Citizens view their municipal address and verified co-residents without
            exposing private contact numbers or notes.
          </p>
        </div>

        {/* Card 3: WhatsApp Bot Automation */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs hover:shadow-md transition-shadow">
          <div className="w-12 h-12 rounded-xl bg-saffron-100 text-saffron-800 flex items-center justify-center mb-4 border border-saffron-200">
            <QrCode className="w-6 h-6 text-saffron-800" />
          </div>
          <h2 className="text-lg font-bold text-slate-900 mb-1.5">Landbot WhatsApp Services</h2>
          <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
            Scan our official QR code to register, check household members, and verify status directly from WhatsApp without
            ever visiting the website.
          </p>
        </div>
      </div>

      {/* Accessibility & Standards Commitment */}
      <div className="bg-[#081c33] text-white rounded-2xl p-6 sm:p-8 shadow-md border-l-4 border-l-saffron-500">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-start gap-4">
            <div className="p-3 rounded-xl bg-white/10 text-saffron-300">
              <Accessibility className="w-7 h-7" />
            </div>
            <div>
              <h3 className="text-base sm:text-lg font-bold">Government Inclusivity & WCAG 2.2 AA Standards</h3>
              <p className="mt-1 text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
                NagrikSetu adheres to Indian Government Web Guidelines (GIGW) and WCAG 2.2 Level AA accessibility, featuring
                high-contrast mode, scalable text, semantic HTML landmarks, and screen reader skip navigation.
              </p>
            </div>
          </div>
          <div className="flex-shrink-0 flex items-center gap-2 text-xs font-semibold text-emerald-300 bg-white/10 px-4 py-2 rounded-lg border border-white/15">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>GIGW & WCAG 2.2 Compliant</span>
          </div>
        </div>
      </div>

      {/* University Demonstration Quick-Access Banner */}
      <div className="border border-primary-300 bg-primary-50/80 rounded-2xl p-6 text-slate-900 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h3 className="font-bold text-primary-950 flex items-center gap-2 text-sm sm:text-base">
              <Lock className="w-4 h-4 text-saffron-600" />
              <span>Demonstration Examination Credentials (Pre-Seeded)</span>
            </h3>
            <p className="text-xs sm:text-sm text-slate-700 mt-1">
              Evaluators and teachers can log in using either portal experience:
            </p>
            <div className="mt-2.5 grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs font-mono">
              <div className="bg-white p-2.5 rounded-lg border border-slate-300 shadow-2xs">
                <span className="text-[11px] font-bold text-emerald-700 block font-sans">Citizen Portal Access:</span>
                <code>aarav.sharma@example.com</code> / <code>CitizenPass123!@</code>
              </div>
              <div className="bg-white p-2.5 rounded-lg border border-slate-300 shadow-2xs">
                <span className="text-[11px] font-bold text-primary-800 block font-sans">Administrator Portal Access:</span>
                <code>admin@civicportal.gov</code> / <code>AdminPass123!@#</code>
              </div>
            </div>
          </div>
          <Link
            to="/admin/login"
            className="inline-flex items-center justify-center gap-1.5 px-4 py-2.5 rounded-lg text-xs sm:text-sm font-bold text-white bg-primary-800 hover:bg-primary-900 transition-colors flex-shrink-0 shadow-xs"
          >
            <span>Admin Portal Login &rarr;</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
