import sqlite3
import os

DB_PATH = "gdscommander.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table to map Discord IDs to Superthread Email/UserIDs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_mapping (
            discord_id TEXT PRIMARY KEY,
            superthread_email TEXT,
            superthread_user_id TEXT,
            preferred_board_id TEXT
        )
    ''')
    # Table to store bot configuration (Board IDs, etc.)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_config (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_user_mapping(discord_id, email, user_id=None, board_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO user_mapping (discord_id, superthread_email, superthread_user_id, preferred_board_id)
        VALUES (?, ?, ?, ?)
    ''', (str(discord_id), email, user_id, board_id))
    conn.commit()
    conn.close()

def get_superthread_id(discord_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT superthread_user_id FROM user_mapping WHERE discord_id = ?', (str(discord_id),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def get_user_config(discord_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT superthread_email, superthread_user_id, preferred_board_id FROM user_mapping WHERE discord_id = ?', (str(discord_id),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"email": row[0], "user_id": row[1], "board_id": row[2]}
    return None

def get_discord_id_from_superthread(superthread_user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT discord_id FROM user_mapping WHERE superthread_user_id = ?', (superthread_user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
