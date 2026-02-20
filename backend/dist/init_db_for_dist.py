import os
import sqlite3
from datetime import datetime

base = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(base, 'db')
os.makedirs(db_dir, exist_ok=True)
DB_FILE = os.path.join(db_dir, 'novel.db')
conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS NovelConfig (
    uid TEXT PRIMARY KEY,
    title TEXT,
    genre TEXT,
    description TEXT,
    latest_chapter_uid TEXT,
    created_at TEXT,
    updated_at TEXT
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Chapters (
    uid TEXT PRIMARY KEY,
    novel_uid TEXT,
    chapter_idx INTEGER,
    title TEXT,
    content TEXT,
    synopsis TEXT DEFAULT '',
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (novel_uid) REFERENCES NovelConfig(uid) ON DELETE CASCADE
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS Characters (
    uid TEXT PRIMARY KEY,
    novel_uid TEXT,
    name TEXT NOT NULL,
    description TEXT,
    is_main INTEGER NOT NULL DEFAULT 0,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (novel_uid) REFERENCES NovelConfig(uid) ON DELETE CASCADE
)
''')

conn.commit()
conn.close()
print('Created DB at', DB_FILE)
