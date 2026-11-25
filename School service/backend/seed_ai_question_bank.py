"""
seed_ai_question_bank.py
Idempotent seeding script for the NagrikSetu School Service AI Assistant Question Bank.
"""

import os
import sys
import json
import sqlite3
import uuid

EXPECTED_DISTRIBUTION = {
    "School Discovery": 30,
    "Student Guidance": 25,
    "Parent Support": 20,
    "School Administration": 25,
    "Teacher Assistance": 20,
    "Government Schemes": 25,
    "Government Officials": 20,
    "Admissions and Records": 15,
    "Platform Administration": 20
}

VALID_ROLES = {
    "Citizen", "Parent", "Student", "Teacher", "Principal",
    "Government Official", "Platform Admin", "General"
}

VALID_ANSWER_METHODS = {
    "Database Retrieval", "Eligibility Rules", "Calculation",
    "Recommendation", "Official Knowledge Base", "AI Explanation"
}

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

def seed_questions(questions_data):
    """
    Idempotently seeds questions into ai_question_bank.
    questions_data: list of dicts containing:
      - question_code: 'Q001' to 'Q200'
      - question_text: str
      - category: str
      - intended_role: str
      - intent: str
      - required_information: str
      - data_source: str
      - answer_method: str
      - expected_answer: str
    """
    db_path = get_db_path()
    print(f"[*] Seeding question bank in database at: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    
    inserted_count = 0
    updated_count = 0
    
    try:
        with conn:
            for q in questions_data:
                code = q["question_code"].strip().upper()
                text = q["question_text"].strip()
                category = q["category"].strip()
                role = q["intended_role"].strip()
                intent = q.get("intent", "").strip()
                req_info = q.get("required_information", "").strip()
                data_src = q.get("data_source", "").strip()
                method = q["answer_method"].strip()
                expected_ans = q.get("expected_answer", "").strip()
                q_id = q.get("id") or str(uuid.uuid4())
                
                # Check if exists
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
                            is_active = 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE question_code = ?
                    """, (text, category, role, intent, req_info, data_src, method, expected_ans, code))
                    updated_count += 1
                else:
                    conn.execute("""
                        INSERT INTO ai_question_bank (
                            id, question_code, question_text, category,
                            intended_role, intent, required_information,
                            data_source, answer_method, expected_answer,
                            is_active, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (q_id, code, text, category, role, intent, req_info, data_src, method, expected_ans))
                    inserted_count += 1
                    
        print(f"[+] Seeding complete: {inserted_count} inserted, {updated_count} updated.")
    finally:
        conn.close()

def verify_question_bank():
    """
    Verifies all criteria:
    1. Total questions = 200.
    2. Codes Q001 to Q200 present with no gaps.
    3. No duplicates.
    4. No empty question texts.
    5. Exact distribution across 9 categories.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    try:
        rows = conn.execute("SELECT * FROM ai_question_bank ORDER BY question_code ASC").fetchall()
        total = len(rows)
        print(f"[*] Verification - Total Questions: {total}")
        
        errors = []
        if total != 200:
            errors.append(f"Expected 200 questions, found {total}")
            
        codes = [r["question_code"] for r in rows]
        expected_codes = [f"Q{i:03d}" for i in range(1, 201)]
        
        missing = set(expected_codes) - set(codes)
        extra = set(codes) - set(expected_codes)
        if missing:
            errors.append(f"Missing codes: {sorted(list(missing))[:10]} (total missing: {len(missing)})")
        if extra:
            errors.append(f"Unexpected codes: {sorted(list(extra))[:10]}")
            
        empty_texts = [r["question_code"] for r in rows if not r["question_text"] or not r["question_text"].strip()]
        if empty_texts:
            errors.append(f"Empty question text for: {empty_texts}")
            
        # Category breakdown
        category_counts = {}
        for r in rows:
            cat = r["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        print("\n--- Category Breakdown ---")
        for cat, expected in EXPECTED_DISTRIBUTION.items():
            actual = category_counts.get(cat, 0)
            status = "MATCH" if actual == expected else "MISMATCH"
            print(f"  {cat}: {actual} / {expected} [{status}]")
            if actual != expected:
                errors.append(f"Category '{cat}' count mismatch: expected {expected}, got {actual}")
                
        unexpected_cats = set(category_counts.keys()) - set(EXPECTED_DISTRIBUTION.keys())
        if unexpected_cats:
            errors.append(f"Unexpected categories found: {unexpected_cats}")
            
        if errors:
            print("\n[-] Verification FAILED with errors:")
            for e in errors:
                print(f"  - {e}")
            return False, errors, category_counts
        else:
            print("\n[+] Verification PASSED: All 200 questions strictly valid and matched!")
            return True, [], category_counts
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_question_bank()
    else:
        json_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ai_questions_seed.json")
        if os.path.exists(json_file):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            seed_questions(data)
            verify_question_bank()
        else:
            print(f"[*] No seed file found at {json_file}. Run with --verify or provide questions JSON.")
