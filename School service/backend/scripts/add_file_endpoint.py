import os

main_py_path = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add FileResponse import if not present
if 'from fastapi.responses import FileResponse' not in content:
    content = 'from fastapi.responses import FileResponse\n' + content

# 2. Add document file route right after get_stage2_documents
file_route = '''

@app.get("/admissions/applications/{application_id}/documents/{document_id}/file")
def get_admission_document_file(
    application_id: str,
    document_id: str,
    current_user: Optional[dict] = Depends(get_optional_current_user),
):
    """
    Retrieves the raw document file for viewing/download.
    """
    conn = get_connection()
    try:
        doc = conn.execute(
            "SELECT file_path, file_name, mime_type FROM admission_documents WHERE document_id = ? AND application_id = ?",
            (document_id, application_id)
        ).fetchone()
        if not doc:
            raise HTTPException(404, "Document not found.")
        fpath = doc["file_path"]
        if not os.path.exists(fpath):
            local_fallback = os.path.join("/app", "data", "uploads", "admissions", application_id, os.path.basename(fpath))
            if os.path.exists(local_fallback):
                fpath = local_fallback
            else:
                host_fallback = os.path.join("backend", "data", "uploads", "admissions", application_id, os.path.basename(fpath))
                if os.path.exists(host_fallback):
                    fpath = host_fallback
                else:
                    raise HTTPException(404, "Document file not found on disk.")
        return FileResponse(fpath, media_type=doc["mime_type"], filename=doc["file_name"])
    finally:
        conn.close()
'''

if '/admissions/applications/{application_id}/documents/{document_id}/file' not in content:
    pos = content.find('def get_stage2_documents(')
    if pos != -1:
        end_pos = content.find('conn.close()', pos)
        if end_pos != -1:
            line_end = content.find('\n', end_pos) + 1
            content = content[:line_end] + file_route + content[line_end:]
            with open(main_py_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print('Successfully injected get_admission_document_file route.')
        else:
            print('Could not find conn.close() in get_stage2_documents')
    else:
        print('Could not find def get_stage2_documents(')
else:
    print('Route already exists.')
