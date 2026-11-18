import requests

for inst in ['SCH011', 'SCH012', 'SCH013', 'SCH014', 'SCH015']:
    r1 = requests.get(f'http://localhost:8001/schools/{inst}/seat-availability')
    d = r1.json()
    r2 = requests.get(f'http://localhost:8001/schools/{inst}/programs')
    p = r2.json()
    print(f"{inst} ({d.get('institution_name')}): Cap={d.get('total_sanctioned_capacity')}, Enr={d.get('total_current_strength')}, Avail={d.get('total_available_seats')}, Secs={d.get('sections_count')}, Progs={len(p)}")
