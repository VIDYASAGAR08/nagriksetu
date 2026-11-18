import re
import os

main_file = r"C:\Users\callm\nagriksetu\backend\main.py"
auth_file = r"C:\Users\callm\nagriksetu\backend\auth.py"

with open(main_file, "r", encoding="utf-8") as f:
    main_code = f.read()

with open(auth_file, "r", encoding="utf-8") as f:
    auth_code = f.read()

print("=== 1. RATE LIMITING AUDIT ===")
rate_limit_hits = re.findall(r"(rate_limit|limiter|throttle|SlowAPIMiddleware|failed_attempts)", main_code, re.IGNORECASE)
print(f"Rate limiting keywords in main.py: {set(rate_limit_hits)}")

print("\n=== 2. CORS AUDIT ===")
cors_block = re.findall(r"CORSMiddleware[\s\S]*?\)", main_code)
for cb in cors_block:
    print(cb)

print("\n=== 3. SQL INJECTION (RAW F-STRINGS IN SQL EXECUTE) AUDIT ===")
# Look for execute(f"..." or execute(f'...'
fstring_sql = re.findall(r"\.execute\(\s*f[\"'][\s\S]*?[\"']", main_code)
print(f"Total f-string executes found: {len(fstring_sql)}")
for item in fstring_sql[:10]:
    print("  RAW SQL:", item[:100].replace("\n", " "))

print("\n=== 4. FILE UPLOADS & DOCUMENTS AUDIT ===")
upload_endpoints = re.findall(r"@app\.(?:post|put|get)\([\"'][^\"']*(?:upload|document|file)[^\"']*[\"'][\s\S]*?(?=def )def \w+\([^)]*\):", main_code)
print(f"Document/Upload endpoint signatures found: {len(upload_endpoints)}")
for ep in upload_endpoints:
    print(" ", ep.strip().replace("\n", " "))

print("\n=== 5. INVITATION & RESET TOKEN AUDIT ===")
token_queries = re.findall(r"SELECT[\s\S]*?FROM\s+(?:invitation_tokens|password_reset_tokens)[\s\S]*?;", main_code)
print(f"Token queries found: {len(token_queries)}")
for tq in token_queries:
    print(" ", tq.strip().replace("\n", " "))

print("\n=== 6. GUARDIAN / PARENT VERIFICATION AUDIT ===")
guardian_checks = re.findall(r"SELECT[\s\S]*?FROM\s+(?:guardians|student_guardians)[\s\S]*?;", main_code)
print(f"Guardian queries found: {len(guardian_checks)}")
for gq in guardian_checks[:5]:
    print(" ", gq.strip().replace("\n", " "))

print("\n=== 7. LOGGING OF PASSWORDS/TOKENS AUDIT ===")
print_logs = re.findall(r"(?:print|logger\.\w+)\([^\)]*(?:password|token|secret)[^\)]*\)", main_code, re.IGNORECASE)
print(f"Potential sensitive logs: {len(print_logs)}")
for pl in print_logs[:10]:
    print(" ", pl.strip())
