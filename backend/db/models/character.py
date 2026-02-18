# db/models/character.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class Character:
    uid: Optional[str] = None
    novel_uid: str = ""
    name: str = ""
    description: str = ""
    is_main: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
