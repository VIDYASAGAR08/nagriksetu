import sys

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

for term in ['@app.get("/school/linking-requests")', '@app.get("/institution/{institution_id}/parent-requests")']:
    m = content.find(term)
    if m != -1:
        print(f"=== {term} ===")
        print(content[m:m+1500])

print("\n--- EMAIL / SMS CONFIGURATION ---")
for kw in ['EMAIL_PROVIDER', 'SMS_PROVIDER', 'OTP_PROVIDER', 'send_email', 'send_sms', 'send_otp']:
    m = content.find(kw)
    if m != -1:
        print(f"Found keyword '{kw}':")
        print(content[m-50:m+250])
