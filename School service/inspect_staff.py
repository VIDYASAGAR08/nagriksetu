with open(r'C:\Users\callm\nagriksetu\frontend\src\pages\staff\StaffDashboard.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

print("--- StaffDashboard.jsx ---")
for line in text.splitlines():
    if any(k in line for k in ['linking-requests', 'linking_requests', 'Linking', 'linking', 'activeTab']):
        print(' ', line[:120])
