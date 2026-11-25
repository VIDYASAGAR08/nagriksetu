import { useEffect, useState, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import { apiGet, apiPost, apiPut } from '../../utils/api.js'
import LoadingSpinner from '../../components/ui/LoadingSpinner.jsx'
import Alert from '../../components/ui/Alert.jsx'
import StatusBadge from '../../components/ui/StatusBadge.jsx'
import Breadcrumbs from '../../components/layout/Breadcrumbs.jsx'
import PlatformRequestOversightDesk from '../../components/requests/PlatformRequestOversightDesk.jsx'

export default function AdminDashboard() {
  const { user, token, isAuthenticated } = useAuth()
  const isPlatformAdmin = user?.role === 'platform_admin'

  // Tab State
  const [activeTab, setActiveTab] = useState(() => {
    if (typeof window !== 'undefined') {
      const p = new URLSearchParams(window.location.search)
      const t = p.get('tab')
      if (t === 'admins') return 'institutions'
      if (t === 'schools') return 'institutions'
      if (t === 'staff-monitoring') return 'staff-activity'
      if (t) return t
    }
    return 'overview'
  })

  const [institutionSubTab, setInstitutionSubTab] = useState(() => {
    if (typeof window !== 'undefined' && window.location.search.includes('tab=admins')) {
      return 'admins'
    }
    return 'schools'
  })

  // Polling & Diagnostics State
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [lastRefreshed, setLastRefreshed] = useState(() => new Date().toLocaleTimeString())
  const [health, setHealth] = useState(null)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Section 1: Overview
  const [overview, setOverview] = useState(null)
  const [loadingOverview, setLoadingOverview] = useState(true)

  // Section 2: Institution Management (Schools & Admins)
  const [schools, setSchools] = useState([])
  const [loadingSchools, setLoadingSchools] = useState(false)
  const [admins, setAdmins] = useState([])
  const [applications, setApplications] = useState([])
  const [loadingApplications, setLoadingApplications] = useState(false)
  const [appFilter, setAppFilter] = useState('ALL')
  const [selectedAppModal, setSelectedAppModal] = useState(null)
  const [actionAppModal, setActionAppModal] = useState(null)
  const [actionType, setActionType] = useState('approve') // approve | reject | request_info
  const [actionComments, setActionComments] = useState('')
  const [actionSubmitting, setActionSubmitting] = useState(false)
  const [loadingAdmins, setLoadingAdmins] = useState(false)
  const [showInviteModal, setShowInviteModal] = useState(() => {
    if (typeof window !== 'undefined') return window.location.href.includes('modal=invite')
    return false
  })
  const [inviteFullName, setInviteFullName] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [invitePhone, setInvitePhone] = useState('')
  const [inviteInstitutionId, setInviteInstitutionId] = useState('')
  const [inviteRoleId, setInviteRoleId] = useState('academic_admin')
  const [eligibleInstitutions, setEligibleInstitutions] = useState([])
  const [loadingEligible, setLoadingEligible] = useState(false)
  const [institutionSearchTerm, setInstitutionSearchTerm] = useState('')
  const [submittingInvite, setSubmittingInvite] = useState(false)
  const [inviteResult, setInviteResult] = useState(null)
  const [inviteError, setInviteError] = useState('')

  // Section 3: Admission Monitoring
  const [admissions, setAdmissions] = useState([])
  const [admissionsTotal, setAdmissionsTotal] = useState(0)
  const [loadingAdmissions, setLoadingAdmissions] = useState(false)
  const [admSearch, setAdmSearch] = useState('')
  const [admCategory, setAdmCategory] = useState('all')
  const [admInstitution, setAdmInstitution] = useState('all')
  const [admStatus, setAdmStatus] = useState('all')
  const [admPage, setAdmPage] = useState(0)
  const [selectedHistory, setSelectedHistory] = useState(null)
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [historyModalOpen, setHistoryModalOpen] = useState(false)

  // Section 4: Platform Activity Feed
  const [feedItems, setFeedItems] = useState([])
  const [feedTotal, setFeedTotal] = useState(0)
  const [loadingFeed, setLoadingFeed] = useState(false)
  const [feedCategory, setFeedCategory] = useState('all')
  const [feedInstitutionCategory, setFeedInstitutionCategory] = useState('all')
  const [feedRole, setFeedRole] = useState('all')
  const [feedSearch, setFeedSearch] = useState('')
  const [feedPage, setFeedPage] = useState(0)
  const [selectedFeedItem, setSelectedFeedItem] = useState(null)
  const [feedModalOpen, setFeedModalOpen] = useState(false)

  // Section 5: Audit Logs
  const [auditLogs, setAuditLogs] = useState([])
  const [auditTotal, setAuditTotal] = useState(0)
  const [loadingAudit, setLoadingAudit] = useState(false)
  const [auditCategory, setAuditCategory] = useState('all')
  const [auditSearch, setAuditSearch] = useState('')
  const [auditPage, setAuditPage] = useState(0)

  // Section 6: User and Staff Activity
  const [staffMonitoring, setStaffMonitoring] = useState(null)
  const [loadingStaffMon, setLoadingStaffMon] = useState(false)
  const [staffCategory, setStaffCategory] = useState('all')
  const [staffActivities, setStaffActivities] = useState([])
  const [loadingStaffActs, setLoadingStaffActs] = useState(false)

  // Section 7: Academic Monitoring
  const [academicActivities, setAcademicActivities] = useState([])
  const [academicTotal, setAcademicTotal] = useState(0)
  const [loadingAcademic, setLoadingAcademic] = useState(false)
  const [academicInstFilter, setAcademicInstFilter] = useState('all')

  // Section 8: Reports and Analytics
  const [analytics, setAnalytics] = useState(null)
  const [loadingAnalytics, setLoadingAnalytics] = useState(false)

  // Modal: Seat Capacity Quick Update
  const [showCapacityModal, setShowCapacityModal] = useState(false)
  const [capacitySchoolId, setCapacitySchoolId] = useState('')
  const [capacitySectionId, setCapacitySectionId] = useState('')
  const [newCapacityValue, setNewCapacityValue] = useState(60)
  const [capacityReason, setCapacityReason] = useState('')
  const [updatingCapacity, setUpdatingCapacity] = useState(false)

  // ==========================================
  // DATA LOADERS
  // ==========================================

  const loadHealthAndSchools = useCallback(async () => {
    try {
      const [hRes, sRes] = await Promise.all([
        apiGet('/health').catch(() => ({ status: 'unavailable' })),
        apiGet('/schools?limit=100').catch(() => [])
      ])
      setHealth(hRes)
      setSchools(Array.isArray(sRes) ? sRes : [])
    } catch {
      // ignore
    }
  }, [])

  const loadOverview = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingOverview(true)
      const data = await apiGet('/admin/overview', token)
      setOverview(data)
      setLastRefreshed(new Date().toLocaleTimeString())
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load platform overview.')
    } finally {
      if (!silent) setLoadingOverview(false)
    }
  }, [token, isPlatformAdmin])

  const loadAdmissions = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingAdmissions(true)
      const params = new URLSearchParams({
        limit: '15',
        offset: String(admPage * 15)
      })
      if (admCategory !== 'all') params.append('institution_category', admCategory)
      if (admInstitution !== 'all') params.append('institution_id', admInstitution)
      if (admStatus !== 'all') params.append('status', admStatus)
      if (admSearch.trim()) params.append('search', admSearch.trim())

      const res = await apiGet(`/admin/admissions/applications?${params.toString()}`, token)
      setAdmissions(res.items || [])
      setAdmissionsTotal(res.total || 0)
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load admissions monitoring data.')
    } finally {
      if (!silent) setLoadingAdmissions(false)
    }
  }, [token, isPlatformAdmin, admCategory, admInstitution, admStatus, admSearch, admPage])

  const loadFeed = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingFeed(true)
      const params = new URLSearchParams({
        limit: '20',
        offset: String(feedPage * 20)
      })
      if (feedCategory !== 'all') params.append('category', feedCategory)
      if (feedInstitutionCategory !== 'all') params.append('institution_category', feedInstitutionCategory)
      if (feedRole !== 'all') params.append('actor_role', feedRole)
      if (feedSearch.trim()) params.append('search', feedSearch.trim())

      const res = await apiGet(`/admin/activity-feed?${params.toString()}`, token)
      setFeedItems(res.items || [])
      setFeedTotal(res.total || 0)
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load activity feed.')
    } finally {
      if (!silent) setLoadingFeed(false)
    }
  }, [token, isPlatformAdmin, feedCategory, feedInstitutionCategory, feedRole, feedSearch, feedPage])

  const loadAudit = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingAudit(true)
      const params = new URLSearchParams({
        limit: '25',
        offset: String(auditPage * 25)
      })
      if (auditCategory !== 'all') params.append('category', auditCategory)
      if (auditSearch.trim()) params.append('search', auditSearch.trim())

      const res = await apiGet(`/admin/audit-logs?${params.toString()}`, token)
      setAuditLogs(res.items || [])
      setAuditTotal(res.total || 0)
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load audit logs.')
    } finally {
      if (!silent) setLoadingAudit(false)
    }
  }, [token, isPlatformAdmin, auditCategory, auditSearch, auditPage])

  const loadStaffMonitoring = useCallback(async () => {
    if (!token || !isPlatformAdmin) return
    try {
      setLoadingStaffMon(true)
      const data = await apiGet('/admin/staff-monitoring', token)
      setStaffMonitoring(data)
    } catch (err) {
      setError(err.message || 'Failed to fetch staff monitoring data.')
    } finally {
      setLoadingStaffMon(false)
    }
  }, [token, isPlatformAdmin])

  const loadStaffActivities = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingStaffActs(true)
      const res = await apiGet('/admin/staff/activities?limit=30', token)
      setStaffActivities(res.items || [])
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load staff activities.')
    } finally {
      if (!silent) setLoadingStaffActs(false)
    }
  }, [token, isPlatformAdmin])

  const loadAcademic = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingAcademic(true)
      const params = new URLSearchParams({ limit: '30' })
      if (academicInstFilter !== 'all') params.append('institution_id', academicInstFilter)
      const res = await apiGet(`/admin/academic/activities?${params.toString()}`, token)
      setAcademicActivities(res.items || [])
      setAcademicTotal(res.total || 0)
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load academic monitoring.')
    } finally {
      if (!silent) setLoadingAcademic(false)
    }
  }, [token, isPlatformAdmin, academicInstFilter])

  const loadAnalytics = useCallback(async (silent = false) => {
    if (!token || !isPlatformAdmin) return
    try {
      if (!silent) setLoadingAnalytics(true)
      const data = await apiGet('/admin/reports/analytics', token)
      setAnalytics(data)
    } catch (err) {
      if (!silent) setError(err.message || 'Failed to load reports and analytics.')
    } finally {
      if (!silent) setLoadingAnalytics(false)
    }
  }, [token, isPlatformAdmin])

  const loadApplications = useCallback(async () => {
    if (!token || !isPlatformAdmin) return
    try {
      setLoadingApplications(true)
      const data = await apiGet('/admin/institution-applications', token)
      setApplications(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to fetch institution applications.')
    } finally {
      setLoadingApplications(false)
    }
  }, [token, isPlatformAdmin])

  const handleApproveApplication = async (appId, comments) => {
    setActionSubmitting(true)
    try {
      const res = await apiPost(`/admin/institution-applications/${appId}/approve`, { comments: comments || null }, token)
      setSuccess(`Application for ${res.institution_name || 'institution'} approved successfully! Administrative node and administrator account activated.`)
      setActionAppModal(null)
      loadApplications()
      loadHealthAndSchools()
    } catch (err) {
      setError(err.message || 'Failed to approve application.')
    } finally {
      setActionSubmitting(false)
    }
  }

  const handleRejectApplication = async (appId, comments) => {
    if (!comments || !comments.trim()) {
      alert('Please provide a reason for rejecting the application.')
      return
    }
    setActionSubmitting(true)
    try {
      const res = await apiPost(`/admin/institution-applications/${appId}/reject`, { comments: comments.trim() }, token)
      setSuccess(`Application ${res.application_ref} has been marked as rejected.`)
      setActionAppModal(null)
      loadApplications()
    } catch (err) {
      setError(err.message || 'Failed to reject application.')
    } finally {
      setActionSubmitting(false)
    }
  }

  const handleRequestInfoApplication = async (appId, comments) => {
    if (!comments || !comments.trim()) {
      alert('Please specify what additional information or documents are required.')
      return
    }
    setActionSubmitting(true)
    try {
      const res = await apiPost(`/admin/institution-applications/${appId}/request-info`, { comments: comments.trim() }, token)
      setSuccess(`Additional information requested for application ${res.application_ref}.`)
      setActionAppModal(null)
      loadApplications()
    } catch (err) {
      setError(err.message || 'Failed to request additional information.')
    } finally {
      setActionSubmitting(false)
    }
  }

  const loadAdmins = useCallback(async () => {
    if (!token || !isPlatformAdmin) return
    try {
      setLoadingAdmins(true)
      const data = await apiGet('/admin/institution-admins', token)
      setAdmins(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to fetch administrator accounts.')
    } finally {
      setLoadingAdmins(false)
    }
  }, [token, isPlatformAdmin])

  const loadEligibleInstitutions = useCallback(async () => {
    if (!token || !isPlatformAdmin) return
    try {
      setLoadingEligible(true)
      const res = await apiGet('/admin/institution-admins/eligible-institutions', token)
      const list = Array.isArray(res) ? res : (res?.institutions || [])
      setEligibleInstitutions(list)
    } catch (err) {
      setInviteError(err.message || 'Failed to load eligible unassigned institutions.')
    } finally {
      setLoadingEligible(false)
    }
  }, [token, isPlatformAdmin])

  // Initial mount
  useEffect(() => {
    loadHealthAndSchools()
    loadOverview()
  }, [loadHealthAndSchools, loadOverview])

  // Tab switch trigger
  useEffect(() => {
    if (activeTab === 'overview') loadOverview()
    if (activeTab === 'admissions') loadAdmissions()
    if (activeTab === 'activity-feed') loadFeed()
    if (activeTab === 'audit-logs') loadAudit()
    if (activeTab === 'staff-activity') {
      loadStaffMonitoring()
      loadStaffActivities()
    }
    if (activeTab === 'academic-monitoring') loadAcademic()
    if (activeTab === 'reports-analytics') loadAnalytics()
    if (activeTab === 'institutions') {
      if (institutionSubTab === 'admins' || institutionSubTab === 'applications') { loadAdmins(); loadApplications(); }
      else loadHealthAndSchools()
    }
  }, [
    activeTab, institutionSubTab, loadOverview, loadAdmissions,
    loadFeed, loadAudit, loadStaffMonitoring, loadStaffActivities,
    loadAcademic, loadAnalytics, loadAdmins, loadHealthAndSchools
  ])

  // Polling loop
  useEffect(() => {
    if (!autoRefresh || !token || !isPlatformAdmin) return
    const interval = setInterval(() => {
      setLastRefreshed(new Date().toLocaleTimeString())
      if (activeTab === 'overview') loadOverview(true)
      else if (activeTab === 'admissions') loadAdmissions(true)
      else if (activeTab === 'activity-feed') loadFeed(true)
      else if (activeTab === 'audit-logs') loadAudit(true)
      else if (activeTab === 'staff-activity') loadStaffActivities(true)
      else if (activeTab === 'academic-monitoring') loadAcademic(true)
    }, 15000)
    return () => clearInterval(interval)
  }, [
    autoRefresh, activeTab, token, isPlatformAdmin,
    loadOverview, loadAdmissions, loadFeed, loadAudit,
    loadStaffActivities, loadAcademic
  ])

  // Manual Refresh
  const handleManualRefresh = async () => {
    setRefreshing(true)
    setError('')
    try {
      if (activeTab === 'overview') await loadOverview()
      else if (activeTab === 'admissions') await loadAdmissions()
      else if (activeTab === 'activity-feed') await loadFeed()
      else if (activeTab === 'audit-logs') await loadAudit()
      else if (activeTab === 'staff-activity') {
        await Promise.all([loadStaffMonitoring(), loadStaffActivities()])
      }
      else if (activeTab === 'academic-monitoring') await loadAcademic()
      else if (activeTab === 'reports-analytics') await loadAnalytics()
      else if (activeTab === 'institutions') {
        if (institutionSubTab === 'admins') await loadAdmins()
        else await loadHealthAndSchools()
      }
      setLastRefreshed(new Date().toLocaleTimeString())
    } finally {
      setRefreshing(false)
    }
  }

  // ==========================================
  // ACTION HANDLERS
  // ==========================================

  const handleOpenHistory = async (appId) => {
    try {
      setLoadingHistory(true)
      setHistoryModalOpen(true)
      const data = await apiGet(`/admin/admissions/applications/${appId}/history`, token)
      setSelectedHistory(data)
    } catch (err) {
      setError(err.message || 'Failed to load chronological admission history.')
      setHistoryModalOpen(false)
    } finally {
      setLoadingHistory(false)
    }
  }

  const handleOpenInviteModal = () => {
    setInviteFullName('')
    setInviteEmail('')
    setInvitePhone('')
    setInviteInstitutionId('')
    setInviteRoleId('academic_admin')
    setInstitutionSearchTerm('')
    setInviteError('')
    setInviteResult(null)
    loadEligibleInstitutions()
    setShowInviteModal(true)
  }

  const handleInviteSubmit = async (e) => {
    e.preventDefault()
    setInviteError('')
    setInviteResult(null)
    setSubmittingInvite(true)
    try {
      const payload = {
        full_name: inviteFullName.trim(),
        email: inviteEmail.trim(),
        phone: invitePhone.trim() || null,
        institution_id: inviteInstitutionId.trim(),
        role_id: 'academic_admin'
      }
      const res = await apiPost('/admin/institution-admins/invite', payload, token)
      setInviteResult(res)
      setSuccess(`Academic Administrator invitation successfully issued for ${res.school_name || inviteInstitutionId}.`)
      setEligibleInstitutions(prev => prev.filter(x => x.school_id !== inviteInstitutionId.trim()))
      loadAdmins()
      loadEligibleInstitutions()
    } catch (err) {
      setInviteError(err.message || 'Failed to dispatch administrator invitation.')
    } finally {
      setSubmittingInvite(false)
    }
  }

  const handleRevokeInvitation = async (adm) => {
    if (!window.confirm(`Revoke pending invitation for ${adm.full_name} (${adm.email})? Target institution will be released immediately.`)) return
    try {
      await apiPost(`/admin/institution-admins/${adm.user_id}/revoke-invitation`, {}, token)
      setSuccess(`Invitation revoked for ${adm.full_name}. Institution released for reassignment.`)
      loadAdmins()
      loadEligibleInstitutions()
    } catch (err) {
      setError(err.message || 'Failed to revoke invitation.')
    }
  }

  const handleSuspendAdmin = async (adm) => {
    if (!window.confirm(`Suspend administrator account for ${adm.full_name} (${adm.email})?`)) return
    try {
      await apiPost(`/admin/institution-admins/${adm.user_id}/suspend`, {}, token)
      setSuccess(`Account for ${adm.full_name} suspended.`)
      loadAdmins()
    } catch (err) {
      setError(err.message || 'Failed to suspend account.')
    }
  }

  const handleReactivateAdmin = async (adm) => {
    try {
      await apiPost(`/admin/institution-admins/${adm.user_id}/reactivate`, {}, token)
      setSuccess(`Account for ${adm.full_name} reactivated.`)
      loadAdmins()
    } catch (err) {
      setError(err.message || 'Failed to reactivate account.')
    }
  }

  const handleResetAllAssignments = async () => {
    if (!window.confirm("RESET ALL ACADEMIC ADMINISTRATOR ASSIGNMENTS?\n\nThis will:\n1. Revoke all pending Academic Administrator invitations.\n2. Release all institution slots.\n3. Safely deactivate administrator access while preserving historical user records and audit trails.\n4. Make all 30 institutions available again for individual invitation.\n\nProceed?")) return
    try {
      const res = await apiPost('/admin/institution-admins/reset-assignments', {}, token)
      setSuccess(`Reset completed: All ${res.total_available_institutions || 30} institutions are now available for reassignment.`)
      loadAdmins()
      loadEligibleInstitutions()
    } catch (err) {
      setError(err.message || 'Failed to execute assignment reset.')
    }
  }

  const handleUpdateCapacity = async (e) => {
    e.preventDefault()
    if (!capacitySchoolId || !capacitySectionId) return
    setUpdatingCapacity(true)
    try {
      const res = await apiPut(`/schools/${capacitySchoolId}/capacity`, {
        section_id: capacitySectionId,
        new_capacity: parseInt(newCapacityValue, 10),
        reason: capacityReason.trim() || 'Central administrative capacity adjustment'
      }, token)
      setSuccess(`Seat capacity for section ${capacitySectionId} updated to ${res.new_capacity}.`)
      setShowCapacityModal(false)
      loadOverview(true)
    } catch (err) {
      setError(err.message || 'Failed to update seat capacity.')
    } finally {
      setUpdatingCapacity(false)
    }
  }

  // Filtered institutions in invite modal
  const filteredEligible = eligibleInstitutions.filter((item) => {
    if (!institutionSearchTerm.trim()) return true
    const q = institutionSearchTerm.toLowerCase()
    return (
      item.school_name.toLowerCase().includes(q) ||
      item.school_id.toLowerCase().includes(q) ||
      (item.district && item.district.toLowerCase().includes(q))
    )
  })

  return (
    <div className="layout-container" style={{ maxWidth: '1440px', margin: '0 auto', padding: '1.5rem 1rem' }}>
      <Breadcrumbs items={[{ label: 'Home', to: '/' }, { label: 'Platform Administration' }]} />

      {/* HEADER BAR */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '1rem',
        marginBottom: '1.5rem',
        paddingBottom: '1rem',
        borderBottom: '2px solid #e2e8f0'
      }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f172a', margin: 0, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span>🏛️</span> NagrikSetu Central Governance & Monitoring
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem', margin: '0.25rem 0 0 0' }}>
            Karnataka State Unified Education Infrastructure — 30 Institutions Across All 4 Tiers
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
          {/* Live Polling Pill */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.4rem',
            background: autoRefresh ? '#ecfdf5' : '#f1f5f9',
            border: `1px solid ${autoRefresh ? '#a7f3d0' : '#cbd5e1'}`,
            borderRadius: '9999px',
            padding: '0.3rem 0.75rem',
            fontSize: '0.8rem',
            color: autoRefresh ? '#065f46' : '#475569'
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: autoRefresh ? '#10b981' : '#94a3b8',
              display: 'inline-block'
            }} />
            <span>{autoRefresh ? 'Live Polling (15s)' : 'Polling Paused'}</span>
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              style={{
                background: 'transparent',
                border: 'none',
                color: '#2563eb',
                cursor: 'pointer',
                fontSize: '0.75rem',
                textDecoration: 'underline',
                padding: '0 0.2rem'
              }}
            >
              {autoRefresh ? 'Pause' : 'Resume'}
            </button>
          </div>

          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
            Updated: <strong>{lastRefreshed}</strong>
          </span>

          <button
            onClick={handleManualRefresh}
            disabled={refreshing}
            className="btn btn--secondary btn--sm"
            style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 600 }}
          >
            <span>🔄</span> {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
      </div>

      {error && <Alert type="error" title="Diagnostics Notice" className="mb-4" onClose={() => setError('')}>{error}</Alert>}
      {success && <Alert type="success" title="Success" className="mb-4" onClose={() => setSuccess('')}>{success}</Alert>}

      {/* 8-TAB NAVIGATION BAR */}
      <nav aria-label="Platform Admin Sections" style={{
        display: 'flex',
        gap: '0.35rem',
        overflowX: 'auto',
        paddingBottom: '0.5rem',
        marginBottom: '1.5rem',
        borderBottom: '1px solid #cbd5e1'
      }}>
        {[
          { id: 'overview', label: 'Platform Overview', icon: '📊' },
          { id: 'institutions', label: 'Institution Management', icon: '🏫' },
          { id: 'admissions', label: 'Admission Monitoring', icon: '📝' },
          { id: 'activity-feed', label: 'Platform Activity Feed', icon: '⚡' },
          { id: 'audit-logs', label: 'Audit Logs', icon: '🛡️' },
          { id: 'staff-activity', label: 'User & Staff Activity', icon: '👥' },
          { id: 'academic-monitoring', label: 'Academic Monitoring', icon: '🎓' },
          { id: 'reports-analytics', label: 'Reports & Analytics', icon: '📈' },
          { id: 'requests', label: 'Platform Request Oversight', icon: '⚖️' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.4rem',
              padding: '0.55rem 0.9rem',
              borderRadius: '6px',
              border: activeTab === tab.id ? '2px solid #1e3a8a' : '1px solid transparent',
              background: activeTab === tab.id ? '#1e3a8a' : '#f8fafc',
              color: activeTab === tab.id ? '#ffffff' : '#334155',
              fontWeight: activeTab === tab.id ? 700 : 500,
              fontSize: '0.875rem',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              transition: 'all 0.15s ease-in-out'
            }}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>

      {/* ======================================================== */}
      {/* SECTION 1: PLATFORM OVERVIEW */}
      {/* ======================================================== */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {loadingOverview && !overview ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
          ) : (
            <>
              {/* PRIMARY METRICS GRID */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '1rem'
              }}>
                <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #2563eb', background: '#ffffff' }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Total Institutions</div>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: '0.25rem 0' }}>{overview?.total_institutions || schools.length}</div>
                  <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                    <span className="badge" style={{ background: '#e0e7ff', color: '#3730a3', fontSize: '0.7rem' }}>Schools: {overview?.institutions_by_category?.k10_school || 15}</span>
                    <span className="badge" style={{ background: '#fef3c7', color: '#92400e', fontSize: '0.7rem' }}>PU: {overview?.institutions_by_category?.pu_college || 5}</span>
                    <span className="badge" style={{ background: '#dcfce7', color: '#166534', fontSize: '0.7rem' }}>Degree: {overview?.institutions_by_category?.degree_college || 5}</span>
                    <span className="badge" style={{ background: '#f3e8ff', color: '#6b21a8', fontSize: '0.7rem' }}>Univ: {overview?.institutions_by_category?.university || 5}</span>
                  </div>
                </div>

                <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #10b981', background: '#ffffff' }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Registered Students</div>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: '0.25rem 0' }}>{(overview?.total_students || 30001).toLocaleString()}</div>
                  <div style={{ fontSize: '0.8rem', color: '#10b981' }}>Standardized Student ID Verified</div>
                </div>

                <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #f59e0b', background: '#ffffff' }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Registered Parents</div>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: '0.25rem 0' }}>{overview?.total_parents || 0}</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Authenticated Citizens & Guardians</div>
                </div>

                <div className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #8b5cf6', background: '#ffffff' }}>
                  <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600, textTransform: 'uppercase' }}>Staff & Administrators</div>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', margin: '0.25rem 0' }}>{overview?.total_staff_and_admins || 0}</div>
                  <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Institutional Role Mappings</div>
                </div>
              </div>

              {/* ADMISSION FUNNEL BREAKDOWN */}
              <div className="card" style={{ padding: '1.25rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#0f172a', fontWeight: 700 }}>
                      Statewide Admission Applications Funnel
                    </h3>
                    <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                      Database-backed metrics across all 30 institutions
                    </p>
                  </div>
                  <button
                    onClick={() => setActiveTab('admissions')}
                    className="btn btn--sm btn--primary"
                    style={{ fontSize: '0.8rem' }}
                  >
                    Open Admission Monitor →
                  </button>
                </div>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
                  gap: '0.75rem'
                }}>
                  <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>TOTAL SUBMISSIONS</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a' }}>{overview?.total_admission_applications || 0}</div>
                  </div>
                  <div style={{ background: '#eff6ff', padding: '1rem', borderRadius: '8px', border: '1px solid #bfdbfe', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#1e40af', fontWeight: 600 }}>AWAITING REVIEW</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#1e40af' }}>{overview?.applications_awaiting_review || 0}</div>
                  </div>
                  <div style={{ background: '#fefce8', padding: '1rem', borderRadius: '8px', border: '1px solid #fef08a', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#854d0e', fontWeight: 600 }}>STAGE 1 APPROVED</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#854d0e' }}>{overview?.applications_stage1_approved || 0}</div>
                  </div>
                  <div style={{ background: '#f0fdf4', padding: '1rem', borderRadius: '8px', border: '1px solid #bbf7d0', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#166534', fontWeight: 600 }}>STAGE 2 SUBMITTED</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#166534' }}>{overview?.applications_stage2_submitted || 0}</div>
                  </div>
                  <div style={{ background: '#ecfdf5', padding: '1rem', borderRadius: '8px', border: '1px solid #6ee7b7', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#047857', fontWeight: 600 }}>FINAL ACCEPTED</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#047857' }}>{overview?.applications_final_accepted || 0}</div>
                  </div>
                  <div style={{ background: '#fef2f2', padding: '1rem', borderRadius: '8px', border: '1px solid #fecaca', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#b91c1c', fontWeight: 600 }}>FINAL REJECTED</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#b91c1c' }}>{overview?.applications_final_rejected || 0}</div>
                  </div>
                  <div style={{ background: '#fffbeb', padding: '1rem', borderRadius: '8px', border: '1px solid #fde68a', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.75rem', color: '#b45309', fontWeight: 600 }}>ACTION REQUIRED</div>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#b45309' }}>{overview?.applications_awaiting_clarification || 0}</div>
                  </div>
                </div>
              </div>

              {/* RECENT UPDATES TWO-COLUMN ROW */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(450px, 1fr))', gap: '1.25rem' }}>
                {/* Recent Institution Updates */}
                <div className="card" style={{ padding: '1.25rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h4 style={{ margin: 0, fontSize: '1rem', color: '#0f172a', fontWeight: 700 }}>
                      🏛️ Recent Institution Updates
                    </h4>
                    <button
                      onClick={() => { setCapacitySchoolId('SCH011'); setCapacitySectionId('SEC-SCH011-PCMB-11-A'); setShowCapacityModal(true); }}
                      className="btn btn--sm btn--ghost"
                      style={{ fontSize: '0.75rem', color: '#2563eb' }}
                    >
                      + Adjust Capacity
                    </button>
                  </div>
                  {overview?.recent_institution_updates && overview.recent_institution_updates.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                      {overview.recent_institution_updates.map((item) => (
                        <div key={item.id} style={{ padding: '0.6rem 0.75rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b', fontSize: '0.75rem' }}>
                            <strong style={{ color: '#1e3a8a' }}>{item.school_name || item.institution_id || 'System'}</strong>
                            <span>{new Date(item.created_at).toLocaleString()}</span>
                          </div>
                          <div style={{ fontWeight: 600, color: '#1e293b', marginTop: '0.2rem' }}>{item.action}</div>
                          {item.remarks && <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '0.1rem' }}>Note: {item.remarks}</div>}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontStyle: 'italic', padding: '1rem 0' }}>No recent institution updates recorded yet.</div>
                  )}
                </div>

                {/* Recent Platform Activities */}
                <div className="card" style={{ padding: '1.25rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h4 style={{ margin: 0, fontSize: '1rem', color: '#0f172a', fontWeight: 700 }}>
                      ⚡ Live Platform Activity
                    </h4>
                    <button
                      onClick={() => setActiveTab('activity-feed')}
                      className="btn btn--sm btn--ghost"
                      style={{ fontSize: '0.75rem', color: '#2563eb' }}
                    >
                      View All →
                    </button>
                  </div>
                  {overview?.recent_activities && overview.recent_activities.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                      {overview.recent_activities.slice(0, 5).map((act) => (
                        <div key={act.id} style={{ padding: '0.6rem 0.75rem', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b', fontSize: '0.75rem' }}>
                            <span><strong>{act.actor_name || 'System'}</strong> ({act.actor_role})</span>
                            <span>{new Date(act.created_at).toLocaleTimeString()}</span>
                          </div>
                          <div style={{ color: '#1e293b', marginTop: '0.2rem' }}>{act.action}</div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ color: '#94a3b8', fontSize: '0.85rem', fontStyle: 'italic', padding: '1rem 0' }}>No activities recorded yet.</div>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 2: INSTITUTION MANAGEMENT */}
      {/* ======================================================== */}
      {activeTab === 'institutions' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Sub Navigation */}
          <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem' }}>
            <button
              onClick={() => setInstitutionSubTab('schools')}
              className={`btn btn--sm ${institutionSubTab === 'schools' ? 'btn--primary' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              Institutional Nodes & Profiles ({schools.length})
            </button>
            <button
              onClick={() => { setInstitutionSubTab('applications'); loadApplications(); }}
              className={`btn btn--sm ${institutionSubTab === 'applications' || institutionSubTab === 'admins' ? 'btn--primary' : 'btn--ghost'}`}
              style={{ fontWeight: 600 }}
            >
              Institution Registration Applications ({applications.length})
            </button>
          </div>

          {/* SUB-TAB A: INSTITUTION PROFILES */}
          {institutionSubTab === 'schools' && (
            <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
              <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1a3a6b' }}>Registered Institutional Nodes ({schools.length})</h3>
                <span className="badge badge--neutral" style={{ fontSize: '0.8rem' }}>Preserved Across 4 Tiers</span>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Tier & Category</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Institution Code</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Institution Name</th>
                      <th style={{ padding: '0.75rem 1rem' }}>District</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Affiliation / Type</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {schools.map((s) => (
                      <tr key={s.school_id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <span className={`badge ${
                            s.category === 'k10_school' ? 'badge--info' :
                            s.category === 'pu_college' ? 'badge--warning' :
                            s.category === 'degree_college' ? 'badge--success' : 'badge--primary'
                          }`} style={{ fontSize: '0.75rem' }}>
                            {s.category === 'k10_school' ? 'Schools' :
                             s.category === 'pu_college' ? 'PU Colleges' :
                             s.category === 'degree_college' ? 'Degree Colleges' : 'Universities'}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700 }}>{s.school_id}</td>
                        <td style={{ padding: '0.75rem 1rem', fontWeight: 600 }}>{s.school_name}</td>
                        <td style={{ padding: '0.75rem 1rem', color: '#64748b' }}>{s.district}</td>
                        <td style={{ padding: '0.75rem 1rem', color: '#64748b' }}>{s.affiliation || s.school_type}</td>
                        <td style={{ padding: '0.75rem 1rem' }}>
                          <button
                            onClick={() => {
                              setCapacitySchoolId(s.school_id)
                              setCapacitySectionId(`SEC-${s.school_id}-A`)
                              setShowCapacityModal(true)
                            }}
                            className="btn btn--xs btn--ghost"
                            style={{ color: '#2563eb', fontWeight: 600 }}
                          >
                            Set Capacity
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* SUB-TAB B: INSTITUTION REGISTRATION APPLICATIONS */}
          {(institutionSubTab === 'applications' || institutionSubTab === 'admins') && (() => {
            const pendingApps = applications.filter(a => a.status === 'pending')
            const approvedApps = applications.filter(a => a.status === 'approved')
            const rejectedApps = applications.filter(a => a.status === 'rejected')
            const infoReqApps = applications.filter(a => a.status === 'additional_info_required')

            const filteredApps = applications.filter(a => {
              if (appFilter === 'ALL') return true
              if (appFilter === 'pending') return a.status === 'pending'
              if (appFilter === 'approved') return a.status === 'approved'
              if (appFilter === 'rejected') return a.status === 'rejected'
              if (appFilter === 'additional_info_required') return a.status === 'additional_info_required'
              return true
            })

            return (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                {/* Header & Stats Banner */}
                <div className="card" style={{ padding: '1.25rem 1.5rem', background: '#ffffff', border: '1px solid #d0d5dd', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#1a3a6b', fontWeight: 700 }}>
                        Institution Registration Applications
                      </h3>
                      <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                        Review, verify, and approve onboarding applications submitted by Schools, PU Colleges, Degree Colleges, and Universities.
                      </p>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span className="badge" style={{ background: '#f8fafc', color: '#334155', border: '1px solid #cbd5e1', fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                        Total: <strong>{applications.length}</strong>
                      </span>
                      <span className="badge" style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a', fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                        Pending Review: <strong>{pendingApps.length}</strong>
                      </span>
                      <span className="badge" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                        Approved: <strong>{approvedApps.length}</strong>
                      </span>
                      {infoReqApps.length > 0 && (
                        <span className="badge" style={{ background: '#f9f5ff', color: '#6941c6', border: '1px solid #e9d7fe', fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                          Action Req: <strong>{infoReqApps.length}</strong>
                        </span>
                      )}
                      {rejectedApps.length > 0 && (
                        <span className="badge" style={{ background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', fontSize: '0.8rem', padding: '0.35rem 0.65rem' }}>
                          Rejected: <strong>{rejectedApps.length}</strong>
                        </span>
                      )}
                      <button
                        onClick={loadApplications}
                        disabled={loadingApplications}
                        className="btn btn--sm btn--outline"
                        style={{ marginLeft: '0.5rem' }}
                      >
                        {loadingApplications ? 'Refreshing...' : '↻ Refresh'}
                      </button>
                    </div>
                  </div>

                  {/* Filter Pills */}
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                    {[
                      { id: 'ALL', label: 'All Applications', count: applications.length },
                      { id: 'pending', label: 'Pending Review', count: pendingApps.length },
                      { id: 'approved', label: 'Approved', count: approvedApps.length },
                      { id: 'additional_info_required', label: 'Action Required', count: infoReqApps.length },
                      { id: 'rejected', label: 'Rejected', count: rejectedApps.length }
                    ].map(tab => (
                      <button
                        key={tab.id}
                        onClick={() => setAppFilter(tab.id)}
                        className={`btn btn--xs ${appFilter === tab.id ? 'btn--primary' : 'btn--ghost'}`}
                        style={{ borderRadius: '20px', padding: '0.25rem 0.65rem', fontWeight: 600 }}
                      >
                        {tab.label} ({tab.count})
                      </button>
                    ))}
                  </div>
                </div>

                {/* Applications Table Card */}
                <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
                  <div style={{ overflowX: 'auto' }}>
                    <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                          <th style={{ padding: '0.75rem 1rem' }}>Application Ref</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Institution ID</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Institution Name</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Type & Tier</th>
                          <th style={{ padding: '0.75rem 1rem' }}>District</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Applicant / Admin</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Submission Date</th>
                          <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                          <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {filteredApps.length === 0 ? (
                          <tr>
                            <td colSpan={9} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                              {loadingApplications ? 'Loading applications from database...' : 'No institution applications found matching current filter.'}
                            </td>
                          </tr>
                        ) : (
                          filteredApps.map((app) => (
                            <tr key={app.application_id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                              <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#155eef' }}>
                                {app.application_ref}
                              </td>
                              <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700 }}>
                                {app.institution_id}
                              </td>
                              <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#0f172a' }}>
                                {app.institution_name}
                              </td>
                              <td style={{ padding: '0.75rem 1rem' }}>
                                <span className={`badge ${
                                  app.institution_category?.includes('School') ? 'badge--info' :
                                  app.institution_category?.includes('PU') ? 'badge--warning' :
                                  app.institution_category?.includes('Degree') ? 'badge--success' : 'badge--primary'
                                }`} style={{ fontSize: '0.75rem' }}>
                                  {app.institution_type || app.institution_category}
                                </span>
                              </td>
                              <td style={{ padding: '0.75rem 1rem', color: '#64748b' }}>
                                {app.district}
                              </td>
                              <td style={{ padding: '0.75rem 1rem' }}>
                                <div style={{ fontWeight: 600 }}>{app.applicant_name}</div>
                                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{app.applicant_email}</div>
                              </td>
                              <td style={{ padding: '0.75rem 1rem', color: '#64748b', whiteSpace: 'nowrap' }}>
                                {app.created_at ? new Date(app.created_at).toLocaleDateString() : 'N/A'}
                              </td>
                              <td style={{ padding: '0.75rem 1rem' }}>
                                {app.status === 'pending' && (
                                  <span className="badge" style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a', fontWeight: 700 }}>
                                    Pending Review
                                  </span>
                                )}
                                {app.status === 'approved' && (
                                  <span className="badge" style={{ background: '#f0fdf4', color: '#166534', border: '1px solid #bbf7d0', fontWeight: 700 }}>
                                    Approved
                                  </span>
                                )}
                                {app.status === 'rejected' && (
                                  <span className="badge" style={{ background: '#fef2f2', color: '#991b1b', border: '1px solid #fecaca', fontWeight: 700 }}>
                                    Rejected
                                  </span>
                                )}
                                {app.status === 'additional_info_required' && (
                                  <span className="badge" style={{ background: '#f9f5ff', color: '#6941c6', border: '1px solid #e9d7fe', fontWeight: 700 }}>
                                    Action Required
                                  </span>
                                )}
                              </td>
                              <td style={{ padding: '0.75rem 1rem', textAlign: 'right', whiteSpace: 'nowrap' }}>
                                <div style={{ display: 'inline-flex', gap: '0.4rem' }}>
                                  <button
                                    onClick={() => setSelectedAppModal(app)}
                                    className="btn btn--xs btn--outline"
                                    title="View complete application details"
                                  >
                                    View Details
                                  </button>
                                  {app.status !== 'approved' && (
                                    <>
                                      <button
                                        onClick={() => {
                                          setActionAppModal(app)
                                          setActionType('approve')
                                          setActionComments('')
                                        }}
                                        className="btn btn--xs btn--primary"
                                        style={{ background: '#16a34a', borderColor: '#16a34a' }}
                                        title="Approve and activate institution"
                                      >
                                        Approve
                                      </button>
                                      <button
                                        onClick={() => {
                                          setActionAppModal(app)
                                          setActionType('request_info')
                                          setActionComments('')
                                        }}
                                        className="btn btn--xs btn--outline"
                                        style={{ color: '#d97706', borderColor: '#fcd34d' }}
                                        title="Request additional information from applicant"
                                      >
                                        Request Info
                                      </button>
                                      <button
                                        onClick={() => {
                                          setActionAppModal(app)
                                          setActionType('reject')
                                          setActionComments('')
                                        }}
                                        className="btn btn--xs btn--outline"
                                        style={{ color: '#dc2626', borderColor: '#fca5a5' }}
                                        title="Reject this application"
                                      >
                                        Reject
                                      </button>
                                    </>
                                  )}
                                </div>
                              </td>
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )
          })()}
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 3: ADMISSION MONITORING */}
      {/* ======================================================== */}
      {activeTab === 'admissions' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Filters Bar */}
          <div className="card" style={{ padding: '1rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>SEARCH</label>
                <input
                  type="text"
                  placeholder="App ID, Applicant, Parent..."
                  value={admSearch}
                  onChange={(e) => setAdmSearch(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>TIER / CATEGORY</label>
                <select
                  value={admCategory}
                  onChange={(e) => { setAdmCategory(e.target.value); setAdmPage(0); }}
                  className="select select--sm"
                  style={{ width: '100%' }}
                >
                  <option value="all">All Tiers (Schools, PU, Degree, Univ)</option>
                  <option value="k10_school">Schools</option>
                  <option value="pu_college">PU Colleges</option>
                  <option value="degree_college">Degree Colleges</option>
                  <option value="university">Universities</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>STATUS</label>
                <select
                  value={admStatus}
                  onChange={(e) => { setAdmStatus(e.target.value); setAdmPage(0); }}
                  className="select select--sm"
                  style={{ width: '100%' }}
                >
                  <option value="all">All Statuses</option>
                  <option value="submitted">Submitted (Stage 1)</option>
                  <option value="under_review">Under Review</option>
                  <option value="approved">Stage 1 Approved</option>
                  <option value="action_required">Action Required (Clarification)</option>
                  <option value="stage2_submitted">Stage 2 Submitted</option>
                  <option value="admitted">Admitted / Enrolled</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem' }}>
                <button
                  onClick={() => loadAdmissions()}
                  className="btn btn--sm btn--primary"
                  style={{ flex: 1, fontWeight: 600 }}
                >
                  Apply Filters
                </button>
                <button
                  onClick={() => { setAdmSearch(''); setAdmCategory('all'); setAdmStatus('all'); setAdmPage(0); }}
                  className="btn btn--sm btn--ghost"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Admissions Table */}
          <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', color: '#1a3a6b', fontWeight: 700 }}>
                Statewide Admission Applications ({admissionsTotal})
              </h3>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Showing page {admPage + 1} of {Math.max(1, Math.ceil(admissionsTotal / 15))}
              </span>
            </div>

            {loadingAdmissions ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Application ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Applicant Name</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Parent / Guardian</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Target Institution</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Programme & Year</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Current Stage & Status</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Audit History</th>
                    </tr>
                  </thead>
                  <tbody>
                    {admissions.length === 0 ? (
                      <tr><td colSpan={7} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>No admission applications match the specified criteria.</td></tr>
                    ) : (
                      admissions.map((a) => (
                        <tr key={a.application_id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontWeight: 700, color: '#1e3a8a' }}>
                            {a.application_id}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600, color: '#0f172a' }}>{a.applicant_name}</div>
                            {a.enrolled_student_id && (
                              <div style={{ fontSize: '0.75rem', color: '#15803d', fontFamily: 'monospace' }}>
                                Enrolled: {a.enrolled_student_id}
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div>{a.parent_name || 'Registered Parent'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{a.parent_phone || a.parent_email}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600 }}>{a.institution_name}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{a.institution_id} • {a.district}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div>{a.program_name || a.education_level}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>AY {a.academic_year}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <StatusBadge status={a.status} />
                            <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '0.2rem' }}>{a.stage}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <button
                              onClick={() => handleOpenHistory(a.application_id)}
                              className="btn btn--xs btn--primary"
                              style={{ fontWeight: 600, whiteSpace: 'nowrap' }}
                            >
                              📜 History & Audit
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination Controls */}
            <div style={{ padding: '0.75rem 1.25rem', background: '#f8fafc', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button
                disabled={admPage === 0}
                onClick={() => setAdmPage(p => Math.max(0, p - 1))}
                className="btn btn--xs btn--secondary"
              >
                ← Previous
              </button>
              <button
                disabled={(admPage + 1) * 15 >= admissionsTotal}
                onClick={() => setAdmPage(p => p + 1)}
                className="btn btn--xs btn--secondary"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 4: PLATFORM ACTIVITY FEED */}
      {/* ======================================================== */}
      {activeTab === 'activity-feed' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Filter Bar */}
          <div className="card" style={{ padding: '1rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>SEARCH</label>
                <input
                  type="text"
                  placeholder="Action, remarks, entity ID..."
                  value={feedSearch}
                  onChange={(e) => setFeedSearch(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>EVENT CATEGORY</label>
                <select
                  value={feedCategory}
                  onChange={(e) => { setFeedCategory(e.target.value); setFeedPage(0); }}
                  className="select select--sm"
                  style={{ width: '100%' }}
                >
                  <option value="all">All Categories</option>
                  <option value="admission">Admission Events</option>
                  <option value="academic">Academic & Marks</option>
                  <option value="institution">Institution & Seat Capacity</option>
                  <option value="staff">Staff & Admin Governance</option>
                  <option value="security">Security & Auth</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>ACTOR ROLE</label>
                <select
                  value={feedRole}
                  onChange={(e) => { setFeedRole(e.target.value); setFeedPage(0); }}
                  className="select select--sm"
                  style={{ width: '100%' }}
                >
                  <option value="all">All Roles</option>
                  <option value="parent">Parent</option>
                  <option value="school_staff">Institution Staff</option>
                  <option value="school_admin">Institution Admin</option>
                  <option value="platform_admin">Platform Admin</option>
                  <option value="student">Student</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem' }}>
                <button onClick={() => loadFeed()} className="btn btn--sm btn--primary" style={{ flex: 1, fontWeight: 600 }}>
                  Filter Feed
                </button>
                <button onClick={() => { setFeedSearch(''); setFeedCategory('all'); setFeedRole('all'); setFeedPage(0); }} className="btn btn--sm btn--ghost">
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Feed List Table */}
          <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', color: '#1a3a6b', fontWeight: 700 }}>
                Central Activity Stream ({feedTotal} recorded activities)
              </h3>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Page {feedPage + 1} of {Math.max(1, Math.ceil(feedTotal / 20))}
              </span>
            </div>

            {loadingFeed ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Category & Type</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Activity Description</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Institution</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Actor</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Entity ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {feedItems.length === 0 ? (
                      <tr><td colSpan={7} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>No activities recorded matching the current filter.</td></tr>
                    ) : (
                      feedItems.map((item) => (
                        <tr key={item.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '0.75rem 1rem', whiteSpace: 'nowrap', color: '#64748b', fontSize: '0.8rem' }}>
                            {new Date(item.created_at).toLocaleString()}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <span className={`badge ${
                              item.event_category === 'admission' ? 'badge--info' :
                              item.event_category === 'academic' ? 'badge--success' :
                              item.event_category === 'institution' ? 'badge--warning' :
                              item.event_category === 'staff' ? 'badge--primary' : 'badge--neutral'
                            }`} style={{ fontSize: '0.7rem' }}>
                              {item.event_category?.toUpperCase()}
                            </span>
                            <div style={{ fontSize: '0.7rem', color: '#475569', marginTop: '0.15rem', fontFamily: 'monospace' }}>
                              {item.event_type}
                            </div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600, color: '#0f172a' }}>{item.action}</div>
                            {item.remarks && (
                              <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '0.15rem' }}>
                                {item.remarks}
                              </div>
                            )}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            {item.institution_name ? (
                              <>
                                <div style={{ fontWeight: 600 }}>{item.institution_name}</div>
                                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.institution_id}</div>
                              </>
                            ) : (
                              <span style={{ color: '#94a3b8' }}>— Global Platform —</span>
                            )}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600 }}>{item.actor_name || 'System'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.actor_role}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem' }}>
                            {item.entity_id}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <button
                              onClick={() => { setSelectedFeedItem(item); setFeedModalOpen(true); }}
                              className="btn btn--xs btn--ghost"
                              style={{ color: '#2563eb', fontWeight: 600 }}
                            >
                              Inspect 🔍
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination Controls */}
            <div style={{ padding: '0.75rem 1.25rem', background: '#f8fafc', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button
                disabled={feedPage === 0}
                onClick={() => setFeedPage(p => Math.max(0, p - 1))}
                className="btn btn--xs btn--secondary"
              >
                ← Previous
              </button>
              <button
                disabled={(feedPage + 1) * 20 >= feedTotal}
                onClick={() => setFeedPage(p => p + 1)}
                className="btn btn--xs btn--secondary"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 5: AUDIT LOGS */}
      {/* ======================================================== */}
      {activeTab === 'audit-logs' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Filter Bar */}
          <div className="card" style={{ padding: '1rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>SEARCH AUDIT TRAIL</label>
                <input
                  type="text"
                  placeholder="Action, actor, entity ID..."
                  value={auditSearch}
                  onChange={(e) => setAuditSearch(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569', display: 'block', marginBottom: '0.2rem' }}>CATEGORY</label>
                <select
                  value={auditCategory}
                  onChange={(e) => { setAuditCategory(e.target.value); setAuditPage(0); }}
                  className="select select--sm"
                  style={{ width: '100%' }}
                >
                  <option value="all">All Audit Categories</option>
                  <option value="admission">Admission Audits</option>
                  <option value="academic">Academic & Marks Audits</option>
                  <option value="staff">Staff & Admin Audits</option>
                  <option value="institution">Institution Audits</option>
                  <option value="security">Security & Ledger</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem' }}>
                <button onClick={() => loadAudit()} className="btn btn--sm btn--primary" style={{ flex: 1, fontWeight: 600 }}>
                  Search Logs
                </button>
                <button onClick={() => { setAuditSearch(''); setAuditCategory('all'); setAuditPage(0); }} className="btn btn--sm btn--ghost">
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Audit Table */}
          <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', color: '#1a3a6b', fontWeight: 700 }}>
                Database-Backed Audit Ledger ({auditTotal} events)
              </h3>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Page {auditPage + 1} of {Math.max(1, Math.ceil(auditTotal / 25))}
              </span>
            </div>

            {loadingAudit ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Audit ID</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Actor</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Action</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Entity</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Institution</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Payload</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditLogs.length === 0 ? (
                      <tr><td colSpan={7} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>No audit logs found.</td></tr>
                    ) : (
                      auditLogs.map((log) => (
                        <tr key={log.audit_id || log.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '0.75rem 1rem', fontFamily: 'monospace', fontSize: '0.75rem', fontWeight: 700, color: '#475569' }}>
                            {log.audit_id || log.id}
                          </td>
                          <td style={{ padding: '0.75rem 1rem', whiteSpace: 'nowrap', color: '#64748b', fontSize: '0.8rem' }}>
                            {new Date(log.created_at).toLocaleString()}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontWeight: 600 }}>{log.actor_name || log.actor_user_id || 'System'}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{log.actor_role}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem', fontWeight: 600, color: '#0f172a' }}>
                            {log.action}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>{log.entity_type}</div>
                            <div style={{ fontSize: '0.75rem', color: '#64748b', fontFamily: 'monospace' }}>{log.entity_id}</div>
                          </td>
                          <td style={{ padding: '0.75rem 1rem', color: '#475569' }}>
                            {log.institution_name || log.institution_id || '—'}
                          </td>
                          <td style={{ padding: '0.75rem 1rem' }}>
                            <button
                              onClick={() => { setSelectedFeedItem(log); setFeedModalOpen(true); }}
                              className="btn btn--xs btn--ghost"
                              style={{ color: '#2563eb', fontWeight: 600 }}
                            >
                              Inspect JSON
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination Controls */}
            <div style={{ padding: '0.75rem 1.25rem', background: '#f8fafc', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
              <button
                disabled={auditPage === 0}
                onClick={() => setAuditPage(p => Math.max(0, p - 1))}
                className="btn btn--xs btn--secondary"
              >
                ← Previous
              </button>
              <button
                disabled={(auditPage + 1) * 25 >= auditTotal}
                onClick={() => setAuditPage(p => p + 1)}
                className="btn btn--xs btn--secondary"
              >
                Next →
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 6: USER AND STAFF ACTIVITY */}
      {/* ======================================================== */}
      {activeTab === 'staff-activity' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Statewide Staff Governance */}
          <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1a3a6b', fontWeight: 700 }}>
                  Statewide Staff Governance & Monitoring
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                  Institutional staff accounts across all 30 institutions
                </p>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <select
                  value={staffCategory}
                  onChange={(e) => setStaffCategory(e.target.value)}
                  className="select select--sm"
                >
                  <option value="all">All Tiers</option>
                  <option value="k10_school">Schools</option>
                  <option value="pu_college">PU Colleges</option>
                  <option value="degree_college">Degree Colleges</option>
                  <option value="university">Universities</option>
                </select>
                <button onClick={loadStaffMonitoring} className="btn btn--sm btn--secondary">Refresh Staff</button>
              </div>
            </div>

            {loadingStaffMon ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}><LoadingSpinner /></div>
            ) : (
              <div style={{ padding: '1rem', overflowX: 'auto' }}>
                {staffMonitoring?.institutions ? (
                  <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                        <th style={{ padding: '0.6rem 0.8rem' }}>Institution</th>
                        <th style={{ padding: '0.6rem 0.8rem' }}>Tier</th>
                        <th style={{ padding: '0.6rem 0.8rem' }}>Admins Assigned</th>
                        <th style={{ padding: '0.6rem 0.8rem' }}>Staff Count</th>
                        <th style={{ padding: '0.6rem 0.8rem' }}>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {staffMonitoring.institutions
                        .filter(inst => staffCategory === 'all' || inst.category === staffCategory)
                        .map(inst => (
                          <tr key={inst.school_id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                            <td style={{ padding: '0.6rem 0.8rem', fontWeight: 600 }}>
                              {inst.school_name} <span style={{ color: '#64748b', fontSize: '0.75rem' }}>({inst.school_id})</span>
                            </td>
                            <td style={{ padding: '0.6rem 0.8rem' }}>
                              <span className="badge badge--neutral" style={{ fontSize: '0.7rem' }}>
                                {(inst.category || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '')}
                              </span>
                            </td>
                            <td style={{ padding: '0.6rem 0.8rem' }}>{inst.admin_count || 1}</td>
                            <td style={{ padding: '0.6rem 0.8rem' }}>{inst.staff_count || 0}</td>
                            <td style={{ padding: '0.6rem 0.8rem' }}>
                              <span className="badge badge--success" style={{ fontSize: '0.7rem' }}>OPERATIONAL</span>
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                ) : (
                  <div style={{ color: '#64748b', textAlign: 'center', padding: '1.5rem' }}>No staff monitoring records found.</div>
                )}
              </div>
            )}
          </div>

          {/* Staff & Admin Lifecycle Activity Events */}
          <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
            <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc' }}>
              <h3 style={{ margin: 0, fontSize: '1rem', color: '#1a3a6b', fontWeight: 700 }}>
                Recent Administrator & Staff Lifecycle Events
              </h3>
            </div>
            {loadingStaffActs ? (
              <div style={{ textAlign: 'center', padding: '2rem' }}><LoadingSpinner /></div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                      <th style={{ padding: '0.6rem 0.8rem' }}>Timestamp</th>
                      <th style={{ padding: '0.6rem 0.8rem' }}>Event</th>
                      <th style={{ padding: '0.6rem 0.8rem' }}>Institution</th>
                      <th style={{ padding: '0.6rem 0.8rem' }}>Actor</th>
                      <th style={{ padding: '0.6rem 0.8rem' }}>Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {staffActivities.length === 0 ? (
                      <tr><td colSpan={5} style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b' }}>No staff lifecycle events recorded yet.</td></tr>
                    ) : (
                      staffActivities.map(item => (
                        <tr key={item.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                          <td style={{ padding: '0.6rem 0.8rem', whiteSpace: 'nowrap', color: '#64748b', fontSize: '0.75rem' }}>
                            {new Date(item.created_at).toLocaleString()}
                          </td>
                          <td style={{ padding: '0.6rem 0.8rem', fontFamily: 'monospace', fontSize: '0.75rem', fontWeight: 600 }}>
                            {item.event_type}
                          </td>
                          <td style={{ padding: '0.6rem 0.8rem' }}>{item.institution_name || item.institution_id || 'Platform'}</td>
                          <td style={{ padding: '0.6rem 0.8rem' }}>{item.actor_name} ({item.actor_role})</td>
                          <td style={{ padding: '0.6rem 0.8rem', color: '#1e293b' }}>{item.action}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 7: ACADEMIC MONITORING */}
      {/* ======================================================== */}
      {activeTab === 'academic-monitoring' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card" style={{ padding: '1rem', background: '#ffffff', border: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#1a3a6b', fontWeight: 700 }}>
                Central Academic Activity & Corrections Audit
              </h3>
              <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                Full visibility into examination entries, attendance batches, and marks corrections
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <select
                value={academicInstFilter}
                onChange={(e) => setAcademicInstFilter(e.target.value)}
                className="select select--sm"
              >
                <option value="all">All Institutions</option>
                {schools.map(s => (
                  <option key={s.school_id} value={s.school_id}>{s.school_name} ({s.school_id})</option>
                ))}
              </select>
              <button onClick={() => loadAcademic()} className="btn btn--sm btn--primary">Filter</button>
            </div>
          </div>

          <div className="card" style={{ border: '1px solid #d0d5dd', borderRadius: '8px', overflow: 'hidden', background: '#ffffff' }}>
            <div style={{ padding: '0.875rem 1.25rem', borderBottom: '1px solid #e8eaed', background: '#f8fafc' }}>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: '#1a3a6b', fontWeight: 700 }}>
                Academic Audit Ledger ({academicActivities.length} items)
              </h4>
            </div>

            {loadingAcademic ? (
              <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table className="table" style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                  <thead>
                    <tr style={{ background: '#f1f5f9', borderBottom: '2px solid #e2e8f0', textAlign: 'left' }}>
                      <th style={{ padding: '0.75rem 1rem' }}>Timestamp</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Event Type</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Institution</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Action & Description</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Correction Details</th>
                      <th style={{ padding: '0.75rem 1rem' }}>Staff Member</th>
                    </tr>
                  </thead>
                  <tbody>
                    {academicActivities.length === 0 ? (
                      <tr><td colSpan={6} style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>No academic events found.</td></tr>
                    ) : (
                      academicActivities.map(item => {
                        const oldV = item.old_values ? JSON.parse(item.old_values) : null
                        const newV = item.new_values ? JSON.parse(item.new_values) : null
                        return (
                          <tr key={item.id} style={{ borderBottom: '1px solid #e2e8f0' }}>
                            <td style={{ padding: '0.75rem 1rem', whiteSpace: 'nowrap', color: '#64748b', fontSize: '0.8rem' }}>
                              {new Date(item.created_at).toLocaleString()}
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <span className={`badge ${
                                item.event_type === 'MARKS_CORRECTED' ? 'badge--warning' :
                                item.event_type === 'ATTENDANCE_RECORDED' ? 'badge--info' : 'badge--success'
                              }`} style={{ fontSize: '0.7rem' }}>
                                {item.event_type}
                              </span>
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 600 }}>{item.institution_name || item.institution_id}</div>
                              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.institution_id}</div>
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div style={{ fontWeight: 600, color: '#0f172a' }}>{item.action}</div>
                              {item.remarks && (
                                <div style={{ fontSize: '0.75rem', color: '#b45309', marginTop: '0.15rem' }}>
                                  Reason: {item.remarks}
                                </div>
                              )}
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              {oldV && newV ? (
                                <div style={{ fontSize: '0.8rem' }}>
                                  <span style={{ color: '#b91c1c', textDecoration: 'line-through' }}>{oldV.marks_obtained || JSON.stringify(oldV)}</span>
                                  {' → '}
                                  <span style={{ color: '#15803d', fontWeight: 700 }}>{newV.marks_obtained || JSON.stringify(newV)}</span>
                                  {newV.maximum_marks && <span style={{ color: '#64748b' }}> / {newV.maximum_marks}</span>}
                                </div>
                              ) : (
                                <span style={{ color: '#94a3b8' }}>—</span>
                              )}
                            </td>
                            <td style={{ padding: '0.75rem 1rem' }}>
                              <div>{item.actor_name}</div>
                              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{item.actor_role}</div>
                            </td>
                          </tr>
                        )
                      })
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 8: REPORTS AND ANALYTICS */}
      {/* ======================================================== */}
      {activeTab === 'reports-analytics' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {loadingAnalytics && !analytics ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
          ) : (
            <>
              {/* TOP ANALYTICS CARDS */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem' }}>
                <div className="card" style={{ padding: '1.25rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#1a3a6b', fontWeight: 700 }}>
                    🏛️ Applications by Education Tier
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {analytics?.applications_by_category && Object.entries(analytics.applications_by_category).map(([cat, count]) => (
                      <div key={cat} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                        <span style={{ textTransform: 'capitalize', color: '#475569' }}>{cat.replace('_', ' ')}</span>
                        <span className="badge badge--neutral" style={{ fontWeight: 700 }}>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card" style={{ padding: '1.25rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#1a3a6b', fontWeight: 700 }}>
                    ⚡ Audit Events by Activity Domain
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {analytics?.events_by_category && Object.entries(analytics.events_by_category).map(([cat, count]) => (
                      <div key={cat} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                        <span style={{ textTransform: 'capitalize', color: '#475569' }}>{cat} Domain</span>
                        <span className="badge badge--info" style={{ fontWeight: 700 }}>{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card" style={{ padding: '1.25rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#1a3a6b', fontWeight: 700 }}>
                    🏆 Top Institutions by Application Volume
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {analytics?.top_institutions && analytics.top_institutions.map(inst => (
                      <div key={inst.school_id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                        <span style={{ fontWeight: 600, color: '#1e293b' }}>{inst.school_name}</span>
                        <span className="badge badge--primary" style={{ fontWeight: 700 }}>{inst.app_count} apps</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* ======================================================== */}
      {/* SECTION 9: PLATFORM REQUEST & COMPLAINTS OVERSIGHT */}
      {/* ======================================================== */}
      {activeTab === 'requests' && (
        <PlatformRequestOversightDesk token={token} />
      )}

      {/* ======================================================== */}
      {/* MODAL 1: APPLICATION CHRONOLOGICAL AUDIT HISTORY */}
      {/* ======================================================== */}
      {historyModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div className="card" style={{
            background: '#ffffff',
            maxWidth: '800px',
            width: '100%',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: '12px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            overflow: 'hidden'
          }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#0f172a', fontWeight: 700 }}>
                  Chronological Admission Audit History
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                  Application ID: <strong style={{ fontFamily: 'monospace', color: '#1e3a8a' }}>{selectedHistory?.application?.application_id}</strong>
                </p>
              </div>
              <button onClick={() => setHistoryModalOpen(false)} className="btn btn--sm btn--ghost" style={{ fontSize: '1.2rem', padding: '0.2rem 0.6rem' }}>×</button>
            </div>

            <div style={{ padding: '1.5rem', overflowY: 'auto' }}>
              {loadingHistory ? (
                <div style={{ textAlign: 'center', padding: '3rem' }}><LoadingSpinner /></div>
              ) : selectedHistory ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  {/* Summary Card */}
                  <div style={{ background: '#f1f5f9', padding: '1rem', borderRadius: '8px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
                    <div><span style={{ color: '#64748b' }}>Applicant:</span> <strong>{selectedHistory.application?.applicant_name}</strong></div>
                    <div><span style={{ color: '#64748b' }}>Parent:</span> <strong>{selectedHistory.application?.parent_name}</strong></div>
                    <div><span style={{ color: '#64748b' }}>Institution:</span> <strong>{selectedHistory.application?.school_name}</strong></div>
                    <div><span style={{ color: '#64748b' }}>Current Status:</span> <StatusBadge status={selectedHistory.application?.status} /></div>
                  </div>

                  {/* Chronological Timeline */}
                  <div>
                    <h4 style={{ margin: '0 0 0.75rem 0', fontSize: '0.95rem', color: '#1a3a6b', fontWeight: 700 }}>
                      Complete Event Timeline ({selectedHistory.events?.length || 0} events)
                    </h4>
                    <div style={{ borderLeft: '2px solid #cbd5e1', marginLeft: '0.75rem', paddingLeft: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                      {selectedHistory.events && selectedHistory.events.map((evt, idx) => (
                        <div key={idx} style={{ position: 'relative' }}>
                          {/* Dot */}
                          <div style={{
                            position: 'absolute',
                            left: '-1.65rem',
                            top: '0.15rem',
                            width: '12px',
                            height: '12px',
                            borderRadius: '50%',
                            background: evt.type === 'STATUS_TRANSITION' ? '#2563eb' : '#10b981',
                            border: '2px solid #ffffff'
                          }} />
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b' }}>
                            <span>{new Date(evt.created_at).toLocaleString()}</span>
                            <span>Actor: <strong>{evt.actor_name}</strong> ({evt.actor_role})</span>
                          </div>
                          <div style={{ fontWeight: 600, color: '#0f172a', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                            {evt.previous_status ? (
                              <span>Status transitioned from <span style={{ color: '#b91c1c' }}>{evt.previous_status}</span> → <span style={{ color: '#15803d' }}>{evt.new_status}</span></span>
                            ) : (
                              <span>Initial status: <span style={{ color: '#15803d' }}>{evt.new_status}</span></span>
                            )}
                          </div>
                          {evt.remarks && (
                            <div style={{ background: '#f8fafc', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0', fontSize: '0.8rem', color: '#334155', marginTop: '0.35rem' }}>
                              {evt.remarks}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            <div style={{ padding: '0.75rem 1.5rem', background: '#f8fafc', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setHistoryModalOpen(false)} className="btn btn--sm btn--secondary">Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* MODAL 2: ACTIVITY / AUDIT JSON DETAIL INSPECTOR */}
      {/* ======================================================== */}
      {feedModalOpen && selectedFeedItem && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div className="card" style={{
            background: '#ffffff',
            maxWidth: '650px',
            width: '100%',
            maxHeight: '90vh',
            display: 'flex',
            flexDirection: 'column',
            borderRadius: '12px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            overflow: 'hidden'
          }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0f172a', fontWeight: 700 }}>
                  Audit Event Payload Inspector
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.8rem', color: '#64748b', fontFamily: 'monospace' }}>
                  ID: {selectedFeedItem.id || selectedFeedItem.audit_id}
                </p>
              </div>
              <button onClick={() => setFeedModalOpen(false)} className="btn btn--sm btn--ghost" style={{ fontSize: '1.2rem', padding: '0.2rem 0.6rem' }}>×</button>
            </div>

            <div style={{ padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem', fontSize: '0.85rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem', background: '#f8fafc', padding: '0.75rem', borderRadius: '6px' }}>
                <div><span style={{ color: '#64748b' }}>Action:</span> <strong>{selectedFeedItem.action}</strong></div>
                <div><span style={{ color: '#64748b' }}>Timestamp:</span> {new Date(selectedFeedItem.created_at).toLocaleString()}</div>
                <div><span style={{ color: '#64748b' }}>Actor:</span> <strong>{selectedFeedItem.actor_name}</strong> ({selectedFeedItem.actor_role})</div>
                <div><span style={{ color: '#64748b' }}>Entity:</span> {selectedFeedItem.entity_type} ({selectedFeedItem.entity_id})</div>
              </div>

              {selectedFeedItem.remarks && (
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#475569' }}>REMARKS / REASON</label>
                  <div style={{ background: '#fffbeb', border: '1px solid #fef08a', padding: '0.5rem 0.75rem', borderRadius: '6px', color: '#92400e' }}>
                    {selectedFeedItem.remarks}
                  </div>
                </div>
              )}

              {selectedFeedItem.old_values && (
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#b91c1c' }}>PREVIOUS VALUES (OLD)</label>
                  <pre style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '0.75rem', borderRadius: '6px', fontSize: '0.8rem', overflowX: 'auto' }}>
                    {JSON.stringify(typeof selectedFeedItem.old_values === 'string' ? JSON.parse(selectedFeedItem.old_values) : selectedFeedItem.old_values, null, 2)}
                  </pre>
                </div>
              )}

              {selectedFeedItem.new_values && (
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 700, color: '#15803d' }}>UPDATED VALUES (NEW)</label>
                  <pre style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '0.75rem', borderRadius: '6px', fontSize: '0.8rem', overflowX: 'auto' }}>
                    {JSON.stringify(typeof selectedFeedItem.new_values === 'string' ? JSON.parse(selectedFeedItem.new_values) : selectedFeedItem.new_values, null, 2)}
                  </pre>
                </div>
              )}
            </div>

            <div style={{ padding: '0.75rem 1.5rem', background: '#f8fafc', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setFeedModalOpen(false)} className="btn btn--sm btn--secondary">Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* MODAL 3: INVITE ACADEMIC ADMINISTRATOR */}
      {/* ======================================================== */}
      {showInviteModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div className="card" style={{
            background: '#ffffff',
            maxWidth: '560px',
            width: '100%',
            borderRadius: '12px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            overflow: 'hidden'
          }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.15rem', color: '#0f172a', fontWeight: 700 }}>
                  Invite Institution Administrator
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                  Assigns exactly one Academic Administrator per institution
                </p>
              </div>
              <button onClick={() => setShowInviteModal(false)} className="btn btn--sm btn--ghost" style={{ fontSize: '1.2rem', padding: '0.2rem 0.6rem' }}>×</button>
            </div>

            <div style={{ padding: '1.5rem' }}>
              {inviteError && <Alert type="error" className="mb-4" onClose={() => setInviteError('')}>{inviteError}</Alert>}
              {inviteResult ? (
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', padding: '1.25rem', borderRadius: '8px', color: '#166534' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
                    <span style={{ fontSize: '1.4rem' }}>✅</span>
                    <h4 style={{ margin: 0, fontWeight: 700, fontSize: '1.15rem', color: '#166534' }}>
                      Invitation Successfully Sent
                    </h4>
                  </div>

                  <div style={{ background: '#ffffff', border: '1px solid #dcfce7', borderRadius: '6px', padding: '1rem', marginBottom: '1rem', color: '#1e293b' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '140px 1fr', rowGap: '0.6rem', fontSize: '0.875rem' }}>
                      <span style={{ fontWeight: 600, color: '#64748b' }}>Institution:</span>
                      <span style={{ fontWeight: 700, color: '#0f172a' }}>{inviteResult.school_name} ({inviteResult.institution_id})</span>

                      <span style={{ fontWeight: 600, color: '#64748b' }}>Administrator:</span>
                      <span style={{ fontWeight: 600, color: '#0f172a' }}>{inviteResult.full_name || inviteFullName}</span>

                      <span style={{ fontWeight: 600, color: '#64748b' }}>Official Email:</span>
                      <span style={{ fontFamily: 'monospace', color: '#0284c7', fontWeight: 600 }}>{inviteResult.email}</span>

                      <span style={{ fontWeight: 600, color: '#64748b' }}>Invitation Status:</span>
                      <span>
                        <span style={{ background: '#fef3c7', color: '#92400e', border: '1px solid #fde68a', padding: '0.2rem 0.55rem', borderRadius: '4px', fontWeight: 700, fontSize: '0.75rem' }}>
                          Sent / Pending
                        </span>
                      </span>
                    </div>
                  </div>

                  <p style={{ margin: '0 0 0.85rem 0', color: '#15803d', fontSize: '0.875rem', lineHeight: 1.5 }}>
                    The administrator invitation has been issued. The intended administrator can proceed with account setup through the NagrikSetu institution portal.
                  </p>

                  <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.775rem', color: '#64748b', lineHeight: 1.45 }}>
                    ℹ️ <em>Delivery Status Notice:</em> Live SMTP relay is not configured in this staging deployment. The invitation is securely recorded in the registry, and the authorized administrator can proceed directly via the official institution portal.
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      type="button"
                      onClick={() => {
                        setShowInviteModal(false)
                        setInviteResult(null)
                      }}
                      className="btn btn--primary"
                      style={{ padding: '0.5rem 1.25rem', fontWeight: 600 }}
                    >
                      Done
                    </button>
                  </div>
                </div>
              ) : (
                <form onSubmit={handleInviteSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div>
                    <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>
                      FULL NAME *
                    </label>
                    <input
                      type="text"
                      required
                      placeholder="e.g. Dr. K. S. Rao"
                      value={inviteFullName}
                      onChange={(e) => setInviteFullName(e.target.value)}
                      className="input input--sm"
                      style={{ width: '100%' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>
                      EMAIL ADDRESS *
                    </label>
                    <input
                      type="email"
                      required
                      placeholder="academic.head@institution.edu.in"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      className="input input--sm"
                      style={{ width: '100%' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>
                      PHONE NUMBER (OPTIONAL)
                    </label>
                    <input
                      type="tel"
                      placeholder="9876543210"
                      value={invitePhone}
                      onChange={(e) => setInvitePhone(e.target.value)}
                      className="input input--sm"
                      style={{ width: '100%' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>
                      ASSIGNED ROLE
                    </label>
                    <div style={{
                      padding: '0.55rem 0.85rem',
                      background: '#f8fafc',
                      border: '1px solid #cbd5e1',
                      borderRadius: '6px',
                      color: '#0f172a',
                      fontWeight: 600,
                      fontSize: '0.875rem',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      userSelect: 'none'
                    }}>
                      <span>Academic Administrator</span>
                      <span style={{ fontSize: '0.72rem', color: '#0369a1', background: '#e0f2fe', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 700 }}>
                        FIXED
                      </span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'block', marginTop: '0.25rem' }}>
                      Role is fixed to Academic Administrator for institutional oversight.
                    </span>
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>
                      TARGET INSTITUTION *
                    </label>
                    <input
                      type="text"
                      placeholder="Filter by institution name or code..."
                      value={institutionSearchTerm}
                      onChange={(e) => setInstitutionSearchTerm(e.target.value)}
                      className="input input--sm mb-2"
                      style={{ width: '100%' }}
                    />
                    <select
                      required
                      value={inviteInstitutionId}
                      onChange={(e) => setInviteInstitutionId(e.target.value)}
                      className="select select--sm"
                      style={{ width: '100%' }}
                    >
                      <option value="">-- Select Unassigned Institution ({filteredEligible.length} available) --</option>
                      {filteredEligible.map(inst => (
                        <option key={inst.school_id} value={inst.school_id}>
                          [{inst.school_id}] {inst.school_name} — ({(inst.category || '').replace(/\s*\([Kk][-–—]?10\)/gi, '').replace(/\s*\(11[-–—]?12\)/gi, '').toUpperCase() || inst.school_type}
                        </option>
                      ))}
                    </select>
                    {filteredEligible.length === 0 && (
                      <div style={{ color: '#92400e', background: '#fef3c7', padding: '0.5rem 0.75rem', borderRadius: '4px', border: '1px solid #fde68a', fontSize: '0.78rem', marginTop: '0.4rem', fontWeight: 600 }}>
                        All institutions have an Academic Administrator invitation or active assignment.
                      </div>
                    )}
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1rem' }}>
                    <button type="button" onClick={() => setShowInviteModal(false)} className="btn btn--sm btn--secondary">Cancel</button>
                    <button
                      type="submit"
                      disabled={submittingInvite || !inviteInstitutionId || filteredEligible.length === 0}
                      className="btn btn--sm btn--primary"
                      style={{ fontWeight: 600 }}
                    >
                      {submittingInvite ? 'Inviting...' : 'Send Invitation'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* MODAL: APPLICATION FULL DETAILS MODAL */}
      {/* ======================================================== */}
      {selectedAppModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1000, padding: '1rem'
        }}>
          <div className="card" style={{
            background: '#ffffff', maxWidth: '780px', width: '100%',
            maxHeight: '90vh', overflowY: 'auto', borderRadius: '12px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
          }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center', position: 'sticky', top: 0, zIndex: 10 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.2rem', color: '#0f172a', fontWeight: 700 }}>
                  Application Dossier: {selectedAppModal.institution_name}
                </h3>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '0.25rem' }}>
                  <span style={{ fontFamily: 'monospace', fontWeight: 700, color: '#155eef', fontSize: '0.85rem' }}>
                    {selectedAppModal.application_ref}
                  </span>
                  <span style={{ color: '#94a3b8' }}>•</span>
                  <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    Code: <strong>{selectedAppModal.institution_id}</strong>
                  </span>
                  <span style={{ color: '#94a3b8' }}>•</span>
                  <span className={`badge ${
                    selectedAppModal.status === 'approved' ? 'badge--success' :
                    selectedAppModal.status === 'rejected' ? 'badge--error' :
                    selectedAppModal.status === 'additional_info_required' ? 'badge--warning' : 'badge--neutral'
                  }`} style={{ fontSize: '0.75rem', fontWeight: 700 }}>
                    {selectedAppModal.status?.toUpperCase()}
                  </span>
                </div>
              </div>
              <button onClick={() => setSelectedAppModal(null)} className="btn btn--sm btn--ghost" style={{ fontSize: '1.2rem', padding: '0.2rem 0.6rem' }}>×</button>
            </div>

            <div style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', fontSize: '0.875rem' }}>
              {/* Section A */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e3a8a', fontSize: '0.95rem' }}>Section A: Institution Profile</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem' }}>
                  <div><span style={{ color: '#64748b' }}>Legal Name:</span> <strong>{selectedAppModal.institution_name}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Type:</span> <strong>{selectedAppModal.institution_type}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Category:</span> <strong>{selectedAppModal.institution_category}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Established Year:</span> <strong>{selectedAppModal.established_year || 'N/A'}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Affiliation:</span> <strong>{selectedAppModal.affiliation || 'N/A'}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Recognition/Reg No:</span> <strong>{selectedAppModal.recognition || 'N/A'}</strong></div>
                </div>
              </div>

              {/* Section B */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e3a8a', fontSize: '0.95rem' }}>Section B: Address Details</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem' }}>
                  <div><span style={{ color: '#64748b' }}>Line 1:</span> {selectedAppModal.address_line1}</div>
                  <div><span style={{ color: '#64748b' }}>Line 2:</span> {selectedAppModal.address_line2 || 'None'}</div>
                  <div><span style={{ color: '#64748b' }}>City:</span> {selectedAppModal.city}</div>
                  <div><span style={{ color: '#64748b' }}>District:</span> <strong>{selectedAppModal.district}</strong></div>
                  <div><span style={{ color: '#64748b' }}>State:</span> {selectedAppModal.state}</div>
                  <div><span style={{ color: '#64748b' }}>PIN:</span> <strong>{selectedAppModal.pincode}</strong></div>
                </div>
              </div>

              {/* Section C */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e3a8a', fontSize: '0.95rem' }}>Section C: Contact Information</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem' }}>
                  <div><span style={{ color: '#64748b' }}>Official Email:</span> <strong>{selectedAppModal.official_email}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Official Phone:</span> <strong>{selectedAppModal.official_phone}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Website:</span> {selectedAppModal.website ? <a href={selectedAppModal.website} target="_blank" rel="noreferrer">{selectedAppModal.website}</a> : 'N/A'}</div>
                </div>
              </div>

              {/* Section D: Academic Information */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e3a8a', fontSize: '0.95rem' }}>Section D: Academic Offerings</h4>
                {(() => {
                  try {
                    const parsed = JSON.parse(selectedAppModal.academic_info_json || '{}')
                    return (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {parsed.school_standards && <div><span style={{ color: '#64748b' }}>Grades/Standards:</span> <strong>{parsed.school_standards}</strong></div>}
                        {parsed.school_medium && <div><span style={{ color: '#64748b' }}>Medium of Instruction:</span> <strong>{parsed.school_medium}</strong></div>}
                        {parsed.pu_streams && <div><span style={{ color: '#64748b' }}>PU Streams:</span> <strong>{parsed.pu_streams.join(', ')}</strong></div>}
                        {parsed.pu_combinations && <div><span style={{ color: '#64748b' }}>Combinations:</span> <strong>{parsed.pu_combinations.join(', ')}</strong></div>}
                        {parsed.degree_programmes && Array.isArray(parsed.degree_programmes) && (
                          <div style={{ marginTop: '0.4rem' }}>
                            <div style={{ fontWeight: 600, color: '#64748b', marginBottom: '0.2rem' }}>Programmes & Intake:</div>
                            <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                              {parsed.degree_programmes.map((p, i) => (
                                <li key={i}>{p.code}: {p.name} ({p.duration}, {p.intake} seats)</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )
                  } catch {
                    return <div style={{ color: '#64748b' }}>{selectedAppModal.academic_info_json || 'Standard curriculum'}</div>
                  }
                })()}
              </div>

              {/* Section E: Authorized Administrator */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem', background: '#f8fafc' }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#1e3a8a', fontSize: '0.95rem' }}>Section E: Authorized Institution Administrator</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.5rem' }}>
                  <div><span style={{ color: '#64748b' }}>Administrator Name:</span> <strong>{selectedAppModal.applicant_name}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Designation:</span> <strong>{selectedAppModal.applicant_designation}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Login Email:</span> <strong style={{ color: '#155eef' }}>{selectedAppModal.applicant_email}</strong></div>
                  <div><span style={{ color: '#64748b' }}>Contact Mobile:</span> <strong>{selectedAppModal.applicant_phone}</strong></div>
                </div>
              </div>

              {/* Review History Notes */}
              {selectedAppModal.review_comments && (
                <div style={{ background: '#fffbeb', border: '1px solid #fef3c7', borderRadius: '8px', padding: '1rem' }}>
                  <div style={{ fontWeight: 700, color: '#b45309', marginBottom: '0.25rem' }}>Reviewer Comments / Instructions:</div>
                  <div style={{ color: '#78350f' }}>{selectedAppModal.review_comments}</div>
                  <div style={{ fontSize: '0.75rem', color: '#92400e', marginTop: '0.4rem' }}>
                    Reviewed by {selectedAppModal.reviewed_by || 'Admin'} at {selectedAppModal.reviewed_at || 'recent'}
                  </div>
                </div>
              )}
            </div>

            <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <button onClick={() => setSelectedAppModal(null)} className="btn btn--outline btn--sm">
                Close Dossier
              </button>
              {selectedAppModal.status !== 'approved' && (
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button
                    onClick={() => {
                      setActionAppModal(selectedAppModal)
                      setActionType('approve')
                      setActionComments('')
                    }}
                    className="btn btn--sm btn--primary"
                    style={{ background: '#16a34a', borderColor: '#16a34a' }}
                  >
                    Approve Application →
                  </button>
                  <button
                    onClick={() => {
                      setActionAppModal(selectedAppModal)
                      setActionType('reject')
                      setActionComments('')
                    }}
                    className="btn btn--sm btn--outline"
                    style={{ color: '#dc2626', borderColor: '#fca5a5' }}
                  >
                    Reject
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* MODAL: APPLICATION REVIEW ACTION (APPROVE / REJECT / REQUEST INFO) */}
      {/* ======================================================== */}
      {actionAppModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          zIndex: 1010, padding: '1rem'
        }}>
          <div className="card" style={{
            background: '#ffffff', maxWidth: '520px', width: '100%',
            borderRadius: '12px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            overflow: 'hidden'
          }}>
            <div style={{
              padding: '1.25rem 1.5rem',
              borderBottom: '1px solid #e2e8f0',
              background: actionType === 'approve' ? '#f0fdf4' : actionType === 'reject' ? '#fef2f2' : '#fffbeb',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center'
            }}>
              <div>
                <h3 style={{
                  margin: 0, fontSize: '1.15rem', fontWeight: 700,
                  color: actionType === 'approve' ? '#166534' : actionType === 'reject' ? '#991b1b' : '#92400e'
                }}>
                  {actionType === 'approve' && 'Approve Institution Application'}
                  {actionType === 'reject' && 'Reject Institution Application'}
                  {actionType === 'request_info' && 'Request Additional Information'}
                </h3>
                <p style={{ margin: '0.2rem 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                  {actionAppModal.institution_name} ({actionAppModal.application_ref})
                </p>
              </div>
              <button onClick={() => setActionAppModal(null)} className="btn btn--sm btn--ghost" style={{ fontSize: '1.2rem', padding: '0.2rem 0.6rem' }}>×</button>
            </div>

            <form onSubmit={(e) => {
              e.preventDefault()
              if (actionType === 'approve') handleApproveApplication(actionAppModal.application_id, actionComments)
              else if (actionType === 'reject') handleRejectApplication(actionAppModal.application_id, actionComments)
              else if (actionType === 'request_info') handleRequestInfoApplication(actionAppModal.application_id, actionComments)
            }} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {actionType === 'approve' && (
                <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.85rem', fontSize: '0.85rem', color: '#166534' }}>
                  <strong>Platform Approval Effect:</strong>
                  <ul style={{ margin: '0.4rem 0 0 0', paddingLeft: '1.25rem' }}>
                    <li>Adds <strong>{actionAppModal.institution_name}</strong> ({actionAppModal.institution_id}) to verified institutions.</li>
                    <li>Provisions <strong>{actionAppModal.applicant_email}</strong> as authorized School Administrator.</li>
                    <li>Enables immediate Administrator Desk login for applicant.</li>
                  </ul>
                </div>
              )}

              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                  {actionType === 'approve' ? 'Approval Comments (Optional):' :
                   actionType === 'reject' ? 'Rejection Reason (Required):' : 'Information Required Details (Required):'}
                </label>
                <textarea
                  required={actionType !== 'approve'}
                  rows={4}
                  value={actionComments}
                  onChange={(e) => setActionComments(e.target.value)}
                  placeholder={
                    actionType === 'approve' ? 'e.g. Documentation verified. Approved for Karnataka Education Platform onboarding.' :
                    actionType === 'reject' ? 'e.g. Recognition document invalid or unrecognized board affiliation.' :
                    'e.g. Please submit latest government recognition order and updated building occupancy certificate.'
                  }
                  style={{ width: '100%', padding: '0.65rem', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '0.875rem', boxSizing: 'border-box' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => setActionAppModal(null)}
                  className="btn btn--outline btn--sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={actionSubmitting}
                  className="btn btn--sm btn--primary"
                  style={{
                    background: actionType === 'approve' ? '#16a34a' : actionType === 'reject' ? '#dc2626' : '#d97706',
                    borderColor: actionType === 'approve' ? '#16a34a' : actionType === 'reject' ? '#dc2626' : '#d97706'
                  }}
                >
                  {actionSubmitting ? 'Processing...' : (
                    actionType === 'approve' ? 'Confirm Approval →' :
                    actionType === 'reject' ? 'Confirm Rejection' : 'Send Request'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ======================================================== */}
      {/* MODAL 4: QUICK SEAT CAPACITY ADJUSTMENT */}
      {/* ======================================================== */}
      {showCapacityModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.65)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }}>
          <div className="card" style={{
            background: '#ffffff',
            maxWidth: '480px',
            width: '100%',
            borderRadius: '12px',
            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
            overflow: 'hidden'
          }}>
            <div style={{ padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', background: '#f8fafc', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0f172a', fontWeight: 700 }}>
                Adjust Institution Seat Capacity
              </h3>
              <button onClick={() => setShowCapacityModal(false)} className="btn btn--sm btn--ghost" style={{ fontSize: '1.2rem', padding: '0.2rem 0.6rem' }}>×</button>
            </div>

            <form onSubmit={handleUpdateCapacity} style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>INSTITUTION CODE</label>
                <input
                  type="text"
                  required
                  value={capacitySchoolId}
                  onChange={(e) => setCapacitySchoolId(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>SECTION ID</label>
                <input
                  type="text"
                  required
                  value={capacitySectionId}
                  onChange={(e) => setCapacitySectionId(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>NEW SANCTIONED CAPACITY (SEATS)</label>
                <input
                  type="number"
                  min="1"
                  max="500"
                  required
                  value={newCapacityValue}
                  onChange={(e) => setNewCapacityValue(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', display: 'block', marginBottom: '0.3rem' }}>REASON FOR ADJUSTMENT</label>
                <input
                  type="text"
                  placeholder="Government directive, extra classroom, etc."
                  value={capacityReason}
                  onChange={(e) => setCapacityReason(e.target.value)}
                  className="input input--sm"
                  style={{ width: '100%' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button type="button" onClick={() => setShowCapacityModal(false)} className="btn btn--sm btn--secondary">Cancel</button>
                <button type="submit" disabled={updatingCapacity} className="btn btn--sm btn--primary">
                  {updatingCapacity ? 'Saving...' : 'Update Capacity'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  )
}
