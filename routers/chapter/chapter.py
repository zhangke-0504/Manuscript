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
    list_chapters
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
def create_chapter_endpoint(payload: ChapterCreateResponse):
    uid = create_chapter(payload.novel_uid, payload.chapter_idx, payload.title, payload.content)
    ch = get_chapter(uid)
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
def get_chapter_endpoint(payload: GetChapterRequest):
    ch = get_chapter(payload.uid)
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
@router.post("/update", response_model=ChapterResponse)
def update_chapter_endpoint(payload: ChapterUpdateRequest):
    # title和content不能同时为空
    if not payload.title and not payload.content:
        raise ManuScriptValidationMsg(msg="Title and content cannot be empty at the same time", code=ResponseCode.CLIENT_ERROR.value)
    # 获取当前章节信息，用来更新
    old_ch = get_chapter(payload.uid)
    if not old_ch:
        raise ManuScriptValidationMsg(msg="Chapter not found", code=ResponseCode.CLIENT_ERROR.value)
    # 根据传入字段来决定哪些字段是老字段不需要更新,从old_ch里取出来传给update_chapter
    title = payload.title if payload.title else old_ch.title
    content = payload.content if payload.content else old_ch.content
    updated = update_chapter(payload.uid, title, content)
    if not updated:
        raise ManuScriptValidationMsg(msg="Failed to update chapter", code=ResponseCode.SERVER_ERROR.value)
    # 获取更新后的章节信息
    ch = get_chapter(payload.uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Chapter not found after update", code=ResponseCode.SERVER_ERROR.value)
    return ChapterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Chapter updated successfully",
        data=asdict(ch),
    )


class DeleteChapterRequest(BaseModel):
    uid: str
@router.post("/delete", response_model=ChapterResponse)
def delete_chapter_endpoint(payload: DeleteChapterRequest):
    deleted = delete_chapter(payload.uid)
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
def list_chapter_endpoint(payload: ChapterListRequest):
    items = list_chapters(payload.novel_uid)  # 按 chapter_idx 排序
    total = len(items)
    start = (payload.page - 1) * payload.size
    end = start + payload.size
    paged = items[start:end]

    # 返回需要的字段
    simplified: List[Dict] = [
        {
            "title": ch.title, 
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