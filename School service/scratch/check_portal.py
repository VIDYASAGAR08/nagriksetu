import urllib.request
import re

with urllib.request.urlopen('http://localhost:5173') as response:
    html = response.read().decode('utf-8')
    scripts = re.findall(r'src=["\']([^"\']+)["\']', html)
    print('Scripts:', scripts)
    for s in scripts:
        url = 'http://localhost:5173' + (s if s.startswith('/') else '/' + s)
        with urllib.request.urlopen(url) as r:
            js = r.read().decode('utf-8', errors='ignore')
            if 'Choose Your Portal Experience' in js:
                print('FOUND Choose Your Portal Experience in', url)
            else:
                print('NOT found in', url)
            if 'CITIZEN & STAKEHOLDER PORTALS' in js:
                print('FOUND CITIZEN & STAKEHOLDER PORTALS in', url)
