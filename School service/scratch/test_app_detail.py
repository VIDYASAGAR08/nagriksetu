import requests

login_res = requests.post('http://localhost:8001/auth/login', data={'username': 'rao@edu.in', 'password': 'Rao@1234'})
token = login_res.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test application detail
detail_res = requests.get('http://localhost:8001/school/admissions/applications/APP-2026-SCH019-30E92E', headers=headers)
print('Detail status:', detail_res.status_code)
if detail_res.status_code == 200:
    d = detail_res.json()
    print('Applicant name:', d.get('applicant_name'))
    print('Parent name:', d.get('parent_name'), '| Phone:', d.get('parent_phone'))
    print('Status:', d.get('status'))
    print('Status history count:', len(d.get('status_history', [])))

# Test application history
hist_res = requests.get('http://localhost:8001/school/admissions/APP-2026-SCH019-30E92E/history', headers=headers)
print('History status:', hist_res.status_code)
if hist_res.status_code == 200:
    print('History entries:', len(hist_res.json()))
