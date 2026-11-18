import sqlite3

def run():
    conn = sqlite3.connect('C:/Users/callm/nagriksetu/backend/data/nagriksetu.db')
    c = conn.cursor()

    # 1. Add BCA and BPharm if missing
    new_programs = [
        # BCA
        ('PROG-COL006-BCA', 'COL006', 'undergraduate', 'Bachelor of Computer Applications (BCA)', 'BCA', 'Computer Applications', 'BCA', 3),
        ('PROG-COL007-BCA', 'COL007', 'undergraduate', 'Bachelor of Computer Applications (BCA)', 'BCA', 'Computer Applications', 'BCA', 3),
        ('PROG-COL009-BCA', 'COL009', 'undergraduate', 'Bachelor of Computer Applications (BCA)', 'BCA', 'Computer Applications', 'BCA', 3),
        # BPharm
        ('PROG-COL001-BPHARM', 'COL001', 'undergraduate', 'Bachelor of Pharmacy (B.Pharm)', 'BPharm', 'Pharmacy', 'B.Pharm', 4),
        ('PROG-COL004-BPHARM', 'COL004', 'undergraduate', 'Bachelor of Pharmacy (B.Pharm)', 'BPharm', 'Pharmacy', 'B.Pharm', 4),
        ('PROG-COL009-BPHARM', 'COL009', 'undergraduate', 'Bachelor of Pharmacy (B.Pharm)', 'BPharm', 'Pharmacy', 'B.Pharm', 4),
        # Ensure BCom & BBA in COL009 if missing
        ('PROG-COL009-BCOM', 'COL009', 'undergraduate', 'Bachelor of Commerce (Honours)', 'BCom', 'Commerce', 'B.Com', 3),
        ('PROG-COL009-BBA', 'COL009', 'undergraduate', 'Bachelor of Business Administration (BBA)', 'BBA', 'Management', 'BBA', 3),
        ('PROG-COL009-BSC', 'COL009', 'undergraduate', 'Bachelor of Science in Physics, Maths & Electronics', 'BSc', 'Science', 'B.Sc', 3),
    ]

    for p in new_programs:
        c.execute('''
            INSERT OR IGNORE INTO academic_programs 
            (program_id, institution_id, education_level, program_name, degree_type, discipline_or_stream, combination_code, duration_years, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', p)

    # 2. Populate program sections for all UG programs currently having 0 sections
    # Find all UG programs without sections
    ug_progs = c.execute('''
        SELECT p.program_id, p.institution_id, p.degree_type, p.duration_years, p.combination_code
        FROM academic_programs p
        WHERE p.education_level = 'undergraduate'
    ''').fetchall()

    for prog_id, inst_id, deg_type, duration, combo in ug_progs:
        # Check if already has sections
        existing_count = c.execute('SELECT count(*) FROM program_sections WHERE program_id = ?', (prog_id,)).fetchone()[0]
        if existing_count > 0:
            continue
        
        # Configure sections for each year of duration
        # Configure non-equal strengths
        base_strength = {
            'BE/B.Tech': 60,
            'BCom': 55,
            'BSc': 42,
            'BCA': 50,
            'BBA': 46,
            'BPharm': 42,
            'Other': 35
        }.get(deg_type, 45)

        for yr in range(1, duration + 1):
            sem = yr * 2
            # For year 1, provide Section A and Section B where capacity is higher
            has_b = deg_type in ['BE/B.Tech', 'BCom', 'BCA'] and yr <= 2
            
            str_a = base_strength - (yr - 1) * 2
            cap_a = str_a + 10
            sec_id_a = f'SEC-{inst_id}-{combo.replace(" ", "").replace(".", "").replace("/", "-")}-Y{yr}-A'
            c.execute('''
                INSERT OR REPLACE INTO program_sections
                (section_id, institution_id, program_id, academic_year, term_or_year, semester, section_name, capacity, current_strength)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (sec_id_a, inst_id, prog_id, '2025-26', yr, sem, 'A', cap_a, str_a))

            if has_b:
                str_b = str_a - 4
                cap_b = str_b + 10
                sec_id_b = f'SEC-{inst_id}-{combo.replace(" ", "").replace(".", "").replace("/", "-")}-Y{yr}-B'
                c.execute('''
                    INSERT OR REPLACE INTO program_sections
                    (section_id, institution_id, program_id, academic_year, term_or_year, semester, section_name, capacity, current_strength)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (sec_id_b, inst_id, prog_id, '2025-26', yr, sem, 'B', cap_b, str_b))

    conn.commit()
    print('Integrity check:', c.execute('PRAGMA integrity_check').fetchall())
    print('FK check:', c.execute('PRAGMA foreign_key_check').fetchall())
    print('Total program_sections now:', c.execute('SELECT count(*) FROM program_sections').fetchone()[0])
    print('Total academic_programs now:', c.execute('SELECT count(*) FROM academic_programs').fetchone()[0])
    conn.close()

if __name__ == '__main__':
    run()
