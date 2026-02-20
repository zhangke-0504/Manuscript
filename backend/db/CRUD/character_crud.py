# db/CRUD/character_crud.py
import uuid
import sqlite3
from typing import Optional, List

import aiosqlite
from db.sqlite import DB_FILE
from db.models.character import Character


async def _connect() -> aiosqlite.Connection:
    conn = await aiosqlite.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn


async def create_character(novel_uid: str, name: str, desc: str, is_main: bool) -> str:
    uid = str(uuid.uuid4())
    conn = await _connect()
    try:
        await conn.execute(
            "INSERT INTO Characters (uid, novel_uid, name, description, is_main) VALUES (?, ?, ?, ?, ?)",
            (uid, novel_uid, name, desc, 1 if is_main else 0),
        )
        await conn.commit()
        return uid
    finally:
        await conn.close()


async def get_character(char_uid: str) -> Optional[Character]:
    conn = await _connect()
    try:
        cur = await conn.execute("SELECT * FROM Characters WHERE uid=?", (char_uid,))
        row = await cur.fetchone()
        return Character(**row) if row else None
    finally:
        await conn.close()


async def list_characters(novel_uid: str) -> List[Character]:
    conn = await _connect()
    try:
        # Order characters by creation time ascending (earlier first)
        cur = await conn.execute("SELECT * FROM Characters WHERE novel_uid=? ORDER BY created_at ASC", (novel_uid,))
        rows = await cur.fetchall()
        return [Character(**r) for r in rows]
    finally:
        await conn.close()


async def update_character(uid: str, name: str, desc: str, is_main: bool) -> bool:
    conn = await _connect()
    try:
        cur = await conn.execute(
            "UPDATE Characters SET name=?, description=?, is_main=? WHERE uid=?",
            (name, desc, 1 if is_main else 0, uid),
        )
        await conn.commit()
        return cur.rowcount > 0
    finally:
        await conn.close()


async def delete_character(uid: str) -> bool:
    conn = await _connect()
    try:
        cur = await conn.execute("DELETE FROM Characters WHERE uid=?", (uid,))
        await conn.commit()
        return cur.rowcount > 0
    finally:
        await conn.close()