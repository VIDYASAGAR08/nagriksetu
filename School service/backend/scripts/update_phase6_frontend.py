import re

desk_path = r"C:\Users\callm\nagriksetu\frontend\src\components\admissions\AdmissionDeskTab.jsx"
with open(desk_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

# 1. Add sections state in AdmissionDeskTab
old_states = "  const [verifyingDocId, setVerifyingDocId] = useState(null)\n  const [docNotesMap, setDocNotesMap] = useState({})"
new_states = """  const [verifyingDocId, setVerifyingDocId] = useState(null)
  const [docNotesMap, setDocNotesMap] = useState({})
  const [availableSections, setAvailableSections] = useState([])
  const [loadingSections, setLoadingSections] = useState(false)
  const [selectedSectionId, setSelectedSectionId] = useState('')"""

text = text.replace(old_states, new_states)

# 2. In handleInspect, fetch available sections
old_inspect_block = """      setHistory(Array.isArray(histData) ? histData : histData?.history || [])
      setStage2Dossier(stage2Data)
      setUploadedDocs(stage2Data?.uploaded_documents || [])
    } catch (err) {
      setHistory([])
      setStage2Dossier(null)
      setUploadedDocs([])
    } finally {
      setLoadingHistory(false)
    }"""

new_inspect_block = """      setHistory(Array.isArray(histData) ? histData : histData?.history || [])
      setStage2Dossier(stage2Data)
      setUploadedDocs(stage2Data?.uploaded_documents || [])

      // Fetch available sections for Phase 6 enrolment
      try {
        setLoadingSections(true)
        const secs = await apiGet(`/school/admissions/${app.application_id}/available-sections`)
        const secList = Array.isArray(secs) ? secs : []
        setAvailableSections(secList)
        if (secList.length > 0) {
          const avail = secList.find(s => !s.is_full) || secList[0]
          setSelectedSectionId(avail.section_id)
        }
      } catch {
        setAvailableSections([])
      } finally {
        setLoadingSections(false)
      }
    } catch (err) {
      setHistory([])
      setStage2Dossier(null)
      setUploadedDocs([])
      setAvailableSections([])
    } finally {
      setLoadingHistory(false)
    }"""

text = text.replace(old_inspect_block, new_inspect_block)

# 3. Add confirm_enrolment in handleExecuteAction
old_action_stage2 = """      } else if (actionType === 'complete_stage2') {
        await apiPost(`/school/admissions/${activeApp.application_id}/stage2-review`, {
          decision: 'detailed_review_completed',
          review_notes: actionNotes.trim() || 'All Stage 2 documents and academic records verified.'
        })
        setSuccess(`Stage 2 review completed for ${activeApp.application_id}. Application marked as verified.`)
      }"""

new_action_stage2 = """      } else if (actionType === 'complete_stage2') {
        await apiPost(`/school/admissions/${activeApp.application_id}/stage2-review`, {
          decision: 'detailed_review_completed',
          review_notes: actionNotes.trim() || 'All Stage 2 documents and academic records verified.'
        })
        setSuccess(`Stage 2 review completed for ${activeApp.application_id}. Application marked as verified.`)
      } else if (actionType === 'confirm_enrolment') {
        if (!selectedSectionId) {
          throw new Error('Please select an active section to complete student enrolment.')
        }
        const enrRes = await apiPost(`/school/admissions/${activeApp.application_id}/final-admission-confirm`, {
          section_id: selectedSectionId,
          notes: actionNotes.trim() || 'Final admission confirmed and student enrolled in official ledger.'
        })
        setSuccess(`🎉 Student Enrolled! Permanent Student ID: ${enrRes.permanent_student_id} (Std ${enrRes.standard}-${enrRes.section})`)
      }"""

text = text.replace(old_action_stage2, new_action_stage2)

# 4. Add Final Admission Confirmation Button to Action Toolbar
old_btn = """                  <button
                    onClick={() => { setActionType('complete_stage2'); setActionError(null); }}
                    style={{
                      background: actionType === 'complete_stage2' ? '#0E7090' : '#ECFEFF',
                      color: actionType === 'complete_stage2' ? '#ffffff' : '#0E7090',
                      border: '1px solid #A5F3FC',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    📋 Complete Stage 2 Review
                  </button>"""

new_btn = """                  <button
                    onClick={() => { setActionType('complete_stage2'); setActionError(null); }}
                    style={{
                      background: actionType === 'complete_stage2' ? '#0E7090' : '#ECFEFF',
                      color: actionType === 'complete_stage2' ? '#ffffff' : '#0E7090',
                      border: '1px solid #A5F3FC',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    📋 Complete Stage 2 Review
                  </button>

                  <button
                    onClick={() => { setActionType('confirm_enrolment'); setActionError(null); }}
                    style={{
                      background: actionType === 'confirm_enrolment' ? '#701A75' : '#FDF4FF',
                      color: actionType === 'confirm_enrolment' ? '#ffffff' : '#701A75',
                      border: '1px solid #F5D0FE',
                      padding: '0.5rem 1rem',
                      borderRadius: '6px',
                      fontWeight: 700,
                      fontSize: '0.85rem',
                      cursor: 'pointer'
                    }}
                  >
                    🎓 Final Admission Confirmation & Enrolment
                  </button>"""

text = text.replace(old_btn, new_btn)

# 5. Add Enrolment Confirmation Panel into modal
enrolment_panel = """              {/* PHASE 6 FINAL ADMISSION & ENROLMENT ACTION PANEL */}
              {actionType === 'confirm_enrolment' && (
                <div style={{ background: '#FDF4FF', border: '1px solid #F5D0FE', borderRadius: '8px', padding: '1.25rem', marginBottom: '1rem' }}>
                  <h4 style={{ margin: '0 0 0.5rem 0', color: '#701A75', fontSize: '1rem', fontWeight: 800 }}>
                    🎓 Phase 6: Official Admission Confirmation & Student Enrolment
                  </h4>
                  <p style={{ margin: '0 0 1rem 0', fontSize: '0.85rem', color: '#86198F' }}>
                    Confirming admission generates a globally unique Permanent Student ID, creates official records in <code>students</code> and <code>enrollments</code>, and atomically updates section seat capacity.
                  </p>

                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 700, color: '#701A75', marginBottom: '0.35rem' }}>
                    Select Program Section Allotment *
                  </label>
                  {loadingSections ? (
                    <p style={{ fontSize: '0.85rem', color: '#64748B' }}>Loading section seat capacities...</p>
                  ) : availableSections.length === 0 ? (
                    <p style={{ fontSize: '0.85rem', color: '#B42318' }}>No active sections found for this standard/program.</p>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem', marginBottom: '1rem' }}>
                      {availableSections.map((sec) => (
                        <div
                          key={sec.section_id}
                          onClick={() => !sec.is_full && setSelectedSectionId(sec.section_id)}
                          style={{
                            border: `2px solid ${selectedSectionId === sec.section_id ? '#701A75' : '#E2E8F0'}`,
                            borderRadius: '8px',
                            padding: '0.75rem',
                            background: selectedSectionId === sec.section_id ? '#FAF5FF' : sec.is_full ? '#F1F5F9' : '#ffffff',
                            cursor: sec.is_full ? 'not-allowed' : 'pointer',
                            opacity: sec.is_full ? 0.6 : 1
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                            <strong style={{ fontSize: '0.95rem', color: '#102B46' }}>
                              Section {sec.section_name} (Std/Year {sec.term_or_year})
                            </strong>
                            {selectedSectionId === sec.section_id && <span style={{ color: '#701A75', fontWeight: 700 }}>✓ Selected</span>}
                          </div>
                          <div style={{ fontSize: '0.8rem', color: '#475569' }}>
                            Capacity: <strong>{sec.capacity}</strong> • Enrolled: <strong>{sec.current_strength}</strong>
                          </div>
                          <div style={{ fontSize: '0.8rem', marginTop: '0.25rem', fontWeight: 600, color: sec.is_full ? '#B42318' : '#027A48' }}>
                            {sec.is_full ? '❌ Full Capacity' : `✓ ${sec.available_seats} Seats Available`}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: '#701A75', marginBottom: '0.35rem' }}>
                    Staff Enrolment Notes / Allotment Order
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Merit quota seat allotment. All statutory admission criteria confirmed."
                    value={actionNotes}
                    onChange={(e) => setActionNotes(e.target.value)}
                    style={{ width: '100%', padding: '0.5rem 0.75rem', borderRadius: '6px', border: '1px solid #F5D0FE', fontSize: '0.85rem', marginBottom: '1rem' }}
                  />

                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    <button
                      onClick={handleExecuteAction}
                      disabled={actionSubmitting || !selectedSectionId}
                      style={{
                        background: '#701A75',
                        color: '#ffffff',
                        border: 'none',
                        padding: '0.6rem 1.5rem',
                        borderRadius: '6px',
                        fontWeight: 700,
                        fontSize: '0.9rem',
                        cursor: actionSubmitting || !selectedSectionId ? 'not-allowed' : 'pointer'
                      }}
                    >
                      {actionSubmitting ? 'Enrolling Student...' : 'Confirm Admission & Enrol Student ✓'}
                    </button>
                    <button
                      onClick={() => setActionType('none')}
                      style={{ background: 'transparent', border: 'none', color: '#64748B', cursor: 'pointer', fontSize: '0.85rem' }}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}"""

# insert enrolment_panel right after complete_stage2 panel
pos_c2 = text.find("{actionType === 'complete_stage2' && (")
pos_end_c2 = text.find("</div>\n              )}", pos_c2) + len("</div>\n              )}")
text = text[:pos_end_c2] + "\n\n" + enrolment_panel + text[pos_end_c2:]

# 6. Add Enrolled Badge Box in Inspection modal header if enrolled
enrolled_info_banner = """              {/* Enrolled Status Banner */}
              {(activeApp.status === 'enrolled' || activeApp.status === 'final_admission_confirmed') && (
                <div style={{ background: '#FDF4FF', border: '1px solid #F5D0FE', borderRadius: '10px', padding: '1rem 1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.75rem' }}>
                  <div>
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#701A75', fontWeight: 800 }}>
                      Official Academic Ledger Record
                    </span>
                    <h4 style={{ margin: '0.2rem 0', color: '#4A044E', fontSize: '1.1rem', fontWeight: 800 }}>
                      🎓 Student Officially Enrolled
                    </h4>
                    <div style={{ fontSize: '0.85rem', color: '#701A75' }}>
                      Permanent Student ID: <code style={{ background: '#FAF5FF', padding: '0.15rem 0.4rem', borderRadius: '4px', border: '1px solid #F5D0FE', fontWeight: 700 }}>{activeApp.enrolled_student_id || 'Active'}</code>
                    </div>
                  </div>
                  <span style={{ background: '#701A75', color: '#ffffff', padding: '0.35rem 0.75rem', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700 }}>
                    Active Enrolment
                  </span>
                </div>
              )}"""

target_modal_body = "            <div style={{ padding: '1.75rem' }}>"
text = text.replace(target_modal_body, target_modal_body + "\n" + enrolled_info_banner)

with open(desk_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("AdmissionDeskTab.jsx upgraded for Phase 6 Final Admission Confirmation.")
