# db/CRUD/novel_crud.py
import uuid
from db.sqlite import get_connection
from db.models.novel import Novel

def create_novel(title: str, genre: str, description: str) -> str:
    conn = get_connection()
    cur = conn.cursor()
    uid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO NovelConfig (uid, title, genre, description) VALUES (?, ?, ?, ?)",
        (uid, title, genre, description)
    )
    conn.commit()
    conn.close()
    return uid

def get_novel(novel_uid: str) -> Novel | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM NovelConfig WHERE uid=?", (novel_uid,))
    row = cur.fetchone()
    conn.close()
    return Novel(**row) if row else None

def list_novels() -> list[Novel]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM NovelConfig")
    rows = cur.fetchall()
    conn.close()
    return [Novel(**r) for r in rows]

def update_novel(novel_uid: str, title: str, genre: str, description: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
       UPDATE NovelConfig 
       SET title=?, genre=?, description=? 
       WHERE uid=?
    """, (title, genre, description, novel_uid))
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_novel(novel_uid: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM NovelConfig WHERE uid=?", (novel_uid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0
