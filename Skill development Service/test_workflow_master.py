import requests
import time

BASE = 'http://127.0.0.1:8003/api'

print("--- 1. CITIZEN LOGIN ---")
res = requests.post(f'{BASE}/auth/login', json={'email': 'mahesh@example.com', 'password': 'Nagrik@2026'})
print('Citizen login status:', res.status_code)
cit_tok = res.json().get('access_token')

print("\n--- 2. GET CENTRE 2 PROGRAMMES ---")
res = requests.get(f'{BASE}/programmes?centre_id=2')
programs = res.json()
print('Centre 2 programs count:', len(programs))

# Find a program citizen hasn't applied for yet
my_existing = requests.get(f'{BASE}/enrollments/my', headers={'Authorization': f'Bearer {cit_tok}'}).json()
applied_prog_ids = {e['program_id'] for e in my_existing}
prog = next(p for p in programs if p['id'] not in applied_prog_ids)
prog_id = prog['id']
print('Selected program:', prog['title'], 'ID:', prog_id)

print("\n--- 3. REQUEST OTP FOR ENROLMENT ---")
for attempt in range(5):
    otp_send = requests.post(
        f'{BASE}/otp/send',
        json={'purpose': 'ENROLMENT', 'phone': '9876543210'},
        headers={'Authorization': f'Bearer {cit_tok}'}
    )
    if otp_send.status_code == 200:
        break
    print(f"Waiting on OTP cooldown: {otp_send.json().get('detail')}")
    time.sleep(15)

print('OTP send status:', otp_send.status_code, otp_send.json())
otp_ref = otp_send.json().get('reference')
otp_code = otp_send.json().get('demo_otp')

print("\n--- 4. VERIFY OTP ---")
otp_ver = requests.post(
    f'{BASE}/otp/verify',
    json={'reference': otp_ref, 'code': otp_code},
    headers={'Authorization': f'Bearer {cit_tok}'}
)
print('OTP verify status:', otp_ver.status_code, otp_ver.json())

print("\n--- 5. SUBMIT ENROLMENT APPLICATION ---")
enr_payload = {
    'program_id': prog_id,
    'applicant_statement': 'Looking to upskill in Mysuru.',
    'otp_reference': otp_ref,
    'application_details': {
        'full_name': 'Mahesh Kumar',
        'email': 'mahesh@example.com',
        'phone': '9876543210',
        'education_level': 'Graduate'
    }
}
enr_res = requests.post(
    f'{BASE}/enrollments',
    json=enr_payload,
    headers={'Authorization': f'Bearer {cit_tok}'}
)
print('Enrollment submit status:', enr_res.status_code, enr_res.json())
enr_id = enr_res.json().get('id')
print(f'Created Enrollment ID: {enr_id}')

print("\n--- 6. ADMIN LOGINS (MYSURU & BENGALURU) ---")
mys_res = requests.post(f'{BASE}/auth/login', json={'email': 'centre.admin.mysuru@nagriksetu.local', 'password': 'CentreAdmin@2026!'})
mys_tok = mys_res.json().get('access_token')

ben_res = requests.post(f'{BASE}/auth/login', json={'email': 'centre.bengaluru@nagriksetu.local', 'password': 'CentreAdmin@2026!'})
ben_tok = ben_res.json().get('access_token')

print("\n--- 7. CENTRE ISOLATION TEST ---")
bad_rev = requests.patch(
    f'{BASE}/centre-admin/enrollments/{enr_id}/review',
    json={'action': 'UNDER_REVIEW', 'remarks': 'Cross-centre breach attempt', 'internal_notes': 'Should fail'},
    headers={'Authorization': f'Bearer {ben_tok}', 'X-Centre-ID': '1'}
)
print('Bengaluru admin attempting review on Mysuru enrollment -> Status:', bad_rev.status_code, bad_rev.json())
assert bad_rev.status_code == 403, 'Cross-centre review must be forbidden (HTTP 403)!'

print("\n--- 8. MYSURU ADMIN REVIEW -> UNDER_REVIEW ---")
rev1 = requests.patch(
    f'{BASE}/centre-admin/enrollments/{enr_id}/review',
    json={'action': 'UNDER_REVIEW', 'remarks': 'Documents undergoing physical verification.', 'internal_notes': 'Applicant credentials verified.'},
    headers={'Authorization': f'Bearer {mys_tok}', 'X-Centre-ID': '2'}
)
print('Mysuru admin marked UNDER_REVIEW status:', rev1.status_code, rev1.json())
assert rev1.status_code == 200

