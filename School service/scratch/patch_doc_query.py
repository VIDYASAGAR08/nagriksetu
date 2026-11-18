path = r'C:\Users\callm\nagriksetu\backend\main.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

target = """                SELECT document_id, document_type, file_name, mime_type, file_size, verification_status, uploaded_at
                FROM student_documents
                WHERE permanent_student_id = ?
                ORDER BY uploaded_at DESC"""

replacement = """                SELECT document_id, document_type, file_name, verification_status, created_at AS uploaded_at
                FROM student_documents
                WHERE permanent_student_id = ?
                ORDER BY created_at DESC"""

if target in text:
    text = text.replace(target, replacement)
    print("Patched document query!")
elif target.replace('\n', '\r\n') in text:
    text = text.replace(target.replace('\n', '\r\n'), replacement.replace('\n', '\r\n'))
    print("Patched document query CRLF!")
else:
    print("Target not found")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
