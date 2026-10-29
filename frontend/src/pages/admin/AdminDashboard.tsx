import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../services/api';
import { AdminDashboardMetrics } from '../../types';
import { Badge } from '../../components/Badge';
import {
  Users,
  Building,
  CheckCircle2,
  Clock,
  ArrowRight,
  ShieldCheck,
  FileText,
  Layers,
} from 'lucide-react';

export const AdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<AdminDashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const data = await api.admin.getDashboard();
        setMetrics(data);
      } catch (err) {
        console.error('Failed to load admin metrics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div id="main-content" className="py-12 text-center" role="status">
        <div className="w-10 h-10 border-4 border-slate-300 border-t-slate-800 rounded-full animate-spin mx-auto mb-4" />
        <span className="text-sm font-medium text-slate-600">Calculating system metrics...</span>
      </div>
    );
  }

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldCheck className="w-5 h-5 text-amber-600" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
              System Administration
            </span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 tracking-tight">
            Administrative Dashboard
          </h1>
          <p className="text-sm text-slate-600 mt-0.5">
            Real-time municipal record indicators derived directly from PostgreSQL administration database.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {/* Admin Scope Badge (FR-ADM-022, FR-ADM-023) */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-300 text-emerald-900 text-xs font-semibold">
            <Layers className="w-4 h-4 text-emerald-700" />
            <span>Scope: {metrics?.admin_scope || 'National (All Areas)'}</span>
          </div>
          <Link
            to="/admin/hierarchy"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-slate-900 hover:bg-black text-white text-sm font-semibold shadow-sm transition-colors"
          >
            <Layers className="w-4 h-4 text-emerald-400" />
            <span>Hierarchy & Scope</span>
          </Link>
        </div>
      </div>

      {/* Metrics Counter Cards (FR-ADM-023) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Total Administrative Units */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Admin Units
            </span>
            <div className="text-3xl font-black text-slate-900 mt-1 font-mono">
              {metrics?.total_administrative_units ?? 0}
            </div>
            <span className="text-xs text-emerald-600 font-medium mt-1 block">
              {metrics?.active_units ?? 0} active units
            </span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-teal-50 text-teal-700 flex items-center justify-center">
            <Layers className="w-6 h-6" />
          </div>
        </div>

        {/* Total Citizens */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Total Citizens
            </span>
            <div className="text-3xl font-black text-slate-900 mt-1 font-mono">
              {metrics?.total_citizens ?? 0}
            </div>
            <span className="text-xs text-slate-500 mt-1 block">In assigned scope</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
            <Users className="w-6 h-6" />
          </div>
        </div>

        {/* Active Profiles */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Active Profiles
            </span>
            <div className="text-3xl font-black text-emerald-700 mt-1 font-mono">
              {metrics?.active_citizens ?? 0}
            </div>
            <span className="text-xs text-emerald-600 font-medium mt-1 block">Verified status</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-700 flex items-center justify-center">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>

        {/* Pending Review */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Pending Review
            </span>
            <div className="text-3xl font-black text-amber-600 mt-1 font-mono">
              {metrics?.pending_citizens ?? 0}
            </div>
            <span className="text-xs text-amber-600 font-medium mt-1 block">Awaiting officer action</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-amber-50 text-amber-700 flex items-center justify-center">
            <Clock className="w-6 h-6" />
          </div>
        </div>

        {/* Total Households */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Households
            </span>
            <div className="text-3xl font-black text-slate-900 mt-1 font-mono">
              {metrics?.total_households ?? 0}
            </div>
            <span className="text-xs text-slate-500 mt-1 block">In assigned scope</span>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-700 flex items-center justify-center">
            <Building className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Two Column Section: Recent Citizen Registrations & Quick Management Links */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Registrations Table (2 cols) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Recent Citizen Registrations</h2>
              <p className="text-xs text-slate-500">Most recently added citizen profile records</p>
            </div>
            <Link
              to="/admin/citizens"
              className="text-xs font-semibold text-primary-700 hover:text-primary-800 flex items-center gap-1"
            >
              <span>View All</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 bg-slate-50">
                  <th scope="col" className="p-3">Citizen Code</th>
                  <th scope="col" className="p-3">Full Legal Name</th>
                  <th scope="col" className="p-3">Status</th>
                  <th scope="col" className="p-3">Language</th>
                  <th scope="col" className="p-3">Registered On</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {metrics?.recent_registrations && metrics.recent_registrations.length > 0 ? (
                  metrics.recent_registrations.map((citizen) => (
                    <tr key={citizen.id} className="hover:bg-slate-50/70">
                      <td className="p-3 font-mono text-xs font-bold text-primary-700">
                        {citizen.citizen_code}
                      </td>
                      <td className="p-3 font-semibold text-slate-900">
                        {citizen.full_name}
                      </td>
                      <td className="p-3">
                        <Badge status={citizen.profile_status} />
                      </td>
                      <td className="p-3 uppercase text-xs text-slate-600 font-semibold">
                        {citizen.preferred_language}
                      </td>
                      <td className="p-3 text-xs text-slate-500">
                        {new Date(citizen.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-xs text-slate-500">
                      No recent citizen records available.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Management Quick Actions (1 col) */}
        <div className="space-y-4">
          <div className="bg-slate-900 text-white rounded-2xl p-6 shadow-md">
            <h2 className="text-base font-bold text-amber-400 mb-2">Administrative Navigation</h2>
            <p className="text-xs text-slate-300 leading-relaxed mb-5">
              Maintain municipal population and residential records with strict accountability.
            </p>

            <div className="space-y-2">
              <Link
                to="/admin/citizens"
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-semibold transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Users className="w-4 h-4 text-primary-400" />
                  <span>Citizen Registry</span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </Link>

              <Link
                to="/admin/households"
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-semibold transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Building className="w-4 h-4 text-emerald-400" />
                  <span>Household Registry</span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </Link>

              <Link
                to="/admin/hierarchy"
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-semibold transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <Layers className="w-4 h-4 text-teal-400" />
                  <span>Hierarchy & Area Scope</span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </Link>

              <Link
                to="/admin/audit"
                className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-sm font-semibold transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  <span>Audit Trail Logs</span>
                </div>
                <ArrowRight className="w-4 h-4 text-slate-400" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
