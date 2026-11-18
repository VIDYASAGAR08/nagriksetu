import sqlite3

conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
c = conn.cursor()

c.execute('SELECT school_id, school_name, category FROM schools ORDER BY school_id')
schools = c.fetchall()

print(f"{'Institution ID':<15} | {'DB Applications':<17} | {'New Applications':<18} | {'Pending Reviews':<17} | {'Status Breakdown'}")
print("-" * 95)

grand_total = 0
grand_new = 0
grand_pending = 0

for s in schools:
    sid = s[0]
    c.execute('SELECT status, COUNT(*) FROM admission_applications WHERE institution_id = ? GROUP BY status', (sid,))
    st_rows = c.fetchall()
    st_map = dict(st_rows)
    total_apps = sum(st_map.values())
    new_apps = st_map.get('submitted', 0)
    pending = (st_map.get('submitted', 0) + 
               st_map.get('under_review', 0) + 
               st_map.get('action_required', 0) + 
               st_map.get('clarification_requested', 0))
    grand_total += total_apps
    grand_new += new_apps
    grand_pending += pending
    st_str = ', '.join([f'{k}: {v}' for k, v in sorted(st_map.items())]) if st_map else '0'
    print(f"{sid:<15} | {total_apps:<17} | {new_apps:<18} | {pending:<17} | {st_str}")

print("-" * 95)
print(f"{'TOTAL':<15} | {grand_total:<17} | {grand_new:<18} | {grand_pending:<17} |")
