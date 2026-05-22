# ==============================
# components/database.py
# ==============================

import sqlite3
import os

os.makedirs("data", exist_ok=True)

conn = sqlite3.connect(
    "data/chats.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    message TEXT
)
""")

conn.commit()

def save_chat(role, message):

    cursor.execute(
        "INSERT INTO chats(role, message) VALUES (?, ?)",
        (role, message)
    )

    conn.commit()
