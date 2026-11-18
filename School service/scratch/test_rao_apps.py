import time
import requests

login_res = requests.post('http://localhost:8001/auth/login', data={'username': 'rao@edu.in', 'password': 'Rao@1234'})
print('Login status:', login_res.status_code)
token = login_res.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

res = requests.get('http://localhost:8001/school/admissions/applications', headers=headers)
print('GET /school/admissions/applications status:', res.status_code)
if res.status_code == 200:
    data = res.json()
    print('Total applications returned:', data.get('total'))
    print('Applications count in list:', len(data.get('applications', [])))
    for app in data.get('applications', []):
        print(f"  - {app.get('application_id')}: {app.get('applicant_name')} | Std: {app.get('requested_standard')} | Status: {app.get('status')} | Alias id: {app.get('id')}")
else:
    print('Error:', res.text)
