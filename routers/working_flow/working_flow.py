from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import logging
from typing import List, Optional, Set
import json
from starlette.responses import StreamingResponse
import asyncio

from db.CRUD.novel_crud import get_novel, update_latest_chapter_uid
from db.CRUD.character_crud import create_character, list_characters
from db.CRUD.chapter_crud import create_chapter, get_chapter, update_chapter
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

class GenerateChapterContentRequest(BaseModel):
    chapter_uid: str
    provider: str
    conversation_messages: Optional[List[dict]] = None  # 可选的多轮 messages（list of {"role","content"}）
    language: Optional[str] = None
    save_threshold: Optional[int] = 200  # 达到多少字符后持久化一次（可调）
    save_timeout_sec: Optional[float] = 1.0  # 没有新 token 时最终持久化前等待的超时时间

@router.post("/create_chapter_content")
async def create_chapter_content(payload: GenerateChapterContentRequest):
    """
    SSE 接口：对指定 chapter_uid 发起多轮/单轮流式生成正文。
    - 支持传入 conversation_messages 以做多轮上下文；
    - 在流式 token 到达时逐步回传 token（event type=token），并在累计达到 save_threshold 字符时将当前已生成内容写回 DB；
    - 最终在生成完成后写入最终 content，并返回 done 事件包含 chapter_uid 与最终长度。
    """
    chapter = await get_chapter(payload.chapter_uid)
    if not chapter:
        raise ManuScriptValidationMsg(msg="Chapter not found", code=ResponseCode.CLIENT_ERROR.value)

    novel_uid = getattr(chapter, "novel_uid", None)
    if not novel_uid:
        raise ManuScriptValidationMsg(msg="Chapter has no novel_uid", code=ResponseCode.CLIENT_ERROR.value)

    characters = await list_characters(novel_uid)

    async def event_generator():
        token_queue: asyncio.Queue = asyncio.Queue()
        buffer_parts: List[str] = []
        last_saved_len = 0
        save_threshold = payload.save_threshold or 200
        save_lock = asyncio.Lock()

        try:
            agent = ChapterAgent(provider=payload.provider)
        except Exception:
            logger.exception("Failed to init ChapterAgent for chapter %s", payload.chapter_uid)
            err = {"type": "error", "message": "Agent init failed"}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"
            return

        # 回调：把 token 放入队列（不直接 yield，避免回调内 yield 问题）
        async def on_token(piece: str):
            await token_queue.put(piece)

        # # 启动生成任务（并行消费 token 队列）
        # 为兼容 ChapterAgent 要求，构造单个 outline_item 来表示当前 chapter
        chapter_index = getattr(chapter, "chapter_idx", getattr(chapter, "index", 1))
        outline_item = ChapterOutlineItem(
            index=int(chapter_index),
            title=getattr(chapter, "title", "") or "",
            synopsis=getattr(chapter, "synopsis", "") or ""
        )
        print("发送给 ChapterAgent 的 入参:", {
            "outline_items": [outline_item],
            "all_characters": characters,
            "chapter_index": chapter_index,
            "prev_synopsis": getattr(chapter, "synopsis", "") or "",
            "next_synopsis": None,
            "language": payload.language,
            "conversation_messages": payload.conversation_messages
        })
        gen_task = asyncio.create_task(
            agent.stream_generate_chapter_content(
                outline_items=[outline_item],
                all_characters=characters,
                chapter_index=outline_item.index,
                prev_synopsis=None,
                next_synopsis=None,
                language=payload.language,
                on_token=on_token,
                conversation_messages=payload.conversation_messages
            )
        )

        # 发送 start 事件
        start = {"type": "start", "chapter_uid": payload.chapter_uid}
        yield f"data: {json.dumps(start, ensure_ascii=False)}\n\n"

        async def try_persist_if_needed():
            nonlocal last_saved_len
            async with save_lock:
                cur_content = "".join(buffer_parts)
                cur_len = len(cur_content)
                if cur_len - last_saved_len >= save_threshold:
                    # 保持 title/synopsis 不变，仅更新 content
                    try:
                        await update_chapter(payload.chapter_uid, chapter.title, cur_content, synopsis=getattr(chapter, "synopsis", None))
                        last_saved_len = cur_len
                        ev = {"type": "persist", "chapter_uid": payload.chapter_uid, "saved_len": cur_len}
                        await token_queue.put(json.dumps({"__persist_event__": ev}, ensure_ascii=False))
                    except Exception:
                        logger.exception("Failed to persist interim content for chapter %s", payload.chapter_uid)

        # 消费 token 队列并向客户端推送事件，同时进行增量持久化
        finished = False
        try:
            while True:
                try:
                    piece = await asyncio.wait_for(token_queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    # 若生成任务已完成且队列空，则退出
                    if gen_task.done():
                        break
                    continue

                # special persist marker
                if isinstance(piece, str) and piece.startswith('{"__persist_event__"'):
                    # 从 queue 中接收到持久化内部事件标记，直接把它转为 SSE 事件
                    try:
                        obj = json.loads(piece)
                        ev = obj.get("__persist_event__")
                        if ev:
                            yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
                        continue
                    except Exception:
                        pass

                # 普通 token：回传并追加缓存
                buffer_parts.append(piece)
                # 逐 token 返回（前端可实时拼接）
                token_ev = {"type": "token", "token": piece}
                yield f"data: {json.dumps(token_ev, ensure_ascii=False)}\n\n"

                # 异步检查是否需要持久化（不阻塞 token 返回）
                # 这里直接创建任务，实际持久化通过 save_lock 序列化
                asyncio.create_task(try_persist_if_needed())

            # 等待生成任务完成并获取最终内容
            try:
                final_content = await asyncio.wait_for(gen_task, timeout=10)
            except Exception:
                # 若任务出错，记录并继续用现有缓冲作为 final_content
                logger.exception("Generation task failed for chapter %s", payload.chapter_uid)
                final_content = "".join(buffer_parts)

            # 如果 final_content 非空且与缓冲一致则使用，否则以 final_content 为准
            if final_content:
                buffer_parts = [final_content]
            final_text = "".join(buffer_parts)

            # 最终持久化（确保写入 DB）
            try:
                await update_chapter(payload.chapter_uid, chapter.title, final_text, synopsis=getattr(chapter, "synopsis", None))
            except Exception:
                logger.exception("Failed to persist final content for chapter %s", payload.chapter_uid)

            done = {"type": "done", "chapter_uid": payload.chapter_uid, "final_length": len(final_text)}
            yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
        finally:
            # 清理：若生成任务还未结束，取消它
            if not gen_task.done():
                gen_task.cancel()
    return StreamingResponse(event_generator(), media_type="text/event-stream")