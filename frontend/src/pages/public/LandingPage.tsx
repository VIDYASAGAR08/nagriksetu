import React, { useState } from 'react';
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
  GraduationCap,
  Briefcase,
  HeartHandshake,
  Sparkles,
  Clock,
  X,
  Building2,
  ChevronRight,
} from 'lucide-react';

interface CivicServiceItem {
  id: string;
  title: string;
  titleHindi: string;
  icon: React.ComponentType<{ className?: string }>;
  colorClass: string;
  iconColor: string;
  borderColor: string;
  description: string;
  highlights: string[];
  department: string;
}

const CITIZEN_SERVICES: CivicServiceItem[] = [
  {
    id: 'education',
    title: 'Education Service',
    titleHindi: 'शिक्षा सेवा',
    icon: GraduationCap,
    colorClass: 'bg-blue-50 text-blue-800 border-blue-200',
    iconColor: 'text-blue-700',
    borderColor: 'border-blue-200 hover:border-blue-400',
    description: 'School/college admissions, DigiLocker academic certificates, scholarship schemes, and degree verifications.',
    highlights: ['National Scholarship Portal (NSP)', 'DigiLocker Marksheets', 'Pre/Post-Matric Grants', 'University Degree Verification'],
    department: 'Department of Higher & School Education (शिक्षा विभाग)',
  },
  {
    id: 'employment',
    title: 'Employment Service',
    titleHindi: 'रोजगार सेवा',
    icon: Briefcase,
    colorClass: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    iconColor: 'text-emerald-700',
    borderColor: 'border-emerald-200 hover:border-emerald-400',
    description: 'National Career Service (NCS) exchange, public employment notifications, job fair enrolments, and unemployment assistance.',
    highlights: ['National Career Service (NCS)', 'Rojgar Mela Enrolment', 'State Employment Exchange', 'Apprenticeship Opportunities'],
    department: 'Ministry of Labour & Employment (श्रम एवं रोजगार मंत्रालय)',
  },
  {
    id: 'skills',
    title: 'Skill Development Service',
    titleHindi: 'कौशल विकास सेवा',
    icon: Sparkles,
    colorClass: 'bg-amber-50 text-amber-800 border-amber-200',
    iconColor: 'text-amber-700',
    borderColor: 'border-amber-200 hover:border-amber-400',
    description: 'Pradhan Mantri Kaushal Vikas Yojana (PMKVY), vocational apprenticeship, ITI technical certifications, and youth upskilling.',
    highlights: ['PMKVY Skill Certification', 'ITI Technical Training', 'Apprenticeship Portal', 'Industry 4.0 Up-skilling'],
    department: 'Ministry of Skill Development & Entrepreneurship (MSDE)',
  },
  {
    id: 'swd',
    title: 'SWD (Social Welfare Development) Service',
    titleHindi: 'सामाजिक कल्याण सेवा',
    icon: HeartHandshake,
    colorClass: 'bg-rose-50 text-rose-800 border-rose-200',
    iconColor: 'text-rose-700',
    borderColor: 'border-rose-200 hover:border-rose-400',
    description: 'Social welfare schemes, old-age and widow pensions, Divyangjan disability support, Direct Benefit Transfer (DBT), and minority grants.',
    highlights: ['National Social Assistance (NSAP)', 'Divyangjan Disability Aid', 'Direct Benefit Transfer (DBT)', 'Senior Citizen Welfare'],
    department: 'Social Welfare & Empowerment Department (सामाजिक न्याय एवं अधिकारिता विभाग)',
  },
];

