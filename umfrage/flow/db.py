import sqlite3
import os
from flask import g, current_app

# --- Sauberes Schema mit 31 Spalten (inkl. id) ---
SCHEMA = """
DROP TABLE IF EXISTS responses;
DROP TABLE IF EXISTS consent_logs;

CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    activity TEXT,
    level TEXT,
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
"""

def get_db():
    """Verbindung zu SQLite holen"""
    if "db" not in g:
        db_path = current_app.config.get("DB_PATH", os.path.join("instance", "flow_study.db"))
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """DB-Verbindung nach Request schließen"""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db(app):
    """Schema anwenden (DB neu erstellen)"""
    with app.app_context():
        db = get_db()
        db.executescript(SCHEMA)
        db.commit()
    app.teardown_appcontext(close_db)
