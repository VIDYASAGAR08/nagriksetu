import os

print("--- CHECKING EMAIL / SMS SERVICES ---")
for fn in ['email_service.py', 'sms_service.py', '.env']:
    path = os.path.join(r'C:\Users\callm\nagriksetu\backend', fn)
    if os.path.exists(path):
        print(f"\n=== {fn} ===")
        with open(path, 'r', encoding='utf-8') as f:
            print(f.read()[:1000])
