# db/CRUD/character_crud.py
import uuid
from db.sqlite import get_connection
from db.models.character import Character

def create_character(novel_uid: str, name: str, desc: str, is_main: bool) -> str:
    conn = get_connection()
    cur = conn.cursor()
    uid = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO Characters (uid, novel_uid, name, description, is_main) VALUES (?, ?, ?, ?, ?)",
        (uid, novel_uid, name, desc, 1 if is_main else 0)
    )
    conn.commit()
    conn.close()
    return uid

def get_character(char_uid: str) -> Character | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Characters WHERE uid=?", (char_uid,))
    row = cur.fetchone()
    conn.close()
    return Character(**row) if row else None

def list_characters(novel_uid: str) -> list[Character]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Characters WHERE novel_uid=?", (novel_uid,))
    rows = cur.fetchall()
    conn.close()
    return [Character(**r) for r in rows]

def update_character(uid: str, name: str, desc: str, is_main: bool) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Characters 
        SET name=?, description=?, is_main=? 
        WHERE uid=?
    """, (name, desc, 1 if is_main else 0, uid))
    conn.commit()
    updated = cur.rowcount
    conn.close()
    return updated > 0

def delete_character(uid: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Characters WHERE uid=?", (uid,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted > 0
