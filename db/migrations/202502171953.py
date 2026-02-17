# migration: rebuild child tables (Chapters, Characters) to add ON DELETE CASCADE on foreign keys
import os
import sqlite3
from datetime import datetime

DB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(DB_DIR, "novel.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_now_sql_expr() -> str:
    try:
        off = datetime.now().astimezone().utcoffset()
        if off is None:
            raise ValueError("no utcoffset")
        return "datetime('now','localtime')"
    except Exception:
        return "datetime('now','+28800 seconds')"

def has_cascade(conn: sqlite3.Connection, table: str, ref_table: str = "NovelConfig") -> bool:
    rows = conn.execute(f"PRAGMA foreign_key_list('{table}')").fetchall()
    for r in rows:
        # r has columns including 'table' and 'on_delete'
        if r["table"] == ref_table and (r["on_delete"].upper() == "CASCADE"):
            return True
    return False

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

def rebuild_table_with_cascade(conn: sqlite3.Connection, table: str) -> None:
    """
    Rebuilds the given child table to ensure FOREIGN KEY (novel_uid) REFERENCES NovelConfig(uid) ON DELETE CASCADE.
    Assumes the child table schema matches the project's expected columns.
    """
    if table == "Chapters":
        cols = ["uid", "novel_uid", "chapter_idx", "title", "content", "synopsis", "created_at", "updated_at"]
        create_sql = f"""
        CREATE TABLE tmp_{table} (
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
        """
    elif table == "Characters":
        cols = ["uid", "novel_uid", "name", "description", "is_main", "created_at", "updated_at"]
        create_sql = f"""
        CREATE TABLE tmp_{table} (
            uid TEXT PRIMARY KEY,
            novel_uid TEXT,
            name TEXT NOT NULL,
            description TEXT,
            is_main INTEGER NOT NULL DEFAULT 0,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (novel_uid) REFERENCES NovelConfig(uid) ON DELETE CASCADE
        )
        """
    else:
        raise RuntimeError("unsupported table")

    cols_str = ", ".join(cols)

    # create tmp table
    conn.execute(create_sql)
    # copy existing data (ignore missing columns by selecting declared cols; if older schema lacks a col, NULL will be inserted)
    conn.execute(f"INSERT INTO tmp_{table} ({cols_str}) SELECT {cols_str} FROM {table}")
    # drop old table and rename tmp
    conn.execute(f"DROP TABLE {table}")
    conn.execute(f"ALTER TABLE tmp_{table} RENAME TO {table}")

def main() -> None:
    print(f"Applying migration to DB: {DB_FILE}")
    conn = get_connection()
    try:
        # quick check whether migration required
        need = False
        for t in ("Chapters", "Characters"):
            if not has_cascade(conn, t):
                need = True
                break
        if not need:
            print("No changes required: child tables already have ON DELETE CASCADE.")
            return

        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("BEGIN")

        # drop existing triggers for those tables (they will be recreated)
        for t in ("Chapters", "Characters"):
            drop_trigger_if_exists(conn, f"trg_{t}_ts_after_insert")
            drop_trigger_if_exists(conn, f"trg_{t}_ts_after_update")

        # rebuild each table
        for t in ("Chapters", "Characters"):
            print(f"Rebuilding table {t} with ON DELETE CASCADE...")
            rebuild_table_with_cascade(conn, t)

        # recreate triggers (use same logic as sqlite.py)
        now_sql = get_now_sql_expr()
        for t in ("NovelConfig", "Chapters", "Characters"):
            recreate_insert_trigger(conn, t, now_sql)
            recreate_update_trigger(conn, t, now_sql)

        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        print("Migration applied successfully: child tables now use ON DELETE CASCADE.")
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()