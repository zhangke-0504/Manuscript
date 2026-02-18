from dataclasses import dataclass
from typing import Optional

@dataclass
class Novel:
    uid: Optional[str] = None
    title: str = ""
    genre: str = ""
    description: str = ""
    latest_chapter_uid: Optional[str] = None  # 用户最新编辑修改的章节uid
    created_at: Optional[str] = None
    updated_at: Optional[str] = None