import React, { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Breadcrumbs from '../../components/layout/Breadcrumbs'
import Alert from '../../components/ui/Alert'
import PasswordInput from '../../components/ui/PasswordInput'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import { apiGet, apiPost } from '../../utils/api'

const KARNATAKA_DISTRICTS = [
  'Bagalkote', 'Ballari', 'Belagavi', 'Bengaluru Rural', 'Bengaluru Urban',
  'Bidar', 'Chamarajanagara', 'Chikkaballapura', 'Chikkamagaluru', 'Chitradurga',
  'Dakshina Kannada', 'Davanagere', 'Dharwad', 'Gadag', 'Hassan',
  'Haveri', 'Kalaburagi', 'Kodagu', 'Kolar', 'Koppal',
  'Mandya', 'Mysuru', 'Raichur', 'Ramanagara', 'Shivamogga',
  'Tumakuru', 'Udupi', 'Uttara Kannada', 'Vijayanagara', 'Vijayapura', 'Yadgir'
]

const INSTITUTION_TYPES = [
  { value: 'Primary School', label: 'Primary School (Class 1-5)', category: 'Schools (K-10)', defaultIdPrefix: 'SCH' },
  { value: 'High School', label: 'High School (Class 6-10)', category: 'Schools (K-10)', defaultIdPrefix: 'SCH' },
  { value: 'Pre-University College (PUC)', label: 'Pre-University College (PUC)', category: 'PU Colleges (11-12)', defaultIdPrefix: 'PUC' },
  { value: 'Degree College', label: 'Degree College (UG / PG)', category: 'Degree Colleges', defaultIdPrefix: 'COL' },
  { value: 'Autonomous College', label: 'Autonomous College', category: 'Degree Colleges', defaultIdPrefix: 'COL' },
  { value: 'State University', label: 'State University', category: 'Universities', defaultIdPrefix: 'UNI' },
  { value: 'Deemed / Private University', label: 'Deemed / Private University', category: 'Universities', defaultIdPrefix: 'UNI' }
]

export default function ApplyInstitutionPage() {
  const navigate = useNavigate()

  // Form State
  const [formData, setFormData] = useState({
    // Section A
    institution_id: '',
    institution_name: '',
    institution_type: 'High School',
    institution_category: 'Schools (K-10)',
    established_year: '',
    affiliation: 'Karnataka State Board',
    recognition: '',

    // Section B
    address_line1: '',
    address_line2: '',
    city: '',
    district: 'Bengaluru Urban',
    state: 'Karnataka',
    pincode: '',
    country: 'India',

    // Section C
    official_email: '',
    official_phone: '',
    website: '',

    // Section E
    applicant_name: '',
    applicant_designation: 'Principal',
    applicant_email: '',
    applicant_phone: '',

    // Section F
    password: '',
    confirm_password: ''
  })

  // Dynamic Academic Offerings (Section D)
  const [schoolMedium, setSchoolMedium] = useState('English & Kannada')
  const [schoolStandards, setSchoolStandards] = useState('Classes 1 to 10')
  const [schoolSectionsCount, setSchoolSectionsCount] = useState('4')

  const [puStreams, setPuStreams] = useState(['Science', 'Commerce'])
  const [puCombinations, setPuCombinations] = useState(['PCMB (Physics, Chemistry, Maths, Bio)', 'CEBA (Comm, Econ, Bus, Acct)'])
  const [newPuComb, setNewPuComb] = useState('')

  const [programmesList, setProgrammesList] = useState([
    { code: 'B.Sc. CS', name: 'Bachelor of Science (Computer Science)', duration: '3 Years', intake: '60' },
    { code: 'B.Com', name: 'Bachelor of Commerce (Honours)', duration: '3 Years', intake: '120' }
  ])
  const [newProg, setNewProg] = useState({ code: '', name: '', duration: '3 Years', intake: '60' })

  // Validation & UI State
  const [idChecking, setIdChecking] = useState(false)
  const [idValidationResult, setIdValidationResult] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [errorMsg, setErrorMsg] = useState('')
  const [submittedApp, setSubmittedApp] = useState(null)

  // Sync Category when Type changes
  const handleTypeChange = (newType) => {
    const selected = INSTITUTION_TYPES.find(t => t.value === newType)
    if (selected) {
      setFormData(prev => ({
        ...prev,
        institution_type: newType,
        institution_category: selected.category,
        affiliation: selected.category === 'Schools (K-10)' ? 'Karnataka State Board' :
                     selected.category === 'PU Colleges (11-12)' ? 'Department of Pre-University Education (PUE)' :
                     selected.category === 'Degree Colleges' ? 'Bangalore University / Affiliated' : 'UGC / NAAC'
      }))
    }
  }

  // Validate Institution ID availability
  const checkIdAvailability = async (idToCheck) => {
    const id = (idToCheck || formData.institution_id).trim().toUpperCase()
    if (!id || id.length < 3) {
      setIdValidationResult({ available: false, message: 'ID must be at least 3 characters' })
      return
    }
    setIdChecking(true)
    try {
      const res = await apiGet(`/institutions/validate-id?institution_id=${encodeURIComponent(id)}`)
      setIdValidationResult(res)
    } catch (err) {
      setIdValidationResult({ available: false, message: err.message || 'Validation failed' })
    } finally {
      setIdChecking(false)
    }
  }

  // Auto-generate suggested ID
  const suggestId = () => {
    const selected = INSTITUTION_TYPES.find(t => t.value === formData.institution_type)
    const prefix = selected ? selected.defaultIdPrefix : 'INST'
    const rand = Math.floor(1000 + Math.random() * 9000)
    const suggested = `${prefix}${rand}`
    setFormData(prev => ({ ...prev, institution_id: suggested }))
    checkIdAvailability(suggested)
  }

  // Handle generic field change
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => {
      const updated = { ...prev, [name]: value }
      // Auto pre-fill applicant email into section F if applicant email changes
      return updated
    })
    if (name === 'institution_id') {
      setIdValidationResult(null)
    }
  }

  // Add Programme for Colleges/Universities
  const handleAddProgramme = () => {
    if (!newProg.name.trim()) return
    setProgrammesList([...programmesList, { ...newProg, code: newProg.code || `PRG${programmesList.length + 1}` }])
    setNewProg({ code: '', name: '', duration: '3 Years', intake: '60' })
  }

  const handleRemoveProgramme = (idx) => {
    setProgrammesList(programmesList.filter((_, i) => i !== idx))
  }

  // Add PU Combination
  const handleAddPuCombination = () => {
    if (!newPuComb.trim()) return
    setPuCombinations([...puCombinations, newPuComb.trim()])
    setNewPuComb('')
  }

  const handleRemovePuCombination = (idx) => {
    setPuCombinations(puCombinations.filter((_, i) => i !== idx))
  }

  // Password rules validation
  const validatePassword = (pwd) => {
    if (!pwd || pwd.length < 8) return 'Password must be at least 8 characters long.'
    if (!/[A-Z]/.test(pwd)) return 'Password must contain at least one uppercase letter.'
    if (!/[a-z]/.test(pwd)) return 'Password must contain at least one lowercase letter.'
    if (!/[0-9]/.test(pwd)) return 'Password must contain at least one digit.'
    if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(pwd)) return 'Password must contain at least one special character.'
    return null
  }

  // Form Submit
  const handleSubmit = async (e) => {
    e.preventDefault()
    setErrorMsg('')

    // Basic Validations
    if (!formData.institution_id.trim()) {
      setErrorMsg('Please provide or generate a unique Institution ID.')
      return
    }
    if (!formData.institution_name.trim()) {
      setErrorMsg('Institution Full Legal Name is required.')
      return
    }
    if (!formData.address_line1.trim() || !formData.city.trim() || !formData.pincode.trim()) {
      setErrorMsg('Complete institution address (Line 1, City, PIN) is required.')
      return
    }
    if (!/^\d{6}$/.test(formData.pincode.trim())) {
      setErrorMsg('PIN Code must be exactly 6 digits.')
      return
    }
    if (!formData.official_email.trim() || !formData.applicant_email.trim()) {
      setErrorMsg('Both Official Institutional Email and Administrator Email are required.')
      return
    }
    if (!formData.applicant_name.trim()) {
      setErrorMsg('Authorized Administrator Full Name is required.')
      return
    }

    // Password Checks
    const pwdErr = validatePassword(formData.password)
    if (pwdErr) {
      setErrorMsg(pwdErr)
      return
    }
    if (formData.password !== formData.confirm_password) {
      setErrorMsg('Password confirmation does not match.')
      return
    }

    // Prepare Academic Info JSON
    const academicInfo = {
      category: formData.institution_category,
      type: formData.institution_type,
      affiliation: formData.affiliation,
      school_medium: schoolMedium,
      school_standards: schoolStandards,
      school_sections_count: schoolSectionsCount,
      pu_streams: puStreams,
      pu_combinations: puCombinations,
      degree_programmes: programmesList
    }

    const payload = {
      institution_id: formData.institution_id.trim().toUpperCase(),
      institution_name: formData.institution_name.trim(),
      institution_type: formData.institution_type,
      institution_category: formData.institution_category,
      established_year: formData.established_year ? parseInt(formData.established_year, 10) : null,
      affiliation: formData.affiliation.trim(),
      recognition: formData.recognition.trim(),
      address_line1: formData.address_line1.trim(),
      address_line2: formData.address_line2 ? formData.address_line2.trim() : null,
      city: formData.city.trim(),
      district: formData.district,
      state: formData.state,
      pincode: formData.pincode.trim(),
      country: formData.country,
      official_email: formData.official_email.trim(),
      official_phone: formData.official_phone.trim(),
      website: formData.website ? formData.website.trim() : null,
      academic_info_json: JSON.stringify(academicInfo),
      applicant_name: formData.applicant_name.trim(),
      applicant_designation: formData.applicant_designation.trim(),
      applicant_email: formData.applicant_email.trim(),
      applicant_phone: formData.applicant_phone.trim(),
      password: formData.password
    }

    setSubmitting(true)
    try {
      const res = await apiPost('/institutions/apply', payload)
      setSubmittedApp(res)
      window.scrollTo({ top: 0, behavior: 'smooth' })
    } catch (err) {
      setErrorMsg(err.message || 'Failed to submit institution application. Please review your entries and try again.')
    } finally {
      setSubmitting(false)
    }
  }

  // Render Confirmation / Success View
  if (submittedApp) {
    return (
      <div style={{ minHeight: '85vh', background: '#F5F7FA', padding: '2rem 1rem 5rem 1rem' }}>
        <Breadcrumbs crumbs={[
          { label: 'Home', href: '/' },
          { label: 'Select Your Institution', href: '/select-institution' },
          { label: 'Application Submitted' }
        ]} />

        <div style={{ maxWidth: '800px', margin: '2rem auto', background: '#FFFFFF', borderRadius: '12px', border: '1px solid #D0D5DD', padding: '2.5rem', boxShadow: '0 4px 16px rgba(16,43,70,0.08)' }}>
          <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
            <div style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: '#ECFDF3',
              border: '2px solid #039855',
              color: '#039855',
              fontSize: '2rem',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem'
            }}>
              ✓
            </div>
            <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#102B46', margin: '0 0 0.5rem 0' }}>
              Application Submitted Successfully
            </h1>
            <p style={{ color: '#475467', fontSize: '1rem', margin: 0 }}>
              Official NagrikSetu Institution Registration Gateway
            </p>
          </div>

          <div style={{
            background: '#F0F9FF',
            border: '1px solid #B9E6FE',
            borderRadius: '8px',
            padding: '1.5rem',
            marginBottom: '2rem'
          }}>
            <div style={{ fontSize: '0.85rem', color: '#026AA2', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Official Application Reference Number
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#004EEB', fontFamily: 'monospace', margin: '0.5rem 0' }}>
              {submittedApp.application_ref}
            </div>
            <div style={{ fontSize: '0.9rem', color: '#034488', lineHeight: 1.5 }}>
              Please preserve this reference number for all administrative communications and status tracking.
            </div>
          </div>

          <div style={{
            background: '#F9FAFB',
            border: '1px solid #EAECF0',
            borderRadius: '8px',
            padding: '1.5rem',
            marginBottom: '2rem',
            fontSize: '0.925rem',
            color: '#344054',
            lineHeight: 1.6
          }}>
            <p style={{ margin: '0 0 1rem 0', fontWeight: 600, color: '#102B46' }}>
              Your institution registration application has been submitted successfully.
            </p>
            <p style={{ margin: '0 0 1rem 0' }}>
              The <strong>NagrikSetu Platform Administration team</strong> will review your submitted institutional information, accreditation, and administrative credentials.
            </p>
            <p style={{ margin: 0 }}>
              Once approved, your administrator account (<strong>{submittedApp.applicant_email}</strong>) will be activated and you will be able to log in directly using your registered credentials.
            </p>
          </div>

          {/* Application Summary Box */}
          <div style={{ border: '1px solid #E4E7EC', borderRadius: '8px', padding: '1.25rem', marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.75rem 0' }}>
              Application Summary
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', fontSize: '0.875rem' }}>
              <div><span style={{ color: '#667085' }}>Institution Name:</span> <strong>{submittedApp.institution_name}</strong></div>
              <div><span style={{ color: '#667085' }}>Institution ID:</span> <strong style={{ fontFamily: 'monospace' }}>{submittedApp.institution_id}</strong></div>
              <div><span style={{ color: '#667085' }}>Application Status:</span> <span className="badge badge--warning" style={{ fontWeight: 700 }}>Pending Review</span></div>
              <div><span style={{ color: '#667085' }}>Administrator:</span> <strong>{submittedApp.applicant_name}</strong></div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <Link
              to="/select-institution"
              className="btn btn--primary"
              style={{ padding: '0.75rem 1.75rem', fontWeight: 700 }}
            >
              ← Return to Institution Selection
            </Link>
            <button
              onClick={() => window.print()}
              className="btn btn--outline"
              style={{ padding: '0.75rem 1.5rem', fontWeight: 600 }}
            >
              Print / Save Reference
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Render Full Application Form
  return (
    <div style={{ minHeight: '85vh', background: '#F5F7FA', padding: '2rem 1rem 5rem 1rem' }}>
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Select Your Institution', href: '/select-institution' },
        { label: 'Apply Institution' }
      ]} />

      <div style={{ maxWidth: '960px', margin: '1rem auto 0 auto' }}>
        {/* Banner Header */}
        <div style={{
          background: '#102B46',
          color: '#FFFFFF',
          padding: '2rem',
          borderRadius: '12px',
          marginBottom: '2rem',
          boxShadow: '0 4px 12px rgba(16,43,70,0.12)'
        }}>
          <div style={{ display: 'inline-block', background: '#155EEF', color: '#FFFFFF', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
            Institutional Self-Registration Portal
          </div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 0.5rem 0', color: '#FFFFFF' }}>
            Register Your School, College or University
          </h1>
          <p style={{ margin: 0, color: '#D0D5DD', fontSize: '1rem', maxWidth: '800px', lineHeight: 1.5 }}>
            Submit an official institutional onboarding application to the Karnataka NagrikSetu Education Platform. Approved institutions receive a verified digital node, admissions desk, and administrative governance tools.
          </p>
        </div>

        {errorMsg && (
          <Alert type="error" title="Submission Error" style={{ marginBottom: '1.5rem' }}>
            {errorMsg}
          </Alert>
        )}

        <form onSubmit={handleSubmit}>
          {/* ======================================================== */}
          {/* SECTION A: INSTITUTION INFORMATION */}
          {/* ======================================================== */}
          <div className="card" style={{ background: '#FFFFFF', border: '1px solid #D0D5DD', borderRadius: '10px', padding: '1.75rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '0.75rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Section A</span>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0.2rem 0 0 0' }}>Institution Information</h2>
              </div>
              <span className="badge badge--neutral" style={{ fontSize: '0.75rem' }}>Required</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
              {/* Institution Type */}
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Institution Type <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <select
                  name="institution_type"
                  value={formData.institution_type}
                  onChange={(e) => handleTypeChange(e.target.value)}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem', color: '#102B46', background: '#FFFFFF' }}
                >
                  {INSTITUTION_TYPES.map(t => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>

              {/* Institution Category (Derived) */}
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Platform Category
                </label>
                <input
                  type="text"
                  readOnly
                  value={(formData.institution_category || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #EAECF0', borderRadius: '6px', fontSize: '0.9rem', background: '#F8F9FA', color: '#475467', cursor: 'not-allowed' }}
                />
              </div>

              {/* Institution ID with Validation */}
              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Proposed Institution ID / Code <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <input
                    type="text"
                    name="institution_id"
                    required
                    placeholder="e.g. SCH0031, PUC0032, COL0033, UNI0034"
                    value={formData.institution_id}
                    onChange={handleChange}
                    style={{
                      flex: 1,
                      padding: '0.65rem 0.85rem',
                      border: idValidationResult ? (idValidationResult.available ? '2px solid #12B76A' : '2px solid #F04438') : '1px solid #D0D5DD',
                      borderRadius: '6px',
                      fontSize: '0.95rem',
                      fontFamily: 'monospace',
                      fontWeight: 700,
                      textTransform: 'uppercase'
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => checkIdAvailability()}
                    disabled={idChecking || !formData.institution_id.trim()}
                    className="btn btn--secondary"
                    style={{ padding: '0.65rem 1rem', fontSize: '0.85rem', whiteSpace: 'nowrap' }}
                  >
                    {idChecking ? 'Checking...' : 'Check Availability'}
                  </button>
                  <button
                    type="button"
                    onClick={suggestId}
                    className="btn btn--ghost"
                    style={{ padding: '0.65rem 0.85rem', fontSize: '0.85rem', color: '#155EEF', whiteSpace: 'nowrap' }}
                    title="Generate suggested unique identifier"
                  >
                    Suggest ID
                  </button>
                </div>
                {idValidationResult && (
                  <div style={{ marginTop: '0.4rem', fontSize: '0.825rem', fontWeight: 600, color: idValidationResult.available ? '#027A48' : '#D92D20' }}>
                    {idValidationResult.available ? `✓ ${idValidationResult.message || 'ID is available'}` : `✗ ${idValidationResult.reason || idValidationResult.message}`}
                  </div>
                )}
                <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.25rem' }}>
                  Official alphanumeric identifier used across platform enrollments and portal URLs.
                </div>
              </div>

              {/* Institution Legal Name */}
              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Institution Full Legal Name <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="institution_name"
                  required
                  placeholder="e.g. Sri Vidya Mandir Composite Pre-University College"
                  value={formData.institution_name}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              {/* Established Year */}
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Established Year
                </label>
                <input
                  type="number"
                  name="established_year"
                  min="1800"
                  max="2026"
                  placeholder="e.g. 1998"
                  value={formData.established_year}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              {/* Affiliation / Board */}
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Affiliation / Board / Accreditation <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="affiliation"
                  required
                  placeholder="e.g. CBSE, ICSE, Karnataka State Board, UGC, AICTE"
                  value={formData.affiliation}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              {/* Recognition Number */}
              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Official Recognition / Order / Registration Number
                </label>
                <input
                  type="text"
                  name="recognition"
                  placeholder="e.g. ED/RECOG/2021/BLR-0492 or DISE Code"
                  value={formData.recognition}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>
            </div>
          </div>

          {/* ======================================================== */}
          {/* SECTION B: INSTITUTION ADDRESS */}
          {/* ======================================================== */}
          <div className="card" style={{ background: '#FFFFFF', border: '1px solid #D0D5DD', borderRadius: '10px', padding: '1.75rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Section B</span>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0.2rem 0 0 0' }}>Institution Address</h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Address Line 1 <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="address_line1"
                  required
                  placeholder="Premises name, street, road, landmark"
                  value={formData.address_line1}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Address Line 2 (Optional)
                </label>
                <input
                  type="text"
                  name="address_line2"
                  placeholder="Area, block, sector"
                  value={formData.address_line2}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  City / Town / Taluk <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="city"
                  required
                  placeholder="e.g. Bengaluru, Mysuru, Hubballi"
                  value={formData.city}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  District (Karnataka) <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <select
                  name="district"
                  value={formData.district}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem', color: '#102B46', background: '#FFFFFF' }}
                >
                  {KARNATAKA_DISTRICTS.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  State
                </label>
                <input
                  type="text"
                  readOnly
                  value={formData.state}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #EAECF0', borderRadius: '6px', fontSize: '0.9rem', background: '#F8F9FA', color: '#475467', cursor: 'not-allowed' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  PIN Code <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="pincode"
                  required
                  maxLength={6}
                  placeholder="e.g. 560001"
                  value={formData.pincode}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>
            </div>
          </div>

          {/* ======================================================== */}
          {/* SECTION C: INSTITUTION CONTACT DETAILS */}
          {/* ======================================================== */}
          <div className="card" style={{ background: '#FFFFFF', border: '1px solid #D0D5DD', borderRadius: '10px', padding: '1.75rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Section C</span>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0.2rem 0 0 0' }}>Institution Contact Details</h2>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Official Institutional Email <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="email"
                  name="official_email"
                  required
                  placeholder="e.g. principal@greenvalley.edu.in"
                  value={formData.official_email}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Official Phone / Landline <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="official_phone"
                  required
                  placeholder="e.g. 080-23456789 or +91 9876543210"
                  value={formData.official_phone}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              <div style={{ gridColumn: 'span 2' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Official Website (Optional)
                </label>
                <input
                  type="url"
                  name="website"
                  placeholder="e.g. https://greenvalleyschool.karnataka.gov.in"
                  value={formData.website}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>
            </div>
          </div>

          {/* ======================================================== */}
          {/* SECTION D: ACADEMIC INFORMATION (DYNAMIC) */}
          {/* ======================================================== */}
          <div className="card" style={{ background: '#FFFFFF', border: '1px solid #D0D5DD', borderRadius: '10px', padding: '1.75rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Section D</span>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0.2rem 0 0 0' }}>
                Academic Information & Programmes ({(formData.institution_category || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')})
              </h2>
            </div>

            {/* D1: SCHOOLS SPECIFIC */}
            {formData.institution_category === 'Schools (K-10)' && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                    Offered Grades / Standards
                  </label>
                  <input
                    type="text"
                    value={schoolStandards}
                    onChange={(e) => setSchoolStandards(e.target.value)}
                    placeholder="e.g. Classes 1 to 10, Kindergarten to 10th"
                    style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                    Number of Sections per Standard
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={schoolSectionsCount}
                    onChange={(e) => setSchoolSectionsCount(e.target.value)}
                    style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                  />
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                    Primary Medium of Instruction
                  </label>
                  <input
                    type="text"
                    value={schoolMedium}
                    onChange={(e) => setSchoolMedium(e.target.value)}
                    placeholder="e.g. English, Kannada, English & Kannada bilingual"
                    style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                  />
                </div>
              </div>
            )}

            {/* D2: PU COLLEGES SPECIFIC */}
            {formData.institution_category === 'PU Colleges (11-12)' && (
              <div>
                <div style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.5rem' }}>
                    Streams Offered:
                  </label>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                    {['Science', 'Commerce', 'Arts'].map(st => (
                      <label key={st} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem', cursor: 'pointer' }}>
                        <input
                          type="checkbox"
                          checked={puStreams.includes(st)}
                          onChange={(e) => {
                            if (e.target.checked) setPuStreams([...puStreams, st])
                            else setPuStreams(puStreams.filter(s => s !== st))
                          }}
                        />
                        {st} Stream
                      </label>
                    ))}
                  </div>
                </div>

                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Subject Combinations Offered
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                  <input
                    type="text"
                    value={newPuComb}
                    onChange={(e) => setNewPuComb(e.target.value)}
                    placeholder="e.g. PCMC (Physics, Chemistry, Maths, Comp Science)"
                    style={{ flex: 1, padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                  />
                  <button
                    type="button"
                    onClick={handleAddPuCombination}
                    className="btn btn--secondary"
                    style={{ fontSize: '0.85rem' }}
                  >
                    + Add Combination
                  </button>
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {puCombinations.map((comb, idx) => (
                    <span key={idx} className="badge badge--info" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}>
                      {comb}
                      <button
                        type="button"
                        onClick={() => handleRemovePuCombination(idx)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#B42318', fontWeight: 'bold' }}
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* D3: DEGREE COLLEGES & UNIVERSITIES SPECIFIC */}
            {(formData.institution_category === 'Degree Colleges' || formData.institution_category === 'Universities') && (
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.5rem' }}>
                  Offered Programmes / Courses:
                </label>
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
                  <input
                    type="text"
                    placeholder="Programme Code (e.g. BTECH-CSE)"
                    value={newProg.code}
                    onChange={(e) => setNewProg({ ...newProg, code: e.target.value })}
                    style={{ flex: '1 1 120px', padding: '0.5rem 0.75rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.85rem' }}
                  />
                  <input
                    type="text"
                    placeholder="Programme Full Name (e.g. B.Tech Computer Science)"
                    value={newProg.name}
                    onChange={(e) => setNewProg({ ...newProg, name: e.target.value })}
                    style={{ flex: '2 1 220px', padding: '0.5rem 0.75rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.85rem' }}
                  />
                  <input
                    type="text"
                    placeholder="Intake (e.g. 120)"
                    value={newProg.intake}
                    onChange={(e) => setNewProg({ ...newProg, intake: e.target.value })}
                    style={{ flex: '1 1 80px', padding: '0.5rem 0.75rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.85rem' }}
                  />
                  <button
                    type="button"
                    onClick={handleAddProgramme}
                    className="btn btn--secondary"
                    style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
                  >
                    + Add Course / Programme
                  </button>
                </div>

                {programmesList.length > 0 && (
                  <div style={{ border: '1px solid #E2E8F0', borderRadius: '6px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead style={{ background: '#F8FAFC', borderBottom: '1px solid #E2E8F0' }}>
                        <tr>
                          <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left' }}>Code</th>
                          <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left' }}>Programme Name</th>
                          <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left' }}>Duration</th>
                          <th style={{ padding: '0.5rem 0.75rem', textAlign: 'left' }}>Approved Intake</th>
                          <th style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {programmesList.map((p, idx) => (
                          <tr key={idx} style={{ borderBottom: '1px solid #E2E8F0' }}>
                            <td style={{ padding: '0.5rem 0.75rem', fontFamily: 'monospace', fontWeight: 600 }}>{p.code}</td>
                            <td style={{ padding: '0.5rem 0.75rem' }}>{p.name}</td>
                            <td style={{ padding: '0.5rem 0.75rem', color: '#64748B' }}>{p.duration}</td>
                            <td style={{ padding: '0.5rem 0.75rem', fontWeight: 600 }}>{p.intake} seats</td>
                            <td style={{ padding: '0.5rem 0.75rem', textAlign: 'center' }}>
                              <button
                                type="button"
                                onClick={() => handleRemoveProgramme(idx)}
                                style={{ background: 'none', border: 'none', color: '#DC2626', cursor: 'pointer', fontWeight: 'bold' }}
                              >
                                Delete
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* ======================================================== */}
          {/* SECTION E: AUTHORIZED INSTITUTION ADMINISTRATOR */}
          {/* ======================================================== */}
          <div className="card" style={{ background: '#FFFFFF', border: '1px solid #D0D5DD', borderRadius: '10px', padding: '1.75rem', marginBottom: '1.5rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Section E</span>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0.2rem 0 0 0' }}>Authorized Institution Administrator</h2>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#667085' }}>
                The designated official authorized to manage institutional operations upon platform approval.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Applicant Full Name <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="text"
                  name="applicant_name"
                  required
                  placeholder="e.g. Dr. Raghavendra Rao"
                  value={formData.applicant_name}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Designation / Role <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <select
                  name="applicant_designation"
                  value={formData.applicant_designation}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem', color: '#102B46', background: '#FFFFFF' }}
                >
                  <option value="Principal">Principal / Headmaster</option>
                  <option value="Registrar">Registrar</option>
                  <option value="Director">Director / Dean</option>
                  <option value="Authorized Signatory">Authorized Signatory / Administrator</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Administrator Email Address <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="email"
                  name="applicant_email"
                  required
                  placeholder="e.g. admin.puc0032@gmail.com"
                  value={formData.applicant_email}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
                <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.25rem' }}>
                  This email will become your login identifier on the Institution Administrator Desk.
                </div>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Contact Mobile Number <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <input
                  type="tel"
                  name="applicant_phone"
                  required
                  maxLength={10}
                  placeholder="e.g. 9876543210"
                  value={formData.applicant_phone}
                  onChange={handleChange}
                  style={{ width: '100%', padding: '0.65rem 0.85rem', border: '1px solid #D0D5DD', borderRadius: '6px', fontSize: '0.9rem' }}
                />
              </div>
            </div>
          </div>

          {/* ======================================================== */}
          {/* SECTION F: CREATE LOGIN CREDENTIALS */}
          {/* ======================================================== */}
          <div className="card" style={{ background: '#FFFFFF', border: '1px solid #D0D5DD', borderRadius: '10px', padding: '1.75rem', marginBottom: '2rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '0.75rem', marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#155EEF', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Section F</span>
              <h2 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#102B46', margin: '0.2rem 0 0 0' }}>Create Login Credentials</h2>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#667085' }}>
                Set your secure password. Upon Platform Admin approval, you will access the desk with this password.
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Create Password <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <PasswordInput
                  required
                  placeholder="Min 8 chars, uppercase, lowercase, number, symbol"
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#344054', marginBottom: '0.35rem' }}>
                  Confirm Password <span style={{ color: '#D92D20' }}>*</span>
                </label>
                <PasswordInput
                  required
                  placeholder="Re-enter same password"
                  value={formData.confirm_password}
                  onChange={(e) => setFormData(prev => ({ ...prev, confirm_password: e.target.value }))}
                />
              </div>
            </div>

            <div style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '6px', padding: '0.75rem 1rem', marginTop: '1rem', fontSize: '0.8rem', color: '#475467' }}>
              <strong>Password Security Requirements:</strong> Minimum 8 characters, at least one uppercase letter (A-Z), one lowercase letter (a-z), one digit (0-9), and one special symbol (e.g. !@#$%^&*). Stored securely using argon2id cryptographic hashing.
            </div>
          </div>

          {/* Submit Action */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <Link
              to="/select-institution"
              className="btn btn--outline"
              style={{ fontWeight: 600 }}
            >
              ← Cancel & Return
            </Link>

            <button
              type="submit"
              disabled={submitting}
              className="btn btn--primary"
              style={{
                padding: '0.85rem 2rem',
                fontSize: '1rem',
                fontWeight: 700,
                background: '#155EEF',
                borderColor: '#155EEF',
                boxShadow: '0 4px 8px rgba(21,94,239,0.25)'
              }}
            >
              {submitting ? 'Submitting Application...' : 'Submit Institution Application →'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
