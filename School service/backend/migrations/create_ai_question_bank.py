"""
create_ai_question_bank.py
Migration to create the ai_question_bank table and necessary indexes
for the NagrikSetu School Service AI Assistant Question Bank.
"""

import os
import sqlite3
import sys

def get_db_path():
    env_path = os.getenv("DATABASE_PATH")
    if env_path and os.path.exists(env_path):
        return env_path
    
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nagriksetu.db"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nagriksetu.db"),
        "/app/data/nagriksetu.db",
        "backend/data/nagriksetu.db",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return candidates[0]

def apply_migration():
    db_path = get_db_path()
    print(f"[*] Applying migration on database at: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ai_question_bank (
                    id TEXT PRIMARY KEY,
                    question_code TEXT UNIQUE NOT NULL,
                    question_text TEXT NOT NULL,
                    category TEXT NOT NULL,
                    intended_role TEXT NOT NULL,
                    intent TEXT NOT NULL,
                    required_information TEXT,
                    data_source TEXT,
                    answer_method TEXT NOT NULL,
                    expected_answer TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_question_bank_code
                ON ai_question_bank(question_code);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_question_bank_category
                ON ai_question_bank(category);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_question_bank_role
                ON ai_question_bank(intended_role);
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_ai_question_bank_active
                ON ai_question_bank(is_active);
            """)
        print("[+] Successfully verified/created ai_question_bank table and indexes.")
    except Exception as e:
        print(f"[-] Migration error: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
