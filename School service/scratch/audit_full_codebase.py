import sqlite3
import json
import re
import os

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 1. Tables and counts
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]
table_counts = {}
for t in tables:
    try:
        cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        table_counts[t] = cnt
    except Exception as e:
        table_counts[t] = str(e)

# 2. PRAGMA checks
cur.execute("PRAGMA integrity_check")
integrity_res = cur.fetchall()

cur.execute("PRAGMA foreign_key_check")
fk_res = cur.fetchall()

# 3. Analyze backend/main.py endpoints
backend_file = r"C:\Users\callm\nagriksetu\backend\main.py"
with open(backend_file, "r", encoding="utf-8") as f:
    backend_code = f.read()

endpoint_pattern = re.compile(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']')
endpoints = endpoint_pattern.findall(backend_code)

# 4. Analyze frontend pages and components
frontend_dir = r"C:\Users\callm\nagriksetu\frontend\src"
frontend_files = []
for root, dirs, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith((".jsx", ".js", ".tsx", ".ts")):
            frontend_files.append(os.path.relpath(os.path.join(root, f), frontend_dir))

# 5. Analyze AI agent
ai_file = r"C:\Users\callm\nagriksetu\backend\ai_agent.py"
with open(ai_file, "r", encoding="utf-8") as f:
    ai_code = f.read()

output = {
    "tables_count": len(tables),
    "table_counts": table_counts,
    "integrity_check": [r[0] for r in integrity_res],
    "foreign_key_violations_count": len(fk_res),
    "foreign_key_violations": [list(r) for r in fk_res[:10]],
    "endpoints_total": len(endpoints),
    "endpoints": [{"method": m.upper(), "path": p} for m, p in endpoints],
    "frontend_files_total": len(frontend_files),
    "frontend_files": frontend_files,
    "ai_agent_length": len(ai_code)
}

with open(r"C:\Users\callm\nagriksetu\scratch\audit_results.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("Audit completed successfully. Results saved to scratch/audit_results.json")
print(f"Total tables: {len(tables)}")
print(f"Total endpoints: {len(endpoints)}")
print(f"Total frontend components/files: {len(frontend_files)}")
print(f"Integrity check: {[r[0] for r in integrity_res]}")
print(f"Foreign key violations: {len(fk_res)}")
