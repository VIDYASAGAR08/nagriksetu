import requests
import time
import urllib.parse

BASE = 'http://127.0.0.1:8003/api'
time.sleep(1)

print("="*80)
print("NAGRIKSETU SKILL DEVELOPMENT - MAIN WORKFLOW 16-POINT END-TO-END VERIFICATION")
print("="*80)

# STEP 1: Citizen Authentication
print("\n[STEP 1] Citizen Authentication")
cit_res = requests.post(f'{BASE}/auth/login', json={'email': 'mahesh@example.com', 'password': 'Nagrik@2026'})
assert cit_res.status_code == 200, f"Citizen login failed: {cit_res.text}"
cit_tok = cit_res.json()['access_token']
cit_ref = cit_res.json().get('citizen_ref')
print(f"PASS: Logged in as Citizen ({cit_ref}) - Mahesh Kumar Sharma")

# STEP 2 & 3: Search for Python skills with preferred location & radius
print("\n[STEP 2 & 3] Search Python skills and discover relevant training centres with radius")
# Skill search query directly verified against /api/centres/search with location=Rajajinagar, radius_km=15, and skill=Python
search_res = requests.get(f'{BASE}/centres/search?location=Rajajinagar&radius_km=15&skill=Python')
assert search_res.status_code == 200, f"Centre search failed: {search_res.text}"
search_data = search_res.json()
centres_found = search_data.get('centres', [])
assert len(centres_found) > 0, "No centres found for Rajajinagar Python search"
print(f"PASS: Discovered {len(centres_found)} training centre(s) offering Python skills near Rajajinagar within 15 km.")

# STEP 4 & 5: Select ABC Training Centre (Centre 1: Bengaluru Central Skill Hub)
print("\n[STEP 4 & 5] Select Target Training Centre")
target_centre = next((c for c in centres_found if 'bengaluru' in c['name'].lower() or c.get('id') == 1 or 'CTR-0001' in str(c.get('code'))), centres_found[0])
target_centre_id = target_centre.get('id') or 1
print(f"Selected Target Centre: {target_centre['name']} (ID: {target_centre_id})")

# Verify matching programmes on the centre
matching_progs_on_centre = target_centre.get('matching_programmes', [])
assert len(matching_progs_on_centre) > 0, "No matching Python programmes annotated on target centre"
for mp in matching_progs_on_centre:
    assert 'python' in mp['title'].lower() or 'python' in mp.get('skill_name', '').lower(), f"Non-Python programme ({mp['title']}) returned in Python search!"
print(f"PASS: Training Centre verified offering genuine Python programme: '{matching_progs_on_centre[0]['title']}'")

# STEP 6: Open Centre Details and Select Python Programme
print("\n[STEP 6] Open Centre Details and strictly select genuine Python programme")
profile_res = requests.get(f'{BASE}/centres/{target_centre_id}/profile')
assert profile_res.status_code == 200
profile_data = profile_res.json()
python_progs = [p for p in profile_data['programs'] if 'python' in p['title'].lower() or 'python' in (p.get('skill_name') or '').lower()]
assert len(python_progs) > 0, "No Python programme offered by Centre 1"

# Check citizen's existing active enrollments to prevent duplicate active state
my_apps = requests.get(f'{BASE}/enrollments/my', headers={'Authorization': f'Bearer {cit_tok}'}).json()
my_app_prog_ids = {a['program_id'] for a in my_apps if a['status'] in ('PENDING', 'UNDER_REVIEW', 'APPROVED', 'ENROLLED', 'IN_PROGRESS')}

selected_prog = next((p for p in python_progs if p['id'] not in my_app_prog_ids), None)
assert selected_prog is not None, "Citizen already has active applications for all available Python programmes at this centre"

# STRICT INTEGRITY CHECK: Selected programme MUST be Python, NEVER C++ or Java
prog_id = selected_prog['id']
prog_title = selected_prog['title']
prog_skill = selected_prog.get('skill_name') or ''
assert 'python' in prog_title.lower() or 'python' in prog_skill.lower(), f"CRITICAL INTEGRITY FAILURE: Selected non-Python programme '{prog_title}'"
assert 'c++' not in prog_title.lower(), "CRITICAL FAILURE: C++ programme selected during Python search!"
assert 'java' not in prog_title.lower(), "CRITICAL FAILURE: Java programme selected during Python search!"
print(f"PASS: Strictly verified selected Programme ID {prog_id}: '{prog_title}' (Skill: {prog_skill}) offered by {profile_data['name']}")