export const LandingPage: React.FC = () => {
  const [selectedService, setSelectedService] = useState<CivicServiceItem | null>(null);

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

      {/* ========================================================================= */}
      {/* CITIZEN SERVICES DIRECTORY (EDUCATION, EMPLOYMENT, SKILL DEV, SWD)         */}
      {/* ========================================================================= */}
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 border-b border-slate-200 pb-4">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-saffron-100 text-saffron-900 text-[11px] font-bold uppercase tracking-wider mb-1.5 border border-saffron-200">
              <Building2 className="w-3.5 h-3.5 text-saffron-700" />
              <span>Unified Civic Services Directory | नागरिक सेवा केंद्र</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-navy-950 tracking-tight">
              Essential Public & Welfare Services <span className="text-saffron-600 font-semibold text-xl block sm:inline sm:ml-2">नागरिक कल्याणकारी सेवाएं</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl">
              Direct access to vital public administration portals, scholarship databases, career exchanges, vocational training, and social welfare programs.
            </p>
          </div>
          <span className="text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1.5 rounded-xl border border-slate-200 shrink-0">
            4 Core Welfare Streams
          </span>
        </div>

        {/* 4 Core Services Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {CITIZEN_SERVICES.map((service) => {
            const Icon = service.icon;
            return (
              <div
                key={service.id}
                onClick={() => setSelectedService(service)}
                className={`bg-white rounded-3xl border ${service.borderColor} p-6 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between group cursor-pointer hover:-translate-y-1 relative overflow-hidden`}
              >
                {/* Accent Top Strip */}
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-saffron-400 via-navy-600 to-emerald-500 opacity-80" />

                <div>
                  {/* Icon & Development Status Badge */}
                  <div className="flex items-start justify-between gap-2 mb-4">
                    <div className={`w-14 h-14 rounded-2xl ${service.colorClass} flex items-center justify-center font-bold shadow-xs border transition-transform group-hover:scale-105`}>
                      <Icon className="w-7 h-7" />
                    </div>
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-full bg-amber-100 text-amber-900 border border-amber-300 shadow-2xs">
                      <Clock className="w-3 h-3 text-amber-600 animate-pulse" />
                      <span>In Development</span>
                    </span>
                  </div>

                  {/* Service Titles */}
                  <h3 className="text-lg font-black text-navy-950 group-hover:text-saffron-600 transition-colors">
                    {service.title}
                  </h3>
                  <span className="text-xs font-bold text-slate-500 block mb-2">
                    {service.titleHindi}
                  </span>

                  {/* Description */}
                  <p className="text-xs text-slate-600 leading-relaxed mb-4">
                    {service.description}
                  </p>

                  {/* Highlights List */}
                  <div className="space-y-1.5 border-t border-slate-100 pt-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      Key Schemes & Facilities:
                    </span>
                    {service.highlights.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-[11px] text-slate-700 font-medium">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600 shrink-0" />
                        <span className="truncate">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Footer Action */}
                <div className="mt-5 pt-3.5 border-t border-slate-100 flex items-center justify-between text-xs font-bold text-navy-900 group-hover:text-saffron-600 transition-colors">
                  <span>View Details & Scope</span>
                  <ChevronRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            );
          })}
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

      {/* ========================================================================= */}
      {/* SERVICE PREVIEW MODAL                                                    */}
      {/* ========================================================================= */}
      {selectedService && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-sm animate-fade-in">
          <div className="w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-3">
                <div className={`p-2.5 rounded-xl ${selectedService.colorClass}`}>
                  <selectedService.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-base text-navy-950">{selectedService.title}</h3>
                  <span className="text-xs font-bold text-slate-500">{selectedService.titleHindi}</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedService(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div className="bg-amber-50/80 border border-amber-200 rounded-2xl p-3.5 flex items-start gap-2.5 text-amber-900">
                <Clock className="w-4 h-4 text-amber-700 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-amber-950">Team Member Active Development Notice</p>
                  <p className="text-amber-800 text-[11px] mt-0.5 leading-relaxed">
                    This civic service is currently under development by our technical team. The backend API endpoints and user interfaces are being authored and will be connected directly to this card once finalized.
                  </p>
                </div>
              </div>

              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
                  Responsible Ministry / Department
                </span>
                <p className="font-bold text-sm text-navy-950 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                  {selectedService.department}
                </p>
              </div>

              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
                  Planned Citizen Facilities
                </span>
                <p className="text-slate-600 leading-relaxed mb-3">
                  {selectedService.description}
                </p>

                <div className="space-y-2 bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                  <span className="text-[10px] uppercase font-bold text-slate-500 block">
                    Underway Deliverables:
                  </span>
                  {selectedService.highlights.map((h, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-slate-800 font-semibold">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>{h}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2 flex justify-end">
                <button
                  type="button"
                  onClick={() => setSelectedService(null)}
                  className="py-2 px-5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white shadow-md transition"
                >
                  Understood (Dismiss)
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LandingPage;
