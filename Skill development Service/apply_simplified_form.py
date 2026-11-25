import sys

app_path = r"C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\frontend\src\App.tsx"

with open(app_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update handleEnrolmentSubmit to create simplified dossier while remaining backwards-compatible
target_submit_old = """      const comprehensiveDossier = {
        section_a_personal: {
          full_name: appFullName,
          email: appEmail,
          phone: appPhone,
          date_of_birth: appDob,
          gender: appGender,
          alternate_phone: appAltPhone
        },
        section_b_address: {
          residential_address: appAddress,
          city: appCity,
          state: appState,
          pincode: appPincode
        },
        section_c_education: {
          highest_qualification: appEducation,
          institution: appInstitution,
          graduation_year: appGradYear,
          specialization: appSpecialization
        },
        section_d_employment: {
          employment_status: appEmploymentStatus,
          occupation: appOccupation,
          experience_years: appExperienceYears
        },
        section_e_training_preferences: {
          program_title: enrollingProgram.title,
          preferred_mode: appPrefMode,
          preferred_timing: appPrefTiming,
          batch_id: selectedBatchId
        },
        section_f_career_motivation: {
          statement_of_purpose: enrolmentStatement,
          target_skills: appTargetSkills,
          placement_assistance_required: appPostJobPlacement
        },
        section_g_documents: {
          id_proof_type: appIdProofType,
          id_proof_reference: appIdProofNumber,
          locker_verification_note: appDocAttachedNote
        },
        section_h_declaration: {
          agreed: true,
          timestamp: new Date().toISOString()
        }
      };"""

replacement_submit = """      const simplifiedDossier = {
        section_a_personal: {
          full_name: appFullName,
          citizen_ref: citizenRef || 'CIT-2026-X',
          email: appEmail,
          phone: appPhone
        },
        section_b_location: {
          city_district: appCity,
          pincode: appPincode
        },
        // Maintained for backward compatibility with existing dashboard views
        section_b_address: {
          residential_address: appCity,
          city: appCity,
          state: 'Karnataka',
          pincode: appPincode
        },
        section_c_education: {
          highest_qualification: appEducation
        },
        section_d_employment: {
          employment_status: appEmploymentStatus
        },
        section_e_training: {
          program_id: enrollingProgram.id,
          program_code: enrollingProgram.code,
          program_title: enrollingProgram.title,
          centre_id: enrollingProgram.centre?.id || enrollingProgram.centre_id,
          centre_name: enrollingProgram.centre?.name || enrollingProgram.centre_name || 'Accredited Training Centre',
          batch_id: selectedBatchId,
          delivery_mode: appPrefMode
        },
        section_declaration: {
          agreed: true,
          terms: "I confirm that the submitted details are accurate and I agree to be contacted by the selected training centre regarding my application.",
          timestamp: new Date().toISOString()
        }
      };"""

if target_submit_old in content:
    content = content.replace(target_submit_old, replacement_submit)
    content = content.replace("application_details: comprehensiveDossier,", "application_details: simplifiedDossier,")
    print("Replaced handleEnrolmentSubmit dossier successfully.")
else:
    print("Could not find target_submit_old in App.tsx")
    sys.exit(1)

# 2. Replace the modal markup
modal_start_target = """      {/* COMPREHENSIVE 8-SECTION ENROLMENT MODAL */}
      {enrollingProgram && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '820px', maxHeight: '92vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f2444' }}>
                  Government Training Programme Enrolment Dossier
                </h3>
                <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
                  Standard NSQF Skill Development Application (Sections A – H)
                </span>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setEnrollingProgram(null)}>
                <X size={20} />
              </button>
            </div>"""

modal_end_target = """              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button className="btn-navy-outline" onClick={() => setEnrollingProgram(null)} disabled={enrolSubmitting}>
                  Cancel
                </button>
                <button className="btn-primary-orange" onClick={handleEnrolmentSubmit} disabled={enrolSubmitting}>
                  {enrolSubmitting ? 'Submitting Application...' : 'Confirm & Submit Application'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}"""

start_pos = content.find(modal_start_target)
if start_pos == -1:
    print("Could not find modal_start_target")
    sys.exit(1)

end_pos = content.find(modal_end_target, start_pos)
if end_pos == -1:
    print("Could not find modal_end_target")
    sys.exit(1)

end_pos += len(modal_end_target)

simplified_modal = """      {/* SIMPLIFIED CITIZEN TRAINING APPLICATION FORM */}
      {enrollingProgram && (
        <div className="modal-overlay" style={{ zIndex: 1100 }}>
          <div className="modal-content-lg" style={{ maxWidth: '680px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header" style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444', margin: 0 }}>
                  Training Programme Application
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Fast & Simple Registration â€¢ Pre-filled from your Citizen Profile
                </span>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setEnrollingProgram(null)}>
                <X size={20} />
              </button>
            </div>

            <div className="modal-body" style={{ display: 'grid', gap: '1.25rem', paddingTop: '1rem' }}>
              {/* Selected Programme Summary Banner */}
              <div style={{ backgroundColor: '#f8fafc', borderLeft: '4px solid #ea580c', borderTop: '1px solid #e2e8f0', borderRight: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '1.05rem' }}>{enrollingProgram.title}</div>
                <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '0.25rem', display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                  <span><strong>Programme Code:</strong> {enrollingProgram.code}</span>
                  <span><strong>Duration:</strong> {enrollingProgram.duration_hours || 40} Hours</span>
                  <span><strong>Fee:</strong> {enrollingProgram.fee === 0 ? 'Free (Govt Subsidized)' : `â‚¹${enrollingProgram.fee}`}</span>
                </div>
              </div>

              {enrolmentErrorMsg && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                  {enrolmentErrorMsg}
                </div>
              )}
              {enrolmentSuccessMsg && (
                <div style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                  {enrolmentSuccessMsg}
                </div>
              )}

              {/* Verified Citizen Profile Autofill Notice */}
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.6rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: '#166534' }}>
                <CheckCircle2 size={16} style={{ color: '#16a34a', flexShrink: 0 }} />
                <span><strong>Profile Autofill Active:</strong> Your verified profile details have been prefilled below. Review and adjust if necessary.</span>
              </div>

              {/* SECTION A: Personal Information */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  A. Personal Information
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Full Name *</label>
                    <input type="text" className="form-control" value={appFullName} onChange={(e) => setAppFullName(e.target.value)} placeholder="Full Name" required />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Citizen ID (Read-only)</label>
                    <input type="text" className="form-control" value={citizenRef || 'CIT-2026-X'} readOnly disabled style={{ backgroundColor: '#f8fafc', cursor: 'not-allowed', color: '#64748b' }} />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Email Address *</label>
                    <input type="email" className="form-control" value={appEmail} onChange={(e) => setAppEmail(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Mobile Number *</label>
                    <input type="tel" className="form-control" value={appPhone} onChange={(e) => setAppPhone(e.target.value)} required />
                  </div>
                </div>
              </div>

              {/* SECTION B: Basic Location */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  B. Basic Location
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>City / District *</label>
                    <input type="text" className="form-control" value={appCity} onChange={(e) => setAppCity(e.target.value)} placeholder="e.g. Bengaluru, Mysuru, Hubballi" required />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>PIN Code *</label>
                    <input type="text" className="form-control" value={appPincode} onChange={(e) => setAppPincode(e.target.value)} placeholder="6-digit PIN" maxLength={6} required />
                  </div>
                </div>
              </div>

              {/* SECTION C: Basic Eligibility Information */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  C. Basic Eligibility Information
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Highest Educational Qualification *</label>
                    <select className="form-control" value={appEducation} onChange={(e) => setAppEducation(e.target.value)}>
                      <option value="Secondary School (10th)">Secondary School (10th)</option>
                      <option value="Higher Secondary (12th / PUC)">Higher Secondary (12th / PUC)</option>
                      <option value="Diploma / Polytechnic">Diploma / Polytechnic</option>
                      <option value="Bachelor of Engineering / Science">Bachelor of Engineering / Science</option>
                      <option value="Bachelor of Commerce / Arts">Bachelor of Commerce / Arts</option>
                      <option value="Master of Technology / Science">Master of Technology / Science</option>
                      <option value="Other / Vocational">Other / Vocational</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Employment Status *</label>
                    <select className="form-control" value={appEmploymentStatus} onChange={(e) => setAppEmploymentStatus(e.target.value)}>
                      <option value="Job Seeker">Job Seeker</option>
                      <option value="Student / Scholar">Student / Scholar</option>
                      <option value="Employed">Employed</option>
                      <option value="Self-Employed / Freelancer">Self-Employed / Freelancer</option>
                      <option value="Apprentice">Apprentice</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* SECTION D: Training Selection */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  D. Training Selection
                </h4>
                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Selected Programme (Populated from your choice)</label>
                    <input type="text" className="form-control" value={enrollingProgram.title} readOnly disabled style={{ backgroundColor: '#f8fafc', color: '#0f2444', fontWeight: 600 }} />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Assigned Training Centre (Derived from database relationship)</label>
                    <input
                      type="text"
                      className="form-control"
                      value={enrollingProgram.centre?.name || enrollingProgram.centre_name || 'Accredited Training Centre'}
                      readOnly
                      disabled
                      style={{ backgroundColor: '#f8fafc', color: '#1e293b', fontWeight: 600 }}
                    />
                    {enrollingProgram.centre?.location && (
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                        Location: {enrollingProgram.centre.location} ({enrollingProgram.centre.district})
                      </div>
                    )}
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Available Training Batch * (Real-time seat capacity checked)</label>
                    <select
                      className="form-control"
                      value={selectedBatchId || ''}
                      onChange={(e) => setSelectedBatchId(Number(e.target.value))}
                      required
                    >
                      {enrollingProgram.batches && enrollingProgram.batches.length > 0 ? (
                        enrollingProgram.batches.map((b: any) => (
                          <option key={b.id} value={b.id} disabled={b.available_seats <= 0}>
                            {b.batch_name} ({b.timings} - {b.mode}) â€” {b.available_seats} / {b.total_seats} seats available {b.available_seats <= 0 ? '(FULL)' : ''}
                          </option>
                        ))
                      ) : (
                        <option value="">No open batches available</option>
                      )}
                    </select>
                  </div>

                  {/* Preferred Delivery Mode only if programme supports choice */}
                  {(!enrollingProgram.mode || enrollingProgram.mode.toLowerCase() === 'hybrid') && (
                    <div className="form-group">
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Preferred Delivery Mode</label>
                      <select className="form-control" value={appPrefMode} onChange={(e) => setAppPrefMode(e.target.value)}>
                        <option value="Hybrid">Hybrid (Online Lectures + Hands-on Lab)</option>
                        <option value="Online">Online Interactive</option>
                        <option value="Classroom">Classroom Full-Time</option>
                      </select>
                    </div>
                  )}
                </div>
              </div>

              {/* SECTION E: Declaration */}
              <div style={{ border: '1px solid #fed7aa', backgroundColor: '#fff7ed', borderRadius: '8px', padding: '1.15rem' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#9a3412', marginBottom: '0.4rem' }}>
                  E. Declaration & Confirmation
                </h4>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <input
                    type="checkbox"
                    id="enrolDeclaration"
                    checked={appDeclarationAgreed}
                    onChange={(e) => setAppDeclarationAgreed(e.target.checked)}
                    style={{ marginTop: '0.25rem', width: '18px', height: '18px', cursor: 'pointer' }}
                    required
                  />
                  <label htmlFor="enrolDeclaration" style={{ fontSize: '0.82rem', color: '#7c2d12', lineHeight: 1.45, cursor: 'pointer', margin: 0 }}>
                    I hereby confirm that all submitted details are accurate and complete to the best of my knowledge, and I agree to be contacted by the assigned Training Centre regarding my application and batch admission formalities.
                  </label>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.25rem', borderTop: '1px solid #e2e8f0', paddingTop: '0.85rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setEnrollingProgram(null)} disabled={enrolSubmitting}>
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn-primary-orange"
                  onClick={handleEnrolmentSubmit}
                  disabled={enrolSubmitting || !appDeclarationAgreed || (enrollingProgram.batches && enrollingProgram.batches.length > 0 && !selectedBatchId)}
                >
                  {enrolSubmitting ? 'Submitting Application...' : 'Submit Training Application'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}"""

content = content[:start_pos] + simplified_modal + content[end_pos:]

with open(app_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Simplified Application Form successfully injected into App.tsx!")
