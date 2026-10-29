import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { Household, CitizenProfile, AdministrativeUnit, HouseholdMembership } from '../../types';
import { Alert } from '../../components/Alert';
import { ConfirmModal } from '../../components/ConfirmModal';
import {
  Building,
  Search,
  Plus,
  Edit2,
  Trash2,
  Users,
  UserPlus,
  UserMinus,
  X,
  FileText,
  AlertTriangle,
  Layers,
  History,
} from 'lucide-react';

export const HouseholdManagementPage: React.FC = () => {
  const [households, setHouseholds] = useState<Household[]>([]);
  const [citizens, setCitizens] = useState<CitizenProfile[]>([]);
  const [units, setUnits] = useState<AdministrativeUnit[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Modals state
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [selectedHousehold, setSelectedHousehold] = useState<Household | null>(null);
  const [memberships, setMemberships] = useState<HouseholdMembership[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Forms state
  const [newHousehold, setNewHousehold] = useState({
    household_code: '',
    address_line: '',
    locality: '',
    city: '',
    state: '',
    postal_code: '',
    administrative_notes: '',
    administrative_unit_id: '',
  });

  const [editHouseholdForm, setEditHouseholdForm] = useState({
    address_line: '',
    locality: '',
    city: '',
    state: '',
    postal_code: '',
    administrative_notes: '',
    administrative_unit_id: '',
  });

  const [assignForm, setAssignForm] = useState({
    citizen_id: '',
    household_relationship: 'Member',
  });

  const loadData = async () => {
    setLoading(true);
    try {
      const [hhs, cits, unitsData] = await Promise.all([
        api.admin.listHouseholds(searchQuery || undefined),
        api.admin.listCitizens(),
        api.hierarchy.list({ page_size: 100 }),
      ]);
      setHouseholds(hhs);
      setCitizens(cits);
      setUnits(unitsData.items);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to load household records.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.admin.createHousehold({
        ...newHousehold,
        household_code: newHousehold.household_code.trim() || undefined,
        administrative_unit_id: newHousehold.administrative_unit_id ? parseInt(newHousehold.administrative_unit_id) : undefined,
      });
      setCreateModalOpen(false);
      setNewHousehold({
        household_code: '',
        address_line: '',
        locality: '',
        city: '',
        state: '',
        postal_code: '',
        administrative_notes: '',
        administrative_unit_id: '',
      });
      setAlert({ type: 'success', message: 'Household record created successfully (FR-ADM-014).' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to create household.' });
    }
  };

  const openEditModal = (hh: Household) => {
    setSelectedHousehold(hh);
    setEditHouseholdForm({
      address_line: hh.address_line,
      locality: hh.locality,
      city: hh.city,
      state: hh.state,
      postal_code: hh.postal_code,
      administrative_notes: hh.administrative_notes || '',
      administrative_unit_id: hh.administrative_unit_id ? String(hh.administrative_unit_id) : '',
    });
    setEditModalOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHousehold) return;

    try {
      await api.admin.updateHousehold(selectedHousehold.id, {
        ...editHouseholdForm,
        administrative_unit_id: editHouseholdForm.administrative_unit_id ? parseInt(editHouseholdForm.administrative_unit_id) : null,
      });
      setEditModalOpen(false);
      setAlert({ type: 'success', message: 'Household updated successfully.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to update household.' });
    }
  };

  const openHistoryModal = async (hh: Household) => {
    setSelectedHousehold(hh);
    setLoadingHistory(true);
    setHistoryModalOpen(true);
    try {
      const historyData = await api.admin.getHouseholdMemberships(hh.id);
      setMemberships(historyData);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to load membership history.' });
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedHousehold) return;
    try {
      await api.admin.deleteHousehold(selectedHousehold.id);
      setDeleteModalOpen(false);
      setSelectedHousehold(null);
      setAlert({ type: 'success', message: 'Household deleted successfully.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to delete household.' });
    }
  };

  const handleAssignSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHousehold || !assignForm.citizen_id) return;

    try {
      await api.admin.assignMember(
        selectedHousehold.id,
        parseInt(assignForm.citizen_id),
        assignForm.household_relationship
      );
      setAssignModalOpen(false);
      setAssignForm({ citizen_id: '', household_relationship: 'Member' });
      setAlert({ type: 'success', message: 'Citizen assigned to household successfully.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to assign citizen.' });
    }
  };

  const handleUnassignMember = async (householdId: number, citizenId: number) => {
    try {
      await api.admin.unassignMember(householdId, citizenId);
      setAlert({ type: 'success', message: 'Member unassigned from household.' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to unassign member.' });
    }
  };

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <Building className="w-6 h-6 text-primary-700" />
            <span>Household Management</span>
          </h1>
          <p className="text-sm text-slate-600 mt-1">
            Maintain municipal dwelling addresses, assign family members, and manage internal notes.
          </p>
        </div>
        <button
          onClick={() => setCreateModalOpen(true)}
          type="button"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary-700 hover:bg-primary-800 text-white font-semibold text-sm shadow transition-all focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <Plus className="w-4 h-4" />
          <span>Add New Household</span>
        </button>
      </div>

      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {/* Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center gap-2">
        <form onSubmit={handleSearchSubmit} className="flex-1 flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by household code, address, locality, or city..."
              aria-label="Search household records"
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
      </div>

      {/* Household Cards Grid */}
      {loading ? (
        <div className="p-12 text-center text-sm text-slate-500">Loading household records...</div>
      ) : households.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-slate-300 p-12 text-center">
          <Building className="w-10 h-10 text-slate-300 mx-auto mb-2" />
          <p className="text-sm font-bold text-slate-700">No households registered</p>
          <p className="text-xs text-slate-500 mt-1">Create your first municipal household dwelling.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {households.map((hh) => (
            <div
              key={hh.id}
              className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-mono text-xs font-bold text-primary-700 bg-primary-50 px-2.5 py-1 rounded-md border border-primary-200">
                        {hh.household_code}
                      </span>
                      {hh.administrative_unit_name && (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                          <Layers className="w-3 h-3 text-emerald-600" />
                          {hh.administrative_unit_name}
                        </span>
                      )}
                    </div>
                    <h2 className="text-base font-bold text-slate-900 mt-2 leading-tight">
                      {hh.address_line}
                    </h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {hh.locality}, {hh.city}, {hh.state} - {hh.postal_code}
                    </p>
                  </div>
                  <div className="flex items-center gap-1.5 flex-shrink-0">
                    <button
                      onClick={() => openEditModal(hh)}
                      aria-label="Edit household"
                      className="p-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => {
                        setSelectedHousehold(hh);
                        setDeleteModalOpen(true);
                      }}
                      aria-label="Delete household"
                      className="p-1.5 rounded-lg border border-rose-200 hover:bg-rose-50 text-rose-600"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Duplicate Household Warning (FR-ADM-020) */}
                {hh.duplicate_warning && (
                  <div className="my-2 p-2.5 bg-amber-50 rounded-lg border border-amber-300 text-xs text-amber-900 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Duplicate Warning (FR-ADM-020):</span> Matches existing household(s):{' '}
                      <span className="font-mono font-semibold">{hh.matching_households?.join(', ')}</span>
                    </div>
                  </div>
                )}

                {/* Consistency Flags (FR-ADM-019) */}
                {hh.consistency_flags && hh.consistency_flags.length > 0 && (
                  <div className="my-2 p-2.5 bg-rose-50 rounded-lg border border-rose-200 text-xs text-rose-900 flex items-start gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Consistency Review (FR-ADM-019):</span>
                      <ul className="list-disc pl-4 mt-1 space-y-0.5">
                        {hh.consistency_flags.map((flag, idx) => (
                          <li key={idx}>{flag.replace(/_/g, ' ')}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Admin Notes */}
                {hh.administrative_notes && (
                  <div className="my-3 p-2.5 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-700 flex items-start gap-2">
                    <FileText className="w-4 h-4 text-slate-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold">Admin Notes:</span> {hh.administrative_notes}
                    </div>
                  </div>
                )}

                {/* Member Summary */}
                <div className="mt-4 pt-4 border-t border-slate-100">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-slate-700 flex items-center gap-1">
                      <Users className="w-3.5 h-3.5 text-slate-500" />
                      <span>Registered Members ({hh.members.length})</span>
                    </span>
                    <div className="flex items-center gap-3">
                      <button
                        onClick={() => openHistoryModal(hh)}
                        type="button"
                        className="text-xs font-semibold text-slate-600 hover:text-slate-900 flex items-center gap-1 focus:outline-none"
                        title="View Membership History Log (FR-ADM-016)"
                      >
                        <History className="w-3.5 h-3.5 text-slate-500" />
                        <span>History Log</span>
                      </button>
                      <button
                        onClick={() => {
                          setSelectedHousehold(hh);
                          setAssignModalOpen(true);
                        }}
                        type="button"
                        className="text-xs font-semibold text-primary-700 hover:text-primary-800 flex items-center gap-1 focus:outline-none"
                      >
                        <UserPlus className="w-3.5 h-3.5" />
                        <span>Assign Member</span>
                      </button>
                    </div>
                  </div>

                  {hh.members.length === 0 ? (
                    <p className="text-xs text-slate-400 italic">No citizens currently assigned.</p>
                  ) : (
                    <div className="space-y-1.5">
                      {hh.members.map((member) => (
                        <div
                          key={member.id}
                          className="flex items-center justify-between p-2 rounded-lg bg-slate-50 text-xs"
                        >
                          <div>
                            <span className="font-semibold text-slate-900">{member.full_name}</span>
                            <span className="text-slate-500 ml-1.5">({member.household_relationship || 'Member'})</span>
                          </div>
                          <button
                            onClick={() => handleUnassignMember(hh.id, member.id)}
                            type="button"
                            title="Unassign citizen from household"
                            className="p-1 text-slate-400 hover:text-rose-600 rounded"
                          >
                            <UserMinus className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal: Create Household */}
      {createModalOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h2 className="text-base font-bold text-slate-900">Add New Household Record</h2>
              <button
                onClick={() => setCreateModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Household Code (Optional, Auto-generated if blank)
                </label>
                <input
                  type="text"
                  value={newHousehold.household_code}
                  onChange={(e) => setNewHousehold({ ...newHousehold, household_code: e.target.value })}
                  placeholder="e.g. HHD-2026-DEL"
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Address Line *
                </label>
                <input
                  type="text"
                  required
                  value={newHousehold.address_line}
                  onChange={(e) => setNewHousehold({ ...newHousehold, address_line: e.target.value })}
                  placeholder="House/Flat No, Building Name, Street"
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Locality / Ward *
                  </label>
                  <input
                    type="text"
                    required
                    value={newHousehold.locality}
                    onChange={(e) => setNewHousehold({ ...newHousehold, locality: e.target.value })}
                    placeholder="e.g. Ward 45, Sector 9"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    City *
                  </label>
                  <input
                    type="text"
                    required
                    value={newHousehold.city}
                    onChange={(e) => setNewHousehold({ ...newHousehold, city: e.target.value })}
                    placeholder="e.g. Bengaluru"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    State / Province *
                  </label>
                  <input
                    type="text"
                    required
                    value={newHousehold.state}
                    onChange={(e) => setNewHousehold({ ...newHousehold, state: e.target.value })}
                    placeholder="e.g. Karnataka"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Postal Code *
                  </label>
                  <input
                    type="text"
                    required
                    value={newHousehold.postal_code}
                    onChange={(e) => setNewHousehold({ ...newHousehold, postal_code: e.target.value })}
                    placeholder="e.g. 560001"
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Jurisdiction Area (Administrative Unit Mapping)
                </label>
                <select
                  value={newHousehold.administrative_unit_id}
                  onChange={(e) => setNewHousehold({ ...newHousehold, administrative_unit_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">None / Unassigned</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.identifier} - {u.unit_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Administrative Notes (Admin-only viewable)
                </label>
                <textarea
                  rows={2}
                  value={newHousehold.administrative_notes}
                  onChange={(e) => setNewHousehold({ ...newHousehold, administrative_notes: e.target.value })}
                  placeholder="Official observations, census records, inspection notes..."
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                />
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
                  Create Household
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Edit Household */}
      {editModalOpen && selectedHousehold && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h2 className="text-base font-bold text-slate-900">
                Edit Household: {selectedHousehold.household_code}
              </h2>
              <button
                onClick={() => setEditModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Address Line
                </label>
                <input
                  type="text"
                  required
                  value={editHouseholdForm.address_line}
                  onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, address_line: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Locality / Ward
                  </label>
                  <input
                    type="text"
                    required
                    value={editHouseholdForm.locality}
                    onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, locality: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    City
                  </label>
                  <input
                    type="text"
                    required
                    value={editHouseholdForm.city}
                    onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, city: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    State
                  </label>
                  <input
                    type="text"
                    required
                    value={editHouseholdForm.state}
                    onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, state: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Postal Code
                  </label>
                  <input
                    type="text"
                    required
                    value={editHouseholdForm.postal_code}
                    onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, postal_code: e.target.value })}
                    className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Jurisdiction Area (Administrative Unit Mapping)
                </label>
                <select
                  value={editHouseholdForm.administrative_unit_id}
                  onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, administrative_unit_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">None / Unassigned</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.identifier} - {u.unit_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Administrative Notes
                </label>
                <textarea
                  rows={2}
                  value={editHouseholdForm.administrative_notes}
                  onChange={(e) => setEditHouseholdForm({ ...editHouseholdForm, administrative_notes: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                />
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
                  Save Updates
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Assign Member */}
      {assignModalOpen && selectedHousehold && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <h2 className="text-base font-bold text-slate-900">
                Assign Citizen to {selectedHousehold.household_code}
              </h2>
              <button
                onClick={() => setAssignModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAssignSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Select Citizen Profile *
                </label>
                <select
                  required
                  value={assignForm.citizen_id}
                  onChange={(e) => setAssignForm({ ...assignForm, citizen_id: e.target.value })}
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm bg-white focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">-- Choose citizen --</option>
                  {citizens.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.citizen_code} - {c.full_name} {c.household_id ? '(Assigned)' : '(Unassigned)'}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Relationship in Household
                </label>
                <input
                  type="text"
                  required
                  value={assignForm.household_relationship}
                  onChange={(e) => setAssignForm({ ...assignForm, household_relationship: e.target.value })}
                  placeholder="e.g. Head of Household, Spouse, Child, Dependent"
                  className="w-full p-2.5 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setAssignModalOpen(false)}
                  className="px-4 py-2 text-sm text-slate-700 border border-slate-300 rounded-lg hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 text-sm font-semibold text-white bg-primary-700 hover:bg-primary-800 rounded-lg shadow"
                >
                  Confirm Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal: Membership History Log (FR-ADM-016) */}
      {historyModalOpen && selectedHousehold && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm"
          role="dialog"
          aria-modal="true"
        >
          <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div>
                <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
                  <History className="w-5 h-5 text-emerald-700" />
                  <span>Membership Audit History: {selectedHousehold.household_code}</span>
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  FR-ADM-016: Historical record of all citizen additions, relationship changes, and terminated memberships.
                </p>
              </div>
              <button
                onClick={() => setHistoryModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {loadingHistory ? (
                <div className="p-8 text-center text-sm text-slate-500">Loading historical records...</div>
              ) : memberships.length === 0 ? (
                <div className="p-8 text-center text-xs text-slate-500">
                  No membership history records found for this household.
                </div>
              ) : (
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 font-semibold text-slate-600 bg-slate-50">
                      <th className="p-2.5">Citizen</th>
                      <th className="p-2.5">Relationship</th>
                      <th className="p-2.5">Duration</th>
                      <th className="p-2.5">Status</th>
                      <th className="p-2.5">Notes</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {memberships.map((m) => (
                      <tr key={m.id} className="hover:bg-slate-50/70">
                        <td className="p-2.5">
                          <div className="font-semibold text-slate-900">{m.citizen_name}</div>
                          <div className="font-mono text-[10px] text-primary-700">{m.citizen_code}</div>
                        </td>
                        <td className="p-2.5 font-medium text-slate-700">{m.relationship_type}</td>
                        <td className="p-2.5 text-slate-600 font-mono text-[11px]">
                          {m.start_date} to {m.end_date || 'Present'}
                        </td>
                        <td className="p-2.5">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                              m.status === 'active'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-slate-100 text-slate-600'
                            }`}
                          >
                            {m.status}
                          </span>
                        </td>
                        <td className="p-2.5 text-slate-500">{m.notes || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            <div className="px-6 py-3 bg-slate-50 border-t border-slate-100 flex justify-end">
              <button
                type="button"
                onClick={() => setHistoryModalOpen(false)}
                className="px-4 py-2 text-sm text-slate-700 border border-slate-300 rounded-lg hover:bg-white"
              >
                Close History
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      <ConfirmModal
        isOpen={deleteModalOpen}
        title="Delete Household Record"
        message={`Are you sure you want to delete household ${selectedHousehold?.household_code}? Any associated citizens will be safely unassigned from this dwelling.`}
        confirmLabel="Yes, Delete Household"
        isDestructive={true}
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setDeleteModalOpen(false);
          setSelectedHousehold(null);
        }}
      />
    </div>
  );
};
