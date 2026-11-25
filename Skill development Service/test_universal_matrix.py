import requests
import urllib.parse

BASE = 'http://127.0.0.1:8003/api'

# Real database expectations mapped to actual MySQL 8.4 curricula
test_cases = [
    # 1. Tech exact / partial
    ('Python', True, 'Python Programming'),
    ('Java', True, 'Enterprise Java & Spring Boot'),
    ('C++', True, 'Modern C++ & STL'),
    ('Machine Learning', True, 'Data Analysis with Python'),
    ('Cloud', True, 'AWS Cloud Practitioner Essentials'),
    ('Cybersecurity', True, 'Cybersecurity Fundamentals'),
    ('Web Development', True, 'HTML5 & Modern CSS3'),
    
    # 2. Collision exclusions
    ('Java', False, 'JavaScript'),
    ('C', False, 'Modern C++'),
    ('Driving', False, 'Selenium WebDriver'),

    # 3. Non-tech / Vocational
    ('Welding', True, 'Manual Metal Arc & TIG Welding'),
    ('Solar', True, 'Solar PV Rooftop System Installation'),
    ('Plumbing', True, 'Plumbing Technician & Pipe Fitting'),
    ('Tailoring', True, 'Apparel Manufacturing & Industrial Tailoring'),
    ('Organic Farming', True, 'Organic Farming & Soil Health Management'),
    ('Automotive', True, 'Automotive Two-Wheeler Technician'),
    ('Hospitality', True, 'Hospitality Front Office Operations'),
    ('Carpentry', True, 'Carpentry & Architectural Woodwork'),
    ('Electrical', True, 'Domestic Electrician & Home Wiring'),

    # 4. Multi-word & Partials
    ('data ana', True, 'Data Analysis with Python'),
    ('react', True, 'React.js Frontend Development'),
    ('docker', True, 'Docker & Containerization'),
    
    # 5. Zero matches
    ('QuantumTeleportationXyz999', None, None)
]

passed = 0
for term, expected, expected_content in test_cases:
    encoded_term = urllib.parse.quote(term)
    res = requests.get(f'{BASE}/programmes?q={encoded_term}')
    data = res.json()
    items = data if isinstance(data, list) else (data.get('programmes') or data.get('items') or [])
    
    if expected is None:
        if len(items) == 0:
            print(f'PASS: Search "{term}" returned 0 results as expected.')
            passed += 1
        else:
            print(f'FAIL: Search "{term}" returned {len(items)} unexpected results!')
    elif expected is True:
        matched = [p for p in items if expected_content.lower() in p['title'].lower() or expected_content.lower() in (p.get('skill_name') or '').lower()]
        if len(matched) > 0:
            print(f'PASS: Search "{term}" found expected programme "{matched[0]["title"]}"')
            passed += 1
        else:
            print(f'FAIL: Search "{term}" did not find expected programme containing "{expected_content}". Total items: {len(items)}')
    elif expected is False:
        conflicts = [p for p in items if expected_content.lower() in p['title'].lower()]
        if len(conflicts) == 0:
            print(f'PASS: Collision search "{term}" successfully excluded conflicting "{expected_content}"')
            passed += 1
        else:
            print(f'FAIL: Collision search "{term}" leaked prohibited term "{expected_content}": {conflicts[0]["title"]}')

print(f'\nUniversal Search Matrix Results: {passed}/{len(test_cases)} PASSED!')
