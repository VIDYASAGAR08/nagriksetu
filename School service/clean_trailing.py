with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Strip any trailing ''' or whitespace
text = text.rstrip()
if text.endswith("'''"):
    text = text[:-3].rstrip()

with open(r'C:\Users\callm\nagriksetu\frontend\src\components\admin\InstitutionParentRequestsDesk.jsx', 'w', encoding='utf-8') as f:
    f.write(text + "\n")

print("Stripped trailing quotes.")