# STEP 7: Request & Verify OTP, Complete and submit the application
print("\n[STEP 7] Complete and submit application with OTP verification")
for attempt in range(5):
    otp_send = requests.post(
        f'{BASE}/otp/send',
        json={'purpose': 'ENROLMENT', 'phone': '9876543210'},
        headers={'Authorization': f'Bearer {cit_tok}'}
    )
    if otp_send.status_code == 200:
        break
    time.sleep(10)

assert otp_send.status_code == 200, f"OTP send failed: {otp_send.text}"
otp_ref = otp_send.json().get('reference')
otp_code = otp_send.json().get('demo_otp')

otp_ver = requests.post(
    f'{BASE}/otp/verify',
    json={'reference': otp_ref, 'code': otp_code},
    headers={'Authorization': f'Bearer {cit_tok}'}
)
assert otp_ver.status_code == 200, f"OTP verify failed: {otp_ver.text}"

enr_payload = {
    'program_id': prog_id,
    'selected_mode': 'Hybrid',
    'applicant_statement': 'BTech graduate seeking Python and Cloud skill certification for employment.',
    'otp_reference': otp_ref,
    'application_details': {
        'full_name': 'Mahesh Kumar Sharma',
        'email': 'mahesh@example.com',
        'phone': '9876543210',
        'education_qualification': 'B.Tech in Computer Science',
        'employment_status': 'Unemployed Graduate'
    }
}
enr_res = requests.post(
    f'{BASE}/enrollments',
    json=enr_payload,
    headers={'Authorization': f'Bearer {cit_tok}'}
)
assert enr_res.status_code == 201, f"Application submission failed: {enr_res.text}"
enr_data = enr_res.json()
app_id = enr_data['id']
app_code = enr_data['application_id']
print(f"PASS: Submitted Application {app_code} (ID: {app_id}) for '{prog_title}'")

# STEP 8: Verify application is saved correctly in MySQL and citizen notification generated
print("\n[STEP 8] Verify persistence in MySQL & in-app notification")
cit_notifs = requests.get(f'{BASE}/notifications', headers={'Authorization': f'Bearer {cit_tok}'}).json()
recent_notif = next((n for n in cit_notifs.get('notifications', []) if app_code in n['message']), None)
assert recent_notif is not None, "Submission in-app notification was not received by citizen"
print(f"PASS: Citizen In-App Notification Verified: '{recent_notif['title']}' -> '{recent_notif['message']}'")

# STEP 9 & 10: Log in as Centre 1 Admin and verify new application appears in queue
print("\n[STEP 9 & 10] Centre 1 Admin Login & Application Discovery")
c1_login = requests.post(f'{BASE}/auth/login', json={'email': 'centre.bengaluru@nagriksetu.local', 'password': 'CentreAdmin@2026!'}).json()
c1_tok = c1_login['access_token']
c1_apps = requests.get(f'{BASE}/centre-admin/enrollments', headers={'Authorization': f'Bearer {c1_tok}', 'X-Centre-ID': '1'}).json()
target_app_in_c1 = next((a for a in c1_apps if a['id'] == app_id), None)
assert target_app_in_c1 is not None, f"Application {app_code} did not route to Centre 1 queue!"
assert target_app_in_c1['program_title'] == prog_title, f"Programme mismatch in Centre queue: {target_app_in_c1['program_title']}"
print(f"PASS: Centre 1 Admin received application {app_code} for '{target_app_in_c1['program_title']}' from {target_app_in_c1['citizen_name']}")

# STEP 11 & 12: Centre 1 Admin marks UNDER_REVIEW with remarks
print("\n[STEP 11 & 12] Centre 1 Admin sets status to UNDER_REVIEW with remarks")
rev1 = requests.patch(
    f'{BASE}/centre-admin/enrollments/{app_id}/review',
    json={
        'action': 'UNDER_REVIEW',
        'remarks': 'Academic credentials and BTech certificates currently under physical verification by admission desk.',
        'internal_notes': 'Applicant possesses valid 2024 degree certificate.'
    },
    headers={'Authorization': f'Bearer {c1_tok}', 'X-Centre-ID': '1'}
)
assert rev1.status_code == 200, f"Review action failed: {rev1.text}"
print(f"PASS: Centre 1 updated status to UNDER_REVIEW. Response: {rev1.json()['message']}")

