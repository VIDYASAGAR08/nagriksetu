import re

with open('C:/Users/callm/nagriksetu/frontend/src/pages/public/SchoolDetailsPage.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

tabs = re.findall(r"activeTab === '([^']+)'", text)
print('Tabs found in SchoolDetailsPage.jsx:', set(tabs))

# Check lines where tabs are rendered
for m in re.finditer(r"activeTab === '([^']+)'", text):
    start = max(0, m.start() - 50)
    end = min(len(text), m.end() + 100)
    print(f"Tab {m.group(1)} around: {text[start:end].strip()[:100]}...\n")
