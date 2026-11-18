import sqlite3

db_path = r"C:\Users\callm\nagriksetu\backend\data\nagriksetu.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS document_ocr_extractions (
    extraction_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    application_id TEXT NOT NULL,
    raw_text TEXT NOT NULL,
    ocr_engine TEXT NOT NULL,
    average_confidence REAL NOT NULL,
    extracted_entities_json TEXT NOT NULL,
    match_status TEXT NOT NULL DEFAULT 'unreviewed',
    discrepancy_notes TEXT,
    extracted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES admission_documents(document_id),
    FOREIGN KEY (application_id) REFERENCES admission_applications(application_id)
)
""")

cur.execute("CREATE INDEX IF NOT EXISTS idx_ocr_document_id ON document_ocr_extractions(document_id)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_ocr_application_id ON document_ocr_extractions(application_id)")

conn.commit()
conn.close()
print("Phase 8 document_ocr_extractions table created successfully.")
