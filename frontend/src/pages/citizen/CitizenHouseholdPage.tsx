import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Household } from '../../types';
import { Alert } from '../../components/Alert';
import { Home, Users, MapPin, ShieldCheck } from 'lucide-react';

export const CitizenHouseholdPage: React.FC = () => {
  const [household, setHousehold] = useState<Household | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchHousehold = async () => {
      try {
        const data = await api.citizen.getMyHousehold();
        setHousehold(data);
      } catch (err: any) {
        setErrorMessage(err.message || 'Unable to retrieve household details.');
      } finally {
        setLoading(false);
      }
    };
    fetchHousehold();
  }, []);

  if (loading) {
    return (
      <div id="main-content" className="py-12 text-center" role="status">
        <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mx-auto mb-4" />
        <span className="text-sm font-medium text-slate-600">Retrieving household records...</span>
      </div>
    );
  }

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-6">
      <div className="border-b border-slate-200 pb-4">
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">My Household Details</h1>
        <p className="text-sm text-slate-600 mt-1">
          View your registered municipal household address and verified family membership.
        </p>
      </div>

      {errorMessage && (
        <Alert
          type="info"
          message={errorMessage}
          onClose={() => setErrorMessage(null)}
        />
      )}

      {/* Privacy Notice Box */}
      <div className="bg-primary-50 border border-primary-200 rounded-2xl p-4 flex items-start gap-3 text-xs text-primary-900">
        <ShieldCheck className="w-5 h-5 text-primary-700 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-bold">Citizen Privacy Guarantee:</span> In accordance with public data protection
          rules, contact details (phone, email) of co-residents and internal administrative notes are withheld from this
          view.
        </div>
      </div>

      {!household ? (
        <div className="bg-white border border-dashed border-slate-300 rounded-2xl p-12 text-center">
          <Home className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-slate-800">No Household Linked</h2>
          <p className="text-sm text-slate-600 max-w-md mx-auto mt-2">
            You are not currently assigned to a registered household. When an administrator links your application to an
            official residence, details will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Address Details Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-100">
              <div className="p-2 rounded-xl bg-emerald-100 text-emerald-800">
                <MapPin className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Registered Residence</h2>
                <span className="text-xs font-mono font-bold text-primary-700">
                  Code: {household.household_code}
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 sm:col-span-2">
                <span className="text-xs text-slate-500 font-medium block">Address Line</span>
                <span className="font-semibold text-slate-900">{household.address_line}</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-xs text-slate-500 font-medium block">Locality</span>
                <span className="font-semibold text-slate-900">{household.locality}</span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-xs text-slate-500 font-medium block">City & State</span>
                <span className="font-semibold text-slate-900">
                  {household.city}, {household.state}
                </span>
              </div>

              <div className="p-3 bg-slate-50 rounded-xl border border-slate-100">
                <span className="text-xs text-slate-500 font-medium block">Postal Code</span>
                <span className="font-semibold text-slate-900">{household.postal_code}</span>
              </div>
            </div>
          </div>

          {/* Members Table */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center gap-3 mb-4 pb-3 border-b border-slate-100">
              <div className="p-2 rounded-xl bg-primary-100 text-primary-800">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-base font-bold text-slate-900">Household Members</h2>
                <span className="text-xs text-slate-500">
                  {household.members.length} registered member{household.members.length !== 1 ? 's' : ''}
                </span>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-sm">
                <thead>
                  <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 bg-slate-50">
                    <th scope="col" className="p-3 rounded-l-lg">Citizen Code</th>
                    <th scope="col" className="p-3">Full Legal Name</th>
                    <th scope="col" className="p-3 rounded-r-lg">Household Role</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {household.members.map((member) => (
                    <tr key={member.id} className="hover:bg-slate-50/70">
                      <td className="p-3 font-mono text-xs font-bold text-primary-700">
                        {member.citizen_code}
                      </td>
                      <td className="p-3 font-semibold text-slate-900">
                        {member.full_name}
                      </td>
                      <td className="p-3">
                        <span className="inline-flex px-2 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                          {member.household_relationship || 'Member'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
