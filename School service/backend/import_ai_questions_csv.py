"""
import_ai_questions_csv.py
Imports the 200 AI Question Bank items from nagriksetu_ai_question_bank_200.csv
into the School Service database table `ai_question_bank`.
"""

import os
import sys
import csv
import sqlite3
import uuid

def classify_question(code, text, category, role, csv_intent, csv_req_info, csv_data_src, csv_method, csv_expected):
    intent = csv_intent.strip() if csv_intent else ""
    req_info = csv_req_info.strip() if csv_req_info else ""
    data_source = csv_data_src.strip() if csv_data_src else ""
    method = csv_method.strip() if csv_method else ""
    expected = csv_expected.strip() if csv_expected else ""

    text_lower = text.lower()

    if "school discovery" in category.lower():
        if not intent:
            intent = f"Discover, filter or compare schools: {text.rstrip('?')}"
        if not req_info:
            req_info = "Location, preferred standard, medium of instruction, fee range, required facilities"
        if not data_source:
            data_source = "schools, academic_programs, institution_divisions"
        if not method:
            method = "Recommendation" if any(w in text_lower for w in ["recommend", "best", "compare", "suitable"]) else "Database Retrieval"
        if not expected:
            expected = "List of matching schools with details (name, district, medium, facilities, contact) or comparative matrix."

    elif "student academic" in category.lower() or "student guidance" in category.lower():
        if not intent:
            intent = f"Academic guidance and learning performance: {text.rstrip('?')}"
        if not req_info:
            req_info = "Student permanent ID, standard, subjects, past examination marks, examination schedule"
        if not data_source:
            data_source = "academic_results, examinations, Official Knowledge Base"
        if not method:
            if any(w in text_lower for w in ["weak", "marks", "performance", "gap", "prioritise", "prioritize"]):
                method = "Calculation"
            elif any(w in text_lower for w in ["recommend", "schedule", "timetable", "path", "skill", "extracurricular"]):
                method = "Recommendation"
            else:
                method = "AI Explanation"
        if not expected:
            expected = "Actionable academic guidance, personalized study timetable, learning gaps analysis, or curriculum resources."

    elif "parent" in category.lower():
        if not intent:
            intent = f"Parent support and child welfare monitoring: {text.rstrip('?')}"
        if not req_info:
            req_info = "Student permanent ID, guardian ID, child attendance records, academic year"
        if not data_source:
            if "attendance" in text_lower:
                data_source = "student_attendance, student_guardians"
            elif any(w in text_lower for w in ["scheme", "scholarship", "support", "rte", "assistance", "textbook", "uniform", "nutritional"]):
                data_source = "scholarships, Official Knowledge Base"
            else:
                data_source = "academic_results, student_attendance, schools"
        if not method:
            if any(w in text_lower for w in ["attendance", "track", "monitor", "progress"]):
                method = "Database Retrieval"
            elif any(w in text_lower for w in ["eligible", "scheme", "rte", "assistance", "support"]):
                method = "Eligibility Rules"
            else:
                method = "Recommendation"
        if not expected:
            expected = "Attendance/progress report, qualifying welfare schemes, or school remediation guidance."

    elif "school administration" in category.lower():
        if not intent:
            intent = f"Institutional administrative oversight: {text.rstrip('?')}"
        if not req_info:
            req_info = "Institution ID, academic year, attendance threshold, section/classroom data"
        if not data_source:
            if any(w in text_lower for w in ["dropout", "attendance", "absenteeism"]):
                data_source = "student_attendance, enrollments, students"
            elif any(w in text_lower for w in ["teacher", "workload"]):
                data_source = "institution_staff_permissions, program_sections"
            elif any(w in text_lower for w in ["infrastructure", "repair", "computer", "budget", "classroom"]):
                data_source = "schools, Official Knowledge Base"
            else:
                data_source = "academic_results, enrollments, program_sections"
        if not method:
            if any(w in text_lower for w in ["dropout", "pass percentage", "shortage", "absenteeism"]):
                method = "Calculation"
            elif any(w in text_lower for w in ["recommend", "prioritise", "prioritize"]):
                method = "Recommendation"
            else:
                method = "Database Retrieval"
        if not expected:
            expected = "Administrative metric summary, at-risk student list, staffing/infrastructure gap assessment, or priority action plan."

    elif "teacher" in category.lower():
        if not intent:
            intent = f"Teacher pedagogical and instructional support: {text.rstrip('?')}"
        if not req_info:
            req_info = "Section ID, subject name, exam results, student attendance log"
        if not data_source:
            data_source = "academic_results, student_attendance, students, program_sections"
        if not method:
            if any(w in text_lower for w in ["remedial", "recommend", "grouped", "activities", "teaching methods"]):
                method = "Recommendation"
            elif any(w in text_lower for w in ["marks", "declining", "improvement", "strengths"]):
                method = "Calculation"
            else:
                method = "Database Retrieval"
        if not expected:
            expected = "Targeted student cohort identification, differentiated instruction plans, or subject-specific teaching recommendations."

    elif "government schemes" in category.lower():
        if not intent:
            intent = f"Discover and verify eligibility for government education schemes: {text.rstrip('?')}"
        if not req_info:
            req_info = "Student category/caste, annual family income, gender, standard, domicile"
        if not data_source:
            data_source = "scholarships, Official Knowledge Base"
        if not method:
            if any(w in text_lower for w in ["eligible", "criteria", "recommend"]):
                method = "Eligibility Rules"
            else:
                method = "Official Knowledge Base"
        if not expected:
            expected = "List of qualifying government schemes/scholarships, eligibility parameters, document checklists, and application steps."

    elif "government official" in category.lower():
        if not intent:
            intent = f"District and state educational governance analysis: {text.rstrip('?')}"
        if not req_info:
            req_info = "District name, taluk, school type, inspection parameters, academic year"
        if not data_source:
            if any(w in text_lower for w in ["enrolment", "dropout", "attendance"]):
                data_source = "schools, enrollments, student_attendance"
            elif any(w in text_lower for w in ["infrastructure", "toilet", "water", "classroom", "laboratory"]):
                data_source = "schools, Official Knowledge Base"
            elif any(w in text_lower for w in ["teacher", "vacancy"]):
                data_source = "schools, institution_staff_permissions"
            else:
                data_source = "schools, academic_results, scholarships"
        if not method:
            if any(w in text_lower for w in ["recommend", "prioritised", "prioritized", "where"]):
                method = "Recommendation"
            elif any(w in text_lower for w in ["rate", "percentage", "high", "low", "poor"]):
                method = "Calculation"
            else:
                method = "Database Retrieval"
        if not expected:
            expected = "District-level governance report, ranked deficiency list, vacancy count, or resource allocation priority."

    elif any(w in category.lower() for w in ["admissions, transfers", "admission", "transfer"]):
        if not intent:
            intent = f"Manage student admission, transfer or official record updates: {text.rstrip('?')}"
        if not req_info:
            req_info = "Student permanent ID, current school ID, target school ID, update field, supporting documents"
        if not data_source:
            if any(w in text_lower for w in ["transfer", "tc", "relocation"]):
                data_source = "school_transfers, enrollments, schools"
            elif any(w in text_lower for w in ["record", "name", "date of birth"]):
                data_source = "update_requests, students, guardians"
            else:
                data_source = "admission_applications, schools, Official Knowledge Base"
        if not method:
            if any(w in text_lower for w in ["transfer", "update", "incorrect", "tc", "out-of-school", "bridge"]):
                method = "Official Knowledge Base"
            elif "which schools" in text_lower:
                method = "Database Retrieval"
            else:
                method = "Eligibility Rules"
        if not expected:
            expected = "Transfer procedure, document checklist, official correction workflow, or eligible bridge admission pathway."

    elif "platform administration" in category.lower():
        if not intent:
            intent = f"Platform compliance monitoring, audit oversight and system health: {text.rstrip('?')}"
        if not req_info:
            req_info = "Audit logs timestamp range, school compliance flags, reporting status"
        if not data_source:
            data_source = "audit_logs, platform_audit_logs, schools, users"
        if not method:
            if any(w in text_lower for w in ["recommend", "prioritise", "prioritize", "what should"]):
                method = "Recommendation"
            else:
                method = "Database Retrieval"
        if not expected:
            expected = "List of non-compliant institutions, pending verification backlogs, audit anomaly flags, or inspection priorities."

    else:
        if not intent: intent = text.rstrip("?")
        if not req_info: req_info = "Relevant school or student parameters"
        if not data_source: data_source = "schools, students"
        if not method: method = "Database Retrieval"
        if not expected: expected = "Relevant informational response."

    return intent, req_info, data_source, method, expected

