import sqlite3

def upgrade_sqlite_schema(db_path='land_records.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Users
    cursor.execute("PRAGMA table_info(users)")
    cols = [row[1] for row in cursor.fetchall()]
    user_additions = [
        ("phone", "TEXT"),
        ("state_id", "INTEGER"),
        ("district_id", "INTEGER"),
        ("updated_at", "DATETIME")
    ]
    for col, ctype in user_additions:
        if col not in cols:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {ctype}")

    # Land Records
    cursor.execute("PRAGMA table_info(land_records)")
    lr_cols = [row[1] for row in cursor.fetchall()]
    lr_additions = [
        ("state_id", "INTEGER"),
        ("district_id", "INTEGER"),
        ("administrative_unit_id", "INTEGER"),
        ("village_id", "INTEGER"),
        ("owner_id", "INTEGER"),
        ("current_owner", "TEXT"),
        ("area_unit", "TEXT DEFAULT 'Acres'"),
        ("document_type", "TEXT DEFAULT 'Sale Deed'"),
        ("last_verification_date", "TEXT"),
        ("verification_status", "TEXT DEFAULT 'Verified'"),
        ("publication_status", "TEXT DEFAULT 'PUBLISHED'")
    ]
    for col, ctype in lr_additions:
        if col not in lr_cols:
            cursor.execute(f"ALTER TABLE land_records ADD COLUMN {col} {ctype}")

    # Documents
    cursor.execute("PRAGMA table_info(documents)")
    doc_cols = [row[1] for row in cursor.fetchall()]
    doc_additions = [
        ("registration_id", "INTEGER"),
        ("file_size", "INTEGER"),
        ("language", "TEXT DEFAULT 'English'"),
        ("ocr_status", "TEXT DEFAULT 'COMPLETED'"),
        ("ocr_raw_text", "TEXT"),
        ("processing_status", "TEXT DEFAULT 'SUCCESS'"),
        ("updated_at", "DATETIME")
    ]
    for col, ctype in doc_additions:
        if col not in doc_cols:
            cursor.execute(f"ALTER TABLE documents ADD COLUMN {col} {ctype}")

    conn.commit()
    conn.close()
    print(f"Database schema at {db_path} upgraded cleanly.")

if __name__ == "__main__":
    upgrade_sqlite_schema()
