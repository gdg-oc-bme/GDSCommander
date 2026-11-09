import sqlite3
import os

# Docker sets DB_PATH to a mounted volume so the data survives redeploys
DB_PATH = os.getenv("DB_PATH", "gdscommander.db")

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
    # meetings made with /meeting, times are utc
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT,
            channel_id TEXT,
            message_id TEXT,
            organizer_id TEXT,
            role_ids TEXT,
            user_ids TEXT,
            starts_at TEXT,
            duration_minutes INTEGER,
            title TEXT,
            description TEXT,
            room TEXT,
            link TEXT,
            status TEXT DEFAULT 'scheduled',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # dbs made before a column existed get it added here
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(meetings)")}
    for column, kind in [("user_ids", "TEXT")]:
        if column not in columns:
            cursor.execute(f"ALTER TABLE meetings ADD COLUMN {column} {kind}")
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

def save_meeting(guild_id, channel_id, message_id, organizer_id, role_ids, user_ids, starts_at, duration_minutes, title, description, room, link):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO meetings (guild_id, channel_id, message_id, organizer_id, role_ids, user_ids, starts_at, duration_minutes, title, description, room, link)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (str(guild_id), str(channel_id), str(message_id), str(organizer_id), ",".join(map(str, role_ids)), ",".join(map(str, user_ids)),
          starts_at, duration_minutes, title, description, room, link))
    conn.commit()
    conn.close()

def list_user_mappings():
    """Returns all current mappings for validation logs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT discord_id, superthread_email, superthread_user_id, preferred_board_id FROM user_mapping")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
