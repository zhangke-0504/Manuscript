# db/sqlite.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "db", "novel.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # 小说表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS NovelConfig (
        uid TEXT PRIMARY KEY,
        title TEXT,
        genre TEXT,
        description TEXT
    )
    """)

    # 章节表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Chapters (
        uid TEXT PRIMARY KEY,
        novel_uid TEXT,
        chapter_idx INTEGER,
        title TEXT,
        content TEXT,
        FOREIGN KEY (novel_uid) REFERENCES NovelConfig(uid)
    )
    """)

    # 角色表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Characters (
        uid TEXT PRIMARY KEY,
        novel_uid TEXT,
        name TEXT NOT NULL,
        description TEXT,
        is_main INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY (novel_uid) REFERENCES NovelConfig(uid)
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("SQLite 数据库初始化完成 😊")
