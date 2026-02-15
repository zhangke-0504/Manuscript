# db/CRUD/chapter_crud.py
import uuid
from db.sqlite import get_connection
from db.models.chapter import Chapter
from typing import Optional, Dict

def create_chapter(novel_uid: str, chapter_idx: int, title: str, content: str) -> str:
    conn = get_connection()
    cur = conn.cursor()
    uid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO Chapters (uid, novel_uid, chapter_idx, title, content) VALUES (?, ?, ?, ?, ?)",
        (uid, novel_uid, chapter_idx, title, content)
    )
    conn.commit()
    conn.close()
    return uid

def get_chapter(ch_uid: str) -> Chapter | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Chapters WHERE uid=?", (ch_uid,))
    row = cur.fetchone()
    conn.close()
    return Chapter(**row) if row else None

def list_chapters(novel_uid: str) -> list[Chapter]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Chapters WHERE novel_uid=? ORDER BY chapter_idx", (novel_uid,))
    rows = cur.fetchall()
    conn.close()
    return [Chapter(**r) for r in rows]

def update_chapter(uid: str, title: str, content: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Chapters SET title=?, content=? WHERE uid=?",
        (title, content, uid)
    )
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_chapter(uid: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Chapters WHERE uid=?", (uid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0
