# db/models/novel.py
from typing import Optional
from dataclasses import asdict
from db.CRUD.novel_crud import (
    create_novel, 
    get_novel, 
    update_novel, 
    delete_novel, 
    list_novels
)
from utils.enum import ResponseCode
from utils.error import ManuScriptValidationMsg
import logging
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import Optional, Dict


router = APIRouter()
logger = logging.getLogger("novel_router")

class NovelResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Dict] = None

class NovelCreate(BaseModel):
    title: str
    genre: str
    description: str
@router.post("/create", response_model=NovelResponse)
def create_novel_endpoint(payload: NovelCreate):
    uid = create_novel(payload.title, payload.genre, payload.description)
    novel = get_novel(uid)
    if not novel:
        raise ManuScriptValidationMsg(msg="Failed to create novel", code=ResponseCode.SERVER_ERROR.value)
    return NovelResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Novel created successfully",
        data=asdict(novel)
    )

class GetNovelRequest(BaseModel):
    uid: str
@router.post("/get", response_model=NovelResponse)
def get_novel_endpoint(payload: GetNovelRequest):
    novel = get_novel(payload.uid)
    if not novel:
        raise ManuScriptValidationMsg(msg="Novel not found", code=ResponseCode.CLIENT_ERROR.value)
    return NovelResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Get novel successfully",
        data=asdict(novel)
    )
class NovelUpdateRequest(BaseModel):
    uid: str
    title: str
    genre: str
    description: str
@router.post("/update", response_model=NovelResponse)
def update_novel_endpoint(payload: NovelUpdateRequest):
    updated = update_novel(payload.uid, payload.title, payload.genre, payload.description)
    if not updated:
        raise ManuScriptValidationMsg(msg="Failed to update novel", code=ResponseCode.SERVER_ERROR.value)
    novel = get_novel(payload.uid)
    if not novel:
        raise ManuScriptValidationMsg(msg="Novel not found after update", code=ResponseCode.SERVER_ERROR.value)
    return NovelResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Novel updated successfully",
        data=asdict(novel)
    )

class DeleteNovelRequest(BaseModel):
    uid: str
@router.post("/delete", response_model=NovelResponse)
def delete_novel_endpoint(payload: DeleteNovelRequest):
    deleted = delete_novel(payload.uid)
    if not deleted:
        raise ManuScriptValidationMsg(msg="Failed to delete novel", code=ResponseCode.SERVER_ERROR.value)
    return NovelResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Novel deleted successfully",
    )

class NovelListRequest(BaseModel):
    page: int = Field(default=1, ge=1)
    size: int = Field(default=100, ge=1, le=1000)

@router.post("/list", response_model=NovelResponse)
def list_novel_endpoint(payload: Optional[NovelListRequest] = None):
    req = payload or NovelListRequest()  # 允许空请求体
    items = list_novels()
    total = len(items)
    start = (req.page - 1) * req.size
    end = start + req.size
    paged = items[start:end]
    return NovelResponse(
        code=ResponseCode.SUCCESS.value,
        msg="List novels successfully",
        data={
            "items": [asdict(n) for n in paged],
            "total": total,
            "page": req.page,
            "size": req.size,
        },
    )