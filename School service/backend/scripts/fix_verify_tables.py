path = r'C:\Users\callm\nagriksetu\backend\scripts\verify_restructured_directory.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

c = c.replace('SELECT count(*) FROM student_enrolments', 'SELECT count(*) FROM enrollments')
c = c.replace('SELECT count(*) FROM academic_programmes', 'SELECT count(*) FROM academic_programs')
c = c.replace('SELECT count(*) FROM programme_sections', 'SELECT count(*) FROM program_sections')

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Updated table names in verify_restructured_directory.py')
