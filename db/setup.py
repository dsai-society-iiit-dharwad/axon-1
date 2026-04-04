import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "armor.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT,
            raw_transcript  TEXT,
            language        TEXT,
            duration_sec    REAL,
            speaker_count   INTEGER DEFAULT 2
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speaker_turns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id     INTEGER,
            speaker     TEXT,
            text        TEXT,
            start_sec   REAL,
            end_sec     REAL,
            FOREIGN KEY (conv_id) REFERENCES conversations(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id     INTEGER,
            speaker     TEXT,
            entity_type TEXT,
            raw_value   TEXT,
            normalized  TEXT,
            FOREIGN KEY (conv_id) REFERENCES conversations(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            conv_id        INTEGER,
            summary_text   TEXT,
            risk_score     INTEGER,
            risk_label     TEXT,
            risk_reasoning TEXT,
            FOREIGN KEY (conv_id) REFERENCES conversations(id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()

    # quick sanity check — list all tables
    conn = get_connection()
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    print(f"Tables created: {[t['name'] for t in tables]}")
    conn.close()
