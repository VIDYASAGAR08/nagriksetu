desk_path = r"C:\Users\callm\nagriksetu\frontend\src\components\admissions\AdmissionDeskTab.jsx"
with open(desk_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

# 1. Add state for OCR results
old_states = "  const [selectedSectionId, setSelectedSectionId] = useState('')"
new_states = """  const [selectedSectionId, setSelectedSectionId] = useState('')
  const [ocrResultsMap, setOcrResultsMap] = useState({})
  const [analyzingDocId, setAnalyzingDocId] = useState(null)"""

text = text.replace(old_states, new_states)

# 2. Add OCR analysis handler
ocr_handler = """  // Run Real IDP / OCR Analysis
  const handleRunOcr = async (docId) => {
    if (!activeApp) return
    try {
      setAnalyzingDocId(docId)
      const res = await apiPost(`/school/admissions/${activeApp.application_id}/documents/${docId}/ocr-analyze`, {})
      setOcrResultsMap(prev => ({ ...prev, [docId]: res }))
      setSuccess(`OCR Intelligence Analysis complete: ${res.ocr_engine} (${res.confidence_percentage}% confidence).`)
    } catch (err) {
      setActionError(err.message || 'OCR extraction failed.')
    } finally {
      setAnalyzingDocId(null)
    }
  }

  // Handle Staff Actions"""

text = text.replace("  // Handle Staff Actions", ocr_handler)

# 3. Add OCR Analysis Button and Intelligence Drawer inside each document card in AdmissionDeskTab
target_doc_actions = """                          <button
                            type="button"
                            disabled={verifyingDocId === doc.document_id}
                            onClick={() => handleVerifyDocument(doc.document_id, 'rejected')}
                            style={{ background: '#B42318', color: '#ffffff', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
                          >
                            ✕ Reject
                          </button>"""

replacement_doc_actions = """                          <button
                            type="button"
                            disabled={verifyingDocId === doc.document_id}
                            onClick={() => handleVerifyDocument(doc.document_id, 'rejected')}
                            style={{ background: '#B42318', color: '#ffffff', border: 'none', padding: '0.3rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, cursor: 'pointer' }}
                          >
                            ✕ Reject
                          </button>
                          <button
                            type="button"
                            disabled={analyzingDocId === doc.document_id}
                            onClick={() => handleRunOcr(doc.document_id)}
                            style={{ background: '#0E7090', color: '#ffffff', border: 'none', padding: '0.3rem 0.75rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 700, cursor: 'pointer' }}
                          >
                            {analyzingDocId === doc.document_id ? 'Analyzing...' : '🔍 Run OCR Intelligence'}
                          </button>"""

text = text.replace(target_doc_actions, replacement_doc_actions)

# 4. Insert OCR Intelligence Result Card below document notes
target_doc_notes = """                        {doc.verification_notes && (
                          <div style={{ fontSize: '0.78rem', color: '#475569', background: '#ffffff', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid #E2E8F0', marginBottom: '0.5rem' }}>
                            <strong>Staff Note:</strong> {doc.verification_notes}
                          </div>
                        )}"""

replacement_doc_notes_with_ocr = """                        {doc.verification_notes && (
                          <div style={{ fontSize: '0.78rem', color: '#475569', background: '#ffffff', padding: '0.4rem 0.6rem', borderRadius: '4px', border: '1px solid #E2E8F0', marginBottom: '0.5rem' }}>
                            <strong>Staff Note:</strong> {doc.verification_notes}
                          </div>
                        )}

                        {/* OCR Intelligence Card */}
                        {ocrResultsMap[doc.document_id] && (
                          <div style={{ background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: '6px', padding: '0.75rem', marginBottom: '0.5rem', fontSize: '0.8rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem', borderBottom: '1px solid #DCFCE7', paddingBottom: '0.25rem' }}>
                              <span style={{ fontWeight: 700, color: '#166534', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                                🤖 Real IDP Extraction: {ocrResultsMap[doc.document_id].ocr_engine}
                              </span>
                              <span style={{ background: '#DCFCE7', color: '#15803D', fontWeight: 800, padding: '0.1rem 0.4rem', borderRadius: '4px', fontSize: '0.72rem' }}>
                                Confidence: {ocrResultsMap[doc.document_id].confidence_percentage}%
                              </span>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.4rem', marginBottom: '0.4rem', color: '#14532D' }}>
                              {ocrResultsMap[doc.document_id].extracted_entities?.candidate_name && (
                                <div>Name: <strong>{ocrResultsMap[doc.document_id].extracted_entities.candidate_name}</strong></div>
                              )}
                              {ocrResultsMap[doc.document_id].extracted_entities?.date_of_birth && (
                                <div>DOB: <strong>{ocrResultsMap[doc.document_id].extracted_entities.date_of_birth}</strong></div>
                              )}
                              {ocrResultsMap[doc.document_id].extracted_entities?.registration_number && (
                                <div>Reg/TC No: <strong>{ocrResultsMap[doc.document_id].extracted_entities.registration_number}</strong></div>
                              )}
                              {ocrResultsMap[doc.document_id].extracted_entities?.issuing_authority && (
                                <div style={{ gridColumn: 'span 2' }}>Authority: <strong>{ocrResultsMap[doc.document_id].extracted_entities.issuing_authority}</strong></div>
                              )}
                            </div>

                            {ocrResultsMap[doc.document_id].discrepancy_notes && (
                              <div style={{ fontSize: '0.75rem', color: ocrResultsMap[doc.document_id].match_status === 'discrepancy_detected' ? '#B91C1C' : '#166534', background: '#ffffff', padding: '0.25rem 0.5rem', borderRadius: '4px', border: '1px solid #DCFCE7' }}>
                                <strong>Comparison Audit:</strong> {ocrResultsMap[doc.document_id].discrepancy_notes}
                              </div>
                            )}
                          </div>
                        )}"""

text = text.replace(target_doc_notes, replacement_doc_notes_with_ocr)

with open(desk_path, 'w', encoding='utf-8') as f:
    f.write(text)

print("AdmissionDeskTab.jsx successfully upgraded with Phase 8 OCR Intelligence.")
