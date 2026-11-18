p = 'C:/Users/callm/nagriksetu/backend/main.py'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

target = """        data = dict(row)
        hist = conn.execute("""

repl = """        data = dict(row)
        data['id'] = data['application_id']
        data['application_reference'] = data['application_id']
        data['student_name'] = data.get('applicant_name')
        data['standard'] = data.get('requested_standard')
        hist = conn.execute("""

target_crlf = target.replace('\n', '\r\n')
repl_crlf = repl.replace('\n', '\r\n')

if target_crlf in text:
    text = text.replace(target_crlf, repl_crlf, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESS CRLF')
elif target in text:
    text = text.replace(target, repl, 1)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print('SUCCESS LF')
else:
    print('NOT FOUND')