# Verify citizen received update and notification
cit_notifs_after_rev1 = requests.get(f'{BASE}/notifications', headers={'Authorization': f'Bearer {cit_tok}'}).json()
under_review_notif = next((n for n in cit_notifs_after_rev1.get('notifications', []) if app_code in n['message'] and 'Under Review' in n['message']), None)
assert under_review_notif is not None, "Citizen did not receive UNDER_REVIEW status notification!"
print(f"PASS: Citizen received in-app update notification: '{under_review_notif['message']}'")

# STEP 13: Centre 1 Admin APPROVES the application
print("\n[STEP 13] Centre 1 Admin APPROVES the application")
rev2 = requests.patch(
    f'{BASE}/centre-admin/enrollments/{app_id}/review',
    json={
        'action': 'APPROVE',
        'remarks': 'Eligibility verified. Applicant successfully approved for Python programming training.',
        'internal_notes': 'Recommended for Morning batch.'
    },
    headers={'Authorization': f'Bearer {c1_tok}', 'X-Centre-ID': '1'}
)
assert rev2.status_code == 200
print(f"PASS: Centre 1 marked application APPROVED. Response: {rev2.json()['message']}")

# STEP 14: Cross-Centre Isolation Test (Mysuru Admin attempting to access Centre 1's application)
print("\n[STEP 14] Cross-Centre Data Isolation Enforcement")
c2_login = requests.post(f'{BASE}/auth/login', json={'email': 'centre.admin.mysuru@nagriksetu.local', 'password': 'CentreAdmin@2026!'}).json()
c2_tok = c2_login['access_token']
c2_apps = requests.get(f'{BASE}/centre-admin/enrollments', headers={'Authorization': f'Bearer {c2_tok}', 'X-Centre-ID': '2'}).json()
app_in_c2 = next((a for a in c2_apps if a['id'] == app_id), None)
assert app_in_c2 is None, "CRITICAL BREACH: Centre 1 application leaked into Centre 2 queue!"

# Unauthorized review attempt
unauth_rev = requests.patch(
    f'{BASE}/centre-admin/enrollments/{app_id}/review',
    json={'action': 'REJECT', 'remarks': 'Breach attempt by Centre 2'},
    headers={'Authorization': f'Bearer {c2_tok}', 'X-Centre-ID': '2'}
)
assert unauth_rev.status_code == 403, f"Expected 403 Forbidden, got {unauth_rev.status_code}"
print(f"PASS: Cross-Centre Isolation Verified: Centre 2 returned HTTP 403 Forbidden ({unauth_rev.json()['detail']})")

# STEP 15: Platform Admin Cross-Centre Oversight
print("\n[STEP 15] Platform Admin Cross-Centre Monitoring")
gov_login = requests.post(f'{BASE}/auth/login', json={'email': 'skill.admin@nagriksetu.local', 'password': 'SkillAdmin@2026!'}).json()
gov_tok = gov_login['access_token']
gov_apps = requests.get(f'{BASE}/admin/enrollments', headers={'Authorization': f'Bearer {gov_tok}'}).json()
gov_app = next((a for a in gov_apps if a['id'] == app_id), None)
assert gov_app is not None, "Platform Admin cannot view the application"
assert gov_app['centre_id'] == 1, f"Expected centre_id 1, got {gov_app['centre_id']}"
assert gov_app['status'] == 'APPROVED', f"Expected status APPROVED, got {gov_app['status']}"
assert 'python' in gov_app['program_title'].lower(), f"Expected Python programme title, got {gov_app['program_title']}"
print(f"PASS: Platform Admin cross-centre monitoring verified! Centre: {gov_app['centre_name']}, Programme: '{gov_app['program_title']}', Status: {gov_app['status']}")

# STEP 16: Verify Application Dashboard Counts
print("\n[STEP 16] Verify Real Database Counts on Platform Admin Dashboard")
gov_stats = requests.get(f'{BASE}/admin/dashboard', headers={'Authorization': f'Bearer {gov_tok}'}).json()
stats = gov_stats['stats']
print(f"PASS: Real Statistics -> Total Programmes: {stats['total_programs']}, Centres: {stats['total_centres']}, Applications: {stats['total_applications']}, Active Learners: {stats['active_learners']}")
assert stats['total_applications'] > 0

print("\n" + "="*80)
print(">>> ALL 16 MANDATORY MAIN WORKFLOW VERIFICATION POINTS PASSED 100%! <<<")
print("="*80)
