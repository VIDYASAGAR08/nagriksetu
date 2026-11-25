import json
import urllib.request
import hashlib
from app.main import SessionLocal, OTPVerificationSession, Enrollment, EnrollmentStatusHistory, Account

BASE_URL = 'http://127.0.0.1:8000/api'
results = {}

def api_post(endpoint, data, token=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_get(endpoint, token=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method='GET')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

def api_patch(endpoint, data, token=None):
    url = f"{BASE_URL}{endpoint}"
    payload = json.dumps(data).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    req = urllib.request.Request(url, data=payload, headers=headers, method='PATCH')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, body

# 1. Send OTP to citizen email for LOGIN
status, res_send = api_post('/otp/send', {
    'destination': 'mahesh@example.com',
    'purpose': 'LOGIN',
    'channel': 'EMAIL',
    'email': 'mahesh@example.com'
})
print('1. Send OTP response:', status, res_send)
results['1_send_otp_status'] = status
results['1_demo_otp_exposed'] = 'demo_otp' in res_send and res_send.get('demo_otp') is not None
otp_ref = res_send.get('reference')
results['1_otp_reference'] = otp_ref

# Check DB for generated OTP session using fresh session
db = SessionLocal()
otp_row = db.query(OTPVerificationSession).filter_by(reference=otp_ref).first()
print('OTP session in DB: ref=', otp_row.reference, 'email=', otp_row.phone, 'hash=', otp_row.hashed_code)
results['1_otp_stored_in_db'] = bool(otp_row and otp_row.hashed_code)

# 2. Test Invalid OTP verification
bad_status, res_bad = api_post('/otp/verify', {
    'reference': otp_ref,
    'code': '000000'
})
print('2. Bad OTP response:', bad_status, res_bad)
results['2_bad_otp_rejected'] = (bad_status == 400)

# 3. Find the actual 6-digit code by matching SHA-256
correct_code = None
for i in range(1000000):
    code_str = f"{i:06d}"
    if hashlib.sha256(code_str.encode('utf-8')).hexdigest() == otp_row.hashed_code:
        correct_code = code_str
        break

print('Found correct OTP code from DB hash for test:', correct_code)
results['3_otp_is_6_digits'] = bool(correct_code and len(correct_code) == 6)

# 3b. Verify with correct code
good_status, res_good = api_post('/otp/verify', {
    'reference': otp_ref,
    'code': correct_code
})
print('3b. Good OTP response:', good_status, res_good)
results['3b_good_otp_verified'] = (good_status == 200 and res_good.get('success') is True)

# 4. Citizen Login using the verified OTP session
otp_login_status, res_otp_login = api_post('/auth/login', {
    'email': 'mahesh@example.com',
    'otp_reference': otp_ref
})
print('4. OTP Login response:', otp_login_status, res_otp_login.get('token_type'), res_otp_login.get('user', {}).get('full_name'))
results['4_otp_login_success'] = (otp_login_status == 200 and 'access_token' in res_otp_login)
citizen_token = res_otp_login.get('access_token')

# 5. Verify OTP reference is now consumed (cannot reuse for another login)
reuse_login_status, res_reuse_login = api_post('/auth/login', {
    'email': 'mahesh@example.com',
    'otp_reference': otp_ref
})
print('5. Reuse OTP Login response:', reuse_login_status)
results['5_reuse_otp_rejected'] = (reuse_login_status == 400)

# Clean up any existing enrollment for program 1 so we can test fresh submission
old_enrols = db.query(Enrollment).filter_by(citizen_email='mahesh@example.com', program_id=1).all()
for oe in old_enrols:
    db.query(EnrollmentStatusHistory).filter_by(enrollment_id=oe.id).delete()
    db.delete(oe)
db.commit()

# 6. Citizen Application Submission WITHOUT mobile OTP (otp_reference=None)
enrol_payload = {
    'program_id': 1,
    'selected_mode': 'Online',
    'applicant_statement': 'I want to build python applications.',
    'application_details': {
        'section_a_personal': {
            'full_name': 'Mahesh Kumar',
            'email': 'mahesh@example.com',
            'phone': '9876543210'
        },
        'section_b_address': {
            'residential_address': 'Koramangala',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560034'
        },
        'section_c_education': {
            'highest_qualification': 'BE_BTECH'
        },
        'section_h_declaration': {
            'agreed': True
        }
    },
    'otp_reference': None
}
enrol_status, res_enrol = api_post('/enrollments', enrol_payload, token=citizen_token)
print('6. Enrolment submission response:', enrol_status, res_enrol)
results['6_enrolment_submission_status'] = enrol_status
enrol_id = res_enrol.get('id') if isinstance(res_enrol, dict) else None
enrol_number = res_enrol.get('application_id') if isinstance(res_enrol, dict) else None
results['6_enrolment_number_generated'] = bool(enrol_number)

# 7. Check Centre 1 Dashboard - Application routed to Centre 1
c1_status, res_c1_login = api_post('/auth/login', {
    'email': 'centre.bengaluru@nagriksetu.local',
    'password': 'CentreAdmin@2026!'
})
centre1_token = res_c1_login.get('access_token')
_, res_centre_enrols = api_get('/centre-admin/enrollments', token=centre1_token)
centre1_app_ids = [e['id'] for e in res_centre_enrols] if isinstance(res_centre_enrols, list) else [e['id'] for e in res_centre_enrols.get('items', [])]
print('7. Centre 1 enrollments count:', len(centre1_app_ids), 'Contains new enrol:', enrol_id in centre1_app_ids)
results['7_routed_to_target_centre'] = enrol_id in centre1_app_ids

# 8. Check Centre 2 Dashboard - Isolation check (must NOT see Centre 1 application)
c2_status, res_c2_login = api_post('/auth/login', {
    'email': 'centre.admin.mysuru@nagriksetu.local',
    'password': 'CentreAdmin@2026!'
})
centre2_token = res_c2_login.get('access_token')
_, res_c2_enrols = api_get('/centre-admin/enrollments', token=centre2_token)
centre2_app_ids = [e['id'] for e in res_c2_enrols] if isinstance(res_c2_enrols, list) else [e['id'] for e in res_c2_enrols.get('items', [])]
print('8. Centre 2 isolation check:', enrol_id not in centre2_app_ids)
results['8_isolated_from_other_centres'] = enrol_id not in centre2_app_ids

# 9. Centre 1 reviews and approves application
review_status, res_review = api_patch(f'/centre-admin/enrollments/{enrol_id}/review', {
    'action': 'APPROVE',
    'remarks': 'Applicant BE/BTech profile verified. Admitted to Python Developer batch.'
}, token=centre1_token)
print('9. Centre review response:', review_status, res_review)
results['9_centre_review_status'] = res_review.get('status') if isinstance(res_review, dict) else review_status

# 10. Platform Admin read-only monitoring check
adm_status, res_admin_login = api_post('/auth/login', {
    'email': 'skill.admin@nagriksetu.local',
    'password': 'SkillAdmin@2026!'
})
admin_token = res_admin_login.get('access_token')
_, res_admin_view = api_get('/admin/enrollments', token=admin_token)
admin_items = res_admin_view if isinstance(res_admin_view, list) else res_admin_view.get('items', [])
admin_found = any(item.get('id') == enrol_id and item.get('status') == 'APPROVED' for item in admin_items)
print('10. Admin view oversight:', admin_found)
results['10_admin_oversight_verified'] = admin_found

# Admin write operation must be rejected with 403 Forbidden
admin_write_status, res_admin_write = api_patch(f'/admin/enrollments/{enrol_id}/review', {
    'status': 'REJECTED',
    'remarks': 'Admin attempted rejection'
}, token=admin_token)
print('10b. Admin write locked (403):', admin_write_status)
results['10b_admin_write_locked'] = (admin_write_status == 403)

# 11. Citizen tracks status in My Applications
_, my_enrols = api_get('/enrollments/my', token=citizen_token)
my_items = my_enrols if isinstance(my_enrols, list) else my_enrols.get('items', [])
my_app = next((a for a in my_items if a.get('id') == enrol_id), None)
print('11. Citizen My Applications check:', my_app.get('status') if my_app else None)
results['11_citizen_tracks_approved_status'] = bool(my_app and my_app.get('status') == 'APPROVED')

print('\nFINAL TEST RESULTS SUMMARY:')
print(json.dumps(results, indent=2))
db.close()
