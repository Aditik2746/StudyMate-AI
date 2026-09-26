import sqlite3
from pathlib import Path

# Always use the database inside the project folder
DB_PATH = Path(__file__).resolve().parent / "studymate.db"


def create_table():
    with sqlite3.connect(DB_PATH) as conn:

        # Create the table if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Check whether user_id already exists
        cursor = conn.execute("PRAGMA table_info(chat_history)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add user_id to an existing database if needed
        if "user_id" not in columns:
            conn.execute("""
                ALTER TABLE chat_history
                ADD COLUMN user_id TEXT
            """)


def save_chat(user_id, user_message, ai_response):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO chat_history
            (user_id, user_message, ai_response)
            VALUES (?, ?, ?)
        """, (user_id, user_message, ai_response))


def get_chat_history(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT id, user_message, ai_response, created_at
            FROM chat_history
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))

        return cursor.fetchall()


def clear_chat_history(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            DELETE FROM chat_history
            WHERE user_id = ?
        """, (user_id,))