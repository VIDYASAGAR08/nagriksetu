import React, { useState, useEffect } from 'react'
import { apiGet, apiPost } from '../../utils/api.js'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'

export default function Stage2AdmissionModal({ applicationId, isOpen, onClose, onSuccess }) {
  const [eligibility, setEligibility] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [currentStep, setCurrentStep] = useState(1) // 1: Demographics, 2: Previous Academic, 3: Documents, 4: Success

  // Form State
  const [dob, setDob] = useState('')
  const [gender, setGender] = useState('male')
  const [bloodGroup, setBloodGroup] = useState('O+')
  const [emergencyName, setEmergencyName] = useState('')
  const [emergencyPhone, setEmergencyPhone] = useState('')

  const [prevSchool, setPrevSchool] = useState('')
  const [prevLocation, setPrevLocation] = useState('')
  const [prevClass, setPrevClass] = useState('')
  const [prevBoard, setPrevBoard] = useState('Karnataka State Board (KSEAB)')
  const [prevMarks, setPrevMarks] = useState('')

  // Documents State
  const [documents, setDocuments] = useState([])
  const [uploadingDocType, setUploadingDocType] = useState(null)
  const [uploadError, setUploadError] = useState(null)

  // Submission State
  const [submittingForm, setSubmittingForm] = useState(false)
  const [formError, setFormError] = useState(null)

  const loadData = async () => {
    if (!applicationId || !isOpen) return
    try {
      setLoading(true)
      setError(null)
      const res = await apiGet(`/admissions/applications/${applicationId}/stage2-eligibility`)
      setEligibility(res)
      setDocuments(res.uploaded_documents || [])

      if (res.stage2_submission) {
        const sub = res.stage2_submission
        setDob(sub.date_of_birth || '')
        setGender(sub.gender || 'male')
        setBloodGroup(sub.blood_group || 'O+')
        setEmergencyName(sub.emergency_contact_name || '')
        setEmergencyPhone(sub.emergency_contact_phone || '')
        setPrevSchool(sub.previous_institution_name || '')
        setPrevLocation(sub.previous_institution_location || '')
        setPrevClass(sub.previous_standard_or_degree || '')
        setPrevBoard(sub.previous_board || 'Karnataka State Board (KSEAB)')
        setPrevMarks(sub.previous_marks_percentage ? String(sub.previous_marks_percentage) : '')
      }
    } catch (err) {
      setError(err.message || 'Unable to access Stage 2 admission dossier.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [applicationId, isOpen])

  if (!isOpen) return null

  // File Upload Handler
  const handleFileUpload = (docType, e) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10 MB limit.')
      return
    }

    setUploadingDocType(docType)
    setUploadError(null)

    const reader = new FileReader()
    reader.onload = async () => {
      try {
        const base64Data = reader.result.split(',')[1]
        const payload = {
          document_type: docType,
          file_name: file.name,
          file_data_base64: base64Data,
          mime_type: file.type || 'application/pdf'
        }
        await apiPost(`/admissions/applications/${applicationId}/documents`, payload)
        // Refresh documents list
        const docsRes = await apiGet(`/admissions/applications/${applicationId}/documents`)
        setDocuments(docsRes)
      } catch (err) {
        setUploadError(`Failed to upload ${file.name}: ${err.message}`)
      } finally {
        setUploadingDocType(null)
      }
    }
    reader.readAsDataURL(file)
  }

  const handleSubmitDossier = async (e) => {
    e.preventDefault()
    setSubmittingForm(true)
    setFormError(null)

    if (!dob) {
      setFormError('Please provide Date of Birth.')
      setSubmittingForm(false)
      return
    }
    if (!emergencyName.trim() || emergencyPhone.replace(/\D/g, '').length < 10) {
      setFormError('Please provide emergency contact name and valid 10-digit mobile number.')
      setSubmittingForm(false)
      return
    }

    const payload = {
      date_of_birth: dob,
      gender: gender,
      blood_group: bloodGroup,
      previous_institution_name: prevSchool.trim() || null,
      previous_institution_location: prevLocation.trim() || null,
      previous_standard_or_degree: prevClass.trim() || null,
      previous_board: prevBoard.trim() || null,
      previous_marks_percentage: prevMarks ? parseFloat(prevMarks) : null,
      emergency_contact_name: emergencyName.trim(),
      emergency_contact_phone: emergencyPhone.replace(/\D/g, '')
    }

    try {
      await apiPost(`/admissions/applications/${applicationId}/stage2-submit`, payload)
      setCurrentStep(3) // Advance to document uploads step
    } catch (err) {
      setFormError(err.message || 'Failed to submit Stage 2 dossier.')
    } finally {
      setSubmittingForm(false)
    }
  }

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(15, 23, 42, 0.72)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '1rem'
    }}>
      <div style={{
        background: '#ffffff',
        borderRadius: '16px',
        width: '100%',
        maxWidth: '760px',
        maxHeight: '92vh',
        overflowY: 'auto',
        boxShadow: '0 20px 45px rgba(0, 0, 0, 0.25)',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #065F46 0%, #047857 100%)',
          color: '#ffffff',
          padding: '1.25rem 1.75rem',
          borderTopLeftRadius: '16px',
          borderTopRightRadius: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <span style={{
                background: 'rgba(255,255,255,0.25)',
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                textTransform: 'uppercase'
              }}>
                Stage 2 Detailed Dossier
              </span>
              <span style={{ fontSize: '0.8rem', color: '#A7F3D0' }}>• Document Verification</span>
            </div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800 }}>
              {eligibility?.institution_name || 'Detailed Admission Form'} ({applicationId})
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              color: '#ffffff',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              fontSize: '1.1rem',
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>

        {/* Stepper Header */}
        {currentStep < 4 && !loading && !error && (
          <div style={{
            display: 'flex',
            background: '#F8FAFC',
            borderBottom: '1px solid #E2E8F0',
            padding: '0.75rem 1.75rem',
            gap: '1rem',
            alignItems: 'center'
          }}>
            {[
              { num: 1, label: 'Demographics & Identity' },
              { num: 2, label: 'Previous Academic Record' },
              { num: 3, label: 'Document Uploads' }
            ].map(step => (
              <div key={step.num} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.85rem',
                fontWeight: currentStep === step.num ? 700 : 500,
                color: currentStep === step.num ? '#065F46' : currentStep > step.num ? '#059669' : '#94A3B8'
              }}>
                <span style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: currentStep === step.num ? '#065F46' : currentStep > step.num ? '#059669' : '#CBD5E1',
                  color: '#ffffff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.75rem',
                  fontWeight: 700
                }}>
                  {currentStep > step.num ? '✓' : step.num}
                </span>
                <span>{step.label}</span>
                {step.num < 3 && <span style={{ color: '#CBD5E1', margin: '0 0.25rem' }}>→</span>}
              </div>
            ))}
          </div>
        )}

        {/* Body Content */}
        <div style={{ padding: '1.75rem', flex: 1 }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}>
              <LoadingSpinner />
              <p style={{ marginTop: '0.75rem', color: '#64748B' }}>Validating Stage 1 approval and eligibility...</p>
            </div>
          ) : error ? (
            <div style={{ background: '#FEF3F2', border: '1px solid #FECDCA', padding: '1.5rem', borderRadius: '10px', color: '#B42318' }}>
              <h3 style={{ margin: '0 0 0.5rem 0' }}>Stage 2 Access Restricted</h3>
              <p style={{ margin: 0, fontSize: '0.9rem', lineHeight: 1.5 }}>{error}</p>
              <div style={{ marginTop: '1.25rem' }}>
                <button onClick={onClose} style={{ background: '#B42318', color: '#ffffff', border: 'none', padding: '0.5rem 1.25rem', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>
                  Close
                </button>
              </div>
            </div>
          ) : (
            <div>
              {formError && (
                <div style={{ background: '#FEF3F2', border: '1px solid #FECDCA', padding: '0.75rem 1rem', borderRadius: '8px', color: '#B42318', marginBottom: '1.25rem', fontSize: '0.85rem' }}>
                  ⚠️ {formError}
                </div>
              )}

              {/* STEP 1: Demographics */}
              {currentStep === 1 && (
                <div>
                  <h3 style={{ margin: '0 0 0.4rem 0', color: '#102B46', fontSize: '1.1rem', fontWeight: 700 }}>
                    Student Demographic Details
                  </h3>
                  <p style={{ margin: '0 0 1.25rem 0', color: '#64748B', fontSize: '0.85rem' }}>
                    Required for official enrolment record association and statutory register entry.
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Date of Birth (YYYY-MM-DD) *
                      </label>
                      <input
                        type="date"
                        value={dob}
                        onChange={(e) => setDob(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Gender *
                      </label>
                      <select
                        value={gender}
                        onChange={(e) => setGender(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      >
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Blood Group
                      </label>
                      <select
                        value={bloodGroup}
                        onChange={(e) => setBloodGroup(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      >
                        <option value="A+">A+</option>
                        <option value="A-">A-</option>
                        <option value="B+">B+</option>
                        <option value="B-">B-</option>
                        <option value="O+">O+</option>
                        <option value="O-">O-</option>
                        <option value="AB+">AB+</option>
                        <option value="AB-">AB-</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Emergency Contact Person *
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Suresh Gowda"
                        value={emergencyName}
                        onChange={(e) => setEmergencyName(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div style={{ gridColumn: 'span 2' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Emergency Contact Mobile Number (10 digits) *
                      </label>
                      <input
                        type="tel"
                        maxLength={10}
                        placeholder="e.g. 9876543210"
                        value={emergencyPhone}
                        onChange={(e) => setEmergencyPhone(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                    <button
                      type="button"
                      onClick={() => {
                        if (!dob || !emergencyName.trim() || emergencyPhone.replace(/\D/g, '').length < 10) {
                          setFormError('Please complete Date of Birth and Emergency Contact coordinates.')
                        } else {
                          setFormError(null)
                          setCurrentStep(2)
                        }
                      }}
                      style={{ background: '#065F46', color: '#ffffff', border: 'none', padding: '0.65rem 1.5rem', borderRadius: '8px', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer' }}
                    >
                      Next: Previous Academic History →
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 2: Previous Academic Record */}
              {currentStep === 2 && (
                <div>
                  <h3 style={{ margin: '0 0 0.4rem 0', color: '#102B46', fontSize: '1.1rem', fontWeight: 700 }}>
                    Previous Schooling & Academic History
                  </h3>
                  <p style={{ margin: '0 0 1.25rem 0', color: '#64748B', fontSize: '0.85rem' }}>
                    Enter previous school details and board credentials for qualifying verification.
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                    <div style={{ gridColumn: 'span 2' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Previous School / Institution Name
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Kendriya Vidyalaya Malleshwaram"
                        value={prevSchool}
                        onChange={(e) => setPrevSchool(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Previous Institution Location / District
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Bengaluru Urban"
                        value={prevLocation}
                        onChange={(e) => setPrevLocation(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Standard / Degree Completed
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Standard 4 / Class 10 / SSLC"
                        value={prevClass}
                        onChange={(e) => setPrevClass(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Examination Board / Council
                      </label>
                      <select
                        value={prevBoard}
                        onChange={(e) => setPrevBoard(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      >
                        <option value="Karnataka State Board (KSEAB)">Karnataka State Board (KSEAB)</option>
                        <option value="Central Board of Secondary Education (CBSE)">Central Board of Secondary Education (CBSE)</option>
                        <option value="Council for the Indian School Certificate Examinations (ICSE)">ICSE</option>
                        <option value="Department of Pre-University Education Karnataka">DPUE Karnataka</option>
                        <option value="Other Recognized State/National Board">Other Recognized Board</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Previous Marks / Aggregate Percentage (%)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        max="100"
                        placeholder="e.g. 88.5"
                        value={prevMarks}
                        onChange={(e) => setPrevMarks(e.target.value)}
                        style={{ width: '100%', padding: '0.6rem 0.75rem', borderRadius: '6px', border: '1px solid #CBD5E1', fontSize: '0.875rem' }}
                      />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
                    <button
                      type="button"
                      onClick={() => setCurrentStep(1)}
                      style={{ background: '#F1F5F9', color: '#475569', border: '1px solid #CBD5E1', padding: '0.65rem 1.25rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
                    >
                      ← Back to Demographics
                    </button>
                    <button
                      type="button"
                      onClick={handleSubmitDossier}
                      disabled={submittingForm}
                      style={{ background: '#065F46', color: '#ffffff', border: 'none', padding: '0.65rem 1.5rem', borderRadius: '8px', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer' }}
                    >
                      {submittingForm ? 'Saving Dossier...' : 'Save Dossier & Proceed to Documents →'}
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 3: Document Uploads Checklist */}
              {currentStep === 3 && (
                <div>
                  <h3 style={{ margin: '0 0 0.4rem 0', color: '#102B46', fontSize: '1.1rem', fontWeight: 700 }}>
                    Upload Required Verification Documents
                  </h3>
                  <p style={{ margin: '0 0 1.25rem 0', color: '#64748B', fontSize: '0.85rem' }}>
                    Uploaded documents are securely processed and verified by authorized institution admission officers.
                  </p>

                  {uploadError && (
                    <div style={{ background: '#FEF3F2', border: '1px solid #FECDCA', padding: '0.75rem 1rem', borderRadius: '8px', color: '#B42318', marginBottom: '1rem', fontSize: '0.85rem' }}>
                      ⚠️ {uploadError}
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', marginBottom: '1.5rem' }}>
                    {(eligibility?.required_documents || []).map((reqDoc, idx) => {
                      const typeDocs = documents.filter(d => d.document_type === reqDoc.document_type)
                      const uploaded = typeDocs.length > 0 ? typeDocs[typeDocs.length - 1] : null
                      const isRejected = uploaded && (uploaded.verification_status === 'rejected' || uploaded.verification_status === 'reupload_requested')
                      const isVerified = uploaded && uploaded.verification_status === 'verified'
                      return (
                        <div key={idx} style={{
                          background: isRejected ? '#FEF3F2' : isVerified ? '#F0FDF4' : uploaded ? '#EFF8FF' : '#F8FAFC',
                          border: `1px solid ${isRejected ? '#FECDCA' : isVerified ? '#BBF7D0' : uploaded ? '#B2DDFF' : '#E2E8F0'}`,
                          borderRadius: '10px',
                          padding: '1rem 1.25rem',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          flexWrap: 'wrap',
                          gap: '1rem'
                        }}>
                          <div style={{ flex: 1, minWidth: '260px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                              <strong style={{ color: '#102B46', fontSize: '0.9rem' }}>{reqDoc.label}</strong>
                              {reqDoc.is_mandatory && (
                                <span style={{ background: '#FEF3F2', color: '#B42318', fontSize: '0.7rem', fontWeight: 700, padding: '0.1rem 0.35rem', borderRadius: '4px' }}>
                                  Mandatory
                                </span>
                              )}
                            </div>
                            {uploaded ? (
                              <div style={{ fontSize: '0.8rem', color: isRejected ? '#B42318' : isVerified ? '#15803D' : '#175CD3', marginTop: '0.25rem' }}>
                                📄 {uploaded.file_name} ({(uploaded.file_size_bytes / 1024).toFixed(1)} KB) • Status: <strong>{uploaded.verification_status?.toUpperCase()}</strong>
                                {uploaded.version && uploaded.version > 1 && (
                                  <span style={{ marginLeft: '0.4rem', fontSize: '0.7rem', background: '#F8FAFC', padding: '0.1rem 0.35rem', borderRadius: '4px', border: '1px solid #CBD5E1' }}>
                                    v{uploaded.version}
                                  </span>
                                )}
                                {uploaded.verification_notes && (
                                  <div style={{ color: isRejected ? '#B42318' : '#334155', marginTop: '0.2rem', background: isRejected ? '#FFF5F5' : '#FFFFFF', padding: '0.25rem 0.5rem', borderRadius: '4px', border: isRejected ? '1px solid #FECDCA' : '1px solid #E2E8F0', fontSize: '0.76rem' }}>
                                    <strong>{isRejected ? 'Rejection Reason:' : 'Note:'}</strong> {uploaded.verification_notes}
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.78rem', color: '#64748B', marginTop: '0.2rem' }}>
                                PDF, JPG or PNG (Max 10 MB).
                              </div>
                            )}
                          </div>

                          <div>
                            <label style={{
                              background: isRejected ? '#D92D20' : uploaded ? '#ffffff' : '#065F46',
                              color: isRejected ? '#ffffff' : uploaded ? '#065F46' : '#ffffff',
                              border: `1px solid ${isRejected ? '#D92D20' : uploaded ? '#A7F3D0' : '#065F46'}`,
                              padding: '0.45rem 1rem',
                              borderRadius: '6px',
                              fontSize: '0.85rem',
                              fontWeight: 600,
                              cursor: uploadingDocType === reqDoc.document_type ? 'not-allowed' : 'pointer',
                              display: 'inline-block'
                            }}>
                              {uploadingDocType === reqDoc.document_type ? 'Uploading...' : isRejected ? 'Upload Replacement File' : uploaded ? 'Replace File' : 'Upload File'}
                              <input
                                type="file"
                                accept=".pdf,.png,.jpg,.jpeg"
                                onChange={(e) => handleFileUpload(reqDoc.document_type, e)}
                                disabled={uploadingDocType === reqDoc.document_type}
                                style={{ display: 'none' }}
                              />
                            </label>
                          </div>
                        </div>
                      )
                    })}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <button
                      type="button"
                      onClick={() => setCurrentStep(2)}
                      style={{ background: '#F1F5F9', color: '#475569', border: '1px solid #CBD5E1', padding: '0.65rem 1.25rem', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
                    >
                      ← Back to Academic History
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        if (onSuccess) onSuccess()
                        onClose()
                      }}
                      style={{ background: '#059669', color: '#ffffff', border: 'none', padding: '0.65rem 1.75rem', borderRadius: '8px', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer' }}
                    >
                      Complete & Return to Dashboard ✓
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
