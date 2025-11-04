import sqlite3, os

db_path = os.path.join("instance", "flow_study.db")

if os.path.exists(db_path):
    os.remove(db_path)
    print("🧹 Alte flow_study.db gelöscht.")

conn = sqlite3.connect(db_path)
conn.executescript("""
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    who5_pre_1 INTEGER,
    who5_pre_2 INTEGER,
    who5_pre_3 INTEGER,
    who5_pre_4 INTEGER,
    who5_pre_5 INTEGER,
    who5_pre_sum INTEGER,
    positive_pre_0_10 INTEGER,
    stressed_pre_0_10 INTEGER,
    flow_1 INTEGER,
    flow_2 INTEGER,
    flow_3 INTEGER,
    flow_4 INTEGER,
    flow_5 INTEGER,
    flow_6 INTEGER,
    flow_score REAL,
    who5_post_1 INTEGER,
    who5_post_2 INTEGER,
    who5_post_3 INTEGER,
    who5_post_4 INTEGER,
    who5_post_5 INTEGER,
    who5_post_sum INTEGER,
    positive_post_0_10 INTEGER,
    stressed_post_0_10 INTEGER,
    who5_pre_x4 INTEGER,
    who5_post_x4 INTEGER,
    delta_who5 INTEGER,
    delta_positive INTEGER,
    delta_stressed INTEGER
);

CREATE TABLE consent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    consent_version TEXT,
    consent_text TEXT,
    agreed INTEGER,
    user_agent TEXT
);
""")
conn.commit()
conn.close()

print("✅ Neue Datenbank erfolgreich erstellt (31 Spalten inklusive id).")
