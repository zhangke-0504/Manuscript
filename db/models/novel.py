# db/models/novel.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Novel:
    uid: Optional[str] = None
    title: str = ""
    genre: str = ""
    description: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
