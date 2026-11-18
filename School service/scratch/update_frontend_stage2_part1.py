import re

dashboard_path = 'C:/Users/callm/nagriksetu/frontend/src/pages/admin/InstitutionAdminDashboard.jsx'
with open(dashboard_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add Stage 2 & Document state variables around line 47
old_state = """  const [submittingAction, setSubmittingAction] = useState(false)
  const [actionFeedback, setActionFeedback] = useState(null) // { type: 'success' | 'error', message: string }"""

new_state = """  const [submittingAction, setSubmittingAction] = useState(false)
  const [actionFeedback, setActionFeedback] = useState(null) // { type: 'success' | 'error', message: string }

  // Stage 2 & Document Review State inside Review Modal
  const [previewDoc, setPreviewDoc] = useState(null)
  const [docActionModal, setDocActionModal] = useState(null) // { doc, actionType: 'verified' | 'reupload_requested' | 'rejected', notes: '' }
  const [submittingDocAction, setSubmittingDocAction] = useState(false)
  const [stage2ReviewNotes, setStage2ReviewNotes] = useState('')"""

# 2. Add document verification and stage 2 review functions around line 645
old_handlers = """      const hist = await apiGet(`/school/admissions/${selectedApp.application_id}/history`, token)
      setAppHistory(Array.isArray(hist) ? hist : hist?.history || [])
      setActionTab('none')
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to request clarification.' })
    } finally {
      setSubmittingAction(false)
    }
  }"""

new_handlers = """      const hist = await apiGet(`/school/admissions/${selectedApp.application_id}/history`, token)
      setAppHistory(Array.isArray(hist) ? hist : hist?.history || [])
      setActionTab('none')
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to request clarification.' })
    } finally {
      setSubmittingAction(false)
    }
  }

  // Handle Quick Verify Document
  async function handleQuickVerifyDoc(doc) {
    if (!selectedApp || !token) return
    const appId = selectedApp.application_id || selectedApp.id
    try {
      await apiPost(`/school/admissions/${appId}/documents/${doc.document_id}/verify`, {
        verification_status: 'verified',
        verification_notes: 'Document verified and found authentic by institution administrator.'
      }, token)
      setActionFeedback({ type: 'success', message: `Document '${doc.file_name}' (${doc.document_type}) verified successfully.` })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to verify document.' })
    }
  }

  // Handle Document Verification Action Submit (Verify / Reupload / Reject)
  async function handleVerifyDocSubmit(e) {
    e.preventDefault()
    if (!docActionModal || !selectedApp || !token) return
    const { doc, actionType, notes } = docActionModal
    if ((actionType === 'reupload_requested' || actionType === 'rejected') && !notes.trim()) {
      setActionFeedback({ type: 'error', message: 'A specific reason/explanation is mandatory when rejecting or requesting document re-upload.' })
      return
    }
    const appId = selectedApp.application_id || selectedApp.id
    try {
      setSubmittingDocAction(true)
      await apiPost(`/school/admissions/${appId}/documents/${doc.document_id}/verify`, {
        verification_status: actionType,
        verification_notes: notes.trim() || undefined
      }, token)
      
      const label = actionType === 'verified' ? 'Verified' : (actionType === 'reupload_requested' ? 'Replacement Requested' : 'Rejected')
      setActionFeedback({ type: 'success', message: `Document '${doc.file_name}' marked as ${label}.` })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
      setDocActionModal(null)
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to update document verification status.' })
    } finally {
      setSubmittingDocAction(false)
    }
  }

  // Handle Stage 2 Review Submit (Detailed Review Completed or Correction Requested)
  async function handleStage2ReviewSubmit(decision) {
    if (!selectedApp || !token) return
    const appId = selectedApp.application_id || selectedApp.id
    if (decision === 'stage2_correction_requested' && !stage2ReviewNotes.trim()) {
      setActionFeedback({ type: 'error', message: 'Please specify the correction instructions required from the parent.' })
      return
    }
    try {
      setSubmittingAction(true)
      await apiPost(`/school/admissions/${appId}/stage2-review`, {
        decision: decision,
        review_notes: stage2ReviewNotes.trim() || undefined
      }, token)
      
      setActionFeedback({
        type: 'success',
        message: decision === 'detailed_review_completed'
          ? 'Stage 2 detailed dossier review completed! All records confirmed. Ready for Final Admission & Enrolment.'
          : 'Stage 2 correction notice published to parent portal.'
      })
      
      const [detailData, histData] = await Promise.all([
        apiGet(`/school/admissions/applications/${appId}`, token),
        apiGet(`/school/admissions/${appId}/history`, token).catch(() => [])
      ])
      setSelectedApp(detailData)
      setAppHistory(Array.isArray(histData) ? histData : histData?.history || [])
      loadApplications()
      loadOverview()
      setActionTab('none')
    } catch (err) {
      setActionFeedback({ type: 'error', message: err.message || 'Failed to submit Stage 2 review decision.' })
    } finally {
      setSubmittingAction(false)
    }
  }"""

# 3. Helper function to format document type nicely
doc_type_names = {
    'birth_certificate': 'Birth Certificate',
    'transfer_certificate': 'Transfer Certificate (TC)',
    'previous_marks_card': 'Previous Marks Card / Report',
    'passport_photo': 'Passport Photograph',
    'caste_certificate': 'Caste / Category Certificate',
    'income_certificate': 'Income Certificate',
    'aadhaar_card': 'Aadhaar Card / ID Proof',
    'conduct_certificate': 'Conduct / Character Certificate'
}

# Update state and handlers
for old_s, new_s, label in [
    (old_state, new_state, "state variables"),
    (old_handlers, new_handlers, "handlers")
]:
    old_crlf = old_s.replace('\n', '\r\n')
    new_crlf = new_s.replace('\n', '\r\n')
    if old_crlf in text:
        text = text.replace(old_crlf, new_crlf, 1)
        print(f"Replaced CRLF: {label}")
    elif old_s in text:
        text = text.replace(old_s, new_s, 1)
        print(f"Replaced LF: {label}")
    else:
        print(f"FAILED to find: {label}")

with open(dashboard_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved stage 1 of frontend update.")
