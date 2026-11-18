import urllib.request
import json

def test():
    import urllib.parse
    data = urllib.parse.urlencode({'username': 'staff.sch001@example.com', 'password': 'Staff@NagrikSetu2026!'}).encode('utf-8')
    req = urllib.request.Request(
        'http://localhost:8001/auth/login',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    resp = urllib.request.urlopen(req)
    token = json.loads(resp.read().decode())['access_token']
    print('Login OK')

    # Test 1: SCH011 term 11 program-sections
    req2 = urllib.request.Request(
        'http://localhost:8001/schools/SCH011/program-sections?term_or_year=11',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp2 = urllib.request.urlopen(req2)
    sections = json.loads(resp2.read().decode())
    print(f'Test 1: Retrieved {len(sections)} sections for SCH011 term 11:')
    for s in sections:
        print(f"  {s['combination_code']} Sec {s['section_name']}: Strength={s['current_strength']}, Capacity={s['capacity']}")

    # Test 2: COL001 diploma Automobile
    req3 = urllib.request.Request(
        'http://localhost:8001/schools/COL001/program-sections?education_level=diploma&combination_code=AUTO-DIP',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp3 = urllib.request.urlopen(req3)
    sections3 = json.loads(resp3.read().decode())
    print(f'\nTest 2: COL001 Diploma Automobile sections: {len(sections3)}')
    for s in sections3:
        print(f"  Year {s['term_or_year']} Sem {s['semester']} Sec {s['section_name']}: Strength={s['current_strength']}, Capacity={s['capacity']}")

    # Test 3: COL006 BA specialisations
    req4 = urllib.request.Request(
        'http://localhost:8001/schools/COL006/program-sections?education_level=undergraduate&discipline_or_stream=History',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp4 = urllib.request.urlopen(req4)
    sections4 = json.loads(resp4.read().decode())
    print(f'\nTest 3: COL006 BA History sections: {len(sections4)}')
    for s in sections4:
        print(f"  {s['program_name']} Yr {s['term_or_year']} Sec {s['section_name']}: Strength={s['current_strength']}")

    # Test 4: Global education program sections
    req5 = urllib.request.Request(
        'http://localhost:8001/education/program-sections?degree_type=BCA',
        headers={'Authorization': f'Bearer {token}'}
    )
    resp5 = urllib.request.urlopen(req5)
    sections5 = json.loads(resp5.read().decode())
    print(f'\nTest 4: Global BCA sections: {len(sections5)}')
    for s in sections5[:4]:
        print(f"  {s['institution_id']} - {s['program_name']} Yr {s['term_or_year']} Sec {s['section_name']}: Strength={s['current_strength']}")

if __name__ == '__main__':
    test()