print("\n--- 9. MYSURU ADMIN REVIEW -> APPROVE ---")
rev2 = requests.patch(
    f'{BASE}/centre-admin/enrollments/{enr_id}/review',
    json={'action': 'APPROVE', 'remarks': 'Application successfully approved. Awaiting batch allocation.', 'internal_notes': 'Eligible for immediate enrolment.'},
    headers={'Authorization': f'Bearer {mys_tok}', 'X-Centre-ID': '2'}
)
print('Mysuru admin marked APPROVE status:', rev2.status_code, rev2.json())
assert rev2.status_code == 200

print("\n--- 10. CITIZEN VERIFIES APPROVED (NO BATCH AUTO-ASSIGNED) ---")
my_apps = requests.get(f'{BASE}/enrollments/my', headers={'Authorization': f'Bearer {cit_tok}'}).json()
my_app = next((a for a in my_apps if a['id'] == enr_id), None)
print(f'Citizen App Status: {my_app["status"]}, Batch ID: {my_app.get("batch_id")}, Remarks: {my_app.get("admin_remarks")}')
assert my_app['status'] == 'APPROVED', 'Status should be APPROVED'
assert my_app.get('batch_id') is None, 'Batch ID must be None before explicit enrolment!'
# Confirm internal notes are NOT leaked to citizen
assert 'internal_notes' not in my_app or not my_app.get('internal_notes'), 'Confidential internal notes must NOT leak to citizen!'

print("\n--- 11. MYSURU ADMIN GETS PROGRAMME BATCHES ---")
batches = requests.get(f'{BASE}/centre-admin/batches', headers={'Authorization': f'Bearer {mys_tok}', 'X-Centre-ID': '2'}).json()
prog_batches = [b for b in batches if b['program_id'] == prog_id]
print(f'Available batches found for Program {prog_id}:', len(prog_batches))
assert len(prog_batches) > 0, f'Expected at least one batch for program {prog_id}'
target_batch = prog_batches[0]
batch_id = target_batch['id']
initial_available_seats = target_batch['available_seats']
print(f'Target Batch: ID {batch_id} ({target_batch["code"]}), Available Seats before: {initial_available_seats}')

print("\n--- 12. MYSURU ADMIN EXPLICITLY ENROLS APPLICANT INTO BATCH ---")
enrol_res = requests.post(
    f'{BASE}/centre-admin/enrollments/{enr_id}/enrol',
    json={'batch_id': batch_id, 'internal_notes': 'Assigned to Morning batch as per applicant schedule.'},
    headers={'Authorization': f'Bearer {mys_tok}', 'X-Centre-ID': '2'}
)
print('Enrolment API status:', enrol_res.status_code, enrol_res.json())
assert enrol_res.status_code == 200

print("\n--- 13. VERIFY BATCH SEAT CAPACITY DECREMENT ---")
batches_after = requests.get(f'{BASE}/centre-admin/batches', headers={'Authorization': f'Bearer {mys_tok}', 'X-Centre-ID': '2'}).json()
updated_batch = next(b for b in batches_after if b['id'] == batch_id)
print(f'Batch Available Seats after: {updated_batch["available_seats"]} (was {initial_available_seats})')
assert updated_batch['available_seats'] == initial_available_seats - 1, 'Seat count must decrement by exactly 1!'

print("\n--- 14. CITIZEN VERIFIES ENROLLED & BATCH DETAILS ---")
my_apps_after = requests.get(f'{BASE}/enrollments/my', headers={'Authorization': f'Bearer {cit_tok}'}).json()
my_app_after = next((a for a in my_apps_after if a['id'] == enr_id), None)
print(f'Citizen Final Status: {my_app_after["status"]}, Batch ID: {my_app_after.get("batch_id")}, Batch Details: {my_app_after.get("batch_details")}')
assert my_app_after['status'] == 'ENROLLED', 'Citizen status must now be ENROLLED'
assert my_app_after.get('batch_details') is not None, 'Assigned Batch details must be present'

print("\n--- 15. PLATFORM ADMIN CROSS-CENTRE OVERSIGHT ---")
gov_res = requests.post(f'{BASE}/auth/login', json={'email': 'skill.admin@nagriksetu.local', 'password': 'SkillAdmin@2026!'})
gov_tok = gov_res.json().get('access_token')
gov_apps = requests.get(f'{BASE}/admin/enrollments', headers={'Authorization': f'Bearer {gov_tok}'}).json()
gov_app = next((a for a in gov_apps if a['id'] == enr_id), None)
print('Platform Admin view -> Status:', gov_app['status'], 'Application ID:', gov_app['application_id'])
assert gov_app is not None, 'Platform Admin must see all enrolments across all centres'

print('\n' + '='*70)
print('>>> SUCCESS: ALL 15 END-TO-END MASTER WORKFLOW STEPS VERIFIED 100%! <<<')
print('='*70)
