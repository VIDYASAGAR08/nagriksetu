import pymysql

conn = pymysql.connect(host='127.0.0.1', port=3308, user='nagriksetu_skill', password='skill-app-pass-2026', database='skill_db')
cur = conn.cursor()

# 1. Create subcategories table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS subcategories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(24) NOT NULL UNIQUE,
    category_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    icon_name VARCHAR(50) DEFAULT 'Folder',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
""")

# 2. Add subcategory_id and subcategory_name to skills table if not exist
cur.execute("SHOW COLUMNS FROM skills LIKE 'subcategory_id'")
if not cur.fetchone():
    cur.execute("ALTER TABLE skills ADD COLUMN subcategory_id INT NULL AFTER category_id")
    cur.execute("ALTER TABLE skills ADD CONSTRAINT fk_skills_subcategory FOREIGN KEY (subcategory_id) REFERENCES subcategories(id) ON DELETE SET NULL")
    print("Added subcategory_id to skills")

cur.execute("SHOW COLUMNS FROM skills LIKE 'subcategory_name'")
if not cur.fetchone():
    cur.execute("ALTER TABLE skills ADD COLUMN subcategory_name VARCHAR(120) NULL AFTER category_name")
    cur.execute("ALTER TABLE skills ADD INDEX idx_skills_subcategory_name (subcategory_name)")
    print("Added subcategory_name to skills")

conn.commit()
print("Migration applied successfully!")
conn.close()
