import sqlite3
from typing import List, Tuple

def get_connection():
    return sqlite3.connect('notes.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        note TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()

def add_note(user_id: int, note: str) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO notes (user_id, note) VALUES (?, ?)', (user_id, note))
    conn.commit()

def get_notes(user_id: int) -> List[Tuple[int, str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, note FROM notes WHERE user_id = ?', (user_id,))
    return cursor.fetchall()

def delete_note(note_id: int) -> None:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()

# Инициализация БД при импорте
init_db()
