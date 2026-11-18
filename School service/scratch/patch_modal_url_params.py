p = r'C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

target = """  // Auto-open staff modals if modal or staff_id provided in URL"""

addition = """  // Auto-open document action modals if provided in URL (preview, accept, reject)
  useEffect(() => {
    if (selectedApp && selectedApp.documents && selectedApp.documents.length > 0) {
      const prevId = searchParams.get('preview_doc_id')
      if (prevId && !previewDoc) {
        const d = selectedApp.documents.find(doc => doc.document_id === prevId) || selectedApp.documents[0]
        if (d) { setPreviewZoom(100); setPreviewDoc(d); }
      }
      const rejId = searchParams.get('reject_doc_id')
      if (rejId && !confirmRejectDoc) {
        const d = selectedApp.documents.find(doc => doc.document_id === rejId) || selectedApp.documents[0]
        if (d) setConfirmRejectDoc({ doc: d, reason: 'Official seal missing and marks statement incomplete.' })
      }
      const accId = searchParams.get('accept_doc_id')
      if (accId && !confirmAcceptDoc) {
        const d = selectedApp.documents.find(doc => doc.document_id === accId) || selectedApp.documents[0]
        if (d) {
          setAcceptDocNotes('Document verified and found authentic by institution administrator.')
          setConfirmAcceptDoc(d)
        }
      }
    }
  }, [selectedApp, searchParams])

  // Auto-open staff modals if modal or staff_id provided in URL"""

assert target in text, "target not found"
text = text.replace(target, addition, 1)

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)

print("SUCCESS: added URL params for preview, accept, and reject modals")
