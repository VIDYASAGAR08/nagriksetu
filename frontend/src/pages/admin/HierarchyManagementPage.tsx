import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { AdministrativeUnit, User } from '../../types';
import { Badge } from '../../components/Badge';
import { Alert } from '../../components/Alert';
import {
  Layers,
  Search,
  Filter,
  Plus,
  Edit2,
  Power,
  X,
  Users,
  Home,
  Shield,
} from 'lucide-react';

export const HierarchyManagementPage: React.FC = () => {
  const [units, setUnits] = useState<AdministrativeUnit[]>([]);
  const [admins, setAdmins] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [activeTab, setActiveTab] = useState<'units' | 'scope'>('units');
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Modals state
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [scopeModalOpen, setScopeModalOpen] = useState(false);
  const [selectedUnit, setSelectedUnit] = useState<AdministrativeUnit | null>(null);
  const [selectedAdmin, setSelectedAdmin] = useState<User | null>(null);

  // Form states
  const [newUnit, setNewUnit] = useState({
    identifier: '',
    name: '',
    unit_type: 'district',
    parent_id: '',
    status: 'active',
  });

  const [editForm, setEditForm] = useState({
    name: '',
    parent_id: '',
    status: 'active',
  });

  const [scopeAssignUnitId, setScopeAssignUnitId] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [unitsData, adminsData] = await Promise.all([
        api.hierarchy.list({
          search: searchQuery || undefined,
          unit_type: typeFilter || undefined,
          status: statusFilter || undefined,
          page_size: 100,
        }),
        api.admin.listAdmins(),
      ]);
      setUnits(unitsData.items);
      setAdmins(adminsData);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to load administrative hierarchy.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [typeFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.hierarchy.create({
        identifier: newUnit.identifier.trim().toUpperCase(),
        name: newUnit.name.trim(),
        unit_type: newUnit.unit_type,
        parent_id: newUnit.parent_id ? parseInt(newUnit.parent_id) : null,
        status: newUnit.status,
      });
      setCreateModalOpen(false);
      setNewUnit({
        identifier: '',
        name: '',
        unit_type: 'district',
        parent_id: '',
        status: 'active',
      });
      setAlert({ type: 'success', message: 'Administrative unit created successfully (FR-ADM-001).' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to create unit.' });
    }
  };

  const openEditModal = (unit: AdministrativeUnit) => {
    setSelectedUnit(unit);
    setEditForm({
      name: unit.name,
      parent_id: unit.parent_id ? String(unit.parent_id) : '',
      status: unit.status,
    });
    setEditModalOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUnit) return;
    try {
      await api.hierarchy.update(selectedUnit.id, {
        name: editForm.name.trim(),
        parent_id: editForm.parent_id ? parseInt(editForm.parent_id) : null,
        status: editForm.status,
      });
      setEditModalOpen(false);
      setSelectedUnit(null);
      setAlert({ type: 'success', message: 'Administrative unit updated successfully (FR-ADM-004).' });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to update unit.' });
    }
  };

  const handleToggleStatus = async (unit: AdministrativeUnit) => {
    const nextStatus = unit.status === 'active' ? 'inactive' : 'active';
    try {
      await api.hierarchy.update(unit.id, { status: nextStatus });
      setAlert({
        type: 'success',
        message: `Unit ${unit.identifier} status changed to ${nextStatus}. Historical links preserved (FR-ADM-004).`,
      });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to change unit status.' });
    }
  };

  const openScopeModal = (adminUser: User) => {
    setSelectedAdmin(adminUser);
    setScopeAssignUnitId(adminUser.administrative_unit_id ? String(adminUser.administrative_unit_id) : '');
    setScopeModalOpen(true);
  };

  const handleScopeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAdmin) return;
    try {
      const res = await api.admin.assignScope(
        selectedAdmin.id,
        scopeAssignUnitId ? parseInt(scopeAssignUnitId) : null
      );
      setScopeModalOpen(false);
      setSelectedAdmin(null);
      setAlert({
        type: 'success',
        message: `Scope successfully updated for ${selectedAdmin.email}: ${res.administrative_unit_name || 'National (All Areas)'} (FR-ADM-021).`,
      });
      loadData();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to assign scope.' });
    }
  };

  const unitTypeLabels: Record<string, string> = {
    country: 'Country (Level 0)',
    state: 'State (Level 1)',
    district: 'District (Level 2)',
    sub_district: 'Sub-District / Taluk (Level 3)',
    ward: 'Urban Ward (Level 4)',
    village: 'Rural Village (Level 4)',
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-6 rounded-lg border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
              Module 3.1 & 3.4
            </span>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <Layers className="h-6 w-6 text-emerald-700" />
              Administrative Hierarchy & User Scope
            </h1>
          </div>
          <p className="text-sm text-slate-600 mt-1">
            Maintain jurisdictional units, parental links, circular validation (FR-ADM-001–005), and manage admin scoped access (FR-ADM-021–022).
          </p>
        </div>
        <div className="flex gap-2">
          {activeTab === 'units' && (
            <button
              onClick={() => setCreateModalOpen(true)}
              className="inline-flex items-center px-4 py-2 bg-emerald-700 text-white rounded-md text-sm font-medium hover:bg-emerald-800 shadow-sm transition"
            >
              <Plus className="h-4 w-4 mr-1.5" />
              New Hierarchy Unit
            </button>
          )}
        </div>
      </div>

      {alert && (
        <Alert
          type={alert.type}
          message={alert.message}
          onClose={() => setAlert(null)}
        />
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-200 bg-white px-6 rounded-t-lg">
        <button
          onClick={() => setActiveTab('units')}
          className={`py-3 px-4 font-semibold text-sm border-b-2 transition flex items-center gap-2 ${
            activeTab === 'units'
              ? 'border-emerald-700 text-emerald-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Layers className="h-4 w-4" />
          Jurisdictional Units ({units.length})
        </button>
        <button
          onClick={() => setActiveTab('scope')}
          className={`py-3 px-4 font-semibold text-sm border-b-2 transition flex items-center gap-2 ${
            activeTab === 'scope'
              ? 'border-emerald-700 text-emerald-800'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Shield className="h-4 w-4" />
          Administrator Area Scope ({admins.length})
        </button>
      </div>

      {activeTab === 'units' ? (
        <>
          {/* Filters & Search */}
          <div className="bg-white p-4 rounded-b-lg border border-slate-200 shadow-sm flex flex-col md:flex-row gap-4 justify-between items-center -mt-6">
            <form onSubmit={handleSearchSubmit} className="flex-1 w-full flex gap-2">
              <div className="relative flex-1">
                <Search className="h-4 w-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search unit by code or name (e.g., IN-KA, Bengaluru)..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-slate-800 text-white rounded-md text-sm hover:bg-slate-900 transition"
              >
                Search
              </button>
            </form>

            <div className="flex gap-3 w-full md:w-auto">
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-slate-500" />
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="border border-slate-300 rounded-md py-2 px-3 text-sm focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
                >
                  <option value="">All Unit Types</option>
                  <option value="country">Country</option>
                  <option value="state">State</option>
                  <option value="district">District</option>
                  <option value="sub_district">Sub-District</option>
                  <option value="ward">Ward</option>
                  <option value="village">Village</option>
                </select>
              </div>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="border border-slate-300 rounded-md py-2 px-3 text-sm focus:ring-2 focus:ring-emerald-600 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>

          {/* Units Table */}
          <div className="bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
            {loading ? (
              <div className="p-8 text-center text-slate-500">Loading administrative hierarchy...</div>
            ) : units.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                No administrative units found matching your search.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50 text-slate-700 text-xs uppercase tracking-wider font-semibold">
                    <tr>
                      <th className="px-6 py-3 text-left">Unit Code</th>
                      <th className="px-6 py-3 text-left">Name & Level</th>
                      <th className="px-6 py-3 text-left">Parent Unit</th>
                      <th className="px-6 py-3 text-left">Sub-Units</th>
                      <th className="px-6 py-3 text-left">Citizens / Households</th>
                      <th className="px-6 py-3 text-left">Status</th>
                      <th className="px-6 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 text-sm">
                    {units.map((unit) => (
                      <tr key={unit.id} className="hover:bg-slate-50/70 transition">
                        <td className="px-6 py-4 whitespace-nowrap font-mono font-medium text-emerald-800">
                          {unit.identifier}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-semibold text-slate-900">{unit.name}</div>
                          <div className="text-xs text-slate-500">
                            {unitTypeLabels[unit.unit_type] || unit.unit_type}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-slate-600">
                          {unit.parent_name ? (
                            <div className="flex items-center text-xs">
                              <span className="font-medium text-slate-800">{unit.parent_name}</span>
                              <span className="text-slate-400 ml-1">({unit.parent_identifier})</span>
                            </div>
                          ) : (
                            <span className="text-xs text-slate-400 italic">None (Top Level)</span>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-slate-100 text-slate-700">
                            {unit.children_count} child unit{unit.children_count === 1 ? '' : 's'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-3 text-xs text-slate-600">
                            <span className="flex items-center gap-1">
                              <Users className="h-3.5 w-3.5 text-blue-600" />
                              {unit.citizens_count}
                            </span>
                            <span className="flex items-center gap-1">
                              <Home className="h-3.5 w-3.5 text-amber-600" />
                              {unit.households_count}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <Badge status={unit.status} />
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right space-x-2">
                          <button
                            onClick={() => openEditModal(unit)}
                            className="p-1.5 text-slate-600 hover:text-emerald-700 hover:bg-slate-100 rounded transition"
                            title="Edit Unit Details"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleToggleStatus(unit)}
                            className={`p-1.5 rounded transition ${
                              unit.status === 'active'
                                ? 'text-amber-600 hover:text-amber-800 hover:bg-amber-50'
                                : 'text-emerald-600 hover:text-emerald-800 hover:bg-emerald-50'
                            }`}
                            title={unit.status === 'active' ? 'Deactivate Unit' : 'Activate Unit'}
                          >
                            <Power className="h-4 w-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : (
        /* Administrator Scope Mapping (FR-ADM-021 & FR-ADM-022) */
        <div className="bg-white rounded-b-lg border border-slate-200 shadow-sm p-6 -mt-6 space-y-6">
          <div className="border-l-4 border-emerald-600 pl-4 py-1 bg-emerald-50/50 rounded-r">
            <h3 className="text-base font-bold text-slate-900">
              Role & Area Scope Enforcement (FR-ADM-021 / FR-ADM-022)
            </h3>
            <p className="text-xs text-slate-600 mt-0.5">
              Administrators assigned to an administrative unit are strictly constrained to view and manage citizens, households, and sub-units within that hierarchy branch. Administrators with no assigned unit possess National/Unrestricted authority.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200">
              <thead className="bg-slate-50 text-slate-700 text-xs uppercase tracking-wider font-semibold">
                <tr>
                  <th className="px-6 py-3 text-left">Admin Email</th>
                  <th className="px-6 py-3 text-left">Assigned Jurisdiction / Scope</th>
                  <th className="px-6 py-3 text-left">Scope Level</th>
                  <th className="px-6 py-3 text-left">Account Status</th>
                  <th className="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 text-sm">
                {admins.map((admin) => (
                  <tr key={admin.id} className="hover:bg-slate-50/70 transition">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-semibold text-slate-900">{admin.email}</div>
                      <div className="text-xs text-slate-500">ID: #{admin.id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {admin.administrative_unit_name ? (
                        <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                          <Layers className="h-3 w-3 mr-1" />
                          {admin.administrative_unit_name}
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300">
                          <Shield className="h-3 w-3 mr-1" />
                          National (All Areas)
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-600">
                      {admin.administrative_unit_id ? 'Hierarchically Scoped' : 'Global Jurisdiction'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge status={admin.account_status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button
                        onClick={() => openScopeModal(admin)}
                        className="px-3 py-1.5 bg-slate-100 hover:bg-emerald-50 text-emerald-800 hover:text-emerald-900 border border-slate-300 rounded text-xs font-semibold transition"
                      >
                        Reassign Scope
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CREATE UNIT MODAL (FR-ADM-001) */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Plus className="h-5 w-5 text-emerald-700" />
                Create Administrative Unit (FR-ADM-001)
              </h3>
              <button
                onClick={() => setCreateModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-sm">
              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Unique Unit Identifier *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., IN-KA-BLR-W150"
                  value={newUnit.identifier}
                  onChange={(e) => setNewUnit({ ...newUnit, identifier: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 font-mono uppercase focus:ring-2 focus:ring-emerald-600"
                />
                <span className="text-xs text-slate-500">Standardized official jurisdiction code</span>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Official Unit Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Ward 150 - Bellandur"
                  value={newUnit.name}
                  onChange={(e) => setNewUnit({ ...newUnit, name: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Administrative Level / Type *
                </label>
                <select
                  value={newUnit.unit_type}
                  onChange={(e) => setNewUnit({ ...newUnit, unit_type: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                >
                  <option value="country">Country</option>
                  <option value="state">State</option>
                  <option value="district">District</option>
                  <option value="sub_district">Sub-District / Taluk</option>
                  <option value="ward">Urban Ward</option>
                  <option value="village">Rural Village</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Parent Unit (Hierarchy Link)
                </label>
                <select
                  value={newUnit.parent_id}
                  onChange={(e) => setNewUnit({ ...newUnit, parent_id: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                >
                  <option value="">None (Top Level National Entity)</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.identifier} - {u.unit_type})
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-700 text-white rounded font-medium hover:bg-emerald-800"
                >
                  Create Unit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT UNIT MODAL (FR-ADM-003, FR-ADM-004) */}
      {editModalOpen && selectedUnit && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Edit2 className="h-5 w-5 text-emerald-700" />
                Edit Unit: {selectedUnit.identifier}
              </h3>
              <button
                onClick={() => setEditModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleEditSubmit} className="space-y-4 text-sm">
              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Unit Name *
                </label>
                <input
                  type="text"
                  required
                  value={editForm.name}
                  onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Parent Unit (Circular Validation Enforced)
                </label>
                <select
                  value={editForm.parent_id}
                  onChange={(e) => setEditForm({ ...editForm, parent_id: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                >
                  <option value="">None (Top Level)</option>
                  {units
                    .filter((u) => u.id !== selectedUnit.id)
                    .map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.name} ({u.identifier} - {u.unit_type})
                      </option>
                    ))}
                </select>
                <span className="text-xs text-slate-500">
                  FR-ADM-003: System automatically rejects invalid parents and circular links.
                </span>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Operational Status (FR-ADM-004)
                </label>
                <select
                  value={editForm.status}
                  onChange={(e) => setEditForm({ ...editForm, status: e.target.value })}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                >
                  <option value="active">Active</option>
                  <option value="inactive">Inactive</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setEditModalOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-700 text-white rounded font-medium hover:bg-emerald-800"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* REASSIGN SCOPE MODAL (FR-ADM-021) */}
      {scopeModalOpen && selectedAdmin && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6 space-y-4">
            <div className="flex justify-between items-center border-b pb-3">
              <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
                <Shield className="h-5 w-5 text-emerald-700" />
                Assign Admin Area Scope (FR-ADM-021)
              </h3>
              <button
                onClick={() => setScopeModalOpen(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleScopeSubmit} className="space-y-4 text-sm">
              <div className="bg-slate-50 p-3 rounded border text-xs text-slate-600">
                Configuring access scope for: <strong>{selectedAdmin.email}</strong>
              </div>

              <div>
                <label className="block font-medium text-slate-700 mb-1">
                  Jurisdictional Administrative Unit
                </label>
                <select
                  value={scopeAssignUnitId}
                  onChange={(e) => setScopeAssignUnitId(e.target.value)}
                  className="w-full border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-600"
                >
                  <option value="">National / Unrestricted Access (No Boundary Limit)</option>
                  {units.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.name} ({u.identifier} - {u.unit_type})
                    </option>
                  ))}
                </select>
                <span className="text-xs text-slate-500 mt-1 block">
                  Selecting a unit restricts this administrator to operations solely within this unit and its child hierarchy (FR-ADM-022).
                </span>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t">
                <button
                  type="button"
                  onClick={() => setScopeModalOpen(false)}
                  className="px-4 py-2 border border-slate-300 rounded text-slate-700 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-700 text-white rounded font-medium hover:bg-emerald-800"
                >
                  Assign Scope
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
