# migration: fix typo column, add latest_chapter_uid to NovelConfig and set to '' for old data
import os
import sqlite3

DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(DB_DIR, "novel.db")
TABLE = "NovelConfig"
CORRECT_COLUMN = "latest_chapter_uid"
WRONG_COLUMN = "lastest_chapter_uid"  # 错误拼写

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)

def rename_column(conn: sqlite3.Connection, table: str, old: str, new: str) -> None:
    # SQLite 不支持直接 RENAME COLUMN，需重建表
    # 1. 获取原表结构
    columns = [r["name"] for r in conn.execute(f"PRAGMA table_info({table})")]
    if old not in columns:
        return
    columns_new = [new if c == old else c for c in columns]
    columns_str = ", ".join(columns)
    columns_new_str = ", ".join(columns_new)
    # 2. 创建临时表
    conn.execute(f"ALTER TABLE {table} RENAME TO {table}_old")
    # 3. 创建新表（修正字段名）
    # 这里直接用最新结构，建议用你项目的建表语句
    conn.execute(f"""
        CREATE TABLE {table} (
            uid TEXT PRIMARY KEY,
            title TEXT,
            genre TEXT,
            description TEXT,
            latest_chapter_uid TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    # 4. 拷贝数据
    conn.execute(f"""
        INSERT INTO {table} ({columns_new_str})
        SELECT {columns_str} FROM {table}_old
    """)
    # 5. 删除旧表
    conn.execute(f"DROP TABLE {table}_old")

def ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if not has_column(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

def upgrade(conn: sqlite3.Connection) -> None:
    # 1) 修正错误字段名
    if has_column(conn, TABLE, WRONG_COLUMN):
        rename_column(conn, TABLE, WRONG_COLUMN, CORRECT_COLUMN)
    # 2) 添加 latest_chapter_uid 字段（如果还没有）
    ensure_column(conn, TABLE, CORRECT_COLUMN, f"{CORRECT_COLUMN} TEXT")
    # 3) 旧数据补空字符串
    conn.execute(f"""
        UPDATE {TABLE}
        SET {CORRECT_COLUMN} = ''
        WHERE {CORRECT_COLUMN} IS NULL
    """)

def main() -> None:
    print(f"Using DB: {DB_FILE}")
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        upgrade(conn)
        conn.commit()
        print("Migration 202602171840 applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Migration 202602171840 failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()