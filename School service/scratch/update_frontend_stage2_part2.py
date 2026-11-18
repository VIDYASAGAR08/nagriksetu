import re

dashboard_path = 'C:/Users/callm/nagriksetu/frontend/src/pages/admin/InstitutionAdminDashboard.jsx'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Target is the Administrator Action Panel header and parent closing div around line 3393
target_str = """                  </div>
                </div>

                {/* =================================================================
                    ADMINISTRATOR ACTION PANEL
                    ================================================================="""

replacement_str = """                  </div>
                </div>

                {/* =================================================================
                    PART 4: SECTION A — STAGE 2 DETAILED STUDENT INFORMATION
                    ================================================================= */}
                <div style={{ background: '#FFFFFF', borderRadius: '8px', border: '1px solid #D0D5DD', padding: '1.25rem', marginBottom: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.03)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <h4 style={{ margin: 0, color: '#102B46', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span>📝</span> Stage 2 Detailed Demographic & Academic Dossier
                    </h4>
                    {selectedApp.stage2_submitted ? (
                      <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 700 }}>
                        ✓ Dossier Submitted {selectedApp.stage2_details?.submitted_at ? new Date(selectedApp.stage2_details.submitted_at).toLocaleDateString() : ''}
                      </span>
                    ) : (
                      <span style={{ background: '#F8F9FA', color: '#667085', border: '1px solid #E2E8F0', padding: '0.2rem 0.6rem', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 600 }}>
                        ⏳ Awaiting Parent Submission
                      </span>
                    )}
                  </div>

                  {selectedApp.stage2_submitted && selectedApp.stage2_details ? (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', background: '#F8F9FA', padding: '1rem', borderRadius: '6px', border: '1px solid #EAECF0' }}>
                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Date of Birth (DOB)</div>
                        <div style={{ color: '#102B46', fontWeight: 700, fontSize: '0.875rem', marginTop: '0.15rem' }}>
                          {selectedApp.stage2_details.date_of_birth ? new Date(selectedApp.stage2_details.date_of_birth).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'Not provided'}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Gender / Blood Group</div>
                        <div style={{ color: '#102B46', fontWeight: 700, fontSize: '0.875rem', marginTop: '0.15rem', textTransform: 'capitalize' }}>
                          {selectedApp.stage2_details.gender || 'N/A'} {selectedApp.stage2_details.blood_group ? `(${selectedApp.stage2_details.blood_group})` : ''}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Previous Institution / School</div>
                        <div style={{ color: '#102B46', fontWeight: 700, fontSize: '0.875rem', marginTop: '0.15rem' }}>
                          {selectedApp.stage2_details.previous_institution_name || 'N/A'}
                          {selectedApp.stage2_details.previous_institution_location ? ` (${selectedApp.stage2_details.previous_institution_location})` : ''}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Previous Standard / Class / Qualifying Exam</div>
                        <div style={{ color: '#102B46', fontWeight: 700, fontSize: '0.875rem', marginTop: '0.15rem' }}>
                          {selectedApp.stage2_details.previous_standard_or_degree || 'N/A'}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Previous Board / University</div>
                        <div style={{ color: '#102B46', fontWeight: 700, fontSize: '0.875rem', marginTop: '0.15rem' }}>
                          {selectedApp.stage2_details.previous_board || 'N/A'}
                        </div>
                      </div>

                      <div>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Previous Marks / Score Percentage</div>
                        <div style={{ color: '#155EEF', fontWeight: 800, fontSize: '0.9rem', marginTop: '0.15rem' }}>
                          {selectedApp.stage2_details.previous_marks_percentage != null ? `${selectedApp.stage2_details.previous_marks_percentage}%` : 'N/A'}
                        </div>
                      </div>

                      <div style={{ gridColumn: '1 / -1', borderTop: '1px solid #E2E8F0', paddingTop: '0.65rem', marginTop: '0.2rem' }}>
                        <div style={{ fontSize: '0.75rem', color: '#667085', fontWeight: 600 }}>Emergency Contact</div>
                        <div style={{ color: '#102B46', fontWeight: 700, fontSize: '0.85rem', marginTop: '0.15rem' }}>
                          {selectedApp.stage2_details.emergency_contact_name || 'N/A'}
                          {selectedApp.stage2_details.emergency_contact_phone ? ` — 📞 ${selectedApp.stage2_details.emergency_contact_phone}` : ''}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ padding: '1rem', background: '#F8F9FA', borderRadius: '6px', border: '1px dashed #D0D5DD', color: '#667085', fontSize: '0.85rem', textAlign: 'center' }}>
                      Stage 2 detailed demographic and academic records have not been submitted yet. The parent completes this stage after Stage 1 approval.
                    </div>
                  )}
                </div>

                {/* =================================================================
                    PART 4: SECTION B & C — UPLOADED DOCUMENTS & VERIFICATION DESK
                    ================================================================= */}
                <div style={{ background: '#FFFFFF', borderRadius: '8px', border: '1px solid #D0D5DD', padding: '1.25rem', marginBottom: '1.5rem', boxShadow: '0 1px 2px rgba(0,0,0,0.03)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div>
                      <h4 style={{ margin: 0, color: '#102B46', fontSize: '0.95rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span>📁</span> Uploaded Verification Documents & Certificates ({selectedApp.documents?.length || 0})
                      </h4>
                      <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.2rem' }}>
                        Inspect, preview, download, and verify applicant supporting certificates individually.
                      </div>
                    </div>

                    {/* Verification Progress Tally */}
                    {selectedApp.documents && selectedApp.documents.length > 0 && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        <span style={{
                          background: (selectedApp.verified_documents_count === selectedApp.total_documents_count && selectedApp.total_documents_count > 0) ? '#ECFDF3' : '#EFF4FF',
                          color: (selectedApp.verified_documents_count === selectedApp.total_documents_count && selectedApp.total_documents_count > 0) ? '#027A48' : '#155EEF',
                          border: (selectedApp.verified_documents_count === selectedApp.total_documents_count && selectedApp.total_documents_count > 0) ? '1px solid #A6F4C5' : '1px solid #B2DDFF',
                          padding: '0.25rem 0.65rem',
                          borderRadius: '12px',
                          fontSize: '0.78rem',
                          fontWeight: 700
                        }}>
                          {selectedApp.verified_documents_count || 0} of {selectedApp.total_documents_count || selectedApp.documents.length} Verified
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Documents List */}
                  {selectedApp.documents && selectedApp.documents.length > 0 ? (
                    <div style={{ border: '1px solid #EAECF0', borderRadius: '6px', overflow: 'hidden' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.825rem', textAlign: 'left' }}>
                        <thead>
                          <tr style={{ background: '#F8F9FA', borderBottom: '1px solid #EAECF0', color: '#475467' }}>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Certificate / Document</th>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Original Filename & Size</th>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Uploaded Date</th>
                            <th style={{ padding: '0.6rem 0.75rem' }}>Status</th>
                            <th style={{ padding: '0.6rem 0.75rem', textAlign: 'right' }}>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedApp.documents.map((doc) => {
                            const typeLabels = {
                              birth_certificate: 'Birth Certificate',
                              transfer_certificate: 'Transfer Certificate (TC)',
                              previous_marks_card: 'Previous Marks Card / Report',
                              passport_photo: 'Passport Photograph',
                              caste_certificate: 'Caste / Category Certificate',
                              income_certificate: 'Income Certificate',
                              aadhaar_card: 'Aadhaar Card / ID Proof',
                              conduct_certificate: 'Conduct Certificate'
                            }
                            const typeLabel = typeLabels[doc.document_type] || doc.document_type.replace(/_/g, ' ')
                            const sizeKb = doc.file_size_bytes ? (doc.file_size_bytes / 1024).toFixed(1) + ' KB' : 'N/A'

                            return (
                              <tr key={doc.document_id} style={{ borderBottom: '1px solid #F2F4F7' }}>
                                <td style={{ padding: '0.6rem 0.75rem' }}>
                                  <div style={{ fontWeight: 700, color: '#102B46' }}>{typeLabel}</div>
                                  <div style={{ fontSize: '0.72rem', color: '#667085', fontFamily: 'monospace' }}>{doc.document_type}</div>
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem', color: '#344054' }}>
                                  <div style={{ fontWeight: 600 }}>{doc.file_name}</div>
                                  <div style={{ fontSize: '0.72rem', color: '#98A2B3' }}>{sizeKb} • {doc.mime_type || 'binary'}</div>
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem', color: '#667085', fontSize: '0.78rem' }}>
                                  {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleDateString() : 'N/A'}
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem' }}>
                                  {doc.verification_status === 'verified' && (
                                    <span style={{ background: '#ECFDF3', color: '#027A48', border: '1px solid #A6F4C5', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      ✓ Verified
                                    </span>
                                  )}
                                  {doc.verification_status === 'pending' && (
                                    <span style={{ background: '#FEF0C7', color: '#B54708', border: '1px solid #FEDF89', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      ⏳ Pending Review
                                    </span>
                                  )}
                                  {doc.verification_status === 'reupload_requested' && (
                                    <span style={{ background: '#F9F5FF', color: '#6941C6', border: '1px solid #D6BBFB', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      🔄 Replacement Requested
                                    </span>
                                  )}
                                  {doc.verification_status === 'rejected' && (
                                    <span style={{ background: '#FEF3F2', color: '#B42318', border: '1px solid #FECDCA', padding: '0.2rem 0.55rem', borderRadius: '12px', fontSize: '0.72rem', fontWeight: 700 }}>
                                      ✕ Rejected
                                    </span>
                                  )}
                                  {doc.verification_notes && (
                                    <div style={{ fontSize: '0.72rem', color: '#475467', fontStyle: 'italic', marginTop: '0.25rem' }}>
                                      "{doc.verification_notes}"
                                    </div>
                                  )}
                                </td>

                                <td style={{ padding: '0.6rem 0.75rem', textAlign: 'right' }}>
                                  <div style={{ display: 'inline-flex', gap: '0.35rem', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                                    {/* Preview Button */}
                                    <button
                                      type="button"
                                      onClick={() => setPreviewDoc(doc)}
                                      title="Preview Document"
                                      style={{
                                        background: '#EFF4FF',
                                        color: '#155EEF',
                                        border: '1px solid #B2DDFF',
                                        borderRadius: '4px',
                                        padding: '0.25rem 0.5rem',
                                        fontSize: '0.72rem',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                      }}
                                    >
                                      👁️ Preview
                                    </button>

                                    {/* Download Button */}
                                    <a
                                      href={`${doc.download_url}?token=${token}`}
                                      target="_blank"
                                      rel="noreferrer"
                                      download={doc.file_name}
                                      title="Download Document"
                                      style={{
                                        background: '#F8F9FA',
                                        color: '#344054',
                                        border: '1px solid #D0D5DD',
                                        borderRadius: '4px',
                                        padding: '0.25rem 0.5rem',
                                        fontSize: '0.72rem',
                                        fontWeight: 600,
                                        textDecoration: 'none',
                                        display: 'inline-block'
                                      }}
                                    >
                                      ⬇️ Download
                                    </a>

                                    {/* Verify Button */}
                                    {doc.verification_status !== 'verified' && (
                                      <button
                                        type="button"
                                        onClick={() => handleQuickVerifyDoc(doc)}
                                        title="Mark Verified"
                                        style={{
                                          background: '#ECFDF3',
                                          color: '#027A48',
                                          border: '1px solid #A6F4C5',
                                          borderRadius: '4px',
                                          padding: '0.25rem 0.5rem',
                                          fontSize: '0.72rem',
                                          fontWeight: 700,
                                          cursor: 'pointer'
                                        }}
                                      >
                                        ✓ Verify
                                      </button>
                                    )}

                                    {/* Request Replacement */}
                                    <button
                                      type="button"
                                      onClick={() => setDocActionModal({ doc, actionType: 'reupload_requested', notes: '' })}
                                      title="Request Replacement Document"
                                      style={{
                                        background: '#F9F5FF',
                                        color: '#6941C6',
                                        border: '1px solid #D6BBFB',
                                        borderRadius: '4px',
                                        padding: '0.25rem 0.5rem',
                                        fontSize: '0.72rem',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                      }}
                                    >
                                      🔄 Replace
                                    </button>

                                    {/* Reject Document */}
                                    {doc.verification_status !== 'rejected' && (
                                      <button
                                        type="button"
                                        onClick={() => setDocActionModal({ doc, actionType: 'rejected', notes: '' })}
                                        title="Reject Document"
                                        style={{
                                          background: '#FEF3F2',
                                          color: '#B42318',
                                          border: '1px solid #FECDCA',
                                          borderRadius: '4px',
                                          padding: '0.25rem 0.5rem',
                                          fontSize: '0.72rem',
                                          fontWeight: 600,
                                          cursor: 'pointer'
                                        }}
                                      >
                                        ✕ Reject
                                      </button>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            )
                          })}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div style={{ padding: '1rem', background: '#F8F9FA', borderRadius: '6px', border: '1px dashed #D0D5DD', color: '#667085', fontSize: '0.85rem', textAlign: 'center' }}>
                      No supporting documents uploaded yet.
                    </div>
                  )}
                </div>

                {/* =================================================================
                    ADMINISTRATOR ACTION PANEL (STAGE 1 vs STAGE 2 DIFFERENTIATED)
                    ================================================================="""

# Replace in text
if target_str in text:
    text = text.replace(target_str, replacement_str, 1)
    print("Replaced target_str LF successfully!")
else:
    target_crlf = target_str.replace('\n', '\r\n')
    if target_crlf in text:
        text = text.replace(target_crlf, replacement_str.replace('\n', '\r\n'), 1)
        print("Replaced target_str CRLF successfully!")
    else:
        print("FAILED to find target_str!")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved stage 2 of frontend update.")
