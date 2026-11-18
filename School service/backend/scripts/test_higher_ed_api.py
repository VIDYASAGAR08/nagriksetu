import urllib.request
import json

try:
    res = urllib.request.urlopen('http://localhost:8001/health').read()
    print('Health:', res.decode())

    # Test Degree College: COL001
    res_prog = urllib.request.urlopen('http://localhost:8001/schools/COL001/programs').read()
    col001_progs = json.loads(res_prog.decode())
    print(f"\n[+] COL001 (Degree College) programs: {len(col001_progs)}")
    for p in col001_progs:
        print(f"  • {p['program_name']} ({p['degree_type']}) - {p['education_level']} | Dept: {p.get('department_name')}")

    # Test University Academic Hierarchy: COL004
    res_hier = urllib.request.urlopen('http://localhost:8001/schools/COL004/academic-hierarchy').read()
    col004_hier = json.loads(res_hier.decode())
    print(f"\n[+] COL004 (PES University) Hierarchy: {len(col004_hier['faculties'])} Faculties")
    for f in col004_hier['faculties']:
        print(f"  [Faculty] {f['faculty_name']} ({f['division_type']}) - Head: {f['head_of_division']}")
        for d in f['departments']:
            print(f"    [Dept] {d['department_name']}")
            for pr in d['programmes']:
                print(f"      [{pr['education_level'].upper()}] {pr['program_name']} | Seats: {pr['available_seats']} avail / {pr['total_capacity']} cap")

    # Test University Academic Hierarchy: COL006 (St. Joseph's)
    res_sju = urllib.request.urlopen('http://localhost:8001/schools/COL006/academic-hierarchy').read()
    col006_hier = json.loads(res_sju.decode())
    print(f"\n[+] COL006 (St. Joseph's University) Hierarchy: {len(col006_hier['faculties'])} Faculties")
    for f in col006_hier['faculties']:
        print(f"  [Faculty] {f['faculty_name']} ({f['division_type']})")
        for d in f['departments']:
            print(f"    [Dept] {d['department_name']} ({len(d['programmes'])} programmes)")

    # Test Seat Availability for COL001
    res_seat = urllib.request.urlopen('http://localhost:8001/schools/COL001/seat-availability').read()
    col001_seat = json.loads(res_seat.decode())
    print(f"\n[+] COL001 Seat Availability: Cap={col001_seat['total_sanctioned_capacity']}, Strength={col001_seat['total_current_strength']}, Avail={col001_seat['total_available_seats']}, Sections={col001_seat['sections_count']}")

    print("\n[+] All API responses verified successfully!")

except Exception as e:
    print("[!] Error testing API:", e)
    raise
