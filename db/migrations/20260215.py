# migration: add created_at / updated_at to three tables and auto-maintain via triggers (localtime or fallback +8)
import os
import sqlite3
from typing import Iterable
from datetime import datetime

# DB 路径：与 sqlite.py 保持一致（db/novel.db）
DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(DB_DIR, "novel.db")

TABLES: Iterable[str] = ("NovelConfig", "Chapters", "Characters")

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

def drop_trigger_if_exists(conn: sqlite3.Connection, name: str) -> None:
    conn.execute(f"DROP TRIGGER IF EXISTS {name}")

def get_now_sql_expr() -> str:
    # 优先使用本地时区；若失败则回退东八区
    try:
        off = datetime.now().astimezone().utcoffset()
        if off is None:
            raise ValueError("no utcoffset")
        # 推荐直接使用 localtime，支持 DST 且随系统时区变化
        return "datetime('now','localtime')"
    except Exception:
        # 回退固定 +8 小时（不随 DST）
        return "datetime('now','+28800 seconds')"

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

def upgrade(conn: sqlite3.Connection) -> None:
    # 1) 添加列（不可带非常量默认）
    for table in TABLES:
        ensure_column(conn, table, "created_at", "created_at TEXT")
        ensure_column(conn, table, "updated_at", "updated_at TEXT")

    now_sql = get_now_sql_expr()

    # 2) 回填历史数据（空值补为当前本地时区或东八区时间）
    for table in TABLES:
        conn.execute(f"""
            UPDATE {table}
            SET created_at = COALESCE(created_at, {now_sql}),
                updated_at = COALESCE(updated_at, {now_sql})
            WHERE created_at IS NULL OR updated_at IS NULL
        """)

    # 3) 触发器：插入时补齐时间戳；更新时刷新 updated_at（重建以应用新的时区策略）
    for table in TABLES:
        recreate_insert_trigger(conn, table, now_sql)
        recreate_update_trigger(conn, table, now_sql)

def main() -> None:
    print(f"Using DB: {DB_FILE}")
    conn = get_connection()
    try:
        conn.execute("BEGIN")
        upgrade(conn)
        conn.commit()
        print("Migration 20260215 applied successfully.")
    except Exception as e:
        conn.rollback()
        print(f"Migration 20260215 failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()