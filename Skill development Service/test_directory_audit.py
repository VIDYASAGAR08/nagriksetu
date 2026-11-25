import requests

BASE = 'http://127.0.0.1:8003/api'

# 1. Search Whitefield, Kaggadasapura, Jalahalli
for loc in ['Whitefield', 'Kaggadasapura', 'Jalahalli']:
    res = requests.get(f'{BASE}/centres/search?location={loc}&radius_km=15')
    assert res.status_code == 200
    data = res.json()
    centres = data.get('centres', [])
    assert len(centres) > 0, f'Expected centres for {loc}'
    first = centres[0]
    first_name = first['name']
    first_dist = first['distance_km']
    print(f'PASS Location Search [{loc}]: {len(centres)} centres found. Nearest: {first_name} ({first_dist} km)')
    for c in centres:
        assert c.get('latitude') is not None and c.get('longitude') is not None

# 2. Centre profile distinctiveness test
c1 = requests.get(f'{BASE}/centres/1/profile').json()
c2 = requests.get(f'{BASE}/centres/2/profile').json()
c3 = requests.get(f'{BASE}/centres/3/profile').json()
c4 = requests.get(f'{BASE}/centres/4/profile').json()
c6 = requests.get(f'{BASE}/centres/6/profile').json()

# Assert distinct names
names = {c1['name'], c2['name'], c3['name'], c4['name'], c6['name']}
assert len(names) == 5, 'All centre names must be distinct'

# Assert distinct addresses
addresses = {c1['address'], c2['address'], c3['address'], c4['address'], c6['address']}
assert len(addresses) == 5, 'All centre addresses must be distinct'

# Assert distinct descriptions
descriptions = {c1['description'], c2['description'], c3['description'], c4['description'], c6['description']}
assert len(descriptions) == 5, 'All centre descriptions must be distinct'

# Assert distinct coordinates
coords = {(c1['latitude'], c1['longitude']), (c2['latitude'], c2['longitude']), (c3['latitude'], c3['longitude']), (c4['latitude'], c4['longitude']), (c6['latitude'], c6['longitude'])}
assert len(coords) == 5, 'All physical centre coordinates must be distinct'

# Assert each centre has its own programs
c1_pids = {p['id'] for p in c1['programs']}
c2_pids = {p['id'] for p in c2['programs']}
c3_pids = {p['id'] for p in c3['programs']}
assert len(c1_pids.intersection(c2_pids)) == 0, 'Centres must not share program IDs'
assert len(c2_pids.intersection(c3_pids)) == 0, 'Centres must not share program IDs'

print('PASS: Centre Profile Distinctiveness and Program Association verified 100%!')

# 3. Discovered real-world centre details test
details_gttc = requests.get(f'{BASE}/centres/details/gttc-sub-whitefield').json()
assert details_gttc['name'] == 'Government Tool Room & Training Centre (GTTC) Sub-Centre Whitefield'
assert details_gttc['locality'] == 'Whitefield'
assert details_gttc['verification_status'] == 'Officially verified'

print('PASS: Discovered Centre Details verified 100%!')
