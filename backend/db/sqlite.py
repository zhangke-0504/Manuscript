import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Allow overriding data directory via environment variable (used in Electron packaging).
DATA_DIR = os.getenv('BACKEND_DATA_DIR') or os.path.join(BASE_DIR, 'db')
# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)
DB_FILE = os.path.join(DATA_DIR, "novel.db")

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_now_sql_expr() -> str:
    try:
        off = datetime.now().astimezone().utcoffset()
        if off is None:
            raise ValueError("no utcoffset")
        return "datetime('now','localtime')"
    except Exception:
        return "datetime('now','+28800 seconds')"

def drop_trigger_if_exists(conn: sqlite3.Connection, name: str) -> None:
    conn.execute(f"DROP TRIGGER IF EXISTS {name}")

def recreate_insert_trigger(conn: sqlite3.Connection, table: str, now_sql: str) -> None:
    trg_name = f"trg_{table}_ts_after_insert"
    drop_trigger_if_exists(conn, trg_name)
    conn.executescript(f"""
    CREATE TRIGGER {trg_name}
    AFTER INSERT ON {table}
    FOR EACH ROW
    WHEN NEW.created_at IS NULL OR NEW.updated_at IS NULL
    BEGIN
        UPDATE {table}
        SET created_at = COALESCE(NEW.created_at, {now_sql}),
            updated_at = COALESCE(NEW.updated_at, {now_sql})
        WHERE uid = NEW.uid;
    END;
    """)

def recreate_update_trigger(conn: sqlite3.Connection, table: str, now_sql: str) -> None:
    trg_name = f"trg_{table}_ts_after_update"
    drop_trigger_if_exists(conn, trg_name)
    conn.executescript(f"""
    CREATE TRIGGER {trg_name}
    AFTER UPDATE ON {table}
    FOR EACH ROW
    BEGIN
        UPDATE {table}
        SET updated_at = {now_sql}
        WHERE uid = NEW.uid;
    END;
    """)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # NovelConfig 表
    cur.execute("""
    CREATE TABLE IF NOT EXISTS NovelConfig (
        uid TEXT PRIMARY KEY,
        title TEXT,
        genre TEXT,
        description TEXT,
        latest_chapter_uid TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)

    # Chapters 表
    cur.execute("""
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
    """)

    # Characters 表
    cur.execute("""
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
    """)

    # 触发器：确保时间戳自动填充/更新
    now_sql = get_now_sql_expr()
    for table in ("NovelConfig", "Chapters", "Characters"):
        recreate_insert_trigger(conn, table, now_sql)
        recreate_update_trigger(conn, table, now_sql)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("SQLite 数据库初始化完成 😊")