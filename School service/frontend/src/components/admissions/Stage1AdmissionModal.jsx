import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiGet, apiPost } from '../../utils/api.js'
import { useAuth } from '../../contexts/AuthContext.jsx'
import LoadingSpinner from '../ui/LoadingSpinner.jsx'

export default function Stage1AdmissionModal({ institutionId, institutionName, isOpen, onClose }) {
  const [config, setConfig] = useState(null)
  const [loadingConfig, setLoadingConfig] = useState(true)
  const [errorConfig, setErrorConfig] = useState(null)

  // Multi-step form state (1: Academic Choices, 2: Applicant & Parent Details, 3: Review, 4: Success)
  const [currentStep, setCurrentStep] = useState(1)

  // Form inputs
  const [educationLevel, setEducationLevel] = useState('')
  const [divisionId, setDivisionId] = useState('')
  const [standardApplied, setStandardApplied] = useState('1')
  const [puStream, setPuStream] = useState('')
  const [puCombination, setPuCombination] = useState('')
  const [selectedProgramId, setSelectedProgramId] = useState('')
  const [firstLanguage, setFirstLanguage] = useState('Kannada')
  const [secondLanguage, setSecondLanguage] = useState('English')

  const [applicantName, setApplicantName] = useState('')
  const [parentName, setParentName] = useState('')
  const [parentPhone, setParentPhone] = useState('')
  const [parentEmail, setParentEmail] = useState('')
  const [residentialAddress, setResidentialAddress] = useState('')

  // Submission state
  const [submitting, setSubmitting] = useState(false)
  const [submissionError, setSubmissionError] = useState(null)
  const [submittedData, setSubmittedData] = useState(null)
  const [copied, setCopied] = useState(false)
  const { user, isAuthenticated } = useAuth()

  // Pre-fill parent details from authenticated profile
  useEffect(() => {
    if (isOpen && user && user.role === 'parent') {
      if (!parentName && (user.full_name || user.name)) {
        setParentName(user.full_name || user.name)
      }
      if (!parentPhone && user.phone) {
        setParentPhone(user.phone)
      }
      if (!parentEmail && user.email) {
        setParentEmail(user.email)
      }
    }
  }, [isOpen, user])

  // Fetch form configuration whenever modal opens
  useEffect(() => {
    if (!isOpen || !institutionId) return

    let isMounted = true
    async function loadConfig() {
      try {
        setLoadingConfig(true)
        setErrorConfig(null)
        setCurrentStep(1)
        setSubmittedData(null)
        setSubmissionError(null)

        const res = await apiGet(`/admissions/form-config/${institutionId}`)
        if (isMounted) {
          setConfig(res)
          const isSch = res.is_school || res.category === 'Schools (K-10)' || res.school_type === 'School'
          const isPUInst = res.category === 'PU Colleges (11-12)' || (res.school_type && res.school_type.includes('PU'))

          const urlParams = new URLSearchParams(window.location.search)
          const requestedProgId = urlParams.get('program_id')
          if (isSch) {
            // Strictly lock to School Education (K-10)
            setEducationLevel('school')
            if (res.school_config?.standards?.length > 0) {
              setStandardApplied(String(res.school_config.standards[0]))
            } else {
              setStandardApplied('1')
            }
            setFirstLanguage('Kannada')
            setSecondLanguage('English')
            if (res.school_config?.programs?.length > 0) {
              setSelectedProgramId(res.school_config.programs[0].program_id)
            }
          } else if (isPUInst) {
            setEducationLevel('higher_secondary')
            if (res.pu_config?.streams?.length > 0) {
              setPuStream(res.pu_config.streams[0])
            }
          } else {
            const levels = res.offered_levels || []
            if (levels.length > 0) {
              setEducationLevel(levels[0])
            }
            if (requestedProgId) {
              setSelectedProgramId(requestedProgId)
            }
          }
        }
      } catch (err) {
        if (isMounted) setErrorConfig(err.message || 'Failed to load admission form settings.')
      } finally {
        if (isMounted) setLoadingConfig(false)
      }
    }

    loadConfig()
    return () => { isMounted = false }
  }, [isOpen, institutionId])

  // Update combinations when stream changes in PU
  useEffect(() => {
    if (educationLevel === 'higher_secondary' && config?.pu_config?.combinations) {
      const filtered = config.pu_config.combinations.filter(c => !puStream || c.stream === puStream)
      if (filtered.length > 0) {
        setPuCombination(filtered[0].combination_code)
        setSelectedProgramId(filtered[0].program_id)
      } else {
        setPuCombination('')
        setSelectedProgramId('')
      }
    }
  }, [educationLevel, puStream, config])

  if (!isOpen) return null

  const isSchool = config?.is_school || config?.category === 'Schools (K-10)' || config?.school_type === 'School'
  const isPU = !isSchool && (config?.category === 'PU Colleges (11-12)' || (config?.school_type && config?.school_type.includes('PU')) || educationLevel === 'higher_secondary')
  const offeredLevels = isSchool ? ['school'] : (config?.offered_levels || [])

  const availableCombinations = (config?.pu_config?.combinations || []).filter(c => !puStream || c.stream === puStream)
  const diplomaPrograms = config?.diploma_config?.programs || []
  const ugPrograms = config?.undergraduate_config?.programs || []

  const validateStep1 = () => {
    if (isSchool || educationLevel === 'school') {
      if (!standardApplied) return 'Please select a target class (Standards 1 to 10).'
      return null
    }
    if (!educationLevel) return 'Please select an education level.'
    if (educationLevel === 'higher_secondary' && !puCombination) return 'Please select a PU combination.'
    if ((educationLevel === 'diploma' || educationLevel === 'undergraduate') && !selectedProgramId) {
      return 'Please select a degree / diploma program.'
    }
    return null
  }

  const validateStep2 = () => {
    if (!applicantName.trim()) return 'Applicant / Student name is required.'
    if (!parentName.trim()) return 'Parent / Guardian name is required.'
    const cleanPhone = parentPhone.replace(/\D/g, '')
    if (cleanPhone.length !== 10) return 'Please enter a valid 10-digit mobile phone number.'
    if (!residentialAddress.trim()) return 'Residential address is required for catchment verification.'
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setSubmissionError(null)

    const payload = {
      institution_id: institutionId,
      division_id: divisionId || null,
      applicant_name: applicantName.trim(),
      parent_name: parentName.trim(),
      parent_phone: parentPhone.replace(/\D/g, ''),
      parent_email: parentEmail.trim() || null,
      residential_address: residentialAddress.trim(),
      academic_year: config?.academic_year || '2026-2027',
      education_level: isSchool ? 'school' : educationLevel,
      requested_standard: (isSchool || educationLevel === 'school') ? parseInt(standardApplied, 10) : null,
      requested_program_id: selectedProgramId || null,
      first_language_preference: (isSchool || educationLevel === 'school') ? (firstLanguage || 'Kannada') : null,
      second_language_preference: (isSchool || educationLevel === 'school') ? 'English' : null,
      stream_preference: !isSchool && educationLevel === 'higher_secondary' ? puStream : null,
      combination_code: !isSchool && educationLevel === 'higher_secondary' ? puCombination : null
    }

    try {
      const res = await apiPost('/admissions/apply', payload)
      setSubmittedData(res)
      setCurrentStep(4) // Move to success step
    } catch (err) {
      setSubmissionError(err.message || 'Submission failed. Please check the provided information and retry.')
    } finally {
      setSubmitting(false)
    }
  }

  const copyAppId = () => {
    if (submittedData?.application_id) {
      navigator.clipboard.writeText(submittedData.application_id)
      setCopied(true)
      setTimeout(() => setCopied(false), 2500)
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
        maxWidth: '720px',
        maxHeight: '92vh',
        overflowY: 'auto',
        boxShadow: '0 20px 45px rgba(0, 0, 0, 0.25)',
        display: 'flex',
        flexDirection: 'column',
        position: 'relative'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #102B46 0%, #153E6A 100%)',
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
                background: 'rgba(255,255,255,0.2)',
                fontSize: '0.72rem',
                fontWeight: 700,
                padding: '0.2rem 0.5rem',
                borderRadius: '4px',
                textTransform: 'uppercase',
                letterSpacing: '0.04em'
              }}>
                Stage 1 Admission
              </span>
              <span style={{ fontSize: '0.8rem', color: '#94A3B8' }}>• Free & Low-Friction</span>
            </div>
            <h2 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.01em' }}>
              {institutionName || config?.institution_name || 'Apply for Admission'}
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.15)',
              border: 'none',
              color: '#ffffff',
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              fontSize: '1.1rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>
        </div>

        {/* Stepper Progress Bar (only steps 1-3) */}
        {currentStep < 4 && (
          <div style={{
            display: 'flex',
            background: '#F8FAFC',
            borderBottom: '1px solid #E2E8F0',
            padding: '0.75rem 1.75rem',
            gap: '1rem',
            alignItems: 'center'
          }}>
            {[
              { num: 1, label: 'Academic Choices' },
              { num: 2, label: 'Applicant & Parent Details' },
              { num: 3, label: 'Review & Confirm' }
            ].map(step => (
              <div key={step.num} style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                fontSize: '0.85rem',
                fontWeight: currentStep === step.num ? 700 : 500,
                color: currentStep === step.num ? '#102B46' : currentStep > step.num ? '#12B76A' : '#94A3B8'
              }}>
                <span style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: currentStep === step.num ? '#102B46' : currentStep > step.num ? '#12B76A' : '#CBD5E1',
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
          {loadingConfig ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <LoadingSpinner />
              <p style={{ marginTop: '1rem', color: '#64748B', fontSize: '0.9rem' }}>
                Loading verified institution academic offerings and seat quotas...
              </p>
            </div>
          ) : errorConfig ? (
            <div style={{
              background: '#FEF3F2',
              border: '1px solid #FECDCA',
              borderRadius: '8px',
              padding: '1.25rem',
              color: '#B42318'
            }}>
              <h4 style={{ margin: '0 0 0.5rem 0' }}>Unable to Open Admission Form</h4>
              <p style={{ margin: 0, fontSize: '0.875rem' }}>{errorConfig}</p>
            </div>
          ) : (
            <div>
              {/* STEP 1: Academic Choices */}
              {currentStep === 1 && (
                <div>
                  <h3 style={{ fontSize: '1.05rem', color: '#102B46', marginBottom: '0.5rem', fontWeight: 700 }}>
                    Select Academic Programme & Preferences
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '1.25rem' }}>
                    Available programmes are synchronized live from institutional approvals in the official registry.
                  </p>

                  {/* Level Display: FOR SCHOOLS, STRICTLY SHOW ONLY SCHOOL EDUCATION (K-10) WITHOUT TOGGLE */}
                  {isSchool ? (
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                        Education Tier / Level *
                      </label>
                      <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.6rem',
                        background: '#EFF6FF',
                        border: '1.5px solid #155EEF',
                        padding: '0.6rem 1.1rem',
                        borderRadius: '8px',
                        color: '#102B46',
                        fontWeight: 700,
                        fontSize: '0.92rem'
                      }}>
                        <span style={{ fontSize: '1.1rem' }}>🏫</span>
                        <span>School Education (K–10)</span>
                      </div>
                    </div>
                  ) : offeredLevels.length > 1 ? (
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                        Education Tier / Level *
                      </label>
                      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        {offeredLevels.map(lvl => (
                          <button
                            type="button"
                            key={lvl}
                            onClick={() => {
                              setEducationLevel(lvl)
                              setSelectedProgramId('')
                            }}
                            style={{
                              padding: '0.5rem 1rem',
                              borderRadius: '6px',
                              border: educationLevel === lvl ? '2px solid #102B46' : '1px solid #CBD5E1',
                              background: educationLevel === lvl ? '#EFF6FF' : '#ffffff',
                              color: educationLevel === lvl ? '#102B46' : '#475569',
                              fontWeight: educationLevel === lvl ? 700 : 500,
                              fontSize: '0.85rem',
                              cursor: 'pointer'
                            }}
                          >
                            {lvl === 'higher_secondary' && '🎓 Pre-University (PU College)'}
                            {lvl === 'diploma' && '📐 Polytechnic / Diploma'}
                            {lvl === 'undergraduate' && '🏛️ Undergraduate Degree'}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  {/* Institution Divisions (if available and not school) */}
                  {!isSchool && config?.divisions?.length > 0 && (
                    <div style={{ marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                        Campus / Wing Division
                      </label>
                      <select
                        value={divisionId}
                        onChange={(e) => setDivisionId(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.6rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid #CBD5E1',
                          fontSize: '0.875rem'
                        }}
                      >
                        <option value="">Main Campus (Default)</option>
                        {config.divisions.map(div => (
                          <option key={div.division_id} value={div.division_id}>
                            {div.division_name} ({div.campus_location})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  {/* Category A: School Fields ONLY (Shows when isSchool is true) */}
                  {isSchool && (
                    <div style={{ background: '#F8FAFC', padding: '1.25rem', borderRadius: '10px', border: '1px solid #E2E8F0', marginBottom: '1.25rem' }}>
                      {/* School Curriculum Program if configured */}
                      {config?.school_config?.programs?.length > 0 && (
                        <div style={{ marginBottom: '1rem' }}>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            School Curriculum & Board
                          </label>
                          <div style={{
                            padding: '0.6rem 0.85rem',
                            background: '#FFFFFF',
                            border: '1px solid #D0D5DD',
                            borderRadius: '6px',
                            fontSize: '0.875rem',
                            color: '#102B46',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.5rem'
                          }}>
                            <span>📚</span>
                            <span>{config.school_config.programs[0].program_name}</span>
                          </div>
                        </div>
                      )}

                      {/* Target Class (1-10) and Academic Year */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Target Class (Standard 1–10) *
                          </label>
                          <select
                            value={standardApplied}
                            onChange={(e) => setStandardApplied(e.target.value)}
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #CBD5E1',
                              fontSize: '0.875rem',
                              background: '#FFFFFF',
                              fontWeight: 600
                            }}
                          >
                            {(config?.school_config?.standards || [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]).map(std => (
                              <option key={std} value={std}>Standard / Class {std}</option>
                            ))}
                          </select>
                        </div>

                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Academic Year
                          </label>
                          <input
                            type="text"
                            value={config?.academic_year || '2026-2027'}
                            readOnly
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #E2E8F0',
                              background: '#F1F5F9',
                              fontSize: '0.875rem',
                              color: '#475569',
                              fontWeight: 600
                            }}
                          />
                        </div>
                      </div>

                      {/* Language / Medium of Instruction Preferences */}
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            First Language Preference *
                          </label>
                          <select
                            id="school-first-language-select"
                            value={firstLanguage}
                            onChange={(e) => setFirstLanguage(e.target.value)}
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #CBD5E1',
                              fontSize: '0.875rem',
                              background: '#FFFFFF',
                              fontWeight: 600,
                              color: '#102B46'
                            }}
                          >
                            <option value="Kannada">Kannada</option>
                            <option value="Hindi">Hindi</option>
                            <option value="Sanskrit">Sanskrit</option>
                          </select>
                          <span style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.25rem', display: 'block' }}>
                            Select primary language of instruction
                          </span>
                        </div>

                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Second Language Preference (Compulsory) *
                          </label>
                          <input
                            id="school-second-language-input"
                            type="text"
                            value="English"
                            readOnly
                            disabled
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #E2E8F0',
                              background: '#F1F5F9',
                              fontSize: '0.875rem',
                              color: '#334155',
                              fontWeight: 700,
                              cursor: 'not-allowed',
                              boxSizing: 'border-box'
                            }}
                          />
                          <span style={{ fontSize: '0.75rem', color: '#64748B', marginTop: '0.25rem', display: 'block' }}>
                            🔒 Fixed standard second language
                          </span>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Category B: PU College Fields (ONLY shown for PU Colleges, NEVER for Schools) */}
                  {!isSchool && isPU && config?.pu_config && (
                    <div style={{ background: '#F8FAFC', padding: '1.25rem', borderRadius: '10px', border: '1px solid #E2E8F0', marginBottom: '1.25rem' }}>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                          Academic Stream *
                        </label>
                        <select
                          value={puStream}
                          onChange={(e) => setPuStream(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '0.6rem 0.75rem',
                            borderRadius: '6px',
                            border: '1px solid #CBD5E1',
                            fontSize: '0.875rem',
                            background: '#FFFFFF'
                          }}
                        >
                          {(config.pu_config.streams || ['Science', 'Commerce', 'Arts']).map(s => (
                            <option key={s} value={s}>{s} Stream</option>
                          ))}
                        </select>
                      </div>

                      <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                          DPUE Approved Subject Combination *
                        </label>
                        <select
                          value={puCombination}
                          onChange={(e) => {
                            setPuCombination(e.target.value)
                            const match = (config.pu_config.combinations || []).find(c => c.combination_code === e.target.value)
                            if (match) setSelectedProgramId(match.program_id)
                          }}
                          style={{
                            width: '100%',
                            padding: '0.6rem 0.75rem',
                            borderRadius: '6px',
                            border: '1px solid #CBD5E1',
                            fontSize: '0.875rem',
                            background: '#FFFFFF'
                          }}
                        >
                          {availableCombinations.map(comb => (
                            <option key={comb.combination_code} value={comb.combination_code}>
                              {comb.combination_code} — {comb.program_name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Medium of Instruction
                          </label>
                          <input
                            type="text"
                            value="English / Bilingual"
                            readOnly
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #E2E8F0',
                              background: '#F1F5F9',
                              fontSize: '0.875rem',
                              color: '#64748B'
                            }}
                          />
                        </div>
                        <div>
                          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                            Target Class
                          </label>
                          <input
                            type="text"
                            value="1st PU (Class 11) - 2026-27"
                            readOnly
                            style={{
                              width: '100%',
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: '1px solid #E2E8F0',
                              background: '#F1F5F9',
                              fontSize: '0.875rem',
                              color: '#64748B'
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Category C & D: Diploma / Undergraduate Fields */}
                  {!isSchool && !isPU && (educationLevel === 'diploma' || educationLevel === 'undergraduate') && (
                    <div style={{ background: '#F8FAFC', padding: '1.25rem', borderRadius: '10px', border: '1px solid #E2E8F0', marginBottom: '1.25rem' }}>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>
                        Approved Academic Programme *
                      </label>
                      <select
                        value={selectedProgramId}
                        onChange={(e) => setSelectedProgramId(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.6rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid #CBD5E1',
                          fontSize: '0.875rem',
                          background: '#FFFFFF'
                        }}
                      >
                        <option value="">-- Choose Programme --</option>
                        {(educationLevel === 'diploma' ? diplomaPrograms : ugPrograms).map(p => (
                          <option key={p.program_id} value={p.program_id}>
                            {p.program_name} {p.discipline_or_stream ? `(${p.discipline_or_stream})` : ''}
                          </option>
                        ))}
                      </select>
                      <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.78rem', color: '#64748B' }}>
                        Under statutory compliance, only pre-approved undergraduate/diploma programmes are selectable.
                      </p>
                    </div>
                  )}

                  {/* Navigation Button */}
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
                    <button
                      type="button"
                      onClick={() => {
                        const err = validateStep1()
                        if (err) alert(err)
                        else setCurrentStep(2)
                      }}
                      style={{
                        background: '#102B46',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '8px',
                        padding: '0.65rem 1.5rem',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        cursor: 'pointer'
                      }}
                    >
                      Next: Applicant Details →
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 2: Applicant & Parent Details */}
              {currentStep === 2 && (
                <div>
                  <h3 style={{ fontSize: '1.05rem', color: '#102B46', marginBottom: '0.5rem', fontWeight: 700 }}>
                    Applicant & Guardian Information
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '1.25rem' }}>
                    Provide basic identity and contact coordinates. Aadhaar and formal document uploads are NOT required at Stage 1.
                  </p>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Full Name *
                      </label>
                      <input
                        type="text"
                        placeholder="Name as per Aadhaar Card"
                        value={applicantName}
                        onChange={(e) => setApplicantName(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.65rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid #CBD5E1',
                          fontSize: '0.875rem'
                        }}
                      />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                          Parent / Guardian Name *
                        </label>
                        <input
                          type="text"
                          placeholder="e.g. Suresh Gowda"
                          value={parentName}
                          onChange={(e) => setParentName(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '0.65rem 0.75rem',
                            borderRadius: '6px',
                            border: '1px solid #CBD5E1',
                            fontSize: '0.875rem'
                          }}
                        />
                      </div>

                      <div>
                        <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                          Primary Mobile Number (10 digits) *
                        </label>
                        <input
                          type="tel"
                          maxLength={10}
                          placeholder="e.g. 9876543210"
                          value={parentPhone}
                          onChange={(e) => setParentPhone(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '0.65rem 0.75rem',
                            borderRadius: '6px',
                            border: '1px solid #CBD5E1',
                            fontSize: '0.875rem'
                          }}
                        />
                      </div>
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Parent Email Address (Optional, for notifications)
                      </label>
                      <input
                        type="email"
                        placeholder="e.g. parent.contact@example.com"
                        value={parentEmail}
                        onChange={(e) => setParentEmail(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.65rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid #CBD5E1',
                          fontSize: '0.875rem'
                        }}
                      />
                    </div>

                    <div>
                      <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                        Residential Address & Ward / Area *
                      </label>
                      <textarea
                        rows={2}
                        placeholder="House / Street, Locality, City / Taluk, PIN Code"
                        value={residentialAddress}
                        onChange={(e) => setResidentialAddress(e.target.value)}
                        style={{
                          width: '100%',
                          padding: '0.65rem 0.75rem',
                          borderRadius: '6px',
                          border: '1px solid #CBD5E1',
                          fontSize: '0.875rem',
                          resize: 'vertical'
                        }}
                      />
                      <span style={{ fontSize: '0.75rem', color: '#64748B' }}>
                        Used for distance catchment determination by the school admission desk.
                      </span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1.5rem' }}>
                    <button
                      type="button"
                      onClick={() => setCurrentStep(1)}
                      style={{
                        background: '#F1F5F9',
                        color: '#475569',
                        border: '1px solid #CBD5E1',
                        borderRadius: '8px',
                        padding: '0.65rem 1.25rem',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        cursor: 'pointer'
                      }}
                    >
                      ← Back to Academic Choices
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        const err = validateStep2()
                        if (err) alert(err)
                        else setCurrentStep(3)
                      }}
                      style={{
                        background: '#102B46',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '8px',
                        padding: '0.65rem 1.5rem',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        cursor: 'pointer'
                      }}
                    >
                      Next: Review & Confirm →
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 3: Review & Confirm */}
              {currentStep === 3 && (
                <div>
                  <h3 style={{ fontSize: '1.05rem', color: '#102B46', marginBottom: '0.5rem', fontWeight: 700 }}>
                    Review Preliminary Application
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: '#64748B', marginBottom: '1.25rem' }}>
                    Please verify your details before submitting to the institutional admissions desk.
                  </p>

                  {submissionError && (
                    <div style={{
                      background: '#FEF3F2',
                      border: '1px solid #FECDCA',
                      borderRadius: '8px',
                      padding: '1rem',
                      color: '#B42318',
                      marginBottom: '1rem',
                      fontSize: '0.875rem'
                    }}>
                      ⚠️ {submissionError}
                    </div>
                  )}

                  {/* Summary Card */}
                  <div style={{
                    background: '#F8FAFC',
                    border: '1px solid #E2E8F0',
                    borderRadius: '10px',
                    padding: '1.25rem',
                    marginBottom: '1.25rem',
                    fontSize: '0.875rem'
                  }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '0.75rem' }}>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>Target Institution</span>
                        <strong style={{ color: '#102B46' }}>{institutionName || config?.institution_name}</strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>Education Level</span>
                        <strong style={{ color: '#102B46' }}>
                          {isSchool ? 'School Education (K–10)' : educationLevel.replace('_', ' ')}
                        </strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>
                          {isSchool ? 'Target Class & Medium' : 'Program / Stream'}
                        </span>
                        <strong style={{ color: '#102B46' }}>
                          {isSchool && `Standard / Class ${standardApplied} • 1st Lang: ${firstLanguage} • 2nd Lang: English (Compulsory)`}
                          {!isSchool && isPU && `Stream: ${puStream} [${puCombination}]`}
                          {!isSchool && !isPU && selectedProgramId}
                        </strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>Academic Cycle</span>
                        <strong style={{ color: '#102B46' }}>{config?.academic_year || '2026-2027'}</strong>
                      </div>
                    </div>

                    <div style={{ borderTop: '1px solid #E2E8F0', paddingTop: '0.75rem', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>Applicant Name</span>
                        <strong style={{ color: '#102B46' }}>{applicantName}</strong>
                      </div>
                      <div>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>Parent / Guardian</span>
                        <strong style={{ color: '#102B46' }}>{parentName} ({parentPhone})</strong>
                      </div>
                      <div style={{ gridColumn: 'span 2' }}>
                        <span style={{ color: '#64748B', fontSize: '0.78rem', display: 'block' }}>Residential Address</span>
                        <span style={{ color: '#334155' }}>{residentialAddress}</span>
                      </div>
                    </div>
                  </div>

                  {/* Declaration Callout */}
                  <div style={{
                    background: '#EFF6FF',
                    border: '1px solid #BFDBFE',
                    borderRadius: '8px',
                    padding: '1rem',
                    marginBottom: '1.5rem',
                    fontSize: '0.82rem',
                    color: '#1E40AF',
                    lineHeight: 1.5
                  }}>
                    🛡️ <strong>NagrikSetu Two-Stage Admission Policy:</strong> This submission constitutes a Stage 1 expression of interest. It reserves a review queue slot under official seat quotas without upfront fees. Final enrolment is subject to Stage 2 document verification following institutional approval.
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <button
                      type="button"
                      onClick={() => setCurrentStep(2)}
                      disabled={submitting}
                      style={{
                        background: '#F1F5F9',
                        color: '#475569',
                        border: '1px solid #CBD5E1',
                        borderRadius: '8px',
                        padding: '0.65rem 1.25rem',
                        fontWeight: 600,
                        fontSize: '0.875rem',
                        cursor: 'pointer'
                      }}
                    >
                      ← Back to Applicant Details
                    </button>

                    <button
                      type="button"
                      onClick={handleSubmit}
                      disabled={submitting}
                      style={{
                        background: '#12B76A',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '8px',
                        padding: '0.75rem 1.75rem',
                        fontWeight: 700,
                        fontSize: '0.95rem',
                        cursor: submitting ? 'not-allowed' : 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        boxShadow: '0 2px 6px rgba(18, 183, 106, 0.25)'
                      }}
                    >
                      {submitting ? 'Submitting Application...' : 'Confirm & Submit Application ✓'}
                    </button>
                  </div>
                </div>
              )}

              {/* STEP 4: Success State */}
              {currentStep === 4 && submittedData && (
                <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                  <div style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '50%',
                    background: '#D1FADF',
                    color: '#027A48',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '2rem',
                    margin: '0 auto 1rem auto'
                  }}>
                    ✓
                  </div>

                  <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
                    Application Successfully Submitted!
                  </h3>
                  <p style={{ color: '#475467', fontSize: '0.9rem', maxWidth: '500px', margin: '0 auto 1.5rem auto' }}>
                    Your Stage 1 preliminary application has been recorded in the official admissions queue for {institutionName || config?.institution_name}.
                  </p>

                  <div style={{
                    background: '#F8FAFC',
                    border: '1.5px dashed #CBD5E1',
                    borderRadius: '10px',
                    padding: '1.25rem',
                    maxWidth: '440px',
                    margin: '0 auto 1.5rem auto'
                  }}>
                    <span style={{ fontSize: '0.78rem', color: '#64748B', display: 'block', textTransform: 'uppercase', letterSpacing: '0.04em', fontWeight: 600 }}>
                      Official Application Reference ID
                    </span>
                    <div style={{
                      fontSize: '1.4rem',
                      fontWeight: 800,
                      color: '#102B46',
                      letterSpacing: '1px',
                      margin: '0.4rem 0 0.75rem 0'
                    }}>
                      {submittedData.application_id}
                    </div>

                    <button
                      type="button"
                      onClick={copyAppId}
                      style={{
                        background: copied ? '#ECFDF3' : '#EFF6FF',
                        border: `1px solid ${copied ? '#A6F4C5' : '#BFDBFE'}`,
                        color: copied ? '#027A48' : '#1D4ED8',
                        padding: '0.35rem 0.75rem',
                        borderRadius: '6px',
                        fontSize: '0.78rem',
                        fontWeight: 600,
                        cursor: 'pointer'
                      }}
                    >
                      {copied ? '✓ Copied to Clipboard!' : '📋 Copy Reference ID'}
                    </button>
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                    <Link
                      to="/parent?tab=admissions"
                      style={{
                        background: '#155EEF',
                        color: '#ffffff',
                        padding: '0.65rem 1.25rem',
                        borderRadius: '8px',
                        fontWeight: 700,
                        textDecoration: 'none',
                        fontSize: '0.9rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.5rem'
                      }}
                    >
                      Track in Parent Dashboard →
                    </Link>
                    <button
                      type="button"
                      onClick={onClose}
                      style={{
                        background: '#102B46',
                        color: '#ffffff',
                        border: 'none',
                        borderRadius: '8px',
                        padding: '0.65rem 1.5rem',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        cursor: 'pointer'
                      }}
                    >
                      Close Window
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
