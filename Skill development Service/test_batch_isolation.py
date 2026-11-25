import urllib.request, json

def login(email, pwd):
    payload = json.dumps({'email': email, 'password': pwd}).encode('utf-8')
    req = urllib.request.Request('http://127.0.0.1:8003/api/auth/login', data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())['access_token']

shv_token = login('centre.shivamogga@nagriksetu.local', 'ShivamoggaMal#2026')
blr_token = login('centre.bengaluru@nagriksetu.local', 'BengaluruHub#2026')

# Check Shivamogga batches
req = urllib.request.Request('http://127.0.0.1:8003/api/centre-admin/batches', headers={'Authorization': f'Bearer {shv_token}'})
with urllib.request.urlopen(req) as resp:
    shv_batches = json.loads(resp.read().decode())
    print(f"Shivamogga batches count: {len(shv_batches)}")
    for b in shv_batches:
        print(f" - ID: {b['id']} | Code: {b['code']} | Prog: {b['program_id']} | Name: {b['batch_name']} | Mode: {b['mode']} | Available: {b['available_seats']}/{b['total_seats']}")

# Check Bengaluru batches
req = urllib.request.Request('http://127.0.0.1:8003/api/centre-admin/batches', headers={'Authorization': f'Bearer {blr_token}'})
with urllib.request.urlopen(req) as resp:
    blr_batches = json.loads(resp.read().decode())
    print(f"Bengaluru batches count: {len(blr_batches)}")
    shv_batch_ids = {b['id'] for b in shv_batches}
    blr_batch_ids = {b['id'] for b in blr_batches}
    overlap = shv_batch_ids.intersection(blr_batch_ids)
    print(f"Batch overlap between Shivamogga and Bengaluru: {overlap}")
