with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

target = '''            # Streams actually configured in academic_programs for this institution
            streams_rows = conn.execute(
                "SELECT DISTINCT discipline_or_stream FROM academic_programs WHERE institution_id = ? AND is_active = 1 ORDER BY discipline_or_stream",
                (inst_id,)
            ).fetchall()'''

replacement = '''            # Streams actually configured in academic_programs for this institution
            streams_rows = conn.execute(
                """
                SELECT DISTINCT discipline_or_stream
                FROM academic_programs
                WHERE institution_id = ? AND is_active = 1
                ORDER BY CASE discipline_or_stream
                    WHEN 'Science' THEN 1
                    WHEN 'Commerce' THEN 2
                    WHEN 'Arts / Humanities' THEN 3
                    ELSE 4
                END
                """,
                (inst_id,)
            ).fetchall()'''

norm_c = content.replace('\r\n', '\n')
norm_t = target.replace('\r\n', '\n')
norm_r = replacement.replace('\r\n', '\n')

assert norm_t in norm_c, "target not found"
norm_c = norm_c.replace(norm_t, norm_r, 1)

with open(r'C:\Users\callm\nagriksetu\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(norm_c)

print("Updated stream ordering in main.py")
