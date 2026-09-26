import sqlite3
from pathlib import Path

# Always use the database inside the project folder
DB_PATH = Path(__file__).resolve().parent / "studymate.db"


def create_table():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_chat(user_message, ai_response):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO chat_history (user_message, ai_response)
            VALUES (?, ?)
        """, (user_message, ai_response))


def get_chat_history():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT id, user_message, ai_response, created_at
            FROM chat_history
            ORDER BY id DESC
        """)
        return cursor.fetchall()


def clear_chat_history():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM chat_history")