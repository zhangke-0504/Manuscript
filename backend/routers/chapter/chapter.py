# routers/chapter/chapter.py
import logging
from dataclasses import asdict
from typing import Optional, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db.CRUD.chapter_crud import (
    create_chapter,
    get_chapter,
    update_chapter,
    delete_chapter,
    list_chapters,
)
from utils.enum import ResponseCode
from utils.error import ManuScriptValidationMsg

router = APIRouter()
logger = logging.getLogger("chapter_router")


class ChapterResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Dict] = None


class ChapterCreateResponse(BaseModel):
    novel_uid: str
    chapter_idx: int
    title: str
    content: str


@router.post("/create", response_model=ChapterResponse)
async def create_chapter_endpoint(payload: ChapterCreateResponse):
    uid = await create_chapter(payload.novel_uid, payload.chapter_idx, payload.title, payload.content)
    ch = await get_chapter(uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Failed to create chapter", code=ResponseCode.SERVER_ERROR.value)
    return ChapterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Chapter created successfully",
        data=asdict(ch),
    )


class GetChapterRequest(BaseModel):
    uid: str


@router.post("/get", response_model=ChapterResponse)
async def get_chapter_endpoint(payload: GetChapterRequest):
    ch = await get_chapter(payload.uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Chapter not found", code=ResponseCode.CLIENT_ERROR.value)
    return ChapterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Get chapter successfully",
        data=asdict(ch),
    )


class ChapterUpdateRequest(BaseModel):
    uid: str
    title: Optional[str] = None
    content: Optional[str] = None
    synopsis: Optional[str] = None


@router.post("/update", response_model=ChapterResponse)
async def update_chapter_endpoint(payload: ChapterUpdateRequest):
    if not payload.title and not payload.content and not payload.synopsis:
        raise ManuScriptValidationMsg(
            msg="Title 、content and synopsis cannot be empty at the same time",
            code=ResponseCode.CLIENT_ERROR.value,
        )
    old_ch = await get_chapter(payload.uid)
    if not old_ch:
        raise ManuScriptValidationMsg(msg="Chapter not found", code=ResponseCode.CLIENT_ERROR.value)

    title = payload.title if payload.title else old_ch.title
    content = payload.content if payload.content else old_ch.content
    synopsis = payload.synopsis if payload.synopsis is not None else old_ch.synopsis

    updated = await update_chapter(
        uid=payload.uid, 
        title=title, 
        content=content,
        synopsis=synopsis
    )
    if not updated:
        raise ManuScriptValidationMsg(msg="Failed to update chapter", code=ResponseCode.SERVER_ERROR.value)

    ch = await get_chapter(payload.uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Chapter not found after update", code=ResponseCode.SERVER_ERROR.value)
    return ChapterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Chapter updated successfully",
        data=asdict(ch),
    )


class DeleteChapterRequest(BaseModel):
    uids: List[str]
@router.post("/delete", response_model=ChapterResponse)
async def delete_chapter_endpoint(payload: DeleteChapterRequest):
    for uid in payload.uids:
        deleted = await delete_chapter(uid)
        if not deleted:
            raise ManuScriptValidationMsg(msg="Failed to delete chapter", code=ResponseCode.SERVER_ERROR.value)
    return ChapterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Chapter deleted successfully",
    )


class ChapterListRequest(BaseModel):
    novel_uid: str
    page: int = Field(default=1, ge=1)
    size: int = Field(default=100, ge=1, le=1000)


@router.post("/list", response_model=ChapterResponse)
async def list_chapter_endpoint(payload: ChapterListRequest):
    items = await list_chapters(payload.novel_uid)  # 按 chapter_idx 排序
    total = len(items)
    start = (payload.page - 1) * payload.size
    end = start + payload.size
    paged = items[start:end]

    simplified: List[Dict] = [
        {
            "title": ch.title,
            "synopsis": ch.synopsis,
            "chapter_uid": ch.uid,
            "chapter_idx": ch.chapter_idx,
            "created_at": ch.created_at,
            "updated_at": ch.updated_at,
        }
        for ch in paged
    ]

    return ChapterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="List chapters successfully",
        data={
            "items": simplified,
            "total": total,
            "page": payload.page,
            "size": payload.size,
        },
    )