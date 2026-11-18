import React, { useEffect, useState, useRef } from 'react'
import { useParams, Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'

// Modular Phase 1 Institution Profile Components
import InstitutionHero from '../../components/institution/InstitutionHero.jsx'
import InstitutionAbout from '../../components/institution/InstitutionAbout.jsx'
import LiveSeatAvailability from '../../components/institution/LiveSeatAvailability.jsx'
import InstitutionFacilities from '../../components/institution/InstitutionFacilities.jsx'
import InstitutionHostel from '../../components/institution/InstitutionHostel.jsx'
import InstitutionTransport from '../../components/institution/InstitutionTransport.jsx'
import InstitutionAcademics from '../../components/institution/InstitutionAcademics.jsx'
import InstitutionAdmissions from '../../components/institution/InstitutionAdmissions.jsx'
import InstitutionAchievements from '../../components/institution/InstitutionAchievements.jsx'
import InstitutionDivisions from '../../components/institution/InstitutionDivisions.jsx'
import InstitutionStudentDirectory from '../../components/institution/InstitutionStudentDirectory.jsx'
import Stage1AdmissionModal from '../../components/admissions/Stage1AdmissionModal.jsx'

export default function SchoolDetailsPage() {
  const { schoolId } = useParams()

  const [institution, setInstitution] = useState(null)
  const [programs, setPrograms] = useState([])
  const [achievements, setAchievements] = useState([])
  const [divisions, setDivisions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeSection, setActiveSection] = useState('about')
  const { user, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false)

  // Redirect unauthenticated users if direct apply link is accessed
  useEffect(() => {
    if (searchParams.get('apply') === 'true') {
      if (!isAuthenticated || user?.role !== 'parent') {
        const progId = searchParams.get('program_id')
        const redirectTarget = `/schools/${schoolId}?apply=true` + (progId ? `&program_id=${encodeURIComponent(progId)}` : '')
        navigate(`/login?category=parent&redirect=${encodeURIComponent(redirectTarget)}`, { replace: true })
      } else {
        setIsApplyModalOpen(true)
      }
    }
  }, [searchParams, isAuthenticated, user, schoolId, navigate])

  function handleApplyClick() {
    if (!isAuthenticated || user?.role !== 'parent') {
      const progId = searchParams.get('program_id')
      const redirectTarget = `/schools/${schoolId}?apply=true` + (progId ? `&program_id=${encodeURIComponent(progId)}` : '')
      navigate(`/login?category=parent&redirect=${encodeURIComponent(redirectTarget)}`)
      return
    }
    setIsApplyModalOpen(true)
  }

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true)
        const [instData, progData, achData, divData] = await Promise.all([
          apiGet(`/schools/${schoolId}`),
          apiGet(`/schools/${schoolId}/programs`).catch(() => []),
          apiGet(`/schools/${schoolId}/achievements`).catch(() => []),
          apiGet(`/schools/${schoolId}/divisions`).catch(() => [])
        ])

        setInstitution(instData)
        setPrograms(Array.isArray(progData) ? progData : [])
        setAchievements(Array.isArray(achData) ? achData : [])
        setDivisions(Array.isArray(divData) ? divData : [])
      } catch (err) {
        setError(err.message || 'Unable to retrieve complete institution details.')
      } finally {
        setLoading(false)
      }
    }

    if (schoolId) {
      loadData()
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }, [schoolId])

  function handleNavigate(sectionId) {
    setActiveSection(sectionId)
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  if (loading) {
    return (
      <div className="container" style={{ maxWidth: '900px', margin: '4rem auto', textAlign: 'center' }}>
        <LoadingSpinner />
        <p style={{ marginTop: '0.75rem', color: '#6b7280', fontSize: '1rem' }}>
          Loading complete public institution profile...
        </p>
      </div>
    )
  }

  if (error || !institution) {
    return (
      <div className="container" style={{ maxWidth: '900px', margin: '2rem auto', padding: '0 1rem' }}>
        <Breadcrumbs crumbs={[
          { label: 'Home', href: '/' },
          { label: 'Directory', href: '/schools' },
          { label: 'Error' }
        ]} />
        <Alert type="error" title="Institution Profile Not Found">
          {error || 'The requested institution record could not be found.'}
        </Alert>
        <Link to="/schools" className="btn btn--secondary" style={{ marginTop: '1rem', textDecoration: 'none' }}>
          ← Back to Institution Directory
        </Link>
      </div>
    )
  }

  return (
    <div className="school-details-page">
      <Breadcrumbs crumbs={[
        { label: 'Home', href: '/' },
        { label: 'Institutions Directory', href: '/schools' },
        { label: institution.school_name }
      ]} />

      <main className="container" style={{ maxWidth: '1180px', margin: '1.5rem auto 4rem auto', padding: '0 1rem' }}>
        {/* SECTION A: Hero & Basic Institutional Information */}
        <InstitutionHero
          institution={institution}
          activeSection={activeSection}
          onNavigate={handleNavigate}
          onApplyClick={handleApplyClick}
        />

        {/* SECTION B: About the Institution */}
        <InstitutionAbout
          about={institution.about}
          schoolName={institution.school_name}
        />

        {/* SECTION B.1: Live Seat Availability & Quotas */}
        <LiveSeatAvailability
          schoolId={institution.school_id}
          schoolName={institution.school_name}
          category={institution.category}
          schoolType={institution.school_type}
          onApplyClick={handleApplyClick}
        />

        {/* SECTION C: Facilities & Infrastructure (13 Standard Categories) */}
        <InstitutionFacilities
          facilities={institution.facilities}
        />

        {/* SECTION D: Hostel & Residential Accommodation */}
        <InstitutionHostel
          hostel={institution.hostel}
        />

        {/* SECTION E: Transportation & Bus Fleet */}
        <InstitutionTransport
          transport={institution.transport}
        />

        {/* SECTION F: Academic Information & Programmes */}
        <InstitutionAcademics
          programs={programs}
          schoolType={institution.school_type}
          category={institution.category}
          affiliation={institution.affiliation}
          recognition={institution.recognition}
          schoolName={institution.school_name}
        />

        {/* SECTION G: Admissions & Fee Structure */}
        <InstitutionAdmissions
          admissions={institution.admissions}
          schoolName={institution.school_name}
        />

        {/* SECTION H: Verified Institutional Achievements & Accreditations */}
        <InstitutionAchievements
          achievements={achievements}
          schoolName={institution.school_name}
        />

        {/* SECTION I: Academic Divisions & Affiliated Campuses */}
        <InstitutionDivisions
          divisions={divisions}
          schoolName={institution.school_name}
          isParentGroup={institution.is_parent_group}
        />

        {/* SECTION J: Enrolled Students Directory (Positioned Strictly at the Bottom) */}
        <InstitutionStudentDirectory
          schoolId={institution.school_id}
          schoolName={institution.school_name}
          schoolType={institution.school_type}
        />

        {/* Phase 4 Stage 1 Admission Modal */}
        <Stage1AdmissionModal
          institutionId={institution.school_id}
          institutionName={institution.school_name}
          isOpen={isApplyModalOpen}
          onClose={() => setIsApplyModalOpen(false)}
        />
      </main>
    </div>
  )
}