def get_db_path():
    env_path = os.getenv("DATABASE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "nagriksetu.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "nagriksetu.db"),
        "/app/data/nagriksetu.db",
        "backend/data/nagriksetu.db",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def get_csv_path():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "nagriksetu_ai_question_bank_200.csv"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nagriksetu_ai_question_bank_200.csv"),
        "nagriksetu_ai_question_bank_200.csv"
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("Could not find nagriksetu_ai_question_bank_200.csv")

def import_and_verify():
    db_path = get_db_path()
    csv_path = get_csv_path()
    
    print(f"[*] Database target: {db_path}")
    print(f"[*] CSV source:     {csv_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # 1. Baseline counts of unrelated tables to prove zero side-effects
    unrelated_tables = ["schools", "students", "guardians", "users", "enrollments"]
    baseline_counts = {}
    for tbl in unrelated_tables:
        count = conn.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
        baseline_counts[tbl] = count
    print(f"[*] Baseline record counts before import: {baseline_counts}")
    
    # 2. Read CSV
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)
        
    print(f"[*] Total rows read from CSV: {len(raw_rows)}")
    
    # 3. Idempotent import into ai_question_bank
    inserted_count = 0
    updated_count = 0
    
    with conn:
        for r in raw_rows:
            code = r["question_code"].strip().upper()
            text = r["question_text"].strip()
            category = r["category"].strip()
            role = r["intended_role"].strip()
            
            is_active_raw = r.get("is_active", "True").strip().lower()
            is_active = 0 if is_active_raw in ["false", "0", "no"] else 1
            
            intent, req_info, data_src, method, expected = classify_question(
                code, text, category, role,
                r.get("intent", ""), r.get("required_information", ""),
                r.get("data_source", ""), r.get("answer_method", ""),
                r.get("expected_answer", "")
            )
            
            existing = conn.execute(
                "SELECT id FROM ai_question_bank WHERE question_code = ?", (code,)
            ).fetchone()
            
            if existing:
                conn.execute("""
                    UPDATE ai_question_bank
                    SET question_text = ?,
                        category = ?,
                        intended_role = ?,
                        intent = ?,
                        required_information = ?,
                        data_source = ?,
                        answer_method = ?,
                        expected_answer = ?,
                        is_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE question_code = ?
                """, (text, category, role, intent, req_info, data_src, method, expected, is_active, code))
                updated_count += 1
            else:
                q_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO ai_question_bank (
                        id, question_code, question_text, category,
                        intended_role, intent, required_information,
                        data_source, answer_method, expected_answer,
                        is_active, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (q_id, code, text, category, role, intent, req_info, data_src, method, expected, is_active))
                inserted_count += 1
                
    print(f"[+] Import finished: {inserted_count} newly inserted, {updated_count} updated.")
    
    # 4. Strict verification
    print("\n" + "="*50)
    print("VERIFICATION SUITE")
    print("="*50)
    
    stored_rows = conn.execute("SELECT * FROM ai_question_bank ORDER BY question_code ASC").fetchall()
    total_stored = len(stored_rows)
    print(f"1. Total questions stored: {total_stored}")
    assert total_stored == 200, f"Error: expected 200 questions, got {total_stored}"
    
    stored_codes = [r["question_code"] for r in stored_rows]
    expected_codes = [f"Q{i:03d}" for i in range(1, 201)]
    print(f"2. All codes Q001 to Q200 check: first={stored_codes[0]}, last={stored_codes[-1]}")
    missing_codes = set(expected_codes) - set(stored_codes)
    extra_codes = set(stored_codes) - set(expected_codes)
    assert not missing_codes, f"Missing codes: {missing_codes}"
    assert not extra_codes, f"Unexpected codes: {extra_codes}"
    print("   -> PASSED: All 200 codes Q001 through Q200 are present with zero gaps.")
    
    # Check duplicates
    code_counts = {}
    for c in stored_codes:
        code_counts[c] = code_counts.get(c, 0) + 1
    duplicates = [c for c, cnt in code_counts.items() if cnt > 1]
    assert not duplicates, f"Duplicate codes found: {duplicates}"
    print("3. Duplicate question codes check: PASSED (0 duplicates)")
    
    # Check empty question text
    empty_texts = [r["question_code"] for r in stored_rows if not r["question_text"] or not r["question_text"].strip()]
    assert not empty_texts, f"Empty question texts found in: {empty_texts}"
    print("4. Empty question text check: PASSED (0 empty texts)")
    
    # Check category distribution
    expected_distribution = {
        "School Discovery and Admissions": 30,
        "Student Academic Guidance and Learning": 25,
        "Parent and Child Support": 20,
        "School Administration": 25,
        "Teacher Assistance": 20,
        "Government Schemes and Student Welfare": 25,
        "Government Officials": 20,
        "Admissions, Transfers and Records": 15,
        "Platform Administration": 20
    }
    
    cat_counts = {}
    for r in stored_rows:
        cat = r["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
    print("\n5. Category Distribution Breakdown:")
    for cat, exp_cnt in expected_distribution.items():
        actual_cnt = cat_counts.get(cat, 0)
        status = "MATCH" if actual_cnt == exp_cnt else "MISMATCH"
        print(f"   - {cat}: {actual_cnt} / {exp_cnt} [{status}]")
        assert actual_cnt == exp_cnt, f"Mismatch in category {cat}: expected {exp_cnt}, got {actual_cnt}"
    print("   -> PASSED: All 9 categories match exact counts (Sum = 200).")
    
    # Check unrelated tables
    print("\n6. Unrelated Database Tables Integrity Check:")
    post_counts = {}
    for tbl in unrelated_tables:
        count = conn.execute(f"SELECT count(*) FROM {tbl}").fetchone()[0]
        post_counts[tbl] = count
        assert post_counts[tbl] == baseline_counts[tbl], f"Side effect detected on {tbl}: was {baseline_counts[tbl]}, now {post_counts[tbl]}"
        print(f"   - {tbl}: {post_counts[tbl]} records (unchanged)")
    print("   -> PASSED: Zero side-effects on existing School Service data.")
    
    conn.close()
    return True

if __name__ == "__main__":
    import_and_verify()
