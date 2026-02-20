import uuid
import sqlite3
from typing import Optional, List

import aiosqlite
from db.sqlite import DB_FILE
from db.models.novel import Novel

async def _connect() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn

async def create_novel(title: str, genre: str, description: str, latest_chapter_uid: Optional[str] = None) -> str:
    uid = str(uuid.uuid4())
    conn = await _connect()
    try:
        await conn.execute(
            "INSERT INTO NovelConfig (uid, title, genre, description, latest_chapter_uid) VALUES (?, ?, ?, ?, ?)",
            (uid, title, genre, description, latest_chapter_uid),
        )
        await conn.commit()
        return uid
    finally:
        await conn.close()

async def get_novel(novel_uid: str) -> Optional[Novel]:
    conn = await _connect()
    try:
        cur = await conn.execute("SELECT * FROM NovelConfig WHERE uid=?", (novel_uid,))
        row = await cur.fetchone()
        return Novel(**row) if row else None
    finally:
        await conn.close()

async def list_novels() -> List[Novel]:
    conn = await _connect()
    try:
        # Order novels by updated_at descending (most recently updated first)
        cur = await conn.execute("SELECT * FROM NovelConfig ORDER BY updated_at DESC")
        rows = await cur.fetchall()
        return [Novel(**r) for r in rows]
    finally:
        await conn.close()

async def update_novel(novel_uid: str, title: str, genre: str, description: str, latest_chapter_uid: Optional[str] = None) -> bool:
    conn = await _connect()
    try:
        cur = await conn.execute(
            "UPDATE NovelConfig SET title=?, genre=?, description=?, latest_chapter_uid=? WHERE uid=?",
            (title, genre, description, latest_chapter_uid, novel_uid),
        )
        await conn.commit()
        return cur.rowcount > 0
    finally:
        await conn.close()

async def update_latest_chapter_uid(novel_uid: str, latest_chapter_uid: str) -> bool:
    conn = await _connect()
    try:
        cur = await conn.execute(
            "UPDATE NovelConfig SET latest_chapter_uid=? WHERE uid=?",
            (latest_chapter_uid, novel_uid),
        )
        await conn.commit()
        return cur.rowcount > 0
    finally:
        await conn.close()

async def delete_novel(novel_uid: str) -> bool:
    conn = await _connect()
    try:
        cur = await conn.execute("DELETE FROM NovelConfig WHERE uid=?", (novel_uid,))
        await conn.commit()
        return cur.rowcount > 0        
    finally:
        await conn.close()