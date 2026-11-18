import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { apiGet, apiPost } from '../../utils/api.js'
import Alert from '../../components/ui/Alert.jsx'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'

export default function StaffCandidateApplicationPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')

  const [loading, setLoading] = useState(true)
  const [appData, setAppData] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form states
  const [candidateName, setCandidateName] = useState('')
  const [candidatePhone, setCandidatePhone] = useState('')
  
  // Qualifications array
  const [qualifications, setQualifications] = useState([
    { degree: '', institution: '', year: '', marks_percentage: '' }
  ])

  // Employment details
  const [currentEmployer, setCurrentEmployer] = useState('')
  const [experienceYears, setExperienceYears] = useState('')
  const [designation, setDesignation] = useState('')
  const [noticePeriod, setNoticePeriod] = useState('')

  // Documents
  const [documents, setDocuments] = useState([
    { doc_type: 'resume', filename: 'curriculum_vitae.pdf' },
    { doc_type: 'id_proof', filename: 'aadhaar_card.pdf' }
  ])

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    async function loadApp() {
      if (!token) {
        setError('Missing staff candidate invitation token. Please check the link provided by your institution administrator.')
        setLoading(false)
        return
      }

      try {
        setLoading(true)
        setError('')
        const res = await apiGet(`/auth/staff-candidate/application?token=${encodeURIComponent(token)}`)
        setAppData(res)
        setCandidateName(res.candidate_name || '')
        setCandidatePhone(res.candidate_phone || '')
        if (Array.isArray(res.qualifications) && res.qualifications.length > 0) {
          setQualifications(res.qualifications)
        }
        if (res.employment_details) {
          setCurrentEmployer(res.employment_details.current_employer || '')
          setExperienceYears(res.employment_details.experience_years || '')
          setDesignation(res.employment_details.designation || '')
          setNoticePeriod(res.employment_details.notice_period || '')
        }
        if (Array.isArray(res.documents) && res.documents.length > 0) {
          setDocuments(res.documents)
        }
      } catch (err) {
        setError(err.message || 'Invalid or expired candidate invitation link.')
      } finally {
        setLoading(false)
      }
    }
    loadApp()
  }, [token])

  function handleAddQual() {
    setQualifications([...qualifications, { degree: '', institution: '', year: '', marks_percentage: '' }])
  }

  function handleQualChange(index, field, value) {
    const updated = [...qualifications]
    updated[index][field] = value
    setQualifications(updated)
  }

  function handleRemoveQual(index) {
    setQualifications(qualifications.filter((_, i) => i !== index))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!candidateName.trim()) {
      setError('Please provide your full legal name.')
      return
    }

    try {
      setSubmitting(true)
      setError('')
      const payload = {
        token,
        candidate_name: candidateName.trim(),
        candidate_phone: candidatePhone.trim() || undefined,
        qualifications: qualifications.filter(q => q.degree.trim()),
        employment_details: {
          current_employer: currentEmployer.trim(),
          experience_years: experienceYears ? parseInt(experienceYears, 10) : 0,
          designation: designation.trim(),
          notice_period: noticePeriod.trim()
        },
        documents
      }

      const res = await apiPost('/auth/staff-candidate/submit', payload)
      setSuccess(res.message)
      // Reload application status
      const updated = await apiGet(`/auth/staff-candidate/application?token=${encodeURIComponent(token)}`)
      setAppData(updated)
    } catch (err) {
      setError(err.message || 'Failed to submit staff application dossier.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
        <LoadingSpinner size="lg" />
        <p style={{ marginTop: '1rem', color: '#667085' }}>Loading staff candidate portal...</p>
      </div>
    )
  }

  if (error && !appData) {
    return (
      <div className="container" style={{ maxWidth: '600px', margin: '3rem auto', padding: '0 1rem' }}>
        <Alert type="error" title="Invitation Error">{error}</Alert>
        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
          <Link to="/login" className="btn btn--primary">Return to Sign In</Link>
        </div>
      </div>
    )
  }

  const isEditable = appData?.status === 'invited' || appData?.status === 'correction_requested'

  return (
    <div style={{ background: '#F5F7FA', minHeight: '85vh', paddingBottom: '4rem' }}>
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Staff Onboarding Portal' }
      ]} />

      <div style={{ maxWidth: '850px', margin: '1.5rem auto 0 auto', padding: '0 1rem' }}>
        {/* Header Banner */}
        <div style={{
          background: 'linear-gradient(135deg, #102B46 0%, #155EEF 100%)',
          color: '#FFFFFF',
          borderRadius: '12px',
          padding: '1.75rem 2rem',
          marginBottom: '1.5rem',
          boxShadow: '0 4px 14px rgba(16,43,70,0.15)'
        }}>
          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
            <span style={{ background: 'rgba(255,255,255,0.2)', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
              {appData?.institution_id}
            </span>
            <span style={{ background: 'rgba(255,255,255,0.2)', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700 }}>
              {appData?.category}
            </span>
            <span style={{
              background: appData?.status === 'approved' ? '#12B76A' : appData?.status === 'declined' ? '#F04438' : '#F79009',
              padding: '0.2rem 0.6rem',
              borderRadius: '4px',
              fontSize: '0.75rem',
              fontWeight: 800,
              textTransform: 'uppercase'
            }}>
              {appData?.status?.replace('_', ' ')}
            </span>
          </div>

          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, margin: '0 0 0.35rem 0' }}>
            Staff Candidate Dossier Submission
          </h1>
          <p style={{ margin: 0, color: '#E0EAFF', fontSize: '0.9rem' }}>
            Target Institution: <strong>{appData?.institution_name}</strong> · Role: <strong style={{ textTransform: 'capitalize' }}>{appData?.role_id?.replace('_', ' ')}</strong>
          </p>
        </div>

        {error && <Alert type="error" title="Notice" style={{ marginBottom: '1.25rem' }}>{error}</Alert>}
        {success && <Alert type="success" title="Success" style={{ marginBottom: '1.25rem' }}>{success}</Alert>}

        {/* Correction Notes from Admin */}
        {appData?.status === 'correction_requested' && appData?.correction_notes && (
          <div style={{ marginBottom: '1.5rem' }}>
            <Alert type="warning" title="Institution Administrator Correction Request">
              <div style={{ fontWeight: 600, color: '#B54708', marginTop: '0.25rem' }}>
                {appData.correction_notes}
              </div>
              <div style={{ fontSize: '0.78rem', marginTop: '0.5rem', color: '#7A2E0E' }}>
                Please review your qualifications, employment details, or documents below and submit an updated dossier.
              </div>
            </Alert>
          </div>
        )}

        {/* Status: Under Review */}
        {(appData?.status === 'submitted' || appData?.status === 'resubmitted') && (
          <div style={{ marginBottom: '1.5rem' }}>
            <Alert type="info" title="Application Dossier Under Review">
              Your staff candidate application has been submitted and is currently being evaluated by the Institution Administrator of <strong>{appData.institution_name}</strong>.
              You will receive an official activation invitation once your credentials are confirmed.
            </Alert>
          </div>
        )}

        {/* Status: Approved */}
        {appData?.status === 'approved' && (
          <div style={{ marginBottom: '1.5rem' }}>
            <Alert type="success" title="Application Approved!">
              Congratulations! Your staff candidate application has been formally approved by the Institution Administrator.
              <div style={{ marginTop: '0.75rem' }}>
                <Link
                  to={`/staff-activation?token=${appData.activation_token}`}
                  className="btn btn--primary"
                  style={{ textDecoration: 'none', display: 'inline-block' }}
                >
                  Activate Your Account & Set Password →
                </Link>
              </div>
            </Alert>
          </div>
        )}

        {/* Status: Declined */}
        {appData?.status === 'declined' && (
          <div style={{ marginBottom: '1.5rem' }}>
            <Alert type="error" title="Application Declined">
              The Institution Administrator has reviewed and declined this application.
              {appData.review_notes && (
                <div style={{ marginTop: '0.5rem', fontWeight: 600 }}>
                  Reason: {appData.review_notes}
                </div>
              )}
            </Alert>
          </div>
        )}

        {/* Candidate Dossier Form */}
        <div style={{ background: '#FFFFFF', border: '1px solid #E2E8F0', borderRadius: '12px', padding: '2rem', boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}>
          <form onSubmit={handleSubmit}>
            
            {/* Section 1: Candidate Identity */}
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '1.5rem', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#102B46', margin: '0 0 1rem 0' }}>
                1. Personal & Contact Information
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Full Legal Name *
                  </label>
                  <input
                    type="text"
                    required
                    disabled={!isEditable}
                    value={candidateName}
                    onChange={(e) => setCandidateName(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Official Email (Locked)
                  </label>
                  <input
                    type="email"
                    disabled
                    value={appData?.candidate_email || ''}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', background: '#F8F9FA', color: '#667085', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Contact Mobile Number
                  </label>
                  <input
                    type="text"
                    disabled={!isEditable}
                    placeholder="e.g. 9845012345"
                    value={candidatePhone}
                    onChange={(e) => setCandidatePhone(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                  />
                </div>
              </div>
            </div>

            {/* Section 2: Educational Qualifications */}
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '1.5rem', marginBottom: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#102B46', margin: 0 }}>
                  2. Educational Qualifications & Degrees
                </h3>
                {isEditable && (
                  <button
                    type="button"
                    onClick={handleAddQual}
                    style={{ background: '#EFF4FF', color: '#155EEF', border: '1px solid #B2DDFF', borderRadius: '6px', padding: '0.35rem 0.75rem', fontSize: '0.78rem', fontWeight: 700, cursor: 'pointer' }}
                  >
                    + Add Qualification
                  </button>
                )}
              </div>

              {qualifications.map((q, idx) => (
                <div key={idx} style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem', marginBottom: '0.75rem' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>Degree / Certificate *</label>
                      <input
                        type="text"
                        placeholder="e.g. M.Sc. Physics / B.Ed."
                        disabled={!isEditable}
                        value={q.degree}
                        onChange={(e) => handleQualChange(idx, 'degree', e.target.value)}
                        style={{ width: '100%', padding: '0.45rem 0.65rem', borderRadius: '4px', border: '1px solid #D0D5DD', fontSize: '0.8rem' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>Board / University</label>
                      <input
                        type="text"
                        placeholder="e.g. Bangalore University"
                        disabled={!isEditable}
                        value={q.institution}
                        onChange={(e) => handleQualChange(idx, 'institution', e.target.value)}
                        style={{ width: '100%', padding: '0.45rem 0.65rem', borderRadius: '4px', border: '1px solid #D0D5DD', fontSize: '0.8rem' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>Graduation Year</label>
                      <input
                        type="text"
                        placeholder="e.g. 2021"
                        disabled={!isEditable}
                        value={q.year}
                        onChange={(e) => handleQualChange(idx, 'year', e.target.value)}
                        style={{ width: '100%', padding: '0.45rem 0.65rem', borderRadius: '4px', border: '1px solid #D0D5DD', fontSize: '0.8rem' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#475467', marginBottom: '0.2rem' }}>Marks / Percentage</label>
                      <input
                        type="text"
                        placeholder="e.g. 84.5%"
                        disabled={!isEditable}
                        value={q.marks_percentage}
                        onChange={(e) => handleQualChange(idx, 'marks_percentage', e.target.value)}
                        style={{ width: '100%', padding: '0.45rem 0.65rem', borderRadius: '4px', border: '1px solid #D0D5DD', fontSize: '0.8rem' }}
                      />
                    </div>
                  </div>
                  {isEditable && qualifications.length > 1 && (
                    <div style={{ textAlign: 'right', marginTop: '0.5rem' }}>
                      <button
                        type="button"
                        onClick={() => handleRemoveQual(idx)}
                        style={{ background: 'none', border: 'none', color: '#F04438', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
                      >
                        Remove
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Section 3: Professional Employment History */}
            <div style={{ borderBottom: '1px solid #EAECF0', paddingBottom: '1.5rem', marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#102B46', margin: '0 0 1rem 0' }}>
                3. Professional Employment Details
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Current / Previous Employer
                  </label>
                  <input
                    type="text"
                    disabled={!isEditable}
                    placeholder="e.g. Carmel High School"
                    value={currentEmployer}
                    onChange={(e) => setCurrentEmployer(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Designation / Title
                  </label>
                  <input
                    type="text"
                    disabled={!isEditable}
                    placeholder="e.g. Senior Teacher / Records Officer"
                    value={designation}
                    onChange={(e) => setDesignation(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Total Experience (Years)
                  </label>
                  <input
                    type="number"
                    disabled={!isEditable}
                    placeholder="e.g. 5"
                    value={experienceYears}
                    onChange={(e) => setExperienceYears(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.825rem', fontWeight: 700, color: '#344054', marginBottom: '0.35rem' }}>
                    Notice Period
                  </label>
                  <input
                    type="text"
                    disabled={!isEditable}
                    placeholder="e.g. Immediate / 30 Days"
                    value={noticePeriod}
                    onChange={(e) => setNoticePeriod(e.target.value)}
                    style={{ width: '100%', padding: '0.6rem 0.8rem', borderRadius: '6px', border: '1px solid #D0D5DD', fontSize: '0.875rem' }}
                  />
                </div>
              </div>
            </div>

            {/* Section 4: Supporting Documents */}
            <div style={{ marginBottom: '1.75rem' }}>
              <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#102B46', margin: '0 0 1rem 0' }}>
                4. Supporting Documents & Credentials
              </h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1rem' }}>
                {documents.map((doc, idx) => (
                  <div key={idx} style={{ background: '#F8F9FA', border: '1px solid #EAECF0', borderRadius: '8px', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#102B46', textTransform: 'capitalize' }}>
                        📄 {doc.doc_type?.replace('_', ' ')}
                      </span>
                      <span style={{ background: '#ECFDF3', color: '#027A48', fontSize: '0.72rem', fontWeight: 700, padding: '0.15rem 0.45rem', borderRadius: '4px' }}>
                        Attached
                      </span>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#667085', marginTop: '0.35rem', fontFamily: 'monospace' }}>
                      {doc.filename}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Submit Action */}
            {isEditable && (
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', paddingTop: '1rem', borderTop: '1px solid #EAECF0' }}>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn btn--primary"
                  style={{ padding: '0.75rem 1.75rem', fontSize: '0.95rem', fontWeight: 700 }}
                >
                  {submitting ? 'Submitting Application Dossier...' : 'Submit Staff Application Dossier →'}
                </button>
              </div>
            )}
          </form>
        </div>

      </div>
    </div>
  )
}
