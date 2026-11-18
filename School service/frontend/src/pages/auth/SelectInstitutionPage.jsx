import React, { useState, useEffect, useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import PasswordInput from '../../components/ui/PasswordInput.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'

export default function SelectInstitutionPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  const [institutions, setInstitutions] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('ALL') // 'ALL' | 'SCHOOLS' | 'PU' | 'DEGREE' | 'UNIVERSITY'

  // Selected Institution & Login Step
  const [selectedInst, setSelectedInst] = useState(null)
  const [step, setStep] = useState('select') // 'select' | 'login'

  // Institution Admin Status Check for Step 2
  const [adminStatus, setAdminStatus] = useState(null)
  const [checkingStatus, setCheckingStatus] = useState(false)

  // Login Form State
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)
  const [loginError, setLoginError] = useState('')

  // Modal State for Action Guidance
  const [activeModal, setActiveModal] = useState(null) // null | { type: string, inst: object }
  const [modalTokenInput, setModalTokenInput] = useState('')
  const [modalTokenError, setModalTokenError] = useState('')

  // 1. Fetch all 30 institutions dynamically from database (with embedded admin_status)
  async function fetchInstitutions(isRefresh = false) {
    try {
      if (isRefresh) {
        setRefreshing(true)
      } else {
        setLoading(true)
      }
      setError('')
      const data = await apiGet('/schools?limit=100')
      const list = Array.isArray(data) ? data : data.value ?? []
      setInstitutions(list)
    } catch (err) {
      setError(err.message || 'Failed to retrieve institutions directory.')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  useEffect(() => {
    fetchInstitutions(false)
  }, [])

  // Auto-select institution from query param (e.g. ?school_id=SCH019)
  useEffect(() => {
    const autoSchoolId = searchParams.get('school_id')
    if (autoSchoolId && institutions.length > 0) {
      const match = institutions.find(s => s.school_id === autoSchoolId)
      if (match) {
        // If active, proceed to login; otherwise open guidance or select
        if (match.admin_status?.can_login) {
          handleContinueToLogin(match)
        } else {
          setSelectedInst(match)
        }
      }
    }
  }, [institutions, searchParams])

  // Calculate dynamic category counts
  const counts = useMemo(() => {
    return {
      all: institutions.length,
      schools: institutions.filter(s => s.category?.toLowerCase().includes('school') || s.school_type === 'School').length,
      pu: institutions.filter(s => s.category?.toLowerCase().includes('pu') || s.school_type === 'PU College').length,
      degree: institutions.filter(s => s.category?.toLowerCase().includes('degree') || s.school_type === 'Degree College').length,
      universities: institutions.filter(s => s.category?.toLowerCase().includes('universit') || s.school_type === 'University').length
    }
  }, [institutions])

  // Filter institutions
  const filtered = useMemo(() => {
    return institutions.filter(inst => {
      // Category filter
      if (categoryFilter === 'SCHOOLS') {
        const isSchool = inst.category?.toLowerCase().includes('school') || inst.school_type === 'School'
        if (!isSchool) return false
      } else if (categoryFilter === 'PU') {
        const isPU = inst.category?.toLowerCase().includes('pu') || inst.school_type === 'PU College'
        if (!isPU) return false
      } else if (categoryFilter === 'DEGREE') {
        const isDegree = inst.category?.toLowerCase().includes('degree') || inst.school_type === 'Degree College'
        if (!isDegree) return false
      } else if (categoryFilter === 'UNIVERSITY') {
        const isUni = inst.category?.toLowerCase().includes('universit') || inst.school_type === 'University'
        if (!isUni) return false
      }

      // Keyword query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim()
        const nameMatch = inst.school_name?.toLowerCase().includes(q)
        const idMatch = inst.school_id?.toLowerCase().includes(q)
        const districtMatch = inst.district?.toLowerCase().includes(q)
        if (!nameMatch && !idMatch && !districtMatch) return false
      }

      return true
    })
  }, [institutions, categoryFilter, searchQuery])

  // Proceed to Step 2: Administrator Login (only allowed if ACTIVE)
  async function handleContinueToLogin(inst) {
    setSelectedInst(inst)
    setLoginError('')
    setIdentifier('')
    setPassword('')
    setStep('login')

    // Fetch freshest administrator status
    try {
      setCheckingStatus(true)
      const statusRes = await apiGet(`/auth/institution/${inst.school_id}/admin-status`)
      setAdminStatus(statusRes)
    } catch {
      setAdminStatus(null)
    } finally {
      setCheckingStatus(false)
    }
  }

  // Handle Card Action Button Click
  function handleCardAction(e, inst) {
    e.stopPropagation()
    const status = inst.admin_status?.status || 'NOT_INVITED'

    if (status === 'ACTIVE') {
      handleContinueToLogin(inst)
    } else if (status === 'INVITED') {
      setModalTokenInput('')
      setModalTokenError('')
      setActiveModal({ type: 'INVITED', inst })
    } else if (status === 'ACCEPTED_PENDING_PASSWORD') {
      setModalTokenInput('')
      setModalTokenError('')
      setActiveModal({ type: 'ACCEPTED_PENDING_PASSWORD', inst })
    } else if (status === 'SUSPENDED') {
      setActiveModal({ type: 'SUSPENDED', inst })
    } else {
      // NOT_INVITED or EXPIRED
      setActiveModal({ type: 'NOT_INVITED', inst })
    }
  }

  // Handle Token Verification from Modal
  function handleVerifyTokenSubmit(e) {
    e.preventDefault()
    if (!modalTokenInput.trim()) {
      setModalTokenError('Please enter your invitation token.')
      return
    }
    navigate(`/accept-invitation?token=${encodeURIComponent(modalTokenInput.trim())}`)
  }

  // Handle administrator authentication
  async function handleAdminLogin(e) {
    e.preventDefault()
    if (!identifier.trim() || !password) {
      setLoginError('Please enter your administrator email/mobile and password.')
      return
    }

    try {
      setLoginLoading(true)
      setLoginError('')
      const res = await login(identifier.trim(), password, selectedInst.school_id)
      
      if (['school_admin', 'academic_admin', 'institution_admin', 'platform_admin'].includes(res.role)) {
        navigate('/institution-admin')
      } else if (['school_staff', 'admissions_officer', 'student_records_officer', 'general_staff'].includes(res.role)) {
        navigate('/staff')
      } else {
        navigate('/institution-admin')
      }
    } catch (err) {
      setLoginError(err.message || 'Authentication failed. Please verify your credentials and institution assignment.')
    } finally {
      setLoginLoading(false)
    }
  }

  // Helper for Status Badge
  function renderStatusPill(status) {
    switch (status) {
      case 'ACTIVE':
        return (
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            background: '#ECFDF3',
            color: '#027A48',
            border: '1px solid #ABEFC6',
            padding: '0.15rem 0.5rem',
            borderRadius: '12px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#12B76A' }}></span>
            Active Administrator
          </span>
        )
      case 'INVITED':
        return (
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            background: '#F0F9FF',
            color: '#026AA2',
            border: '1px solid #B9E6FE',
            padding: '0.15rem 0.5rem',
            borderRadius: '12px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#0BA5EC' }}></span>
            Invitation Dispatched
          </span>
        )
      case 'ACCEPTED_PENDING_PASSWORD':
        return (
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            background: '#F9F5FF',
            color: '#6941C6',
            border: '1px solid #E9D7FE',
            padding: '0.15rem 0.5rem',
            borderRadius: '12px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#9E77ED' }}></span>
            Complete Setup Pending
          </span>
        )
      case 'SUSPENDED':
        return (
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 700,
            background: '#FEF3F2',
            color: '#B42318',
            border: '1px solid #FECDCA',
            padding: '0.15rem 0.5rem',
            borderRadius: '12px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#F04438' }}></span>
            Access Suspended
          </span>
        )
      default:
        return (
          <span style={{
            fontSize: '0.72rem',
            fontWeight: 600,
            background: '#F8F9FA',
            color: '#667085',
            border: '1px solid #EAECF0',
            padding: '0.15rem 0.5rem',
            borderRadius: '12px',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.3rem'
          }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#98A2B3' }}></span>
            Not Provisioned
          </span>
        )
    }
  }

  return (
    <div className="select-institution-page" style={{ minHeight: '85vh', background: '#F5F7FA', padding: '2rem 1rem 5rem 1rem' }}>
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Select Your Institution' }
      ]} />

      <div style={{ maxWidth: '1100px', margin: '1rem auto 0 auto' }}>
        {step === 'select' ? (
          <div>
            {/* Header Banner */}
            <div style={{
              background: '#102B46',
              color: '#FFFFFF',
              padding: '2rem',
              borderRadius: '12px',
              marginBottom: '2rem',
              boxShadow: '0 4px 12px rgba(16,43,70,0.12)'
            }}>
              <div style={{ display: 'inline-block', background: '#155EEF', color: '#FFFFFF', fontWeight: 700, padding: '0.25rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.5rem', textTransform: 'uppercase' }}>
                Official Administrative Gateway
              </div>
              <h1 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 0.5rem 0', color: '#FFFFFF' }}>
                Select Your Institution
              </h1>
              <p style={{ margin: 0, color: '#D0D5DD', fontSize: '1rem', maxWidth: '800px', lineHeight: 1.5 }}>
                Identify your authorized Karnataka school, PU college, degree college, or university to access the Institution Administrator Desk.
              </p>
            </div>

            {error && <Alert type="error" title="Error Loading Institutions" style={{ marginBottom: '1.5rem' }}>{error}</Alert>}

            {/* Filter Controls Bar */}
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #E2E8F0',
              borderRadius: '12px',
              padding: '1.25rem',
              marginBottom: '1.5rem',
              boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
            }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', justifyContent: 'space-between', alignItems: 'center' }}>
                {/* Search Input */}
                <div style={{ flex: '1 1 300px', maxWidth: '400px' }}>
                  <input
                    type="text"
                    placeholder="Search by Institution Name or ID (e.g. SCH019, Ballari)..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.65rem 0.9rem',
                      borderRadius: '8px',
                      border: '1px solid #D0D5DD',
                      fontSize: '0.9rem',
                      color: '#102B46',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                {/* Category Pills & Refresh Button */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', alignItems: 'center' }}>
                  {[
                    { id: 'ALL', label: 'All Institutions', count: counts.all },
                    { id: 'SCHOOLS', label: 'Schools', count: counts.schools },
                    { id: 'PU', label: 'PU Colleges', count: counts.pu },
                    { id: 'DEGREE', label: 'Degree Colleges', count: counts.degree },
                    { id: 'UNIVERSITY', label: 'Universities', count: counts.universities }
                  ].map((tab) => (
                    <button
                      key={tab.id}
                      onClick={() => setCategoryFilter(tab.id)}
                      style={{
                        padding: '0.45rem 0.85rem',
                        borderRadius: '20px',
                        border: categoryFilter === tab.id ? '2px solid #155EEF' : '1px solid #D0D5DD',
                        background: categoryFilter === tab.id ? '#EFF4FF' : '#FFFFFF',
                        color: categoryFilter === tab.id ? '#155EEF' : '#475467',
                        fontWeight: 700,
                        fontSize: '0.825rem',
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.35rem'
                      }}
                    >
                      <span>{tab.label}</span>
                      <span style={{
                        background: categoryFilter === tab.id ? '#155EEF' : '#EAECF0',
                        color: categoryFilter === tab.id ? '#FFFFFF' : '#475467',
                        padding: '0.1rem 0.4rem',
                        borderRadius: '10px',
                        fontSize: '0.72rem'
                      }}>
                        {tab.count}
                      </span>
                    </button>
                  ))}

                  {/* Real-time Refresh Button */}
                  <button
                    type="button"
                    onClick={() => fetchInstitutions(true)}
                    disabled={refreshing}
                    title="Refresh administrator invitation and activation statuses from server"
                    style={{
                      padding: '0.45rem 0.75rem',
                      borderRadius: '8px',
                      border: '1px solid #D0D5DD',
                      background: '#FFFFFF',
                      color: '#344054',
                      fontSize: '0.825rem',
                      fontWeight: 600,
                      cursor: refreshing ? 'not-allowed' : 'pointer',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.35rem'
                    }}
                  >
                    <span style={{ display: 'inline-block', transform: refreshing ? 'rotate(180deg)' : 'none', transition: 'transform 0.4s ease' }}>↻</span>
                    <span>{refreshing ? 'Updating...' : 'Refresh Status'}</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Institution Cards Grid */}
            {loading ? (
              <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
                <LoadingSpinner size="lg" />
                <p style={{ marginTop: '1rem', color: '#667085', fontSize: '0.95rem' }}>
                  Retrieving authorized institution directory...
                </p>
              </div>
            ) : filtered.length === 0 ? (
              <div style={{ background: '#FFFFFF', padding: '3rem', borderRadius: '12px', textAlign: 'center', border: '1px solid #E2E8F0' }}>
                <div style={{ fontSize: '2.5rem', marginBottom: '0.75rem' }}>🔍</div>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#102B46' }}>No matching institutions found</h3>
                <p style={{ color: '#667085', margin: 0 }}>Try clearing your search query or switching category filters.</p>
              </div>
            ) : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                {filtered.map((inst) => {
                  const isSelected = selectedInst?.school_id === inst.school_id
                  const categoryBadgeColor = 
                    inst.category?.toLowerCase().includes('universit') ? '#444CE7' :
                    inst.category?.toLowerCase().includes('degree') ? '#155EEF' :
                    inst.category?.toLowerCase().includes('pu') ? '#C11574' : '#12B76A'

                  const adminStatusObj = inst.admin_status || {
                    status: 'NOT_INVITED',
                    button_label: 'Invitation Required',
                    can_login: false,
                    status_description: 'No administrator invitation generated yet.'
                  }
                  const status = adminStatusObj.status

                  // Dynamic Button Styling based on verified backend status
                  let buttonBg = '#F8F9FA'
                  let buttonColor = '#344054'
                  let buttonBorder = '1px solid #D0D5DD'
                  let buttonLabel = adminStatusObj.button_label || 'Invitation Required'
                  let buttonBoxShadow = 'none'

                  if (status === 'ACTIVE') {
                    buttonBg = isSelected ? '#155EEF' : '#102B46'
                    buttonColor = '#FFFFFF'
                    buttonBorder = 'none'
                    buttonLabel = 'Continue to Administrator Login →'
                    buttonBoxShadow = '0 2px 4px rgba(16,43,70,0.2)'
                  } else if (status === 'INVITED') {
                    buttonBg = '#026AA2'
                    buttonColor = '#FFFFFF'
                    buttonBorder = 'none'
                    buttonLabel = 'Invitation Available'
                    buttonBoxShadow = '0 2px 4px rgba(2,106,162,0.2)'
                  } else if (status === 'ACCEPTED_PENDING_PASSWORD') {
                    buttonBg = '#6941C6'
                    buttonColor = '#FFFFFF'
                    buttonBorder = 'none'
                    buttonLabel = 'Complete Account Setup'
                    buttonBoxShadow = '0 2px 4px rgba(105,65,198,0.2)'
                  } else if (status === 'SUSPENDED') {
                    buttonBg = '#FEF3F2'
                    buttonColor = '#B42318'
                    buttonBorder = '1px solid #FECDCA'
                    buttonLabel = 'Account Suspended'
                    buttonBoxShadow = 'none'
                  } else {
                    // NOT_INVITED / EXPIRED
                    buttonBg = '#F8F9FA'
                    buttonColor = '#475467'
                    buttonBorder = '1px solid #D0D5DD'
                    buttonLabel = 'Invitation Required'
                    buttonBoxShadow = 'none'
                  }

                  return (
                    <div
                      key={inst.school_id}
                      onClick={() => setSelectedInst(inst)}
                      style={{
                        background: '#FFFFFF',
                        border: isSelected ? '2px solid #155EEF' : '1px solid #E2E8F0',
                        borderRadius: '12px',
                        padding: '1.25rem',
                        cursor: 'pointer',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between',
                        boxShadow: isSelected ? '0 4px 14px rgba(21,94,239,0.18)' : '0 1px 3px rgba(0,0,0,0.04)',
                        transition: 'transform 0.15s ease, box-shadow 0.15s ease'
                      }}
                      onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 6px 16px rgba(16,43,70,0.08)' }}
                      onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = isSelected ? '0 4px 14px rgba(21,94,239,0.18)' : '0 1px 3px rgba(0,0,0,0.04)' }}
                    >
                      <div>
                        {/* Top Badges */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                          <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                            <span style={{
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              background: '#EFF4FF',
                              color: '#155EEF',
                              padding: '0.2rem 0.5rem',
                              borderRadius: '4px',
                              fontFamily: 'monospace'
                            }}>
                              {inst.school_id}
                            </span>
                            <span style={{
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              background: categoryBadgeColor,
                              color: '#FFFFFF',
                              padding: '0.2rem 0.55rem',
                              borderRadius: '4px'
                            }}>
                              {inst.category || inst.school_type}
                            </span>
                          </div>

                          {/* Dynamic State Pill */}
                          {renderStatusPill(status)}
                        </div>

                        {/* Title & Location */}
                        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#102B46', margin: '0 0 0.4rem 0', lineHeight: 1.3 }}>
                          {inst.school_name}
                        </h3>

                        <p style={{ fontSize: '0.85rem', color: '#667085', margin: '0 0 0.5rem 0' }}>
                          📍 {inst.district}, {inst.state}
                        </p>

                        <div style={{ fontSize: '0.8rem', color: '#344054', marginBottom: '0.5rem' }}>
                          🏛️ Type: <strong>{inst.school_type}</strong>
                        </div>

                        {inst.affiliation && (
                          <div style={{ fontSize: '0.78rem', color: '#155EEF', fontWeight: 500, marginBottom: '0.75rem' }}>
                            🎓 {inst.affiliation}
                          </div>
                        )}
                      </div>

                      {/* Card Action */}
                      <div style={{ borderTop: '1px solid #F2F4F7', paddingTop: '0.85rem', marginTop: '0.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.78rem', color: '#667085' }}>
                          {inst.established_year ? `Est. ${inst.established_year}` : 'Verified'}
                        </span>

                        <button
                          type="button"
                          onClick={(e) => handleCardAction(e, inst)}
                          style={{
                            background: buttonBg,
                            color: buttonColor,
                            border: buttonBorder,
                            borderRadius: '6px',
                            padding: '0.55rem 0.95rem',
                            fontSize: '0.825rem',
                            fontWeight: 700,
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.35rem',
                            boxShadow: buttonBoxShadow,
                            transition: 'all 0.15s ease'
                          }}
                        >
                          {buttonLabel}
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* =================================================================
               GUIDANCE MODAL OVERLAYS (For non-active / action states)
               ================================================================= */}
            {activeModal && (
              <div
                style={{
                  position: 'fixed',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  backgroundColor: 'rgba(16, 43, 70, 0.65)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 9999,
                  padding: '1rem',
                  backdropFilter: 'blur(3px)'
                }}
                onClick={() => setActiveModal(null)}
              >
                <div
                  style={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    width: '100%',
                    maxWidth: '520px',
                    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
                    overflow: 'hidden'
                  }}
                  onClick={(e) => e.stopPropagation()}
                >
                  {/* Modal Header */}
                  <div style={{
                    padding: '1.25rem 1.5rem',
                    borderBottom: '1px solid #EAECF0',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    background: 
                      activeModal.type === 'SUSPENDED' ? '#FEF3F2' :
                      activeModal.type === 'INVITED' ? '#F0F9FF' :
                      activeModal.type === 'ACCEPTED_PENDING_PASSWORD' ? '#F9F5FF' : '#F8F9FA'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span style={{ fontSize: '1.25rem' }}>
                        {activeModal.type === 'SUSPENDED' ? '⛔' :
                         activeModal.type === 'INVITED' ? '✉️' :
                         activeModal.type === 'ACCEPTED_PENDING_PASSWORD' ? '⚙️' : '🔒'}
                      </span>
                      <h3 style={{
                        margin: 0,
                        fontSize: '1.1rem',
                        fontWeight: 700,
                        color: activeModal.type === 'SUSPENDED' ? '#B42318' : '#102B46'
                      }}>
                        {activeModal.type === 'SUSPENDED' && 'Administrative Access Suspended'}
                        {activeModal.type === 'INVITED' && 'Administrator Invitation Available'}
                        {activeModal.type === 'ACCEPTED_PENDING_PASSWORD' && 'Complete Account Setup'}
                        {activeModal.type === 'NOT_INVITED' && 'Administrator Invitation Required'}
                      </h3>
                    </div>
                    <button
                      onClick={() => setActiveModal(null)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        fontSize: '1.3rem',
                        color: '#667085',
                        cursor: 'pointer',
                        padding: '0.2rem 0.5rem',
                        lineHeight: 1
                      }}
                    >
                      ✕
                    </button>
                  </div>

                  {/* Modal Body */}
                  <div style={{ padding: '1.5rem' }}>
                    {/* Institution Meta Banner */}
                    <div style={{
                      background: '#F8F9FA',
                      borderRadius: '8px',
                      padding: '0.85rem 1rem',
                      marginBottom: '1.25rem',
                      border: '1px solid #EAECF0'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                        <span style={{ fontWeight: 700, color: '#102B46', fontSize: '0.95rem' }}>
                          {activeModal.inst.school_name}
                        </span>
                        <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '0.75rem', background: '#EFF4FF', color: '#155EEF', padding: '0.15rem 0.45rem', borderRadius: '4px' }}>
                          {activeModal.inst.school_id}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#667085' }}>
                        📍 {activeModal.inst.district}, {activeModal.inst.state} · {activeModal.inst.school_type}
                      </div>
                    </div>

                    {/* MODAL CASE 1: NOT INVITED */}
                    {activeModal.type === 'NOT_INVITED' && (
                      <div>
                        <p style={{ margin: '0 0 1rem 0', color: '#344054', fontSize: '0.9rem', lineHeight: 1.5 }}>
                          No Academic Administrator invitation has been issued for this institution yet. In compliance with Department governance standards, access to the Institution Administrator Desk is strictly restricted to verified heads of institutions appointed by the Directorate.
                        </p>
                        <div style={{ background: '#FEF0C7', border: '1px solid #FDB022', borderRadius: '8px', padding: '0.85rem', marginBottom: '1.25rem' }}>
                          <p style={{ margin: 0, color: '#7A271A', fontSize: '0.825rem', lineHeight: 1.45 }}>
                            <strong>Authorized Institutional Heads:</strong> If you are the appointed principal or registrar for this institution, please contact the Central Platform Administration or your district nodal officer to receive your official registration invitation.
                          </p>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                          <button
                            type="button"
                            onClick={() => setActiveModal(null)}
                            style={{
                              background: '#102B46',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.6rem 1.25rem',
                              fontSize: '0.875rem',
                              fontWeight: 600,
                              cursor: 'pointer'
                            }}
                          >
                            Understood
                          </button>
                        </div>
                      </div>
                    )}

                    {/* MODAL CASE 2: INVITED */}
                    {activeModal.type === 'INVITED' && (
                      <div>
                        <div style={{ background: '#F0F9FF', border: '1px solid #B9E6FE', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                          <p style={{ margin: '0 0 0.4rem 0', color: '#026AA2', fontSize: '0.95rem', fontWeight: 700 }}>
                            Administrator Invitation Available
                          </p>
                          <p style={{ margin: 0, color: '#0369A1', fontSize: '0.85rem', lineHeight: 1.5 }}>
                            An official Academic Administrator invitation has been issued for <strong>{activeModal.inst.school_name}</strong> (<strong>{activeModal.inst.school_id}</strong>).
                          </p>
                        </div>

                        <p style={{ margin: '0 0 1.25rem 0', color: '#344054', fontSize: '0.875rem', lineHeight: 1.5 }}>
                          The appointed educational administrator can proceed directly to verify their credentials and finalize account setup.
                        </p>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                          <button
                            type="button"
                            onClick={() => setActiveModal(null)}
                            style={{
                              background: '#FFFFFF',
                              color: '#344054',
                              border: '1px solid #D0D5DD',
                              borderRadius: '6px',
                              padding: '0.6rem 1rem',
                              fontSize: '0.875rem',
                              fontWeight: 600,
                              cursor: 'pointer'
                            }}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              const sid = activeModal.inst.school_id
                              setActiveModal(null)
                              navigate(`/accept-invitation?school_id=${encodeURIComponent(sid)}`)
                            }}
                            style={{
                              background: '#026AA2',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.6rem 1.25rem',
                              fontSize: '0.875rem',
                              fontWeight: 700,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.35rem',
                              boxShadow: '0 2px 4px rgba(2,106,162,0.2)'
                            }}
                          >
                            Proceed to Account Setup →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* MODAL CASE 3: ACCEPTED PENDING PASSWORD */}
                    {activeModal.type === 'ACCEPTED_PENDING_PASSWORD' && (
                      <div>
                        <div style={{ background: '#F9F5FF', border: '1px solid #E9D7FE', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                          <p style={{ margin: '0 0 0.4rem 0', color: '#6941C6', fontSize: '0.95rem', fontWeight: 700 }}>
                            Account Setup Incomplete
                          </p>
                          <p style={{ margin: 0, color: '#53389E', fontSize: '0.85rem', lineHeight: 1.5 }}>
                            The administrator invitation for <strong>{activeModal.inst.school_name}</strong> (<strong>{activeModal.inst.school_id}</strong>) has been verified. Final password configuration is pending.
                          </p>
                        </div>

                        <p style={{ margin: '0 0 1.25rem 0', color: '#344054', fontSize: '0.875rem', lineHeight: 1.5 }}>
                          The appointed administrator can proceed directly to complete their password setup and activate the administrative desk.
                        </p>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                          <button
                            type="button"
                            onClick={() => setActiveModal(null)}
                            style={{
                              background: '#FFFFFF',
                              color: '#344054',
                              border: '1px solid #D0D5DD',
                              borderRadius: '6px',
                              padding: '0.6rem 1rem',
                              fontSize: '0.875rem',
                              fontWeight: 600,
                              cursor: 'pointer'
                            }}
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              const sid = activeModal.inst.school_id
                              setActiveModal(null)
                              navigate(`/accept-invitation?school_id=${encodeURIComponent(sid)}`)
                            }}
                            style={{
                              background: '#6941C6',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.6rem 1.25rem',
                              fontSize: '0.875rem',
                              fontWeight: 700,
                              cursor: 'pointer',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '0.35rem',
                              boxShadow: '0 2px 4px rgba(105,65,198,0.2)'
                            }}
                          >
                            Proceed to Account Setup →
                          </button>
                        </div>
                      </div>
                    )}

                    {/* MODAL CASE 4: SUSPENDED */}
                    {activeModal.type === 'SUSPENDED' && (
                      <div>
                        <div style={{ background: '#FEF3F2', border: '1px solid #FECDCA', borderRadius: '8px', padding: '0.9rem', marginBottom: '1.25rem' }}>
                          <p style={{ margin: 0, color: '#B42318', fontSize: '0.85rem', lineHeight: 1.45, fontWeight: 500 }}>
                            Administrative access and portal sign-ins for <strong>{activeModal.inst.school_name}</strong> ({activeModal.inst.school_id}) have been suspended by the Central Platform Administrator.
                          </p>
                        </div>
                        <p style={{ margin: '0 0 1.25rem 0', color: '#475467', fontSize: '0.85rem', lineHeight: 1.5 }}>
                          While under suspension, staff operations and administrative logins for this institution are disabled to preserve audit and governance compliance.
                        </p>
                        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                          <button
                            type="button"
                            onClick={() => setActiveModal(null)}
                            style={{
                              background: '#B42318',
                              color: '#FFFFFF',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '0.6rem 1.25rem',
                              fontSize: '0.875rem',
                              fontWeight: 600,
                              cursor: 'pointer'
                            }}
                          >
                            Close
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          /* =================================================================
             STEP 2: INSTITUTION-SPECIFIC ADMINISTRATOR LOGIN
             ================================================================= */
          <div style={{ maxWidth: '540px', margin: '0 auto' }}>
            {/* Back Button */}
            <button
              onClick={() => {
                setStep('select')
                setLoginError('')
              }}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#155EEF',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer',
                marginBottom: '1rem',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.35rem',
                padding: 0
              }}
            >
              ← Back to Institution Selection
            </button>

            {/* Institution Context Card */}
            <div style={{
              background: '#102B46',
              color: '#FFFFFF',
              borderRadius: '12px',
              padding: '1.5rem',
              marginBottom: '1.5rem',
              boxShadow: '0 4px 12px rgba(16,43,70,0.12)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span style={{
                    fontSize: '0.75rem',
                    fontWeight: 700,
                    background: 'rgba(255,255,255,0.95)',
                    color: '#102B46',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px',
                    fontFamily: 'monospace'
                  }}>
                    {selectedInst?.school_id}
                  </span>

                  <span style={{
                    fontSize: '0.72rem',
                    fontWeight: 700,
                    background: '#155EEF',
                    color: '#FFFFFF',
                    padding: '0.2rem 0.5rem',
                    borderRadius: '4px'
                  }}>
                    {selectedInst?.category || selectedInst?.school_type}
                  </span>
                </div>

                {adminStatus && renderStatusPill(adminStatus.status)}
              </div>

              <h2 style={{ fontSize: '1.4rem', fontWeight: 800, margin: '0 0 0.4rem 0', color: '#FFFFFF' }}>
                {selectedInst?.school_name}
              </h2>
              <p style={{ color: '#D0D5DD', fontSize: '0.85rem', margin: 0 }}>
                📍 {selectedInst?.district}, {selectedInst?.state} · {selectedInst?.school_type}
              </p>
            </div>

            {/* Login Form Container */}
            <div style={{
              background: '#FFFFFF',
              border: '1px solid #D0D5DD',
              borderRadius: '12px',
              padding: '2rem',
              boxShadow: '0 4px 10px rgba(0,0,0,0.06)'
            }}>
              <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.3rem', color: '#102B46', margin: '0 0 0.35rem 0', fontWeight: 700 }}>
                  Administrator Authentication
                </h3>
                <p style={{ color: '#667085', fontSize: '0.85rem', margin: 0 }}>
                  Enter credentials authorized for <strong>{selectedInst?.school_id}</strong>
                </p>
              </div>

              {loginError && (
                <Alert type="error" title="Authentication Error" style={{ marginBottom: '1.25rem' }}>
                  {loginError}
                </Alert>
              )}

              {/* Verify administrator provisioning status */}
              {checkingStatus ? (
                <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
                  <LoadingSpinner size="md" />
                  <p style={{ marginTop: '0.5rem', color: '#667085', fontSize: '0.85rem' }}>
                    Verifying administrator provisioning status...
                  </p>
                </div>
              ) : adminStatus && !adminStatus.can_login ? (
                /* Non-loginable State Guard in Step 2 */
                <div style={{
                  background: adminStatus.status === 'SUSPENDED' ? '#FEF3F2' : '#FEF0C7',
                  border: `1px solid ${adminStatus.status === 'SUSPENDED' ? '#FECDCA' : '#FDB022'}`,
                  borderRadius: '8px',
                  padding: '1.25rem',
                  marginBottom: '1.5rem'
                }}>
                  <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'flex-start' }}>
                    <span style={{ fontSize: '1.3rem' }}>
                      {adminStatus.status === 'SUSPENDED' ? '⛔' : '⚠️'}
                    </span>
                    <div>
                      <h4 style={{
                        margin: '0 0 0.35rem 0',
                        color: adminStatus.status === 'SUSPENDED' ? '#B42318' : '#B54708',
                        fontSize: '0.95rem',
                        fontWeight: 700
                      }}>
                        {adminStatus.button_label || 'Login Not Permitted'}
                      </h4>
                      <p style={{
                        margin: '0 0 0.85rem 0',
                        color: adminStatus.status === 'SUSPENDED' ? '#7A271A' : '#7A271A',
                        fontSize: '0.85rem',
                        lineHeight: 1.45
                      }}>
                        {adminStatus.status_description || 'This institution does not currently have an active administrator account authorized for login.'}
                      </p>
                      <button
                        onClick={() => setStep('select')}
                        className="btn btn--secondary btn--sm"
                        style={{ fontSize: '0.8rem' }}
                      >
                        ← Return to Institution Selection
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                /* ACTIVE: Show Administrator Login Form */
                <form onSubmit={handleAdminLogin}>
                  <div style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                      Administrator Email or Registered Mobile
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. admin.sch019@gmail.com"
                      value={identifier}
                      onChange={(e) => setIdentifier(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        border: '1px solid #D0D5DD',
                        borderRadius: '6px',
                        fontSize: '0.925rem',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>

                  <div style={{ marginBottom: '0.75rem' }}>
                    <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 600, color: '#102B46', marginBottom: '0.35rem' }}>
                      Password
                    </label>
                    <PasswordInput
                      required
                      placeholder="Enter administrator password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      style={{
                        width: '100%',
                        padding: '0.65rem 0.85rem',
                        border: '1px solid #D0D5DD',
                        borderRadius: '6px',
                        fontSize: '0.925rem',
                        boxSizing: 'border-box'
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '1.25rem' }}>
                    <Link to="/forgot-password" style={{ fontSize: '0.8125rem', color: '#155EEF', textDecoration: 'underline' }}>
                      Forgot password?
                    </Link>
                  </div>

                  <button
                    type="submit"
                    disabled={loginLoading}
                    style={{
                      width: '100%',
                      background: '#155EEF',
                      color: '#FFFFFF',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '0.75rem 1rem',
                      fontSize: '0.95rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem',
                      boxShadow: '0 2px 6px rgba(21,94,239,0.25)'
                    }}
                  >
                    {loginLoading ? <LoadingSpinner size="sm" /> : 'Sign In as Institution Administrator →'}
                  </button>

                  {/* Security Notice */}
                  <div style={{
                    marginTop: '1.5rem',
                    padding: '0.85rem',
                    background: '#F8F9FA',
                    borderRadius: '6px',
                    border: '1px solid #EAECF0',
                    fontSize: '0.75rem',
                    color: '#667085',
                    lineHeight: 1.4
                  }}>
                    🔒 <strong>Strict Institution Isolation:</strong> Your account assignment will be authenticated against <strong>{selectedInst?.school_id}</strong> on the server. Cross-institution access attempts are strictly blocked and audited.
                  </div>
                </form>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
