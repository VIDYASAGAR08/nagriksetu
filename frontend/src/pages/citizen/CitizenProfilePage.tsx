import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { Alert } from '../../components/Alert';
import { Badge } from '../../components/Badge';
import { User, Phone, Globe, Calendar, Lock, Save } from 'lucide-react';

export const CitizenProfilePage: React.FC = () => {
  const { citizenProfile, user, refreshUser } = useAuth();

  const [formData, setFormData] = useState({
    full_name: '',
    phone_number: '',
    preferred_language: 'en',
    date_of_birth: '',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (citizenProfile) {
      setFormData({
        full_name: citizenProfile.full_name || '',
        phone_number: citizenProfile.phone_number || '',
        preferred_language: citizenProfile.preferred_language || 'en',
        date_of_birth: citizenProfile.date_of_birth || '',
      });
    }
  }, [citizenProfile]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMessage(null);
    setErrorMessage(null);

    if (formData.full_name.trim().length < 2) {
      setErrorMessage('Full name must contain at least 2 characters.');
      return;
    }

    setIsSaving(true);
    try {
      await api.citizen.updateMyProfile({
        full_name: formData.full_name.trim(),
        phone_number: formData.phone_number.trim() || undefined,
        preferred_language: formData.preferred_language,
        date_of_birth: formData.date_of_birth || undefined,
      });
      await refreshUser();
      setSuccessMessage('Your profile attributes have been successfully updated.');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">My Citizen Profile</h1>
          <p className="text-sm text-slate-600 mt-1">
            View your official record and update your permitted contact preferences.
          </p>
        </div>
        {citizenProfile?.profile_status && (
          <Badge status={citizenProfile.profile_status} className="text-sm px-3 py-1" />
        )}
      </div>

      {successMessage && (
        <Alert
          type="success"
          message={successMessage}
          onClose={() => setSuccessMessage(null)}
        />
      )}

      {errorMessage && (
        <Alert
          type="error"
          message={errorMessage}
          onClose={() => setErrorMessage(null)}
        />
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Protected Official Attributes (Read-only) */}
        <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-slate-700 font-bold text-sm">
            <Lock className="w-4 h-4 text-slate-500" />
            <span>Protected Official Fields</span>
          </div>
          <p className="text-xs text-slate-500 leading-relaxed">
            These fields are verified against administrative records and cannot be altered directly.
          </p>

          <div className="space-y-3 text-xs">
            <div className="p-2.5 bg-white rounded-lg border border-slate-200">
              <span className="text-slate-400 block font-medium">Citizen Identifier</span>
              <span className="font-mono font-bold text-slate-800 text-sm">
                {citizenProfile?.citizen_code}
              </span>
            </div>

            <div className="p-2.5 bg-white rounded-lg border border-slate-200">
              <span className="text-slate-400 block font-medium">Account Role</span>
              <span className="font-bold text-slate-800 uppercase">{user?.role}</span>
            </div>

            <div className="p-2.5 bg-white rounded-lg border border-slate-200">
              <span className="text-slate-400 block font-medium">Account Status</span>
              <span className="font-bold text-slate-800 capitalize">{user?.account_status}</span>
            </div>

            <div className="p-2.5 bg-white rounded-lg border border-slate-200">
              <span className="text-slate-400 block font-medium">Household Assignment</span>
              <span className="font-bold text-slate-800">
                {citizenProfile?.household_relationship || 'None Assigned'}
              </span>
            </div>
          </div>
        </div>

        {/* Editable Permitted Fields (2 cols) */}
        <div className="md:col-span-2 bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
          <h2 className="text-lg font-bold text-slate-900 mb-4 pb-2 border-b border-slate-100">
            Editable Personal Information
          </h2>

          <form onSubmit={handleSave} className="space-y-4" noValidate>
            <div>
              <label htmlFor="prof-name" className="block text-sm font-semibold text-slate-700 mb-1">
                Full Legal Name <span className="text-rose-600">*</span>
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <User className="w-4 h-4" />
                </div>
                <input
                  id="prof-name"
                  name="full_name"
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={handleChange}
                  className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                />
              </div>
            </div>

            <div>
              <label htmlFor="prof-phone" className="block text-sm font-semibold text-slate-700 mb-1">
                Contact Phone Number
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                  <Phone className="w-4 h-4" />
                </div>
                <input
                  id="prof-phone"
                  name="phone_number"
                  type="tel"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="+91 98765 43210"
                  className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label htmlFor="prof-dob" className="block text-sm font-semibold text-slate-700 mb-1">
                  Date of Birth
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Calendar className="w-4 h-4" />
                  </div>
                  <input
                    id="prof-dob"
                    name="date_of_birth"
                    type="date"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                    className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm bg-white"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="prof-lang" className="block text-sm font-semibold text-slate-700 mb-1">
                  Preferred Language
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Globe className="w-4 h-4" />
                  </div>
                  <select
                    id="prof-lang"
                    name="preferred_language"
                    value={formData.preferred_language}
                    onChange={handleChange}
                    className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-slate-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm bg-white"
                  >
                    <option value="en">English (EN)</option>
                    <option value="hi">Hindi (हिंदी)</option>
                    <option value="kn">Kannada (ಕನ್ನಡ)</option>
                    <option value="ta">Tamil (தமிழ்)</option>
                    <option value="te">Telugu (తెలుగు)</option>
                    <option value="mr">Marathi (मराठी)</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-end">
              <button
                type="submit"
                disabled={isSaving}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-700 hover:bg-primary-800 text-white font-semibold text-sm shadow-md transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-600 disabled:opacity-70 min-h-[44px]"
              >
                {isSaving ? (
                  <span>Saving Changes...</span>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>Save Profile Updates</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
