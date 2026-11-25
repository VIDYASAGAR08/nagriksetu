import sys, urllib.request, ssl
sys.path.append(r'C:\Users\karth\OneDrive\Documents\NagrikSetu_Skill_Development_FINAL\backend')
from app.places_registry import AUTHENTIC_REAL_WORLD_CENTRES

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print(f"{'ID':25} | {'Status':8} | {'URL':45} | {'Institute Name'}")
print("-" * 110)

unique_urls = {}
for inst in AUTHENTIC_REAL_WORLD_CENTRES:
    url = inst.get('website', '').strip()
    iid = inst.get('id', '')
    name = inst.get('name', '')
    if url not in unique_urls:
        unique_urls[url] = []
    unique_urls[url].append((iid, name))

for url, insts in unique_urls.items():
    if not url:
        for iid, name in insts:
            print(f"{iid:25} | NO_URL   | {'<empty>':45} | {name[:35]}")
        continue
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=ctx) as resp:
            status = resp.status
    except Exception as e:
        status = f"ERR: {type(e).__name__}"
    
    for iid, name in insts:
        print(f"{iid:25} | {str(status):8} | {url[:45]:45} | {name[:35]}")
