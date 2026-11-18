import os

file_path = r"C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add state variables around line 85
target_state = """  // Password Reset Notification Banner
  const [resetFeedback, setResetFeedback] = useState(null)"""

replacement_state = """  // Password Reset Notification Banner
  const [resetFeedback, setResetFeedback] = useState(null)

  // Level 2: Candidate Applications State
  const [staffSubTab, setStaffSubTab] = useState('roster') // 'roster' | 'candidates'
  const [candidateApps, setCandidateApps] = useState([])
  const [loadingCandidates, setLoadingCandidates] = useState(false)
  const [selectedCandidateApp, setSelectedCandidateApp] = useState(null)
  const [candidateActionTab, setCandidateActionTab] = useState('none') // 'none' | 'correct' | 'approve' | 'decline'
  const [correctionInput, setCorrectionInput] = useState('')
  const [declineInput, setDeclineInput] = useState('')
  const [approvalNotesInput, setApprovalNotesInput] = useState('')
  const [candidateActionSubmitting, setCandidateActionSubmitting] = useState(false)
  const [candidateActionFeedback, setCandidateActionFeedback] = useState(null)

  // Candidate Invite Modal State
  const [showCandidateInviteModal, setShowCandidateInviteModal] = useState(false)
  const [candInviteName, setCandInviteName] = useState('')
  const [candInviteEmail, setCandInviteEmail] = useState('')
  const [candInvitePhone, setCandInvitePhone] = useState('')
  const [candInviteRole, setCandInviteRole] = useState('admissions_officer')
  const [candInviteResult, setCandInviteResult] = useState(null)
  const [candInviteError, setCandInviteError] = useState('')
  const [submittingCandInvite, setSubmittingCandInvite] = useState(false)"""

assert target_state in content, "target_state not found"
content = content.replace(target_state, replacement_state, 1)

# 2. Add methods for candidate applications
target_methods = """  // Save Staff Permissions
  async function handleSavePermissions(e) {"""

replacement_methods = """  // Load Candidate Applications for this institution
  async function loadCandidateApps() {
    if (!token) return
    try {
      setLoadingCandidates(true)
      const data = await apiGet('/school/admin/staff-applications', token)
      setCandidateApps(Array.isArray(data) ? data : [])
    } catch (err) {
      // Fallback gracefully
    } finally {
      setLoadingCandidates(false)
    }
  }

  // Handle Candidate Invitation
  async function handleInviteCandidateSubmit(e) {
    e.preventDefault()
    if (!candInviteName.trim() || !candInviteEmail.trim()) {
      setCandInviteError('Please fill in candidate name and email.')
      return
    }

    try {
      setSubmittingCandInvite(true)
      setCandInviteError('')
      const res = await apiPost('/school/admin/staff-applications/invite', {
        candidate_name: candInviteName.trim(),
        candidate_email: candInviteEmail.trim(),
        candidate_phone: candInvitePhone.trim() || undefined,
        role_id: candInviteRole,
        institution_id: institutionId
      }, token)
      setCandInviteResult(res)
      loadCandidateApps()
    } catch (err) {
      setCandInviteError(err.message || 'Failed to generate candidate invitation.')
    } finally {
      setSubmittingCandInvite(false)
    }
  }

  // Inspect Candidate Application
  async function handleInspectCandidateApp(app) {
    setSelectedCandidateApp(app)
    setCandidateActionTab('none')
    setCorrectionInput('')
    setDeclineInput('')
    setApprovalNotesInput('')
    setCandidateActionFeedback(null)
    try {
      const full = await apiGet(`/school/admin/staff-applications/${app.application_id}`, token)
      setSelectedCandidateApp(full)
    } catch {
      // Keep existing app summary
    }
  }

  // Request Correction
  async function handleRequestCorrectionSubmit(e) {
    e.preventDefault()
    if (!correctionInput.trim()) {
      setCandidateActionFeedback({ type: 'error', message: 'Correction notes are mandatory.' })
      return
    }
    try {
      setCandidateActionSubmitting(true)
      setCandidateActionFeedback(null)
      await apiPost(`/school/admin/staff-applications/${selectedCandidateApp.application_id}/request-correction`, {
        correction_notes: correctionInput.trim()
      }, token)
      setCandidateActionFeedback({ type: 'success', message: 'Correction request dispatched to candidate dossier.' })
      setSelectedCandidateApp(prev => ({ ...prev, status: 'correction_requested', correction_notes: correctionInput.trim() }))
      loadCandidateApps()
      setCandidateActionTab('none')
    } catch (err) {
      setCandidateActionFeedback({ type: 'error', message: err.message || 'Failed to request correction.' })
    } finally {
      setCandidateActionSubmitting(false)
    }
  }

  // Approve Candidate Application
  async function handleApproveCandidateSubmit(e) {
    e.preventDefault()
    try {
      setCandidateActionSubmitting(true)
      setCandidateActionFeedback(null)
      const res = await apiPost(`/school/admin/staff-applications/${selectedCandidateApp.application_id}/approve`, {
        review_notes: approvalNotesInput.trim() || undefined
      }, token)
      setCandidateActionFeedback({ type: 'success', message: `Application approved! Activation token issued: ${res.activation_token}` })
      setSelectedCandidateApp(prev => ({ ...prev, status: 'approved', activation_token: res.activation_token, activation_url: res.activation_url }))
      loadCandidateApps()
      setCandidateActionTab('none')
    } catch (err) {
      setCandidateActionFeedback({ type: 'error', message: err.message || 'Failed to approve application.' })
    } finally {
      setCandidateActionSubmitting(false)
    }
  }

  // Decline Candidate Application
  async function handleDeclineCandidateSubmit(e) {
    e.preventDefault()
    if (!declineInput.trim()) {
      setCandidateActionFeedback({ type: 'error', message: 'Decline reason is mandatory.' })
      return
    }
    try {
      setCandidateActionSubmitting(true)
      setCandidateActionFeedback(null)
      await apiPost(`/school/admin/staff-applications/${selectedCandidateApp.application_id}/decline`, {
        reason: declineInput.trim()
      }, token)
      setCandidateActionFeedback({ type: 'success', message: 'Application declined with formal reason.' })
      setSelectedCandidateApp(prev => ({ ...prev, status: 'declined', review_notes: declineInput.trim() }))
      loadCandidateApps()
      setCandidateActionTab('none')
    } catch (err) {
      setCandidateActionFeedback({ type: 'error', message: err.message || 'Failed to decline application.' })
    } finally {
      setCandidateActionSubmitting(false)
    }
  }

  // Save Staff Permissions
  async function handleSavePermissions(e) {"""

assert target_methods in content, "target_methods not found"
content = content.replace(target_methods, replacement_methods, 1)

# 3. Add loadCandidateApps to useEffect
target_effect = """      loadOverview()
      loadApplications()
      loadStaffList()"""

replacement_effect = """      loadOverview()
      loadApplications()
      loadStaffList()
      loadCandidateApps()"""

assert target_effect in content, "target_effect not found"
content = content.replace(target_effect, replacement_effect, 1)

with open(file_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(content)

print("Updated InstitutionAdminDashboard.jsx state and methods!")
