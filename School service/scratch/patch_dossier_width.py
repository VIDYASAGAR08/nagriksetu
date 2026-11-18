p = r'C:\Users\callm\nagriksetu\frontend\src\pages\admin\InstitutionAdminDashboard.jsx'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("maxWidth: '850px',", "maxWidth: '1020px',", 1)
text = text.replace("width: '24%'", "width: '22%'", 1)
text = text.replace("width: '22%'", "width: '20%'", 1)
text = text.replace("width: '14%'", "width: '13%'", 1)
text = text.replace("width: '40%'", "width: '45%'", 1)

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print('SUCCESS: updated dossier width to 1020px')
