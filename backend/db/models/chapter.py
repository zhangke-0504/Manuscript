# ...existing code...
from dataclasses import dataclass
from typing import Optional

@dataclass
class Chapter:
    uid: Optional[str] = None
    novel_uid: str = ""
    chapter_idx: int = 0
    title: str = ""
    content: str = ""
    synopsis: str = ""  
    created_at: Optional[str] = None
    updated_at: Optional[str] = None