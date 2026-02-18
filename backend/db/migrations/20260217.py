import os
import sqlite3
from typing import Iterable

DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(DB_DIR, "novel.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def has_column(conn: sqlite3.Connection, table: str, column: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r["name"] == column for r in rows)

def ensure_column(conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
    if not has_column(conn, table, column):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {ddl}")

def upgrade(conn: sqlite3.Connection) -> None:
    # 1) 添加 synopsis 列（默认空字符串，便于回退与查询）
    ensure_column(conn, "Chapters", "synopsis", "synopsis TEXT DEFAULT ''")

    # 2) 回填历史数据（将 NULL 置为 ''）
    conn.execute("""
        UPDATE Chapters
        SET synopsis = COALESCE(synopsis, '')
        WHERE synopsis IS NULL
    """)

def main() -> None:
    print(f"Using DB: {DB_FILE}")
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        upgrade(conn)
        conn.commit()
        print("Migration 20260217 applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Migration 20260217 failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()