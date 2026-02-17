from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import List, Optional, Set
import json
from starlette.responses import StreamingResponse
import asyncio

from db.CRUD.novel_crud import get_novel, update_latest_chapter_uid
from db.CRUD.character_crud import create_character, list_characters
from db.CRUD.chapter_crud import create_chapter
from agents.character_agent import CharacterAgent
from agents.chapter_agent import ChapterAgent, ChapterOutlineItem

from utils.enum import ResponseCode
from utils.error import ManuScriptValidationMsg

router = APIRouter()
logger = logging.getLogger("working_flow_router")



class GenerateCharactersRequest(BaseModel):
    novel_uid: str
    provider: str  
@router.post("/create_characters")
async def create_characters(payload: GenerateCharactersRequest):
    """
    SSE 接口：根据小说 uid 读取小说信息，使用 CharacterAgent 流式生成角色。
    每当流中完整拼凑出一个角色字典并持久化后，向前端推送一个 SSE 事件（单条 JSON data）。
    最后推送一个完成事件，包含所有已创建的 character uids 列表。
    """
    logger.info("Create characters (SSE) for novel uid=%s", payload.novel_uid)
    novel = await get_novel(payload.novel_uid)
    if not novel:
        raise ManuScriptValidationMsg(msg="Novel not found", code=ResponseCode.CLIENT_ERROR.value)

    async def event_generator():
        created_uids: List[str] = []
        try:
            agent = CharacterAgent(provider=payload.provider)
        except Exception as e:
            logger.exception("Failed to init CharacterAgent for novel %s", payload.novel_uid)
            err = {"type": "error", "message": "Agent init failed"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
            return

        try:
            start = {"type": "start", "character_uids": created_uids}
            yield f"data: {json.dumps(start, ensure_ascii=False)}\n\n"
            async for char in agent.generate_characters_stream(novel):
                try:
                    # char 可能是 dataclass Character 类型或类字典类型；进行标准化处理
                    if hasattr(char, "__dict__"):
                        novel_uid = getattr(char, "novel_uid", payload.novel_uid)
                        name = getattr(char, "name", "")
                        description = getattr(char, "description", "")
                        is_main = bool(getattr(char, "is_main", False))
                    elif isinstance(char, dict):
                        novel_uid = char.get("novel_uid") or payload.novel_uid
                        name = char.get("name", "")
                        description = char.get("description", "")
                        is_main = bool(char.get("is_main", False))
                    else:
                        # 不支持的条目，跳过
                        continue

                    uid = await create_character(novel_uid, name, description, is_main)
                    created_uids.append(uid)

                    payload_event = {
                        "type": "character",
                        "character": {
                            "uid": uid,
                            "novel_uid": novel_uid,
                            "name": name,
                            "description": description,
                            "is_main": is_main,
                        },
                        "created_count": len(created_uids),
                    }
                    yield f"data: {json.dumps(payload_event, ensure_ascii=False)}\n\n"
                except Exception:
                    logger.exception("Failed to persist or send character for novel %s", payload.novel_uid)
                    # 为此角色发送一个错误事件，然后继续
                    err = {"type": "error", "message": "persist failed for a character"}
                    yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
                    continue

        except Exception:
            logger.exception("Character generation stream failed for novel %s", payload.novel_uid)
            err = {"type": "error", "message": "character generation stream failed"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
        finally:
            done = {"type": "done", "character_uids": created_uids}
            yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class GenerateOutlineRequest(BaseModel):
    novel_uid: str
    provider: str
    target_chapters: Optional[int] = None

@router.post("/create_chapter_outline")
async def create_chapter_outline(payload: GenerateOutlineRequest):
    logger.info("Create chapter outline (SSE) for novel uid=%s", payload.novel_uid)
    novel = await get_novel(payload.novel_uid)
    if not novel:
        raise ManuScriptValidationMsg(msg="Novel not found", code=ResponseCode.CLIENT_ERROR.value)

    characters = await list_characters(payload.novel_uid)

    async def event_generator():
        created_uids: List[str] = []
        created_indices: Set[int] = set()
        queue: asyncio.Queue = asyncio.Queue()

        try:
            agent = ChapterAgent(provider=payload.provider)
        except Exception:
            logger.exception("Failed to init ChapterAgent for novel %s", payload.novel_uid)
            err = {"type": "error", "message": "Agent init failed"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
            return

        # callback: 当流式解析出一个 ChapterOutlineItem 时放入队列
        async def on_outline_item(item: ChapterOutlineItem):
            await queue.put(item)

        # 启动生成目录任务
        gen_task = asyncio.create_task(
            agent.stream_generate_directory(
                novel_title=novel.title,
                genre=novel.genre,
                description=novel.description,
                characters=characters,
                target_chapters=payload.target_chapters,
                language=None,
                on_outline_item=on_outline_item,
                on_token=None
            )
        )

        # 发送 start 事件
        start = {"type": "start", "chapter_uids": created_uids}
        yield f"data: {json.dumps(start, ensure_ascii=False)}\n\n"

        try:
            # 持续消费队列并持久化每个章节，直到生成任务结束且队列为空
            while True:
                try:
                    item: ChapterOutlineItem = await asyncio.wait_for(queue.get(), timeout=0.2)
                except asyncio.TimeoutError:
                    if gen_task.done():
                        break
                    continue

                try:
                    # 持久化章节到 DB
                    chapter_uid = await create_chapter(
                        novel_uid=payload.novel_uid, 
                        chapter_idx=item.index, 
                        title=item.title, 
                        synopsis=item.synopsis
                    )
                    created_uids.append(chapter_uid)
                    created_indices.add(item.index)

                    payload_event = {
                        "type": "chapter",
                        "chapter": {
                            "uid": chapter_uid,
                            "novel_uid": payload.novel_uid,
                            "index": item.index,
                            "title": item.title,
                            "synopsis": item.synopsis,
                        },
                        "created_count": len(created_uids),
                    }
                    yield f"data: {json.dumps(payload_event, ensure_ascii=False)}\n\n"
                except Exception:
                    logger.exception("Failed to persist or send chapter for novel %s", payload.novel_uid)
                    err = {"type": "error", "message": "persist failed for a chapter"}
                    yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
                    continue

            # 等待生成任务完成以收集可能的后备解析结果（stream_generate_directory 会返回完整列表）
            try:
                final_items = await gen_task
            except Exception:
                logger.exception("Chapter generation task failed for novel %s", payload.novel_uid)
                err = {"type": "error", "message": "chapter generation failed"}
                yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
                final_items = []

            # final_items 可能为 List[ChapterOutlineItem]
            for it in final_items:
                if it.index in created_indices:
                    continue
                # 尝试持久化补充项（若数据库已有该 index，可在 create_chapter 内处理冲突）
                try:
                    chapter_uid = await create_chapter(
                        novel_uid=payload.novel_uid, 
                        chapter_idx=item.index, 
                        title=item.title, 
                        synopsis=item.synopsis
                    )
                    created_uids.append(chapter_uid)
                    created_indices.add(it.index)
                    payload_event = {
                        "type": "chapter",
                        "chapter": {
                            "uid": chapter_uid,
                            "novel_uid": payload.novel_uid,
                            "index": it.index,
                            "title": it.title,
                            "synopsis": it.synopsis,
                        },
                        "created_count": len(created_uids),
                    }
                    yield f"data: {json.dumps(payload_event, ensure_ascii=False)}\n\n"
                except Exception:
                    # 忽略重复或持久化失败
                    continue
        finally:
            done = {"type": "done", "chapter_uids": created_uids}
            yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")