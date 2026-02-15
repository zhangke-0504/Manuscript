# routers/character/character.py
import logging
from dataclasses import asdict
from typing import Optional, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from db.CRUD.character_crud import (
    create_character,
    get_character,
    update_character,
    delete_character,
    list_characters,
)
from utils.enum import ResponseCode
from utils.error import ManuScriptValidationMsg

router = APIRouter()
logger = logging.getLogger("character_router")


class CharacterResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Dict] = None


class CharacterCreateRequest(BaseModel):
    novel_uid: str
    name: str
    description: str
    is_main: bool = False
@router.post("/create", response_model=CharacterResponse)
def create_character_endpoint(payload: CharacterCreateRequest):
    uid = create_character(payload.novel_uid, payload.name, payload.description, payload.is_main)
    ch = get_character(uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Failed to create character", code=ResponseCode.SERVER_ERROR.value)
    return CharacterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Character created successfully",
        data=asdict(ch),
    )


class GetCharacterRequest(BaseModel):
    uid: str
@router.post("/get", response_model=CharacterResponse)
def get_character_endpoint(payload: GetCharacterRequest):
    ch = get_character(payload.uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Character not found", code=ResponseCode.CLIENT_ERROR.value)
    return CharacterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Get character successfully",
        data=asdict(ch),
    )


class CharacterUpdateRequest(BaseModel):
    uid: str
    name: Optional[str] = None
    description: Optional[str] = None
    is_main: Optional[bool] = None
@router.post("/update", response_model=CharacterResponse)
def update_character_endpoint(payload: CharacterUpdateRequest):
    if payload.name is None and payload.description is None and payload.is_main is None:
        raise ManuScriptValidationMsg(
            msg="At least one of name/description/is_main must be provided",
            code=ResponseCode.CLIENT_ERROR.value,
        )
    old = get_character(payload.uid)
    if not old:
        raise ManuScriptValidationMsg(msg="Character not found", code=ResponseCode.CLIENT_ERROR.value)

    # 合并变更
    name = payload.name if payload.name is not None else old.name
    desc = payload.description if payload.description is not None else old.description
    is_main = payload.is_main if payload.is_main is not None else bool(old.is_main)

    updated = update_character(payload.uid, name, desc, is_main)
    if not updated:
        raise ManuScriptValidationMsg(msg="Failed to update character", code=ResponseCode.SERVER_ERROR.value)

    ch = get_character(payload.uid)
    if not ch:
        raise ManuScriptValidationMsg(msg="Character not found after update", code=ResponseCode.SERVER_ERROR.value)
    return CharacterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Character updated successfully",
        data=asdict(ch),
    )


class DeleteCharacterRequest(BaseModel):
    uid: str
@router.post("/delete", response_model=CharacterResponse)
def delete_character_endpoint(payload: DeleteCharacterRequest):
    deleted = delete_character(payload.uid)
    if not deleted:
        raise ManuScriptValidationMsg(msg="Failed to delete character", code=ResponseCode.SERVER_ERROR.value)
    return CharacterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Character deleted successfully",
    )


class CharacterListRequest(BaseModel):
    novel_uid: str
    page: int = Field(default=1, ge=1)
    size: int = Field(default=100, ge=1, le=1000)
@router.post("/list", response_model=CharacterResponse)
def list_character_endpoint(payload: CharacterListRequest):
    items = list_characters(payload.novel_uid)
    total = len(items)
    start = (payload.page - 1) * payload.size
    end = start + payload.size
    paged = items[start:end]

    simplified: List[Dict] = [
        {
            "name": c.name,
            "character_uid": c.uid,
            "is_main": bool(c.is_main),
            "created_at": c.created_at,
            "updated_at": c.updated_at,
        }
        for c in paged
    ]

    return CharacterResponse(
        code=ResponseCode.SUCCESS.value,
        msg="List characters successfully",
        data={
            "items": simplified,
            "total": total,
            "page": payload.page,
            "size": payload.size,
        },
    )