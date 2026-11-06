import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { HouseholdDossier, FamilyMemberDossier, MedicalRecord, EducationRecord, HouseholdLinkRequest } from '../../types';
import { Alert } from '../../components/Alert';
import { OTPChallengeModal } from '../../components/OTPChallengeModal';
import {
  Home,
  Users,
  MapPin,
  ShieldCheck,
  HeartPulse,
  GraduationCap,
  LandPlot,
  Lock,
  Unlock,
  Edit3,
  PlusCircle,
  CheckCircle2,
  Building,
  Phone,
  Globe,
  X,
  Hospital,
  Crown,
  GitBranch,
  ListChecks,
  UserCheck,
  CreditCard,
  Receipt,
  Sparkles,
  ChevronRight,
  ArrowRight,
  Clock,
} from 'lucide-react';

export const CitizenHouseholdPage: React.FC = () => {
  const [dossier, setDossier] = useState<HouseholdDossier | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Active Tab
  const [activeTab, setActiveTab] = useState<'members' | 'tree' | 'menu' | 'medical' | 'education' | 'land'>('members');

  // Member Link Requests States
  const [linkRequests, setLinkRequests] = useState<HouseholdLinkRequest[]>([]);
  const [linkMemberModalOpen, setLinkMemberModalOpen] = useState(false);
  const [isSubmittingLink, setIsSubmittingLink] = useState(false);
  const [linkForm, setLinkForm] = useState({
    target_citizen_code: '',
    relationship: 'Son',
    household_role: 'MEMBER',
    assigned_tasks: ['can_manage_medical'] as string[],
  });

  // Simulated Civic Tax Payment State
  const [taxPaidNotice, setTaxPaidNotice] = useState<string | null>(null);

  // Confidential View Toggles (Protection against open display as required by teacher)
  const [revealMedical, setRevealMedical] = useState(false);
  const [revealEducation, setRevealEducation] = useState(false);
  const [revealLand, setRevealLand] = useState(false);

  // Modal & OTP States
  const [otpModalOpen, setOtpModalOpen] = useState(false);
  const [otpPurpose, setOtpPurpose] = useState<string>('FAMILY_MEMBER_UPDATE');
  const [pendingAction, setPendingAction] = useState<(() => Promise<void>) | null>(null);

  // Edit Family Member State
  const [editMemberModalOpen, setEditMemberModalOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<FamilyMemberDossier | null>(null);
  const [memberForm, setMemberForm] = useState({
    phone_number: '',
    preferred_language: 'en',
  });

  // Edit Medical Record State
  const [editMedicalModalOpen, setEditMedicalModalOpen] = useState(false);
  const [medicalForm, setMedicalForm] = useState<Partial<MedicalRecord>>({});
  const [medicalTargetMemberId, setMedicalTargetMemberId] = useState<number | null>(null);

  // Edit Education Record State
  const [editEducationModalOpen, setEditEducationModalOpen] = useState(false);
  const [educationForm, setEducationForm] = useState<Partial<EducationRecord>>({});
  const [educationTargetMemberId, setEducationTargetMemberId] = useState<number | null>(null);

  // Add Land Record State
  const [addLandModalOpen, setAddLandModalOpen] = useState(false);
  const [landForm, setLandForm] = useState({
    survey_number: '',
    land_type: 'Agricultural',
    area_measurement: '',
    patta_passbook_number: '',
    district_sub_registrar: '',
    property_tax_status: 'Cleared',
    market_valuation_inr: 0,
  });

  const fetchLinkRequests = async () => {
    try {
      const data = await api.household.getMyHouseholdLinkRequests();
      setLinkRequests(data);
    } catch (e) {
      console.warn('Could not fetch household link requests', e);
    }
  };

  const fetchDossier = async () => {
    try {
      setLoading(true);
      const data = await api.household.getMyDossier();
      setDossier(data);
      fetchLinkRequests();
    } catch (err: any) {
      setErrorMessage(err.message || 'Unable to retrieve complete household dossier.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitLinkRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    if (!linkForm.target_citizen_code.trim()) {
      setErrorMessage('Please provide the Citizen Code or Phone Number of the family member to link.');
      return;
    }

    if (!linkForm.relationship.trim()) {
      setErrorMessage('Please specify the exact family relationship.');
      return;
    }

    setIsSubmittingLink(true);
    try {
      const res = await api.household.submitMemberLinkRequest({
        target_citizen_code: linkForm.target_citizen_code.trim(),
        relationship: linkForm.relationship.trim(),
        household_role: linkForm.household_role,
        assigned_tasks: linkForm.assigned_tasks,
      });
      setSuccessMessage(
        `Linkage request for ${res.target_citizen_name} (${res.relationship}) submitted successfully! Awaiting administrative verification.`
      );
      setLinkMemberModalOpen(false);
      setLinkForm({
        target_citizen_code: '',
        relationship: 'Son',
        household_role: 'MEMBER',
        assigned_tasks: ['can_manage_medical'],
      });
      fetchLinkRequests();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to submit member linkage request.');
    } finally {
      setIsSubmittingLink(false);
    }
  };

  const toggleTaskInLinkForm = (taskCode: string) => {
    setLinkForm((prev) => {
      const exists = prev.assigned_tasks.includes(taskCode);
      return {
        ...prev,
        assigned_tasks: exists
          ? prev.assigned_tasks.filter((t) => t !== taskCode)
          : [...prev.assigned_tasks, taskCode],
      };
    });
  };

  useEffect(() => {
    fetchDossier();
  }, []);

  // 1. FAMILY MEMBER UPDATE HANDLERS
  const openEditMember = (member: FamilyMemberDossier) => {
    setSelectedMember(member);
    setMemberForm({
      phone_number: member.phone_number || '',
      preferred_language: member.preferred_language || 'en',
    });
    setEditMemberModalOpen(true);
  };

  const handleRequestMemberSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMember) return;
    setOtpPurpose('FAMILY_MEMBER_UPDATE');
    setPendingAction(() => async (otpRefId?: string) => {
      await api.citizen.updateFamilyMemberProfile(selectedMember.id, {
        phone_number: memberForm.phone_number.trim() || undefined,
        preferred_language: memberForm.preferred_language,
        otp_reference_id: otpRefId,
      });
      setSuccessMessage(`Family member "${selectedMember.full_name}" updated successfully with 2-Step OTP clearance.`);
      setEditMemberModalOpen(false);
      await fetchDossier();
    });
    setOtpModalOpen(true);
  };

  // 2. MEDICAL RECORD UPDATE HANDLERS
  const openEditMedical = (member: FamilyMemberDossier) => {
    setMedicalTargetMemberId(member.id);
    setSelectedMember(member);
    setMedicalForm({
      blood_group: member.medical_record?.blood_group || 'O+',
      chronic_conditions: member.medical_record?.chronic_conditions || '',
      allergies: member.medical_record?.allergies || '',
      vaccination_status: member.medical_record?.vaccination_status || 'Fully Vaccinated',
      disability_status: member.medical_record?.disability_status || 'None',
      abha_id: member.medical_record?.abha_id || '',
      emergency_hospital: member.medical_record?.emergency_hospital || '',
      emergency_contact_name: member.medical_record?.emergency_contact_name || '',
      emergency_contact_phone: member.medical_record?.emergency_contact_phone || '',
    });
    setEditMedicalModalOpen(true);
  };

  const handleRequestMedicalSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!medicalTargetMemberId) return;
    setOtpPurpose('HEALTH_RECORD_UPDATE');
    setPendingAction(() => async (otpRefId?: string) => {
      await api.citizen.updateMedicalRecord(medicalTargetMemberId, {
        ...medicalForm,
        otp_reference_id: otpRefId,
      });
      setSuccessMessage('Confidential health dossier updated successfully with 2-Step OTP clearance.');
      setEditMedicalModalOpen(false);
      await fetchDossier();
    });
    setOtpModalOpen(true);
  };

  // 3. EDUCATION RECORD UPDATE HANDLERS
  const openEditEducation = (member: FamilyMemberDossier) => {
    setEducationTargetMemberId(member.id);
    setSelectedMember(member);
    setEducationForm({
      highest_qualification: member.education_record?.highest_qualification || 'Bachelor of Technology',
      institution_name: member.education_record?.institution_name || '',
      specialization: member.education_record?.specialization || '',
      year_of_completion: member.education_record?.year_of_completion || 2020,
      literacy_status: member.education_record?.literacy_status || 'Literate',
      certificate_number: member.education_record?.certificate_number || '',
    });
    setEditEducationModalOpen(true);
  };

  const handleRequestEducationSave = (e: React.FormEvent) => {
    e.preventDefault();
    if (!educationTargetMemberId) return;
    setOtpPurpose('EDUCATION_RECORD_UPDATE');
    setPendingAction(() => async (otpRefId?: string) => {
      await api.citizen.updateEducationRecord(educationTargetMemberId, {
        ...educationForm,
        otp_reference_id: otpRefId,
      });
      setSuccessMessage('Confidential academic records updated successfully with 2-Step OTP clearance.');
      setEditEducationModalOpen(false);
      await fetchDossier();
    });
    setOtpModalOpen(true);
  };

  // 4. LAND RECORD REGISTRATION HANDLERS
  const handleAddLandRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!landForm.survey_number.trim()) {
      setErrorMessage('Survey/Khasra number is mandatory.');
      return;
    }
    try {
      await api.household.addLandRecord({
        survey_number: landForm.survey_number.trim(),
        land_type: landForm.land_type,
        area_measurement: landForm.area_measurement.trim() || '1 Acre',
        patta_passbook_number: landForm.patta_passbook_number.trim() || undefined,
        district_sub_registrar: landForm.district_sub_registrar.trim() || undefined,
        property_tax_status: landForm.property_tax_status,
        market_valuation_inr: Number(landForm.market_valuation_inr) || 0,
      });
      setSuccessMessage('New land asset parcel registered under household records.');
      setAddLandModalOpen(false);
      setLandForm({
        survey_number: '',
        land_type: 'Agricultural',
        area_measurement: '',
        patta_passbook_number: '',
        district_sub_registrar: '',
        property_tax_status: 'Cleared',
        market_valuation_inr: 0,
      });
      await fetchDossier();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to register land parcel.');
    }
  };

  // OTP verified callback execution
  const handleOtpVerified = async (otpReferenceId: string) => {
    if (pendingAction) {
      try {
        await (pendingAction as any)(otpReferenceId);
      } catch (err: any) {
        setErrorMessage(err.message || 'Operation failed after OTP verification.');
      } finally {
        setPendingAction(null);
      }
    }
  };

  if (loading) {
    return (
      <div id="main-content" className="py-16 text-center" role="status">
        <div className="w-12 h-12 border-4 border-navy-200 border-t-navy-900 rounded-full animate-spin mx-auto mb-4" />
        <span className="text-sm font-bold text-slate-700">Loading Official Household & Family Dossier...</span>
      </div>
    );
  }

  const selfMember = dossier?.family_members.find((m) => m.is_self);
  const selfRole = selfMember?.household_role || (selfMember?.household_relationship === 'Head of Household' ? 'HEAD' : 'MEMBER');
  const selfTasks = selfMember?.assigned_tasks || [];
  const isHead = selfRole === 'HEAD' || selfMember?.household_relationship === 'Head of Household';
  const canManageMembers = isHead || selfRole === 'DEPUTY' || selfTasks.includes('can_manage_members');
  const canManageAssets = isHead || selfRole === 'DEPUTY' || selfTasks.includes('can_manage_assets');
  const canManageMedical = isHead || selfRole === 'DEPUTY' || selfTasks.includes('can_manage_medical');
  const canManageEducation = isHead || selfRole === 'DEPUTY' || selfTasks.includes('can_manage_education');
  const canPayTaxes = isHead || selfRole === 'DEPUTY' || selfTasks.includes('can_pay_taxes');

  // Generational Categorization for Family Tree (वंश-वृक्ष)
  const gen1Members = dossier ? dossier.family_members.filter((m) => {
    const rel = (m.household_relationship || '').toLowerCase();
    return rel.includes('grand') || rel.includes('elder') || rel.includes('दादा') || rel.includes('दादी') || rel.includes('नाना') || rel.includes('नानी');
  }) : [];

  const gen2Members = dossier ? dossier.family_members.filter((m) => {
    const rel = (m.household_relationship || '').toLowerCase();
    if (gen1Members.some((g) => g.id === m.id)) return false;
    return (
      rel.includes('head') ||
      rel.includes('spouse') ||
      rel.includes('wife') ||
      rel.includes('husband') ||
      rel.includes('brother') ||
      rel.includes('sister') ||
      rel.includes('पति') ||
      rel.includes('पत्नी') ||
      rel.includes('भाई') ||
      rel.includes('बहन') ||
      rel.includes('मुखिया') ||
      m.is_self
    );
  }) : [];

  const gen3Members = dossier ? dossier.family_members.filter((m) => {
    const rel = (m.household_relationship || '').toLowerCase();
    if (gen1Members.some((g) => g.id === m.id) || gen2Members.some((g) => g.id === m.id)) return false;
    return (
      rel.includes('son') ||
      rel.includes('daughter') ||
      rel.includes('child') ||
      rel.includes('पुत्र') ||
      rel.includes('पुत्री') ||
      rel.includes('बच्चा')
    );
  }) : [];

  const otherMembers = dossier ? dossier.family_members.filter((m) => {
    return (
      !gen1Members.some((g) => g.id === m.id) &&
      !gen2Members.some((g) => g.id === m.id) &&
      !gen3Members.some((g) => g.id === m.id)
    );
  }) : [];

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-saffron-600 mb-1">
            <Building className="w-4 h-4" />
            <span>National Household Administrative Registry</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-navy-950 tracking-tight">
            Household Dossier & Family Records
          </h1>
          <p className="text-sm font-medium text-slate-600 mt-1">
            Access dwelling details, verified family relationships, confidential health ABHA records, education credentials, and land assets.
          </p>
        </div>

        {dossier && (
          <div className="px-4 py-2.5 rounded-2xl bg-navy-900 text-white shadow-md flex items-center gap-3">
            <Home className="w-5 h-5 text-saffron-400" />
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-300 block">Household Code</span>
              <span className="text-sm font-mono font-bold text-white">{dossier.household_code}</span>
            </div>
          </div>
        )}
      </div>

      {errorMessage && (
        <Alert
          type="error"
          message={errorMessage}
          onClose={() => setErrorMessage(null)}
        />
      )}

      {successMessage && (
        <Alert
          type="success"
          message={successMessage}
          onClose={() => setSuccessMessage(null)}
        />
      )}

      {!dossier ? (
        <div className="bg-white border-2 border-dashed border-slate-300 rounded-3xl p-12 text-center">
          <Home className="w-12 h-12 text-slate-400 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-slate-800">No Household Record Linked</h2>
          <p className="text-sm text-slate-600 max-w-md mx-auto mt-2">
            You are not currently assigned to a verified household residence. When an administrative officer reviews and associates your citizen code with an official dwelling, records will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* DWELLING DETAILS CARD */}
          <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
            <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-2xl bg-emerald-50 text-emerald-800 border border-emerald-200">
                  <MapPin className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-navy-950">Registered Dwelling Address</h2>
                  <span className="text-xs text-slate-500 font-medium">Verified by Department of Revenue & Municipal Records</span>
                </div>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                Active Residence
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 sm:col-span-2">
                <span className="text-[11px] text-slate-500 font-bold uppercase tracking-wider block mb-1">Address Line</span>
                <span className="font-semibold text-slate-900">{dossier.address_line}</span>
              </div>
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                <span className="text-[11px] text-slate-500 font-bold uppercase tracking-wider block mb-1">Locality / Sector</span>
                <span className="font-semibold text-slate-900">{dossier.locality}</span>
              </div>
              <div className="p-3.5 bg-slate-50 rounded-2xl border border-slate-100">
                <span className="text-[11px] text-slate-500 font-bold uppercase tracking-wider block mb-1">City, State & PIN</span>
                <span className="font-semibold text-slate-900">{dossier.city}, {dossier.state} — {dossier.postal_code}</span>
              </div>
            </div>
          </div>

          {/* CONFIDENTIAL DOSSIER SELECTIVE DRAWER TABS */}
          <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-1">
            <button
              type="button"
              onClick={() => setActiveTab('members')}
              className={`py-3 px-5 rounded-2xl font-bold text-xs transition flex items-center gap-2 ${
                activeTab === 'members'
                  ? 'bg-navy-900 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:text-navy-900 border border-slate-200'
              }`}
            >
              <Users className="w-4 h-4 text-saffron-400" />
              <span>Family Members ({dossier.members_count})</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('tree')}
              className={`py-3 px-5 rounded-2xl font-bold text-xs transition flex items-center gap-2 ${
                activeTab === 'tree'
                  ? 'bg-navy-900 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:text-navy-900 border border-slate-200'
              }`}
            >
              <GitBranch className="w-4 h-4 text-emerald-400" />
              <span>Family Tree (वंश-वृक्ष)</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('menu')}
              className={`py-3 px-5 rounded-2xl font-bold text-xs transition flex items-center gap-2 ${
                activeTab === 'menu'
                  ? 'bg-navy-900 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:text-navy-900 border border-slate-200'
              }`}
            >
              <ListChecks className="w-4 h-4 text-amber-400" />
              <span>Roles & Civic Actions</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('medical')}
              className={`py-3 px-5 rounded-2xl font-bold text-xs transition flex items-center gap-2 ${
                activeTab === 'medical'
                  ? 'bg-navy-900 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:text-navy-900 border border-slate-200'
              }`}
            >
              <HeartPulse className="w-4 h-4 text-rose-500" />
              <span>Confidential Health & ABHA</span>
              {!revealMedical && <Lock className="w-3.5 h-3.5 text-slate-400 ml-1" />}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('education')}
              className={`py-3 px-5 rounded-2xl font-bold text-xs transition flex items-center gap-2 ${
                activeTab === 'education'
                  ? 'bg-navy-900 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:text-navy-900 border border-slate-200'
              }`}
            >
              <GraduationCap className="w-4 h-4 text-blue-500" />
              <span>Education & DigiLocker</span>
              {!revealEducation && <Lock className="w-3.5 h-3.5 text-slate-400 ml-1" />}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('land')}
              className={`py-3 px-5 rounded-2xl font-bold text-xs transition flex items-center gap-2 ${
                activeTab === 'land'
                  ? 'bg-navy-900 text-white shadow-md'
                  : 'bg-white text-slate-600 hover:text-navy-900 border border-slate-200'
              }`}
            >
              <LandPlot className="w-4 h-4 text-emerald-600" />
              <span>Land & Property ({dossier.land_records?.length || 0})</span>
              {!revealLand && <Lock className="w-3.5 h-3.5 text-slate-400 ml-1" />}
            </button>
          </div>

          {/* TAB 1: FAMILY MEMBERS & PERMITTED MUTATION */}
          {activeTab === 'members' && (
            <div className="space-y-6">
              {/* Header Bar with Link Member Action */}
              <div className="bg-white border border-slate-200 rounded-3xl p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="font-bold text-base text-navy-950 flex items-center gap-2">
                    <Users className="w-5 h-5 text-saffron-600" />
                    <span>Registered Family Members ({dossier.members_count})</span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Family members linked to dwelling <strong className="font-mono">{dossier.household_code}</strong> with user-specified relationships.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={() => setLinkMemberModalOpen(true)}
                  disabled={!canManageMembers}
                  className={`py-2.5 px-4 rounded-xl text-xs font-bold transition flex items-center justify-center gap-2 ${
                    canManageMembers
                      ? 'bg-saffron-600 hover:bg-saffron-500 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200'
                  }`}
                  title={!canManageMembers ? 'Only Household Head or authorized members can link new family members' : 'Request to link family member'}
                >
                  <PlusCircle className="w-4 h-4" />
                  <span>+ Request Member Linkage</span>
                </button>
              </div>

              {/* Pending Member Linkage Requests Notice */}
              {linkRequests.length > 0 && (
                <div className="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-3xl p-5 shadow-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-amber-950 flex items-center gap-2">
                      <Clock className="w-4 h-4 text-amber-600 animate-pulse" />
                      Pending Family Member Linkage Requests ({linkRequests.filter((r) => r.status === 'pending_admin_approval').length})
                    </span>
                    <span className="text-[11px] font-semibold text-amber-800 bg-amber-100/80 px-2.5 py-0.5 rounded-full border border-amber-300">
                      Awaiting Administrator Activation
                    </span>
                  </div>
                  <p className="text-xs text-amber-900/90 leading-relaxed">
                    Under civic regulations, relationships and tasks are chosen by the citizen. The municipal administrator acts strictly as an activation gate to approve or reject the request.
                  </p>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
                    {linkRequests.map((req) => (
                      <div key={req.id} className="bg-white/90 border border-amber-200 rounded-2xl p-3 text-xs space-y-1.5 shadow-xs">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900">{req.target_citizen_name}</span>
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            req.status === 'pending_admin_approval'
                              ? 'bg-amber-100 text-amber-900 border border-amber-300'
                              : req.status === 'approved'
                              ? 'bg-emerald-100 text-emerald-900'
                              : 'bg-rose-100 text-rose-900'
                          }`}>
                            {req.status === 'pending_admin_approval' ? 'Pending Approval' : req.status === 'approved' ? 'Approved' : 'Rejected'}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-[11px] text-slate-600">
                          <span>Relation: <strong className="text-amber-950">{req.relationship}</strong></span>
                          <span>•</span>
                          <span>Role: <strong className="text-navy-950">{req.household_role}</strong></span>
                        </div>
                        {req.assigned_tasks && req.assigned_tasks.length > 0 && (
                          <div className="flex flex-wrap gap-1 pt-1">
                            {req.assigned_tasks.map((t) => (
                              <span key={t} className="text-[9px] font-bold bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">
                                {t.replace('can_manage_', '').replace('can_', '')}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Privacy Notice */}
              <div className="bg-saffron-50/70 border border-saffron-200 rounded-2xl p-4 flex items-start gap-3 text-xs text-saffron-950">
                <ShieldCheck className="w-5 h-5 text-saffron-700 flex-shrink-0 mt-0.5" />
                <div>
                  <span className="font-bold">Household Privacy & Mutation Protocol:</span> Citizens can edit permitted secondary fields (Phone Number & Preferred Language) of registered members in their own household. Any mutation requires an instant <strong>2-Step OTP clearance</strong>. Outside or unrelated parties are cryptographically prohibited (`403 Forbidden`).
                </div>
              </div>

              {/* Members Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dossier.family_members.map((member) => (
                  <div
                    key={member.id}
                    className={`bg-white border rounded-3xl p-5 shadow-sm transition hover:shadow-md flex flex-col justify-between ${
                      member.is_self ? 'border-navy-300 ring-2 ring-navy-100' : 'border-slate-200'
                    }`}
                  >
                    <div>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-2xl bg-navy-950 text-white flex items-center justify-center font-bold text-sm shadow-xs">
                            {member.full_name.charAt(0)}
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <h3 className="font-bold text-base text-navy-950">{member.full_name}</h3>
                              {member.is_self && (
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-navy-900 text-saffron-400">
                                  You
                                </span>
                              )}
                            </div>
                            <span className="text-xs font-mono font-bold text-saffron-700">
                              {member.citizen_code}
                            </span>
                          </div>
                        </div>

                        <div className="flex flex-col items-end gap-1">
                          <span className="px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-800 border border-slate-200">
                            {member.household_relationship || 'Member'}
                          </span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                            (member.household_role === 'HEAD' || member.household_relationship === 'Head of Household')
                              ? 'bg-amber-100 text-amber-900 border border-amber-300'
                              : member.household_role === 'DEPUTY'
                              ? 'bg-indigo-100 text-indigo-900'
                              : member.household_role === 'DEPENDENT'
                              ? 'bg-slate-100 text-slate-600'
                              : 'bg-emerald-100 text-emerald-900'
                          }`}>
                            {(member.household_role === 'HEAD' || member.household_relationship === 'Head of Household')
                              ? '👑 Head of Household'
                              : member.household_role === 'DEPUTY'
                              ? '🛡️ Deputy Custodian'
                              : member.household_role === 'DEPENDENT'
                              ? '👶 Dependent / Minor'
                              : '👤 Adult Member'}
                          </span>
                        </div>
                      </div>

                      {/* Assigned Tasks Tags */}
                      {member.assigned_tasks && member.assigned_tasks.length > 0 && (
                        <div className="mt-3 pt-2.5 border-t border-slate-100">
                          <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block mb-1">
                            Assigned Civic Tasks:
                          </span>
                          <div className="flex flex-wrap gap-1">
                            {member.assigned_tasks.map((task) => (
                              <span key={task} className="text-[10px] font-bold bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md border border-slate-200/80">
                                {task === 'can_manage_assets' ? '📜 Land Assets' : task === 'can_manage_medical' ? '🏥 Health ABHA' : task === 'can_manage_education' ? '🎓 DigiLocker' : task === 'can_manage_members' ? '👨‍👩‍👦 Link Members' : task === 'can_pay_taxes' ? '💳 Taxes' : task}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      <div className="mt-3 pt-2.5 border-t border-slate-100 grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-slate-400 font-medium block">Phone Contact</span>
                          <span className="font-bold text-slate-800">{member.phone_number || 'Not Registered'}</span>
                        </div>
                        <div>
                          <span className="text-slate-400 font-medium block">Language</span>
                          <span className="font-bold text-slate-800 uppercase">{member.preferred_language}</span>
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[11px] text-slate-500 font-medium">
                        {member.is_self ? 'Your primary profile' : 'Family member record'}
                      </span>
                      <button
                        type="button"
                        onClick={() => openEditMember(member)}
                        className="py-1.5 px-3 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-navy-950 transition flex items-center gap-1.5"
                      >
                        <Edit3 className="w-3.5 h-3.5 text-navy-700" />
                        <span>Edit Info (OTP Guarded)</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 2: VISUAL FAMILY TREE HIERARCHY (वंश-वृक्ष) */}
          {activeTab === 'tree' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-emerald-900 to-navy-950 rounded-3xl p-6 text-white shadow-lg border border-emerald-700/40">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-saffron-400 block mb-1 flex items-center gap-1.5">
                      <GitBranch className="w-4 h-4" />
                      <span>Generational Relationship Hierarchy</span>
                    </span>
                    <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                      Household Family Tree <span className="text-saffron-400 font-normal">वंश-वृक्ष</span>
                    </h2>
                    <p className="text-xs text-slate-300 mt-1 max-w-xl">
                      Structured hierarchical visualization of family generations. Relationships and roles are explicitly specified by the citizen and officially verified.
                    </p>
                  </div>
                  <div className="px-3.5 py-2 rounded-2xl bg-white/10 border border-white/20 text-xs font-bold flex items-center gap-2">
                    <Users className="w-4 h-4 text-emerald-400" />
                    <span>{dossier.family_members.length} Enrolled Relatives</span>
                  </div>
                </div>
              </div>

              {/* GENERATIONAL TIERS */}
              <div className="space-y-8 relative before:absolute before:left-1/2 before:top-4 before:bottom-4 before:w-0.5 before:bg-slate-200 before:-translate-x-1/2 hidden sm:block" />

              <div className="space-y-8">
                {/* GENERATION 1: ELDERS & GRANDPARENTS */}
                {gen1Members.length > 0 && (
                  <div className="bg-amber-50/50 border border-amber-200/80 rounded-3xl p-5 shadow-xs space-y-4">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-amber-900 border-b border-amber-200 pb-2">
                      <Crown className="w-4 h-4 text-amber-600" />
                      <span>Generation I: Senior Elders & Grandparents (प्रथम पीढ़ी - वरिष्ठ सदस्य)</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                      {gen1Members.map((m) => (
                        <div key={m.id} className="bg-white border border-amber-300/80 rounded-2xl p-4 shadow-sm hover:shadow-md transition">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="w-11 h-11 rounded-xl bg-amber-500 text-white font-bold flex items-center justify-center text-sm shadow-xs">
                              {m.full_name.charAt(0)}
                            </div>
                            <div>
                              <h4 className="font-bold text-sm text-navy-950">{m.full_name}</h4>
                              <span className="text-[11px] font-mono text-slate-500">{m.citizen_code}</span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                            <span className="px-2.5 py-0.5 rounded-full font-bold bg-amber-100 text-amber-900 text-[11px]">
                              {m.household_relationship || 'Elder'}
                            </span>
                            <span className="text-[11px] font-semibold text-slate-600">
                              {m.household_role || 'Member'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* GENERATION 2: CORE HOUSEHOLD & SPOUSES */}
                <div className="bg-blue-50/50 border border-blue-200/80 rounded-3xl p-5 shadow-xs space-y-4">
                  <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-navy-950 border-b border-blue-200 pb-2">
                    <Home className="w-4 h-4 text-navy-700" />
                    <span>Generation II: Household Core & Spouses (द्वितीय पीढ़ी - प्रमुख व दंपत्ति)</span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {gen2Members.map((m) => (
                      <div
                        key={m.id}
                        className={`bg-white border rounded-2xl p-4 shadow-sm hover:shadow-md transition ${
                          m.is_self ? 'border-navy-400 ring-2 ring-navy-100' : 'border-blue-200'
                        }`}
                      >
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-11 h-11 rounded-xl bg-navy-900 text-saffron-400 font-bold flex items-center justify-center text-sm shadow-xs">
                            {m.full_name.charAt(0)}
                          </div>
                          <div>
                            <div className="flex items-center gap-1.5">
                              <h4 className="font-bold text-sm text-navy-950">{m.full_name}</h4>
                              {m.is_self && (
                                <span className="px-1.5 py-0.2 rounded font-bold text-[9px] bg-navy-900 text-saffron-400">
                                  You
                                </span>
                              )}
                            </div>
                            <span className="text-[11px] font-mono text-slate-500">{m.citizen_code}</span>
                          </div>
                        </div>

                        <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                          <span className="px-2.5 py-0.5 rounded-full font-bold bg-navy-100 text-navy-950 text-[11px]">
                            {m.household_relationship || 'Core'}
                          </span>
                          <span className="px-2 py-0.5 rounded font-bold text-[10px] bg-emerald-100 text-emerald-900">
                            {(m.household_role === 'HEAD' || m.household_relationship === 'Head of Household')
                              ? '👑 Head of Household'
                              : m.household_role || 'Member'}
                          </span>
                        </div>

                        {m.assigned_tasks && m.assigned_tasks.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2 pt-2 border-t border-slate-100">
                            {m.assigned_tasks.slice(0, 3).map((t) => (
                              <span key={t} className="text-[9px] font-bold bg-slate-100 text-slate-700 px-1.5 py-0.5 rounded">
                                {t.replace('can_manage_', '').replace('can_', '')}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* GENERATION 3: YOUTH & CHILDREN */}
                {gen3Members.length > 0 && (
                  <div className="bg-emerald-50/50 border border-emerald-200/80 rounded-3xl p-5 shadow-xs space-y-4">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-900 border-b border-emerald-200 pb-2">
                      <Sparkles className="w-4 h-4 text-emerald-600" />
                      <span>Generation III: Children & Youth (तृतीय पीढ़ी - संतान व युवा)</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                      {gen3Members.map((m) => (
                        <div key={m.id} className="bg-white border border-emerald-200 rounded-2xl p-4 shadow-sm hover:shadow-md transition">
                          <div className="flex items-center gap-3 mb-3">
                            <div className="w-11 h-11 rounded-xl bg-emerald-600 text-white font-bold flex items-center justify-center text-sm shadow-xs">
                              {m.full_name.charAt(0)}
                            </div>
                            <div>
                              <h4 className="font-bold text-sm text-navy-950">{m.full_name}</h4>
                              <span className="text-[11px] font-mono text-slate-500">{m.citizen_code}</span>
                            </div>
                          </div>
                          <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
                            <span className="px-2.5 py-0.5 rounded-full font-bold bg-emerald-100 text-emerald-900 text-[11px]">
                              {m.household_relationship || 'Son / Daughter'}
                            </span>
                            <span className="text-[11px] font-semibold text-slate-600">
                              {m.household_role === 'DEPENDENT' ? '👶 Dependent' : '👤 Adult Member'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* OTHER EXTENDED KIN */}
                {otherMembers.length > 0 && (
                  <div className="bg-slate-50 border border-slate-200 rounded-3xl p-5 shadow-xs space-y-4">
                    <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-700 border-b border-slate-200 pb-2">
                      <Users className="w-4 h-4 text-slate-500" />
                      <span>Extended Family Members (अन्य पारिवारिक सदस्य)</span>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                      {otherMembers.map((m) => (
                        <div key={m.id} className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
                          <h4 className="font-bold text-sm text-navy-950">{m.full_name}</h4>
                          <span className="text-[11px] font-mono text-slate-500 block">{m.citizen_code}</span>
                          <span className="mt-2 inline-block px-2.5 py-0.5 rounded-full font-bold bg-slate-100 text-slate-800 text-[11px]">
                            {m.household_relationship || 'Relative'}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 3: DISPLAY MENU & ROLES DEFINITION (भूमिका व अधिकार मेनू) */}
          {activeTab === 'menu' && (
            <div className="space-y-6">
              {/* Active Role Definition Card */}
              <div className="bg-white border border-slate-200 rounded-3xl p-6 shadow-sm">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-5 border-b border-slate-100">
                  <div className="flex items-center gap-3.5">
                    <div className="w-14 h-14 rounded-2xl bg-navy-900 text-saffron-400 flex items-center justify-center font-bold text-xl shadow-md border border-saffron-400/30">
                      {isHead ? <Crown className="w-7 h-7" /> : <ShieldCheck className="w-7 h-7" />}
                    </div>
                    <div>
                      <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400 block">
                        Your Enrolled Household Role
                      </span>
                      <h2 className="text-xl font-black text-navy-950 flex items-center gap-2">
                        <span>
                          {isHead
                            ? 'Head of Household (मुखिया)'
                            : selfRole === 'DEPUTY'
                            ? 'Deputy Custodian (सह-मुखिया)'
                            : selfRole === 'DEPENDENT'
                            ? 'Dependent / Minor (आश्रित)'
                            : 'Adult Family Member (व्यस्क सदस्य)'}
                        </span>
                      </h2>
                      <span className="text-xs font-mono font-bold text-saffron-700">
                        {selfMember?.citizen_code} • {selfMember?.full_name}
                      </span>
                    </div>
                  </div>

                  <span className={`px-3.5 py-1.5 rounded-full text-xs font-bold ${
                    isHead ? 'bg-amber-100 text-amber-900 border border-amber-300' : 'bg-emerald-100 text-emerald-900'
                  }`}>
                    {isHead ? 'Full Civic Authority' : 'Assigned Task Capabilities'}
                  </span>
                </div>

                <div className="mt-5 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">Role Authority & Civic Scope:</h4>
                  <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-2xl border border-slate-100">
                    {isHead
                      ? 'As the primary Head of Household, you hold sovereign administrative custody over this registered dwelling. You are authorized to link family members, delegate operational tasks, register immovable land parcels, and review confidential family dossiers.'
                      : selfRole === 'DEPUTY'
                      ? 'As a Deputy Custodian (सह-मुखिया), you possess delegated authority to assist the Head in managing household assets, updating family dossiers, and monitoring civic tax obligations.'
                      : selfRole === 'DEPENDENT'
                      ? 'As an enrolled dependent resident, you hold view privileges for registered household identity records. Modifications require head authorization.'
                      : 'As a verified adult family member, you are authorized to manage your personal health and education credentials, as well as any specific civic tasks assigned to your profile.'}
                  </p>
                </div>
              </div>

              {/* INTERACTIVE ACTION MATRIX */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-navy-950 flex items-center gap-2">
                  <ListChecks className="w-4 h-4 text-saffron-600" />
                  <span>Household Civic Action Menu & Task Status</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Action 1: Land Assets */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="p-2 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 inline-block">
                          <LandPlot className="w-5 h-5" />
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          canManageAssets ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'
                        }`}>
                          {canManageAssets ? 'Authorized' : 'Requires Head Authorization'}
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-navy-950">Immovable Land & Property Registry</h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Register agricultural, commercial, or residential parcels under the official household code.
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => setActiveTab('land')}
                        className="py-1.5 px-3 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-navy-950 transition"
                      >
                        View Land Records
                      </button>
                      {canManageAssets && (
                        <button
                          type="button"
                          onClick={() => setAddLandModalOpen(true)}
                          className="py-1.5 px-3 rounded-xl text-xs font-bold bg-emerald-700 hover:bg-emerald-800 text-white transition flex items-center gap-1 shadow-xs"
                        >
                          <PlusCircle className="w-3.5 h-3.5" />
                          <span>+ Add Land Parcel</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Action 2: Member Linkage */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="p-2 rounded-xl bg-saffron-50 text-saffron-700 border border-saffron-200 inline-block">
                          <UserCheck className="w-5 h-5" />
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          canManageMembers ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'
                        }`}>
                          {canManageMembers ? 'Authorized' : 'Requires Head Authorization'}
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-navy-950">Family Member Linkage & Delegation</h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Request to link a family member with user-specified relationship, role, and task delegation.
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2">
                      <button
                        type="button"
                        disabled={!canManageMembers}
                        onClick={() => setLinkMemberModalOpen(true)}
                        className={`py-1.5 px-3 rounded-xl text-xs font-bold transition flex items-center gap-1 ${
                          canManageMembers
                            ? 'bg-saffron-600 hover:bg-saffron-500 text-white shadow-xs'
                            : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                        }`}
                      >
                        <PlusCircle className="w-3.5 h-3.5" />
                        <span>Request Member Linkage</span>
                      </button>
                    </div>
                  </div>

                  {/* Action 3: Health & ABHA */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="p-2 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 inline-block">
                          <HeartPulse className="w-5 h-5" />
                        </span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800">
                          {canManageMedical ? 'Authorized (Confidential)' : 'Self-Only'}
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-navy-950">Ayushman ABHA Health Dossier</h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Inspect confidential blood group, chronic conditions, and emergency hospitals protected by drawer encryption.
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveTab('medical');
                          setRevealMedical(true);
                        }}
                        className="py-1.5 px-3 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white transition flex items-center gap-1 shadow-xs"
                      >
                        <span>Open Health Drawer</span>
                        <ChevronRight className="w-3.5 h-3.5 text-saffron-400" />
                      </button>
                    </div>
                  </div>

                  {/* Action 4: Education & DigiLocker */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="p-2 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 inline-block">
                          <GraduationCap className="w-5 h-5" />
                        </span>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800">
                          {canManageEducation ? 'Authorized' : 'Self-Only'}
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-navy-950">DigiLocker Educational Credentials</h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Inspect certified university degrees, literacy status, and completion credentials of household residents.
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100 flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveTab('education');
                          setRevealEducation(true);
                        }}
                        className="py-1.5 px-3 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white transition flex items-center gap-1 shadow-xs"
                      >
                        <span>Open Education Drawer</span>
                        <ChevronRight className="w-3.5 h-3.5 text-saffron-400" />
                      </button>
                    </div>
                  </div>

                  {/* Action 5: Civic Property Taxes */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-xs flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="p-2 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 inline-block">
                          <CreditCard className="w-5 h-5" />
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                          canPayTaxes ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-100 text-slate-500'
                        }`}>
                          {canPayTaxes ? 'Authorized' : 'Requires Authorization'}
                        </span>
                      </div>
                      <h4 className="font-bold text-sm text-navy-950">Municipal Property Tax & Civic Dues</h4>
                      <p className="text-xs text-slate-500 mt-1">
                        Verify municipal clearance for household dwelling {dossier.household_code} and generate digital tax token.
                      </p>
                    </div>

                    <div className="mt-4 pt-3 border-t border-slate-100">
                      {taxPaidNotice ? (
                        <div className="p-2 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 font-bold flex items-center gap-1.5">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          <span>{taxPaidNotice}</span>
                        </div>
                      ) : (
                        <button
                          type="button"
                          disabled={!canPayTaxes}
                          onClick={() => setTaxPaidNotice(`Tax Assessment #TX-${Math.floor(100000 + Math.random() * 900000)} Cleared Successfully!`)}
                          className={`py-1.5 px-3 rounded-xl text-xs font-bold transition flex items-center gap-1 ${
                            canPayTaxes
                              ? 'bg-blue-700 hover:bg-blue-800 text-white shadow-xs'
                              : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                          }`}
                        >
                          <Receipt className="w-3.5 h-3.5" />
                          <span>Pay Civic Assessment</span>
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: CONFIDENTIAL HEALTH & AYUSHMAN ABHA DOSSIER */}
          {activeTab === 'medical' && (
            <div className="space-y-4">
              {/* Privacy Wall / Lock Control */}
              <div className="bg-white border border-rose-200 rounded-3xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="p-3 rounded-2xl bg-rose-50 text-rose-700 border border-rose-200">
                    <HeartPulse className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-black text-base text-navy-950">Ayushman Bharat Digital Health Dossier</h3>
                    <p className="text-xs text-slate-600 mt-1 max-w-xl">
                      As mandated by the National Health Authority (NHA), personal medical histories and ABHA IDs are protected behind confidential viewing drawers.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setRevealMedical(!revealMedical)}
                  className={`py-2.5 px-5 rounded-2xl font-bold text-xs transition flex items-center justify-center gap-2 ${
                    revealMedical
                      ? 'bg-slate-200 text-slate-800 hover:bg-slate-300'
                      : 'bg-rose-600 hover:bg-rose-700 text-white shadow-md'
                  }`}
                >
                  {revealMedical ? (
                    <>
                      <Lock className="w-4 h-4" />
                      <span>Conceal Confidential Health Records</span>
                    </>
                  ) : (
                    <>
                      <Unlock className="w-4 h-4" />
                      <span>Unlock & View Family Health Dossier</span>
                    </>
                  )}
                </button>
              </div>

              {!revealMedical ? (
                <div className="bg-slate-50 border border-dashed border-slate-300 rounded-3xl p-10 text-center">
                  <Lock className="w-10 h-10 text-rose-400 mx-auto mb-3" />
                  <h4 className="font-bold text-slate-800 text-sm">Health Records Concealed for Privacy</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                    Click "Unlock & View Family Health Dossier" above to reveal blood groups, chronic conditions, and Ayushman ABHA credentials.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
                  {dossier.family_members.map((member) => {
                    const med = member.medical_record;
                    return (
                      <div key={member.id} className="bg-white border border-rose-100 rounded-3xl p-5 shadow-sm space-y-4">
                        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                          <div>
                            <span className="text-[10px] uppercase font-bold tracking-wider text-rose-600 block">ABHA Cardholder</span>
                            <h4 className="font-bold text-base text-navy-950">{member.full_name}</h4>
                          </div>
                          <span className="px-3 py-1 rounded-full text-xs font-black bg-rose-50 text-rose-700 border border-rose-200">
                            Blood Group: {med?.blood_group || 'Not Set'}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-xs">
                          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                            <span className="text-slate-400 block font-medium">Ayushman ABHA ID</span>
                            <span className="font-mono font-bold text-slate-900">{med?.abha_id || 'Pending Generation'}</span>
                          </div>
                          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                            <span className="text-slate-400 block font-medium">Vaccination Status</span>
                            <span className="font-bold text-emerald-700">{med?.vaccination_status || 'Unspecified'}</span>
                          </div>
                          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                            <span className="text-slate-400 block font-medium">Chronic Conditions</span>
                            <span className="font-semibold text-slate-800">{med?.chronic_conditions || 'None Reported'}</span>
                          </div>
                          <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                            <span className="text-slate-400 block font-medium">Known Allergies</span>
                            <span className="font-semibold text-slate-800">{med?.allergies || 'None'}</span>
                          </div>
                        </div>

                        <div className="p-2.5 rounded-xl bg-rose-50/50 border border-rose-100 text-xs flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Hospital className="w-4 h-4 text-rose-600" />
                            <span className="text-slate-700">Hospital: <strong>{med?.emergency_hospital || 'Govt District Hospital'}</strong></span>
                          </div>
                          <span className="text-slate-500 font-mono text-[11px]">{med?.emergency_contact_phone || '112 / 108'}</span>
                        </div>

                        <div className="pt-2 flex justify-end">
                          <button
                            type="button"
                            onClick={() => openEditMedical(member)}
                            className="py-1.5 px-3.5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white transition flex items-center gap-1.5"
                          >
                            <Edit3 className="w-3.5 h-3.5 text-saffron-400" />
                            <span>Update Health Record (OTP Clearance)</span>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: CONFIDENTIAL EDUCATION & DIGILOCKER ACADEMIC DOSSIER */}
          {activeTab === 'education' && (
            <div className="space-y-4">
              <div className="bg-white border border-blue-200 rounded-3xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="p-3 rounded-2xl bg-blue-50 text-blue-700 border border-blue-200">
                    <GraduationCap className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-black text-base text-navy-950">National Academic Depository (NAD) & DigiLocker</h3>
                    <p className="text-xs text-slate-600 mt-1 max-w-xl">
                      Academic degrees, university certifications, and literacy credentials linked directly with Ministry of Education systems.
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => setRevealEducation(!revealEducation)}
                  className={`py-2.5 px-5 rounded-2xl font-bold text-xs transition flex items-center justify-center gap-2 ${
                    revealEducation
                      ? 'bg-slate-200 text-slate-800 hover:bg-slate-300'
                      : 'bg-blue-600 hover:bg-blue-700 text-white shadow-md'
                  }`}
                >
                  {revealEducation ? (
                    <>
                      <Lock className="w-4 h-4" />
                      <span>Conceal Academic Records</span>
                    </>
                  ) : (
                    <>
                      <Unlock className="w-4 h-4" />
                      <span>Unlock & View Educational Dossier</span>
                    </>
                  )}
                </button>
              </div>

              {!revealEducation ? (
                <div className="bg-slate-50 border border-dashed border-slate-300 rounded-3xl p-10 text-center">
                  <Lock className="w-10 h-10 text-blue-400 mx-auto mb-3" />
                  <h4 className="font-bold text-slate-800 text-sm">Educational Dossier Concealed for Privacy</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                    Click "Unlock & View Educational Dossier" above to inspect verified degrees, universities, and certificates.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fade-in">
                  {dossier.family_members.map((member) => {
                    const edu = member.education_record;
                    return (
                      <div key={member.id} className="bg-white border border-blue-100 rounded-3xl p-5 shadow-sm space-y-4">
                        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                          <div>
                            <span className="text-[10px] uppercase font-bold tracking-wider text-blue-600 block">Candidate Dossier</span>
                            <h4 className="font-bold text-base text-navy-950">{member.full_name}</h4>
                          </div>
                          <span className="px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                            {edu?.literacy_status || 'Literate'}
                          </span>
                        </div>

                        <div className="space-y-2 text-xs">
                          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                            <span className="text-slate-400 block font-medium">Highest Qualification</span>
                            <span className="font-bold text-slate-900 text-sm">{edu?.highest_qualification || 'Graduate'}</span>
                            {edu?.specialization && (
                              <span className="text-slate-600 block mt-0.5">Specialization: {edu.specialization}</span>
                            )}
                          </div>

                          <div className="grid grid-cols-2 gap-2">
                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                              <span className="text-slate-400 block font-medium">Institution / University</span>
                              <span className="font-semibold text-slate-900">{edu?.institution_name || 'University of Delhi'}</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                              <span className="text-slate-400 block font-medium">Passing Year</span>
                              <span className="font-semibold text-slate-900">{edu?.year_of_completion || '2020'}</span>
                            </div>
                          </div>

                          {edu?.certificate_number && (
                            <div className="p-2 rounded-lg bg-blue-50/50 border border-blue-100 flex items-center justify-between text-[11px]">
                              <span className="text-blue-800 font-medium">DigiLocker Doc ID</span>
                              <span className="font-mono font-bold text-blue-950">{edu.certificate_number}</span>
                            </div>
                          )}
                        </div>

                        <div className="pt-2 flex justify-end">
                          <button
                            type="button"
                            onClick={() => openEditEducation(member)}
                            className="py-1.5 px-3.5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white transition flex items-center gap-1.5"
                          >
                            <Edit3 className="w-3.5 h-3.5 text-saffron-400" />
                            <span>Update Education (OTP Clearance)</span>
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 4: CONFIDENTIAL LAND & PROPERTY RECORDS (BHULEKH / PATTA) */}
          {activeTab === 'land' && (
            <div className="space-y-4">
              <div className="bg-white border border-emerald-200 rounded-3xl p-6 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-start gap-3">
                  <div className="p-3 rounded-2xl bg-emerald-50 text-emerald-700 border border-emerald-200">
                    <LandPlot className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-black text-base text-navy-950">State Bhulekh & Patta Revenue Assets</h3>
                    <p className="text-xs text-slate-600 mt-1 max-w-xl">
                      Registered agricultural parcels, residential plots, and official revenue passbooks assigned to this household dwelling.
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => setRevealLand(!revealLand)}
                    className={`py-2.5 px-5 rounded-2xl font-bold text-xs transition flex items-center justify-center gap-2 ${
                      revealLand
                        ? 'bg-slate-200 text-slate-800 hover:bg-slate-300'
                        : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-md'
                    }`}
                  >
                    {revealLand ? (
                      <>
                        <Lock className="w-4 h-4" />
                        <span>Conceal Land Assets</span>
                      </>
                    ) : (
                      <>
                        <Unlock className="w-4 h-4" />
                        <span>Unlock & View Land Holdings</span>
                      </>
                    )}
                  </button>

                  <button
                    type="button"
                    onClick={() => setAddLandModalOpen(true)}
                    className="py-2.5 px-4 rounded-2xl font-bold text-xs bg-navy-900 hover:bg-navy-800 text-white transition flex items-center gap-1.5 shadow-md"
                  >
                    <PlusCircle className="w-4 h-4 text-saffron-400" />
                    <span>Register New Parcel</span>
                  </button>
                </div>
              </div>

              {!revealLand ? (
                <div className="bg-slate-50 border border-dashed border-slate-300 rounded-3xl p-10 text-center">
                  <Lock className="w-10 h-10 text-emerald-500 mx-auto mb-3" />
                  <h4 className="font-bold text-slate-800 text-sm">Land & Property Records Concealed for Privacy</h4>
                  <p className="text-xs text-slate-500 max-w-md mx-auto mt-1">
                    Click "Unlock & View Land Holdings" above to inspect survey/khasra numbers, acreage, and patta certificates.
                  </p>
                </div>
              ) : (
                <div className="space-y-4 animate-fade-in">
                  {(!dossier.land_records || dossier.land_records.length === 0) ? (
                    <div className="bg-white border border-dashed border-slate-200 rounded-3xl p-8 text-center">
                      <LandPlot className="w-10 h-10 text-slate-300 mx-auto mb-2" />
                      <p className="text-sm font-bold text-slate-700">No Land Parcels Registered</p>
                      <p className="text-xs text-slate-500 mt-1">Click "Register New Parcel" to add survey and revenue asset records.</p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {dossier.land_records.map((land) => (
                        <div key={land.id} className="bg-white border border-emerald-100 rounded-3xl p-5 shadow-sm space-y-4">
                          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                            <div>
                              <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-700 block">Khasra / Survey Number</span>
                              <h4 className="font-mono font-bold text-lg text-navy-950">{land.survey_number}</h4>
                            </div>
                            <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-200">
                              {land.land_type}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-3 text-xs">
                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                              <span className="text-slate-400 block font-medium">Area / Measurement</span>
                              <span className="font-bold text-slate-900">{land.area_measurement}</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                              <span className="text-slate-400 block font-medium">Patta Passbook No.</span>
                              <span className="font-mono font-bold text-slate-900">{land.patta_passbook_number || 'N/A'}</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                              <span className="text-slate-400 block font-medium">Tax Clearance Status</span>
                              <span className="font-bold text-emerald-700">{land.property_tax_status || 'Cleared'}</span>
                            </div>
                            <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                              <span className="text-slate-400 block font-medium">Est. Revenue Valuation</span>
                              <span className="font-bold text-navy-950">
                                {land.market_valuation_inr ? `₹${land.market_valuation_inr.toLocaleString('en-IN')}` : '₹35,00,000'}
                              </span>
                            </div>
                          </div>

                          {land.district_sub_registrar && (
                            <div className="p-2 rounded-xl bg-slate-50 text-slate-600 text-[11px] flex items-center justify-between">
                              <span>Sub-Registrar Office:</span>
                              <span className="font-semibold text-slate-900">{land.district_sub_registrar}</span>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ================= MODAL: EDIT FAMILY MEMBER ================= */}
      {editMemberModalOpen && selectedMember && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-md p-6 overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-navy-100 text-navy-900">
                  <Edit3 className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-navy-950">Update Family Member Details</h3>
                  <span className="text-xs text-slate-500">{selectedMember.full_name} ({selectedMember.citizen_code})</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEditMemberModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRequestMemberSave} className="space-y-4">
              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  10-Digit Mobile Contact
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Phone className="w-4 h-4" />
                  </div>
                  <input
                    type="tel"
                    value={memberForm.phone_number}
                    onChange={(e) => setMemberForm({ ...memberForm, phone_number: e.target.value })}
                    placeholder="+91 98765 43210"
                    className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-navy-600"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Preferred Language
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
                    <Globe className="w-4 h-4" />
                  </div>
                  <select
                    value={memberForm.preferred_language}
                    onChange={(e) => setMemberForm({ ...memberForm, preferred_language: e.target.value })}
                    className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-navy-600 bg-white"
                  >
                    <option value="en">English</option>
                    <option value="hi">हिन्दी (Hindi)</option>
                    <option value="bn">বাংলা (Bengali)</option>
                    <option value="te">తెలుగు (Telugu)</option>
                    <option value="mr">मराठी (Marathi)</option>
                    <option value="ta">தமிழ் (Tamil)</option>
                  </select>
                </div>
              </div>

              <div className="p-3 bg-saffron-50 rounded-xl text-[11px] text-saffron-900 border border-saffron-200">
                <strong>Government Privacy Notice:</strong> Core identity (legal name, citizen code, date of birth) cannot be mutated by family members. Submitting will trigger a <strong>2-Step OTP challenge</strong>.
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setEditMemberModalOpen(false)}
                  className="py-2 px-4 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="py-2 px-5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white shadow-md flex items-center gap-1.5"
                >
                  <span>Proceed to OTP Clearance</span>
                  <ShieldCheck className="w-3.5 h-3.5 text-saffron-400" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: EDIT MEDICAL RECORD ================= */}
      {editMedicalModalOpen && selectedMember && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-lg p-6 overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-rose-100 text-rose-700">
                  <HeartPulse className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-navy-950">Update Confidential Health Record</h3>
                  <span className="text-xs text-slate-500">{selectedMember.full_name}</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEditMedicalModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRequestMedicalSave} className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Blood Group</label>
                  <select
                    value={medicalForm.blood_group}
                    onChange={(e) => setMedicalForm({ ...medicalForm, blood_group: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm bg-white"
                  >
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Ayushman ABHA ID</label>
                  <input
                    type="text"
                    value={medicalForm.abha_id || ''}
                    onChange={(e) => setMedicalForm({ ...medicalForm, abha_id: e.target.value })}
                    placeholder="14-8921-4321-0987"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Chronic Medical Conditions</label>
                <input
                  type="text"
                  value={medicalForm.chronic_conditions || ''}
                  onChange={(e) => setMedicalForm({ ...medicalForm, chronic_conditions: e.target.value })}
                  placeholder="e.g. Type-2 Diabetes, Hypertension"
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Known Allergies</label>
                <input
                  type="text"
                  value={medicalForm.allergies || ''}
                  onChange={(e) => setMedicalForm({ ...medicalForm, allergies: e.target.value })}
                  placeholder="e.g. Penicillin, Sulfa"
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Vaccination Status</label>
                  <select
                    value={medicalForm.vaccination_status}
                    onChange={(e) => setMedicalForm({ ...medicalForm, vaccination_status: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm bg-white"
                  >
                    <option value="Fully Vaccinated">Fully Vaccinated</option>
                    <option value="Partially Vaccinated">Partially Vaccinated</option>
                    <option value="Not Vaccinated">Not Vaccinated</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Emergency Hospital</label>
                  <input
                    type="text"
                    value={medicalForm.emergency_hospital || ''}
                    onChange={(e) => setMedicalForm({ ...medicalForm, emergency_hospital: e.target.value })}
                    placeholder="e.g. AIIMS New Delhi"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setEditMedicalModalOpen(false)}
                  className="py-2 px-4 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="py-2 px-5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white shadow-md flex items-center gap-1.5"
                >
                  <span>Verify with OTP</span>
                  <ShieldCheck className="w-3.5 h-3.5 text-saffron-400" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: EDIT EDUCATION RECORD ================= */}
      {editEducationModalOpen && selectedMember && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-lg p-6 overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-blue-100 text-blue-700">
                  <GraduationCap className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-navy-950">Update Academic & DigiLocker Record</h3>
                  <span className="text-xs text-slate-500">{selectedMember.full_name}</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setEditEducationModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleRequestEducationSave} className="space-y-3.5">
              <div>
                <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Highest Qualification</label>
                <input
                  type="text"
                  value={educationForm.highest_qualification || ''}
                  onChange={(e) => setEducationForm({ ...educationForm, highest_qualification: e.target.value })}
                  placeholder="e.g. Master of Science / B.Tech"
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Institution / Board</label>
                  <input
                    type="text"
                    value={educationForm.institution_name || ''}
                    onChange={(e) => setEducationForm({ ...educationForm, institution_name: e.target.value })}
                    placeholder="e.g. Delhi University / CBSE"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Passing Year</label>
                  <input
                    type="number"
                    value={educationForm.year_of_completion || 2020}
                    onChange={(e) => setEducationForm({ ...educationForm, year_of_completion: Number(e.target.value) })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Specialization / Discipline</label>
                  <input
                    type="text"
                    value={educationForm.specialization || ''}
                    onChange={(e) => setEducationForm({ ...educationForm, specialization: e.target.value })}
                    placeholder="e.g. Computer Science"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">DigiLocker Certificate ID</label>
                  <input
                    type="text"
                    value={educationForm.certificate_number || ''}
                    onChange={(e) => setEducationForm({ ...educationForm, certificate_number: e.target.value })}
                    placeholder="e.g. DL-CERT-9042"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-mono"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setEditEducationModalOpen(false)}
                  className="py-2 px-4 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="py-2 px-5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white shadow-md flex items-center gap-1.5"
                >
                  <span>Verify with OTP</span>
                  <ShieldCheck className="w-3.5 h-3.5 text-saffron-400" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: ADD LAND ASSET ================= */}
      {addLandModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-xs animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl border border-slate-200 w-full max-w-lg p-6 overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-emerald-100 text-emerald-800">
                  <LandPlot className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-base text-navy-950">Register New Land Asset Parcel</h3>
                  <span className="text-xs text-slate-500">Bhulekh Revenue Department Recording</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setAddLandModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddLandRecord} className="space-y-3.5">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">
                    Survey / Khasra No. <span className="text-rose-600">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={landForm.survey_number}
                    onChange={(e) => setLandForm({ ...landForm, survey_number: e.target.value })}
                    placeholder="e.g. KH-409/2A"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-mono"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Land Classification</label>
                  <select
                    value={landForm.land_type}
                    onChange={(e) => setLandForm({ ...landForm, land_type: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm bg-white"
                  >
                    <option value="Agricultural">Agricultural</option>
                    <option value="Residential">Residential</option>
                    <option value="Commercial">Commercial</option>
                    <option value="Industrial">Industrial</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Area / Measurement</label>
                  <input
                    type="text"
                    value={landForm.area_measurement}
                    onChange={(e) => setLandForm({ ...landForm, area_measurement: e.target.value })}
                    placeholder="e.g. 2.45 Acres or 1800 Sq.Ft."
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Patta Passbook No.</label>
                  <input
                    type="text"
                    value={landForm.patta_passbook_number}
                    onChange={(e) => setLandForm({ ...landForm, patta_passbook_number: e.target.value })}
                    placeholder="e.g. PATTA-2026-99"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Est. Valuation (₹ INR)</label>
                  <input
                    type="number"
                    value={landForm.market_valuation_inr}
                    onChange={(e) => setLandForm({ ...landForm, market_valuation_inr: Number(e.target.value) })}
                    placeholder="e.g. 4500000"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm font-bold"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase text-slate-700 mb-1">Sub-Registrar Office</label>
                  <input
                    type="text"
                    value={landForm.district_sub_registrar}
                    onChange={(e) => setLandForm({ ...landForm, district_sub_registrar: e.target.value })}
                    placeholder="e.g. South Delhi Sub-Registrar"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3">
                <button
                  type="button"
                  onClick={() => setAddLandModalOpen(false)}
                  className="py-2 px-4 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="py-2 px-5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white shadow-md flex items-center gap-1.5"
                >
                  <span>Submit Parcel Registration</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= MODAL: REQUEST MEMBER LINKAGE ================= */}
      {linkMemberModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-sm">
          <div className="w-full max-w-lg bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden animate-fade-in max-h-[92vh] flex flex-col">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-saffron-100 text-saffron-800">
                  <UserCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-black text-base text-navy-950">Request Family Member Linkage</h3>
                  <span className="text-[11px] text-slate-500 font-medium">Link new family member to dwelling {dossier?.household_code}</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setLinkMemberModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitLinkRequest} className="p-6 space-y-4 overflow-y-auto">
              <div className="bg-amber-50/80 border border-amber-200 rounded-2xl p-3 text-xs text-amber-900 leading-relaxed">
                <strong>Governance Rule:</strong> The relationship and role are explicitly chosen by the family requester. System and municipal administrators never auto-decide relationships. Administrators act solely to approve or reject.
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1">
                  Target Citizen Code or Phone Number <span className="text-rose-600">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={linkForm.target_citizen_code}
                  onChange={(e) => setLinkForm({ ...linkForm, target_citizen_code: e.target.value })}
                  placeholder="e.g. CTZ-SON002 or 9876543210"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-saffron-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Relationship (Specified by You) <span className="text-rose-600">*</span>
                  </label>
                  <select
                    value={linkForm.relationship}
                    onChange={(e) => setLinkForm({ ...linkForm, relationship: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-saffron-500 font-medium"
                  >
                    <option value="Son">Son (पुत्र)</option>
                    <option value="Daughter">Daughter (पुत्री)</option>
                    <option value="Spouse">Spouse (पति / पत्नी)</option>
                    <option value="Father">Father (पिता)</option>
                    <option value="Mother">Mother (माता)</option>
                    <option value="Brother">Brother (भाई)</option>
                    <option value="Sister">Sister (बहन)</option>
                    <option value="Grandfather">Grandfather (दादाजी / नानाजी)</option>
                    <option value="Grandmother">Grandmother (दादीजी / नानीजी)</option>
                    <option value="Daughter-in-law">Daughter-in-law (पुत्रवधू)</option>
                    <option value="Son-in-law">Son-in-law (दामाद)</option>
                    <option value="Grandson">Grandson (पोता / नाती)</option>
                    <option value="Granddaughter">Granddaughter (पोती / नातिन)</option>
                    <option value="Relative">Other Relative (अन्य रिश्तेदार)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1">
                    Household Role
                  </label>
                  <select
                    value={linkForm.household_role}
                    onChange={(e) => setLinkForm({ ...linkForm, household_role: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 text-sm focus:ring-2 focus:ring-saffron-500 font-medium"
                  >
                    <option value="MEMBER">Adult Member (व्यस्क सदस्य)</option>
                    <option value="DEPUTY">Deputy Custodian (सह-मुखिया)</option>
                    <option value="DEPENDENT">Dependent / Minor (आश्रित)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-700 mb-1.5">
                  Individually Assigned Tasks & Civic Capabilities:
                </label>
                <div className="space-y-2 bg-slate-50 p-3 rounded-2xl border border-slate-200 text-xs">
                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={linkForm.assigned_tasks.includes('can_manage_medical')}
                      onChange={() => toggleTaskInLinkForm('can_manage_medical')}
                      className="rounded text-navy-900 focus:ring-navy-600"
                    />
                    <span>🏥 Manage Family Health & ABHA Dossier</span>
                  </label>

                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={linkForm.assigned_tasks.includes('can_manage_education')}
                      onChange={() => toggleTaskInLinkForm('can_manage_education')}
                      className="rounded text-navy-900 focus:ring-navy-600"
                    />
                    <span>🎓 Manage Educational & DigiLocker Credentials</span>
                  </label>

                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={linkForm.assigned_tasks.includes('can_manage_assets')}
                      onChange={() => toggleTaskInLinkForm('can_manage_assets')}
                      className="rounded text-navy-900 focus:ring-navy-600"
                    />
                    <span>📜 Register & Manage Immovable Land Holdings</span>
                  </label>

                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={linkForm.assigned_tasks.includes('can_manage_members')}
                      onChange={() => toggleTaskInLinkForm('can_manage_members')}
                      className="rounded text-navy-900 focus:ring-navy-600"
                    />
                    <span>👨‍👩‍👧‍👦 Request Member Linkages to Household</span>
                  </label>

                  <label className="flex items-center gap-2.5 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={linkForm.assigned_tasks.includes('can_pay_taxes')}
                      onChange={() => toggleTaskInLinkForm('can_pay_taxes')}
                      className="rounded text-navy-900 focus:ring-navy-600"
                    />
                    <span>💳 Pay Municipal Taxes & Civic Dues</span>
                  </label>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setLinkMemberModalOpen(false)}
                  className="py-2 px-4 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingLink}
                  className="py-2 px-5 rounded-xl text-xs font-bold bg-navy-900 hover:bg-navy-800 text-white shadow-md flex items-center gap-1.5 disabled:opacity-50"
                >
                  {isSubmittingLink ? (
                    <>
                      <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <span>Submit Request for Activation</span>
                      <ArrowRight className="w-3.5 h-3.5 text-saffron-400" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ================= 2-STEP OTP CHALLENGE MODAL ================= */}
      <OTPChallengeModal
        isOpen={otpModalOpen}
        onClose={() => {
          setOtpModalOpen(false);
          setPendingAction(null);
        }}
        purpose={otpPurpose}
        actionTitle="Civic Security — 2-Step OTP Verification"
        onVerified={handleOtpVerified}
      />
    </div>
  );
};
