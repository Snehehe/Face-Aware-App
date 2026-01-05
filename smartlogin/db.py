import sqlite3
from pathlib import Path

# Database file lives in project root
DB_PATH = Path(__file__).resolve().parents[1] / "smartlogin.db"

def connect():
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("PRAGMA foreign_keys=ON;")
    return con

def init_db():
    con = connect()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS people (
        person_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS face_templates (
        template_id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id TEXT NOT NULL,
        embedding BLOB NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(person_id) REFERENCES people(person_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        person_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        confidence REAL NOT NULL,
        FOREIGN KEY(person_id) REFERENCES people(person_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS app_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        event_time TEXT NOT NULL,
        app_name TEXT NOT NULL,
        pid INTEGER,
        window_title TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(session_id)
    );
    """)

    con.commit()
    con.close()
