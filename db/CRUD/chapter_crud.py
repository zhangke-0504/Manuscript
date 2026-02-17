import uuid
import sqlite3
from typing import List, Optional

import aiosqlite
from db.sqlite import DB_FILE
from db.models.chapter import Chapter


async def _connect() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn


async def create_chapter(novel_uid: str, chapter_idx: int, title: str, content: str, synopsis: str = "") -> str:
    uid = str(uuid.uuid4())
    conn = await _connect()
    try:
        await conn.execute(
            "INSERT INTO Chapters (uid, novel_uid, chapter_idx, title, content, synopsis) VALUES (?, ?, ?, ?, ?, ?)",
            (uid, novel_uid, chapter_idx, title, content, synopsis),
        )
        await conn.commit()
        return uid
    finally:
        await conn.close()


async def get_chapter(ch_uid: str) -> Optional[Chapter]:
    conn = await _connect()
    try:
        cur = await conn.execute("SELECT * FROM Chapters WHERE uid=?", (ch_uid,))
        row = await cur.fetchone()
        return Chapter(**row) if row else None
    finally:
        await conn.close()


async def list_chapters(novel_uid: str) -> List[Chapter]:
    conn = await _connect()
    try:
        cur = await conn.execute(
            "SELECT * FROM Chapters WHERE novel_uid=? ORDER BY chapter_idx",
            (novel_uid,),
        )
        rows = await cur.fetchall()
        return [Chapter(**r) for r in rows]
    finally:
        await conn.close()


async def update_chapter(uid: str, title: str, content: str, synopsis: Optional[str] = None) -> bool:
    conn = await _connect()
    try:
        if synopsis is None:
            cur = await conn.execute(
                "UPDATE Chapters SET title=?, content=? WHERE uid=?",
                (title, content, uid),
            )
        else:
            cur = await conn.execute(
                "UPDATE Chapters SET title=?, content=?, synopsis=? WHERE uid=?",
                (title, content, synopsis, uid),
            )
        await conn.commit()
        return cur.rowcount > 0
    finally:
        await conn.close()


async def delete_chapter(uid: str) -> bool:
    conn = await _connect()
    try:
        cur = await conn.execute("DELETE FROM Chapters WHERE uid=?", (uid,))
        await conn.commit()
        return cur.rowcount > 0
    finally:
        await conn.close()