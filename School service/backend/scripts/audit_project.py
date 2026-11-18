import sqlite3
import json

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("=== SQLITE TABLES & ROW COUNTS ===")
for t in tables:
    count = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [f"{r[1]} ({r[2]})" for r in c.execute(f"PRAGMA table_info({t})").fetchall()]
    print(f"\nTable: {t} [{count} rows]")
    print("  Columns:", ", ".join(cols))

print("\n=== INTEGRITY CHECKS ===")
print("PRAGMA integrity_check:", c.execute("PRAGMA integrity_check").fetchone()[0])
print("PRAGMA foreign_key_check:", c.execute("PRAGMA foreign_key_check").fetchall())

# Sample counts for key metrics
print("\n=== VERIFIED MASTER METRICS ===")
print("Students:", c.execute("SELECT COUNT(*) FROM students").fetchone()[0])
print("Enrollments:", c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0])
print("Academic Programs:", c.execute("SELECT COUNT(*) FROM academic_programs").fetchone()[0])
print("Program Sections:", c.execute("SELECT COUNT(*) FROM program_sections").fetchone()[0])
print("Schools/Colleges:", c.execute("SELECT COUNT(*) FROM schools").fetchone()[0])
print("Users:", c.execute("SELECT COUNT(*) FROM users").fetchone()[0])
print("Users by role:")
for r in c.execute("SELECT role, COUNT(*) FROM users GROUP BY role").fetchall():
    print(f"  {r[0]}: {r[1]}")

conn.close()
