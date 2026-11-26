import React, { useState, useEffect } from 'react';
import {
  FileText,
  Printer,
  Download,
  CheckCircle2,
  ShieldCheck,
  Users,
  HeartPulse,
  GraduationCap,
  Landmark,
  X,
  QrCode,
  Award,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { api } from '../services/api';
import { CitizenDossierReport } from '../types';

interface CitizenDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
  citizenId: number;
}

export const CitizenDossierModal: React.FC<CitizenDossierModalProps> = ({
  isOpen,
  onClose,
  citizenId,
}) => {
  const [report, setReport] = useState<CitizenDossierReport | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen && citizenId) {
      loadReport(citizenId);
    } else {
      setReport(null);
      setError(null);
    }
  }, [isOpen, citizenId]);

  const loadReport = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.reports.getCitizenDossier(id);
      setReport(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to generate citizen comprehensive dossier.');
    } finally {
      setLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${report.metadata.report_serial}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/75 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 print:p-0 print:bg-white print:static">
      <div className="relative bg-white w-full max-w-5xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[95vh] print:max-h-none print:shadow-none print:border-none print:rounded-none">
        
        {/* Modal Top Bar (Hidden during print) */}
        <div className="flex items-center justify-between px-6 py-4 bg-slate-900 text-white print:hidden">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white tracking-wide">
                Certified Comprehensive Citizen Dossier
              </h2>
              <p className="text-xs text-slate-400">
                Official Multi-Service Registry Record • Formally Attested
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrint}
              disabled={loading || !report}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold rounded-lg shadow transition"
              title="Print official report or save to PDF"
            >
              <Printer className="w-4 h-4" />
              <span>Print / Save PDF</span>
            </button>
            <button
              onClick={handleDownloadJSON}
              disabled={loading || !report}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition"
              title="Download structured JSON dataset"
            >
              <Download className="w-4 h-4" />
              <span>Export JSON</span>
            </button>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Modal Body / Printable Document Canvas */}
        <div className="overflow-y-auto p-6 sm:p-10 space-y-8 bg-slate-50 print:bg-white print:p-6 print:overflow-visible">
          {loading && (
            <div className="py-24 text-center">
              <Loader2 className="w-10 h-10 text-blue-600 animate-spin mx-auto mb-4" />
              <p className="text-sm font-semibold text-slate-700">
                Aggregating cross-service civic records & cryptographic verification...
              </p>
              <p className="text-xs text-slate-500 mt-1">
                Querying identity, household relations, medical records, education, and land registry.
              </p>
            </div>
          )}

          {error && (
            <div className="p-6 bg-red-50 border border-red-200 rounded-xl flex items-start space-x-3 text-red-800">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5 text-red-600" />
              <div>
                <h4 className="font-semibold text-sm">Failed to generate report</h4>
                <p className="text-xs mt-1 text-red-700">{error}</p>
                <button
                  onClick={() => citizenId && loadReport(citizenId)}
                  className="mt-3 px-3 py-1 text-xs font-semibold bg-red-600 text-white rounded hover:bg-red-700 transition"
                >
                  Retry
                </button>
              </div>
            </div>
          )}

          {report && (
            <div className="bg-white p-8 sm:p-10 rounded-xl shadow-sm border border-slate-200 print:border-none print:shadow-none print:p-0 space-y-8">
              
              {/* Official Government Header */}
              <div className="border-b-2 border-slate-800 pb-6">
                <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
                  <div className="flex items-center space-x-4">
                    <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-amber-600 via-amber-700 to-amber-900 text-white flex items-center justify-center font-black text-2xl shadow-md border-2 border-amber-300">
                      🏛️
                    </div>
                    <div>
                      <p className="text-xs font-extrabold tracking-widest text-blue-900 uppercase">
                        Government of India • Ministry of Electronics & IT
                      </p>
                      <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">
                        NagrikSetu Unified Civic Governance Authority
                      </h1>
                      <p className="text-xs text-slate-600 font-medium">
                        Central Administrative Citizen Registry & Family Census Archive
                      </p>
                    </div>
                  </div>

                  <div className="text-right sm:text-right border-t sm:border-t-0 pt-2 sm:pt-0 border-slate-200">
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-300">
                      <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                      {report.metadata.verification_status}
                    </span>
                    <p className="text-[11px] font-mono text-slate-500 mt-1">
                      Serial: {report.metadata.report_serial}
                    </p>
                    <p className="text-[11px] text-slate-500">
                      Issued: {new Date(report.metadata.issued_at).toLocaleString()}
                    </p>
                  </div>
                </div>

                {/* Sub-header Banner */}
                <div className="mt-4 px-4 py-2 bg-slate-900 text-white rounded-lg flex flex-col sm:flex-row items-center justify-between text-xs font-semibold gap-2">
                  <span>DOCUMENT: OFFICIAL CITIZEN COMPREHENSIVE DOSSIER</span>
                  <span className="font-mono text-slate-300">
                    SHA256: {report.metadata.digital_checksum_sha256.substring(0, 16)}...
                  </span>
                </div>
              </div>

              {/* Citizen Identity Section */}
              <section className="space-y-3">
                <div className="flex items-center space-x-2 text-slate-900 border-b border-slate-200 pb-1.5">
                  <Award className="w-5 h-5 text-blue-700" />
                  <h3 className="text-sm font-bold uppercase tracking-wider">
                    1. Primary Citizen Demographics & Familial Relationship
                  </h3>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-slate-50 p-4 rounded-xl border border-slate-200 text-xs">
                  <div>
                    <span className="text-slate-500 block uppercase text-[10px] font-bold">Full Legal Name</span>
                    <span className="text-slate-900 font-bold text-sm">{report.citizen.full_name}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block uppercase text-[10px] font-bold">National Citizen ID</span>
                    <span className="text-blue-700 font-mono font-bold text-sm">{report.citizen.citizen_code}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block uppercase text-[10px] font-bold">Date of Birth</span>
                    <span className="text-slate-900 font-semibold">{report.citizen.date_of_birth}</span>
                  </div>

                  <div>
                    <span className="text-slate-500 block uppercase text-[10px] font-bold">Registered Mobile</span>
                    <span className="text-slate-900 font-semibold">{report.citizen.phone_number}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block uppercase text-[10px] font-bold">Preferred Language</span>
                    <span className="text-slate-900 font-semibold uppercase">{report.citizen.preferred_language}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block uppercase text-[10px] font-bold">Census Status</span>
                    <span className="inline-block px-2 py-0.5 rounded text-[11px] font-bold bg-blue-100 text-blue-800 uppercase">
                      {report.citizen.profile_status}
                    </span>
                  </div>

                  {/* Highlight Family Relationship */}
                  <div className="sm:col-span-3 bg-amber-50/80 border border-amber-200 p-3 rounded-lg flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
                    <div>
                      <span className="text-amber-900 font-bold text-xs flex items-center gap-1.5">
                        🤝 Family Relationship Designation:
                        <span className="px-2 py-0.5 rounded bg-amber-200 text-amber-950 font-black">
                          {report.citizen.relationship}
                        </span>
                      </span>
                      <p className="text-xs text-amber-800 mt-0.5 font-medium">
                        {report.citizen.relationship_details}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">Dwelling Role</span>
                      <span className="text-xs font-bold text-slate-800">{report.citizen.household_role}</span>
                    </div>
                  </div>
                </div>
              </section>

              {/* Household & Family Census Section */}
              <section className="space-y-3">
                <div className="flex items-center space-x-2 text-slate-900 border-b border-slate-200 pb-1.5">
                  <Users className="w-5 h-5 text-indigo-700" />
                  <h3 className="text-sm font-bold uppercase tracking-wider">
                    2. Household Dwelling & Family Members Census
                  </h3>
                </div>

                {report.household ? (
                  <div className="space-y-3">
                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                      <div>
                        <span className="text-slate-500 block text-[10px] font-bold uppercase">Household Code</span>
                        <span className="font-mono font-bold text-indigo-800 text-sm">
                          {report.household.household_code}
                        </span>
                      </div>
                      <div className="sm:col-span-2">
                        <span className="text-slate-500 block text-[10px] font-bold uppercase">Dwelling Address</span>
                        <span className="text-slate-900 font-medium">
                          {report.household.address_line}, {report.household.locality}, {report.household.city},{' '}
                          {report.household.state} - {report.household.postal_code}
                        </span>
                      </div>
                    </div>

                    {/* Family Members Roster Table */}
                    <div className="overflow-x-auto rounded-lg border border-slate-200">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200 uppercase text-[10px]">
                          <tr>
                            <th className="px-3 py-2">Citizen Code</th>
                            <th className="px-3 py-2">Full Name</th>
                            <th className="px-3 py-2">Family Relationship</th>
                            <th className="px-3 py-2">Relationship Details</th>
                            <th className="px-3 py-2">Role</th>
                            <th className="px-3 py-2">DOB</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 bg-white">
                          {report.family_members.map((m) => (
                            <tr
                              key={m.id}
                              className={m.is_current ? 'bg-blue-50/50 font-semibold' : ''}
                            >
                              <td className="px-3 py-2 font-mono text-blue-700">{m.citizen_code}</td>
                              <td className="px-3 py-2 font-medium text-slate-900">
                                {m.full_name} {m.is_current && <span className="text-[10px] text-blue-600 font-bold">(Subject)</span>}
                              </td>
                              <td className="px-3 py-2">
                                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                                  {m.relationship}
                                </span>
                              </td>
                              <td className="px-3 py-2 text-slate-600 text-[11px]">{m.relationship_details}</td>
                              <td className="px-3 py-2 text-slate-700">{m.household_role}</td>
                              <td className="px-3 py-2 text-slate-600">{m.date_of_birth}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 rounded-lg text-xs text-slate-500 italic">
                    Citizen is registered as an independent individual (not linked to a multi-member household dwelling).
                  </div>
                )}
              </section>

              {/* Medical & Education Split Section */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* Health & Medical Passport */}
                <section className="space-y-3">
                  <div className="flex items-center space-x-2 text-slate-900 border-b border-slate-200 pb-1.5">
                    <HeartPulse className="w-5 h-5 text-rose-600" />
                    <h3 className="text-sm font-bold uppercase tracking-wider">
                      3. Health & Medical Profile
                    </h3>
                  </div>

                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2.5 text-xs">
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Blood Group</span>
                      <span className="font-bold text-rose-700">{report.medical_health_passport.blood_group}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Immunization / UIP</span>
                      <span className="font-semibold text-slate-900">{report.medical_health_passport.vaccination_status}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">ABHA Health ID</span>
                      <span className="font-mono text-slate-800">{report.medical_health_passport.abha_id}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Chronic Conditions</span>
                      <span className="text-slate-900">{report.medical_health_passport.chronic_conditions}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Allergies / Disabilities</span>
                      <span className="text-slate-900">{report.medical_health_passport.allergies} / {report.medical_health_passport.disability_status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Emergency Hospital</span>
                      <span className="text-slate-900 font-medium">{report.medical_health_passport.emergency_hospital}</span>
                    </div>
                  </div>
                </section>

                {/* Education & Literacy Record */}
                <section className="space-y-3">
                  <div className="flex items-center space-x-2 text-slate-900 border-b border-slate-200 pb-1.5">
                    <GraduationCap className="w-5 h-5 text-emerald-600" />
                    <h3 className="text-sm font-bold uppercase tracking-wider">
                      4. Education & Literacy Profile
                    </h3>
                  </div>

                  <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 space-y-2.5 text-xs">
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Literacy Status</span>
                      <span className="font-bold text-emerald-700">{report.education_credentials.literacy_status}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Highest Qualification</span>
                      <span className="font-bold text-slate-900">{report.education_credentials.highest_qualification}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Institution / Board</span>
                      <span className="text-slate-900 font-medium">{report.education_credentials.institution_name || 'Government Board'}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Specialization</span>
                      <span className="text-slate-900">{report.education_credentials.specialization || 'General Studies'}</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-200 pb-1">
                      <span className="text-slate-500">Year Completed</span>
                      <span className="text-slate-900">{report.education_credentials.year_of_completion || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Certificate Number</span>
                      <span className="font-mono text-slate-800">{report.education_credentials.certificate_number || 'VERIFIED'}</span>
                    </div>
                  </div>
                </section>
              </div>

              {/* Land & Immovable Property Holdings */}
              <section className="space-y-3">
                <div className="flex items-center space-x-2 text-slate-900 border-b border-slate-200 pb-1.5">
                  <Landmark className="w-5 h-5 text-amber-700" />
                  <h3 className="text-sm font-bold uppercase tracking-wider">
                    5. Immovable Property & Land Registry
                  </h3>
                </div>

                {report.land_property_assets.length > 0 ? (
                  <div className="overflow-x-auto rounded-lg border border-slate-200">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-100 text-slate-700 font-bold border-b border-slate-200 uppercase text-[10px]">
                        <tr>
                          <th className="px-3 py-2">Survey / Khasra No.</th>
                          <th className="px-3 py-2">Classification</th>
                          <th className="px-3 py-2">Extent / Area</th>
                          <th className="px-3 py-2">Patta / Passbook</th>
                          <th className="px-3 py-2">Sub-Registrar Authority</th>
                          <th className="px-3 py-2">Property Tax</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 bg-white">
                        {report.land_property_assets.map((l) => (
                          <tr key={l.id}>
                            <td className="px-3 py-2 font-mono font-bold text-amber-900">{l.survey_number}</td>
                            <td className="px-3 py-2 text-slate-800">{l.land_type}</td>
                            <td className="px-3 py-2 text-slate-700 font-semibold">{l.area_measurement}</td>
                            <td className="px-3 py-2 font-mono text-slate-600">{l.patta_passbook_number}</td>
                            <td className="px-3 py-2 text-slate-600">{l.district_sub_registrar}</td>
                            <td className="px-3 py-2">
                              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                                {l.property_tax_status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-4 bg-slate-50 rounded-lg text-xs text-slate-500 italic">
                    No immovable land holdings registered under this household dwelling in the Central Land Registry.
                  </div>
                )}
              </section>

              {/* Digital Attestation, QR Stamp & Signatures */}
              <div className="border-t-2 border-slate-800 pt-6 mt-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  
                  {/* QR Code Block */}
                  <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 flex items-center space-x-4">
                    <div className="w-20 h-20 bg-white p-1 rounded-lg border border-slate-300 shadow-sm flex items-center justify-center">
                      <QrCode className="w-16 h-16 text-slate-900" />
                    </div>
                    <div className="text-[11px] space-y-1">
                      <span className="font-bold text-slate-800 block">Digital Verification QR</span>
                      <p className="text-slate-500 text-[10px] leading-tight">
                        Scan via NagrikSetu Mobile Verifier to inspect tamper-evident cryptographic hash.
                      </p>
                      <span className="font-mono text-[9px] text-blue-700 block truncate max-w-[160px]">
                        {report.metadata.qr_verification_payload}
                      </span>
                    </div>
                  </div>

                  {/* Legal Attestation Text */}
                  <div className="text-[11px] text-slate-600 leading-relaxed border-l-2 border-slate-300 pl-4">
                    <span className="font-bold text-slate-800 uppercase text-[10px] block mb-1">
                      Statutory Attestation & Validity
                    </span>
                    <p>{report.legal_attestation.declaration}</p>
                    <p className="mt-1 font-semibold text-slate-700">
                      Validity: {report.legal_attestation.validity}
                    </p>
                  </div>

                  {/* Digital Signature & Seal */}
                  <div className="text-center sm:text-right space-y-1">
                    <div className="inline-block border-2 border-dashed border-slate-400 p-3 rounded-lg bg-slate-50 text-center min-w-[180px]">
                      <div className="text-emerald-700 font-bold text-xs flex items-center justify-center gap-1">
                        <CheckCircle2 className="w-4 h-4" />
                        <span>DIGITALLY SIGNED</span>
                      </div>
                      <p className="text-[10px] text-slate-500 mt-1">Registrar of Public Records</p>
                      <p className="text-[9px] font-mono text-slate-400 mt-0.5">
                        {report.metadata.digital_checksum_sha256.substring(0, 20)}...
                      </p>
                    </div>
                  </div>

                </div>
              </div>

            </div>
          )}

        </div>

      </div>
    </div>
  );
};
