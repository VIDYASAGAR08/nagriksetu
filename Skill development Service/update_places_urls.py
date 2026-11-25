import sys

path = r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend\app\places_registry.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace generic / broken emptrg.karnataka.gov.in with official Kaushalkar Karnataka portal
content = content.replace(
    '"website": "https://emptrg.karnataka.gov.in"',
    '"website": "https://kaushalkar.karnataka.gov.in"'
)

# 2. Replace broken aptech URL
content = content.replace(
    '"website": "https://www.aptech-education.com"',
    '"website": "https://www.aptechlearning.com"'
)

# 3. Replace broken CITD Hyderabad URL
content = content.replace(
    '"website": "https://citdindia.org"',
    '"website": "https://www.citd.in"'
)

# 4. Replace dgt.gov.in (HTTP 500 error) with MSDE official portal
content = content.replace(
    '"website": "https://dgt.gov.in"',
    '"website": "https://msde.gov.in"'
)

# 5. Set unavailable / SSL error websites to None
content = content.replace(
    '"website": "https://ncvtmis.gov.in"',
    '"website": None'
)
content = content.replace(
    '"website": "https://admission.dvet.gov.in"',
    '"website": None'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated places_registry.py successfully.")
