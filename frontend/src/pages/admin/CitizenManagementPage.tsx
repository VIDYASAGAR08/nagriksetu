import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { CitizenProfile, Household, AdministrativeUnit } from '../../types';
import { Badge } from '../../components/Badge';
import { Alert } from '../../components/Alert';
import { ConfirmModal } from '../../components/ConfirmModal';
import {
  Users,
  Search,
  Filter,
  Plus,
  Edit2,
  Trash2,
  X,
  Layers,
} from 'lucide-react';

export const CitizenManagementPage: React.FC = () => {
  const [citizens, setCitizens] = useState<CitizenProfile[]>([]);
  const [households, setHouseholds] = useState<Household[]>([]);
  const [units, setUnits] = useState<AdministrativeUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Modals state
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [selectedCitizen, setSelectedCitizen] = useState<CitizenProfile | null>(null);

  // Form states
  const [newCitizen, setNewCitizen] = useState({
    full_name: '',
    email: '',
    initial_password: '',
    phone_number: '',
    preferred_language: 'en',
    profile_status: 'pending_review',
    household_id: '',
    household_relationship: '',
    administrative_unit_id: '',
  });

  const [editForm, setEditForm] = useState({
    full_name: '',
    phone_number: '',
    preferred_language: 'en',
    profile_status: 'pending_review',
    date_of_birth: '',
    household_id: '',
    household_relationship: '',
    administrative_unit_id: '',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [citizensData, householdsData, unitsData] = await Promise.all([
        api.admin.listCitizens(searchQuery || undefined, statusFilter || undefined),
        api.admin.listHouseholds(),
        api.hierarchy.list({ page_size: 100 }),
      ]);
      setCitizens(citizensData);
      setHouseholds(householdsData);
      setUnits(unitsData.items);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to load citizens.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.admin.createCitizen({
        ...newCitizen,
        email: newCitizen.email.trim() || undefined,
        household_id: newCitizen.household_id ? parseInt(newCitizen.household_id) : undefined,
        administrative_unit_id: newCitizen.administrative_unit_id ? parseInt(newCitizen.administrative_unit_id) : undefined,
      });
      setCreateModalOpen(false);
      setNewCitizen({
        full_name: '',
        email: '',
        initial_password: '',
        phone_number: '',
        preferred_language: 'en',
        profile_status: 'pending_review',
        household_id: '',
        household_relationship: '',
        administrative_unit_id: '',
      });
      setAlert({ type: 'success', message: 'Citizen profile created successfully.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to create citizen profile.' });
    }
  };

  const openEditModal = (citizen: CitizenProfile) => {
    setSelectedCitizen(citizen);
    setEditForm({
      full_name: citizen.full_name,
      phone_number: citizen.phone_number || '',
      preferred_language: citizen.preferred_language,
      profile_status: citizen.profile_status,
      date_of_birth: citizen.date_of_birth || '',
      household_id: citizen.household_id ? String(citizen.household_id) : '',
      household_relationship: citizen.household_relationship || '',
      administrative_unit_id: citizen.administrative_unit_id ? String(citizen.administrative_unit_id) : '',
    });
    setEditModalOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCitizen) return;

    try {
      await api.admin.updateCitizen(selectedCitizen.id, {
        full_name: editForm.full_name,
        phone_number: editForm.phone_number || undefined,
        preferred_language: editForm.preferred_language,
        profile_status: editForm.profile_status,
        date_of_birth: editForm.date_of_birth || undefined,
        household_id: editForm.household_id ? parseInt(editForm.household_id) : null,
        household_relationship: editForm.household_relationship || null,
        administrative_unit_id: editForm.administrative_unit_id ? parseInt(editForm.administrative_unit_id) : null,
      });
      setEditModalOpen(false);
      setAlert({ type: 'success', message: 'Citizen profile updated successfully.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to update citizen profile.' });
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedCitizen) return;
    try {
      await api.admin.deleteCitizen(selectedCitizen.id);
      setDeleteModalOpen(false);
      setSelectedCitizen(null);
      setAlert({ type: 'success', message: 'Citizen profile record deleted successfully.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to delete citizen.' });
    }
  };

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Users className="w-6 h-6 text-primary-700" />
            <span>Citizen Management</span>
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Search, review, provision accounts, and manage official citizen profiles.
          </p>
        </div>
        <button
          onClick={() => setCreateModalOpen(true)}
          type="button"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary-700 hover:bg-primary-800 text-white font-semibold text-sm shadow transition-all focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Citizen</span>
        </button>
      </div>

      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col md:flex-row items-center justify-between gap-4">
        <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by legal name, citizen code, or phone number..."
              aria-label="Search citizen records"
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-slate-900 hover:bg-black text-white text-sm font-semibold rounded-lg"
          >
            Search
          </button>
        </form>

        <div className="flex items-center gap-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <label htmlFor="status-filter" className="sr-only">Filter by profile status</label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm bg-white text-slate-800 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="pending_review">Pending Review</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Citizens Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-sm text-slate-500">Loading citizen records...</div>
        ) : citizens.length === 0 ? (
          <div className="p-12 text-center">
            <Users className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-sm font-bold text-slate-700">No citizen records found</p>
            <p className="text-xs text-slate-500 mt-1">Try adjusting your search criteria or add a new record.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-xs font-semibold text-slate-500 bg-slate-50">
                  <th scope="col" className="p-3.5">Citizen Code</th>
                  <th scope="col" className="p-3.5">Full Legal Name</th>
                  <th scope="col" className="p-3.5">Status</th>
                  <th scope="col" className="p-3.5">Completeness (FR-ADM-013)</th>
                  <th scope="col" className="p-3.5">Jurisdiction Area</th>
                  <th scope="col" className="p-3.5">Contact Phone</th>
                  <th scope="col" className="p-3.5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {citizens.map((citizen) => (
                  <tr key={citizen.id} className="hover:bg-slate-50/80">
                    <td className="p-3.5 font-mono text-xs font-bold text-primary-700">
                      {citizen.citizen_code}
                    </td>
                    <td className="p-3.5 font-semibold text-slate-900">
                      {citizen.full_name}
                    </td>
                    <td className="p-3.5">
                      <Badge status={citizen.profile_status} />
                    </td>
                    <td className="p-3.5">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-slate-200 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-2 rounded-full ${
                              (citizen.completeness_score ?? 100) === 100
                                ? 'bg-emerald-600'
                                : (citizen.completeness_score ?? 100) >= 60
                                ? 'bg-amber-500'
                                : 'bg-rose-500'
                            }`}
                            style={{ width: `${citizen.completeness_score ?? 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-bold text-slate-700 font-mono">
                          {citizen.completeness_score ?? 100}%
                        </span>
                      </div>
                      {citizen.missing_fields && citizen.missing_fields.length > 0 && (
                        <span className="text-[10px] text-slate-400 block truncate max-w-xs" title={`Missing: ${citizen.missing_fields.join(', ')}`}>
                          Missing: {citizen.missing_fields.join(', ')}
                        </span>
                      )}
                    </td>
                    <td className="p-3.5 text-xs text-slate-600">
                      {citizen.administrative_unit_name ? (
                        <span className="inline-flex items-center gap-1 text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-medium">
                          <Layers className="w-3 h-3 text-emerald-600" />
                          {citizen.administrative_unit_name}
                        </span>
                      ) : (
                        <span className="text-slate-400 italic">Unassigned</span>
                      )}
                    </td>
                    <td className="p-3.5 text-slate-600 font-mono text-xs">
                      {citizen.phone_number || '—'}
                    </td>
                    <td className="p-3.5 text-right space-x-2">
                      <button
                        onClick={() => openEditModal(citizen)}
                        type="button"
                        aria-label={`Edit ${citizen.full_name}`}
                        className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => {
                          setSelectedCitizen(citizen);
                          setDeleteModalOpen(true);
                        }}
                        type="button"
                        aria-label={`Delete ${citizen.full_name}`}
                        className="p-1.5 rounded-lg border border-rose-200 hover:bg-rose-50 text-rose-600 focus:outline-none focus:ring-2 focus:ring-rose-500"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal: Create Citizen */}
      {createModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="create-modal-title"
        >
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h2 id="create-modal-title" className="text-base font-bold text-slate-900">
                Register New Citizen Profile
              </h2>
              <button
                onClick={() => setCreateModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Legal Name *
                </label>
                <input
                  type="text"
                  required
                  value={newCitizen.full_name}
                  onChange={(e) => setNewCitizen({ ...newCitizen, full_name: e.target.value })}
                  placeholder="e.g. Suresh Nair"
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Email Account (Optional)
                  </label>
                  <input
                    type="email"
                    value={newCitizen.email}
                    onChange={(e) => setNewCitizen({ ...newCitizen, email: e.target.value })}
                    placeholder="user@example.com"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Initial Password
                  </label>
                  <input
                    type="password"
                    value={newCitizen.initial_password}
                    onChange={(e) => setNewCitizen({ ...newCitizen, initial_password: e.target.value })}
                    placeholder="Default: Welcome123!@"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    value={newCitizen.phone_number}
                    onChange={(e) => setNewCitizen({ ...newCitizen, phone_number: e.target.value })}
                    placeholder="+91 98765 00000"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Status
                  </label>
                  <select
                    value={newCitizen.profile_status}
                    onChange={(e) => setNewCitizen({ ...newCitizen, profile_status: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  >
                    <option value="pending_review">Pending Review</option>
                    <option value="active">Active</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Assign to Household (Optional)
                </label>
                <select
                  value={newCitizen.household_id}
                  onChange={(e) => setNewCitizen({ ...newCitizen, household_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                >
                  <option value="">None / Unassigned</option>
                  {households.map((hh) => (
                    <option key={hh.id} value={hh.id}>
                      {hh.household_code} - {hh.address_line}, {hh.city}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Jurisdiction Area (Administrative Unit Mapping)
                </label>
                <select
                  value={newCitizen.administrative_unit_id}
                  onChange={(e) => setNewCitizen({ ...newCitizen, administrative_unit_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                >
                  <option value="">None / Unassigned</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.identifier} - {u.unit_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-semibold text-white bg-primary-700 hover:bg-primary-800 rounded-lg shadow"
                >
                  Create Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Edit Citizen */}
      {editModalOpen && selectedCitizen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
          aria-labelledby="edit-modal-title"
        >
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h2 id="edit-modal-title" className="text-base font-bold text-slate-900">
                Edit Profile: {selectedCitizen.citizen_code}
              </h2>
              <button
                onClick={() => setEditModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
                aria-label="Close dialog"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Legal Name *
                </label>
                <input
                  type="text"
                  required
                  value={editForm.full_name}
                  onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Contact Phone
                  </label>
                  <input
                    type="tel"
                    value={editForm.phone_number}
                    onChange={(e) => setEditForm({ ...editForm, phone_number: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Administrative Review Status *
                  </label>
                  <select
                    value={editForm.profile_status}
                    onChange={(e) => setEditForm({ ...editForm, profile_status: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  >
                    <option value="pending_review">Pending Review</option>
                    <option value="active">Active</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Language
                  </label>
                  <select
                    value={editForm.preferred_language}
                    onChange={(e) => setEditForm({ ...editForm, preferred_language: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  >
                    <option value="en">English (EN)</option>
                    <option value="hi">Hindi (हिंदी)</option>
                    <option value="kn">Kannada (ಕನ್ನಡ)</option>
                    <option value="ta">Tamil (தமிழ்)</option>
                    <option value="te">Telugu (తెలుగు)</option>
                    <option value="mr">Marathi (मराठी)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Household Role
                  </label>
                  <input
                    type="text"
                    value={editForm.household_relationship}
                    onChange={(e) => setEditForm({ ...editForm, household_relationship: e.target.value })}
                    placeholder="e.g. Head of Household"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Assigned Household
                </label>
                <select
                  value={editForm.household_id}
                  onChange={(e) => setEditForm({ ...editForm, household_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                >
                  <option value="">None / Unassigned</option>
                  {households.map((hh) => (
                    <option key={hh.id} value={hh.id}>
                      {hh.household_code} - {hh.address_line}, {hh.city}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Jurisdiction Area (Administrative Unit Mapping)
                </label>
                <select
                  value={editForm.administrative_unit_id}
                  onChange={(e) => setEditForm({ ...editForm, administrative_unit_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500 focus:outline-none"
                >
                  <option value="">None / Unassigned</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.identifier} - {u.unit_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-semibold text-white bg-primary-700 hover:bg-primary-800 rounded-lg shadow"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Accessible Confirmation Modal: Delete Citizen */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        title="Delete Citizen Profile"
        message={`Are you sure you want to permanently delete profile for "${selectedCitizen?.full_name}" (${selectedCitizen?.citizen_code})? This action will unlink their household membership and cannot be undone.`}
        confirmLabel="Yes, Delete Profile"
        isDestructive={true}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setDeleteModalOpen(false);
          setSelectedCitizen(null);
        }}
      />
    </div>
  );
};
