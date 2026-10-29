import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { Household } from '../../types';
import { Badge } from '../../components/Badge';
import {
  User,
  Home,
  QrCode,
  ShieldCheck,
  Calendar,
  Phone,
  Globe,
  ArrowRight,
  Info,
} from 'lucide-react';

export const CitizenDashboard: React.FC = () => {
  const { citizenProfile, user } = useAuth();
  const [household, setHousehold] = useState<Household | null>(null);
  const [loadingHousehold, setLoadingHousehold] = useState<boolean>(true);

  useEffect(() => {
    const fetchHousehold = async () => {
      try {
        const data = await api.citizen.getMyHousehold();
        setHousehold(data);
      } catch (err) {
        setHousehold(null);
      } finally {
        setLoadingHousehold(false);
      }
    };
    fetchHousehold();
  }, []);

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-primary-800 to-primary-950 text-white rounded-2xl p-6 sm:p-8 shadow-lg">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs uppercase tracking-wider text-primary-200 font-semibold">
                Citizen Portal
              </span>
              <span className="text-primary-400">•</span>
              <span className="text-xs text-primary-300 font-mono">
                Code: {citizenProfile?.citizen_code || 'Pending'}
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              Welcome back, {citizenProfile?.full_name || user?.email}
            </h1>
            <p className="mt-1 text-sm text-primary-200">
              Manage your personal administrative profile and registered household records.
            </p>
          </div>
          <div className="flex-shrink-0">
            {citizenProfile?.profile_status && (
              <Badge
                status={citizenProfile.profile_status}
                className="text-sm px-3.5 py-1 bg-white/10 text-white border-white/20"
              />
            )}
          </div>
        </div>
      </div>

      {/* Main Grid: Profile Overview & Household Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Card (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-100">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-xl bg-primary-100 text-primary-800">
                <User className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-slate-900">Profile Summary</h2>
                <p className="text-xs text-slate-500">Official registered identity attributes</p>
              </div>
            </div>
            <Link
              to="/citizen/profile"
              className="inline-flex items-center gap-1 text-sm font-semibold text-primary-700 hover:text-primary-800 focus:outline-none"
            >
              <span>Edit Details</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium block">Full Legal Name</span>
              <span className="text-base font-semibold text-slate-900">{citizenProfile?.full_name}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium block">Registered Email</span>
              <span className="text-base font-semibold text-slate-900 font-mono text-xs sm:text-sm">
                {user?.email}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium block flex items-center gap-1">
                <Phone className="w-3.5 h-3.5" />
                <span>Contact Phone</span>
              </span>
              <span className="text-base font-semibold text-slate-900">
                {citizenProfile?.phone_number || 'Not provided'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium block flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>Date of Birth</span>
              </span>
              <span className="text-base font-semibold text-slate-900">
                {citizenProfile?.date_of_birth || 'Not registered'}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium block flex items-center gap-1">
                <Globe className="w-3.5 h-3.5" />
                <span>Interface Language</span>
              </span>
              <span className="text-base font-semibold text-slate-900 uppercase">
                {citizenProfile?.preferred_language}
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100">
              <span className="text-xs text-slate-500 font-medium block flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Household Role</span>
              </span>
              <span className="text-base font-semibold text-slate-900">
                {citizenProfile?.household_relationship || 'Unassigned'}
              </span>
            </div>
          </div>
        </div>

        {/* WhatsApp & Municipal Bot Access Widget (1 col) */}
        <div className="bg-gradient-to-br from-emerald-800 to-teal-950 text-white rounded-2xl p-6 shadow-md flex flex-col justify-between">
          <div>
            <div className="w-12 h-12 rounded-xl bg-white/10 flex items-center justify-center mb-4">
              <QrCode className="w-6 h-6 text-emerald-300" />
            </div>
            <h2 className="text-xl font-bold mb-2">Municipal WhatsApp Bot</h2>
            <p className="text-sm text-emerald-100 leading-relaxed">
              Access municipal records, look up household details, and verify profile review status directly via our automated bot.
            </p>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10">
            <Link
              to="/whatsapp"
              className="w-full inline-flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm shadow transition-all focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              <span>Open WhatsApp Bot</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Household Status Section */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-100 text-emerald-800">
              <Home className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-900">Household Association</h2>
              <p className="text-xs text-slate-500">Your registered residential record</p>
            </div>
          </div>
          {household && (
            <Link
              to="/citizen/household"
              className="inline-flex items-center gap-1 text-sm font-semibold text-primary-700 hover:text-primary-800"
            >
              <span>View Full Household</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>

        {loadingHousehold ? (
          <div className="p-4 text-center text-sm text-slate-500">Loading household status...</div>
        ) : household ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 md:col-span-2">
              <span className="text-xs text-slate-500 font-medium block">Residential Address</span>
              <p className="text-sm font-semibold text-slate-900 mt-0.5">
                {household.address_line}, {household.locality}
              </p>
              <p className="text-xs text-slate-600">
                {household.city}, {household.state} - {household.postal_code}
              </p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 flex flex-col justify-center">
              <span className="text-xs text-slate-500 font-medium block">Household Code</span>
              <span className="text-sm font-bold text-primary-800 font-mono mt-0.5">
                {household.household_code}
              </span>
              <span className="text-xs text-slate-500 mt-1">
                {household.members.length} registered member{household.members.length !== 1 ? 's' : ''}
              </span>
            </div>
          </div>
        ) : (
          <div className="p-6 rounded-xl bg-slate-50 border border-dashed border-slate-300 text-center">
            <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <h3 className="text-sm font-bold text-slate-800">No Household Linked</h3>
            <p className="text-xs text-slate-600 max-w-md mx-auto mt-1">
              Your profile is not currently assigned to a household. An administrative officer will link your record
              upon reviewing your municipal documents.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
