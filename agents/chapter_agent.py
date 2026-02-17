import asyncio
import json
import inspect
from dataclasses import dataclass
from typing import List, Optional, Callable, Awaitable, Union, Any, Set, Dict

from db.models.character import Character
# from db.models.chapter import Chapter

from tools.deepseek.create_model_response import DeepSeekClient
from tools.openai.create_model_response import GPTClient


@dataclass
class ChapterOutlineItem:
    index: int
    title: str
    synopsis: str


class ProviderAdapter:
    """
    适配不同大语言模型供应商的适配器，统一提供以下功能：
        - stream_text：流式返回 token 并输出最终拼接的完整文本
        - text：非流式返回结果
    支持传入多轮 messages（list of {role, content}）
    """
    def __init__(self, provider: str = "openai", openai_config: Optional[str] = None, deepseek_config: Optional[str] = None):
        self.provider = provider.lower()
        if self.provider == "deepseek":
            self.client = DeepSeekClient(config_path=deepseek_config or "config/deepseek/config.yaml")
        else:
            self.client = GPTClient(config_path=openai_config or "config/openai/config.yaml")

    async def _emit(self, on_token: Optional[Callable[[str], Union[None, Awaitable[None]]]], piece: str):
        """
        回调适配器：把每次流式生成的文本片段 piece 发送给 on_token 回调。
        兼容同步/异步回调。
        """
        if on_token:
            res = on_token(piece)
            if inspect.isawaitable(res):
                await res

    async def stream_text(
        self,
        prompt: Optional[str] = None,
        instructions: Optional[str] = None,
        on_token: Optional[Callable[[str], Union[None, Awaitable[None]]]] = None,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        支持通过 messages 发起多轮对话流式请求；若 messages=None 则按 instructions+prompt 构造单轮。
        """
        buffer: List[str] = []
        if isinstance(self.client, DeepSeekClient):
            async for evt in self.client.async_stream_response(prompt=prompt, instructions=instructions, is_structured=False, messages=messages):
                piece = ""
                if hasattr(evt, "delta") and evt.delta:
                    piece = evt.delta if isinstance(evt.delta, str) else str(evt.delta)
                elif hasattr(evt, "choices") and evt.choices:
                    delta = evt.choices[0].delta if hasattr(evt.choices[0], "delta") else None
                    if delta:
                        piece = delta if isinstance(delta, str) else str(delta)
                if piece:
                    buffer.append(piece)
                    await self._emit(on_token, piece)
        else:
            async for evt in self.client.async_stream_response(prompt=prompt, instructions=instructions, text_format=None, messages=messages):
                piece = ""
                if hasattr(evt, "delta") and evt.delta:
                    piece = evt.delta if isinstance(evt.delta, str) else str(evt.delta)
                elif hasattr(evt, "choices") and evt.choices:
                    delta = evt.choices[0].delta if hasattr(evt.choices[0], "delta") else None
                    if delta:
                        piece = delta if isinstance(delta, str) else str(delta)
                if piece:
                    buffer.append(piece)
                    await self._emit(on_token, piece)

        return "".join(buffer)

    async def text(self, prompt: Optional[str] = None, instructions: Optional[str] = None, messages: Optional[List[Dict[str, str]]] = None) -> str:
        if isinstance(self.client, DeepSeekClient):
            return await self.client.async_non_stream_response(prompt=prompt, instructions=instructions, is_structured=False, messages=messages)
        else:
            return await self.client.async_non_stream_response(prompt=prompt, instructions=instructions, text_format=None, messages=messages)


class ChapterAgent:
    def __init__(self, provider: str = "openai", openai_config: Optional[str] = None, deepseek_config: Optional[str] = None):
        self.adapter = ProviderAdapter(provider=provider, openai_config=openai_config, deepseek_config=deepseek_config)

    @staticmethod
    def _detect_lang_from_characters(characters: List[Character]) -> str:
        sample = "".join([(c.name or "") + (c.description or "") for c in characters])
        # 简单 CJK 检测：存在中文字符则判为 zh，否则 en（可按需扩展）
        return "zh" if any("\u4e00" <= ch <= "\u9fff" for ch in sample) else "en"

    @staticmethod
    def _detect_lang_from_text(text: str) -> str:
        return "zh" if any("\u4e00" <= ch <= "\u9fff" for ch in (text or "")) else "en"

    @staticmethod
    def _lang_label(code: str) -> str:
        return {
            "zh": "Chinese",
            "en": "English",
            "ja": "Japanese",
            "ko": "Korean",
            "es": "Spanish",
        }.get((code or "").lower(), "Chinese")

    @staticmethod
    def _char_unit(code: str) -> str:
        return "Chinese characters" if (code or "").lower() == "zh" else "characters"

    @staticmethod
    def _characters_to_compact_dicts(characters: List[Character]) -> List[dict]:
        out: List[dict] = []
        for c in characters:
            out.append({
                "uid": c.uid,
                "name": c.name,
                "description": c.description,
                "is_main": c.is_main
            })
        return out

    @staticmethod
    def _clean_llm_text(txt: str) -> str:
        # 如有常见的格式标记（如代码块围栏），则将其移除。
        lines = []
        for line in txt.splitlines():
            s = line.strip()
            if s.startswith("```") and s.endswith("```"):
                continue
            if s.startswith("```") or s.endswith("```"):
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    @staticmethod
    def _parse_outline_result(text: str) -> List[ChapterOutlineItem]:
        text = ChapterAgent._clean_llm_text(text)
        # 尝试解析为完整的 JSON 数组
        try:
            data = json.loads(text)
            if isinstance(data, list):
                items: List[ChapterOutlineItem] = []
                for i in data:
                    idx = i.get("index") or i.get("chapter_index") or i.get("idx")
                    title = i.get("title") or i.get("chapter_title")
                    synopsis = i.get("synopsis") or i.get("summary") or i.get("brief")
                    if idx is not None and title and synopsis:
                        items.append(ChapterOutlineItem(index=int(idx), title=str(title), synopsis=str(synopsis)))
                if items:
                    return items
        except Exception:
            pass

        # 回退方案：NDJSON 行格式
        items: List[ChapterOutlineItem] = []
        for line in text.splitlines():
            s = line.strip().rstrip(",")
            if not s:
                continue
            # 忽略 Markdown 列表标记
            if s.startswith("- "):
                s = s[2:]
            try:
                obj = json.loads(s)
                idx = obj.get("index") or obj.get("chapter_index") or obj.get("idx")
                title = obj.get("title") or obj.get("chapter_title")
                synopsis = obj.get("synopsis") or obj.get("summary") or obj.get("brief")
                if idx is not None and title and synopsis:
                    items.append(ChapterOutlineItem(index=int(idx), title=str(title), synopsis=str(synopsis)))
            except Exception:
                # 启发式: "1. 标题 —— 概述"
                if "." in s and "——" in s:
                    try:
                        left, right = s.split(".", 1)
                        idx = int(left.strip())
                        title, synopsis = right.split("——", 1)
                        items.append(ChapterOutlineItem(index=idx, title=title.strip(), synopsis=synopsis.strip()))
                    except Exception:
                        continue
                continue
        return items

    async def _emit_item(self, cb: Optional[Callable[[ChapterOutlineItem], Union[None, Awaitable[None]]]], item: ChapterOutlineItem):
        if cb:
            r = cb(item)
            if inspect.isawaitable(r):
                await r

    async def stream_generate_directory(
        self,
        novel_title: str,
        genre: str,
        description: str,
        characters: List[Character],
        target_chapters: Optional[int] = None,
        language: Optional[str] = None,  # 可显式指定语言（如 "zh"/"en"...）
        on_outline_item: Optional[Callable[[ChapterOutlineItem], Union[None, Awaitable[None]]]] = None,  # 流式结构化回调
        on_token: Optional[Callable[[str], Union[None, Awaitable[None]]]] = None  # 若需要原始 token，可传
    ) -> List[ChapterOutlineItem]:
        """
        流式生成章节目录（标题 + 简介），以“结构化对象”逐条回调 on_outline_item，并在结束时返回完整列表。
        实现方式：提示模型输出 NDJSON / 顺序 JSON 对象；在流式 token 中按花括号配平解析每个 JSON 对象。
        """
        char_info = self._characters_to_compact_dicts(characters)
        lang_code = (language or self._detect_lang_from_characters(characters)).lower()
        lang_label = self._lang_label(lang_code)
        char_unit = self._char_unit(lang_code)

        # 更强约束：逐条 JSON 对象输出，便于流式解析
        instructions_template = (
            "你是一名资深小说分章与大纲设计师。请严格按以下要求输出：\n"
            "- 按顺序逐条输出 JSON 对象（每个对象表示一章），不要输出数组、列表标记或任何多余文本；\n"
            "- 每个对象必须包含字段：index（从1开始的整数）、title（章节标题）、synopsis（该章1-2句，约30-60字符）；\n"
            "- 输出语言：{LANG}；\n"
            "- 对象之间直接换行分隔（NDJSON），便于流式解析；\n"
            "- 总共输出 {COUNT} 个对象。\n"
            "示例（仅示意，一行一个完整 JSON 对象）：\n"
            '{"index":1,"title":"示例","synopsis":"示例简介..."}\n'
            '{"index":2,"title":"示例2","synopsis":"示例2简介..."}\n'
            "不要输出任何解释或前后缀。"
        )
        instructions = instructions_template.replace(
            "{LANG}", lang_label
        ).replace(
            "{COUNT}", str(target_chapters if target_chapters else "若干")
        )

        user_payload = {
            "novel_title": novel_title,
            "genre": genre,
            "theme": description,
            "chapter_count": target_chapters if target_chapters else "根据题材和内容合理决定",
            "characters": char_info,
            "output_requirements": {
                "format": "NDJSON (one JSON object per line)",
                "fields": ["index", "title", "synopsis"],
                "synopsis_length": f"30-60 {char_unit}",
                "language": lang_label
            }
        }
        prompt = json.dumps(user_payload, ensure_ascii=False)

        # 流式解析：基于花括号配平提取完整 JSON 对象
        items: List[ChapterOutlineItem] = []
        seen_indices: Set[int] = set()
        final_text_parts: List[str] = []

        in_string = False
        escape = False
        depth = 0
        cur_buf: List[str] = []

        async def handle_piece(piece: str):
            nonlocal in_string, escape, depth, cur_buf
            if on_token:
                await self.adapter._emit(on_token, piece)
            final_text_parts.append(piece)

            if target_chapters and len(items) >= target_chapters:
                # 已够数量，忽略后续解析（但仍允许 on_token 打印）
                return

            for ch in piece:
                # 记录字符到当前缓冲（当开始遇到 { 或已在对象中时）
                if depth > 0 or ch == "{":
                    cur_buf.append(ch)
                # 处理转义与字符串状态
                if escape:
                    escape = False
                    continue
                if ch == "\\" and in_string:
                    escape = True
                    continue
                if ch == '"' and not escape:
                    in_string = not in_string
                if not in_string:
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0 and cur_buf:
                            # 一个完整对象
                            obj_text = "".join(cur_buf).strip()
                            cur_buf = []
                            try:
                                obj = json.loads(obj_text)
                                idx = obj.get("index") or obj.get("chapter_index") or obj.get("idx")
                                title = obj.get("title") or obj.get("chapter_title")
                                synopsis = obj.get("synopsis") or obj.get("summary") or obj.get("brief")
                                if idx is not None and title and synopsis:
                                    ci = ChapterOutlineItem(index=int(idx), title=str(title), synopsis=str(synopsis))
                                    # 去重（防止重复流）
                                    if ci.index not in seen_indices:
                                        seen_indices.add(ci.index)
                                        items.append(ci)
                                        await self._emit_item(on_outline_item, ci)
                            except Exception:
                                # 忽略无法解析的片段，等待更多 token
                                pass

        # 使用适配器进行流式请求，并在回调中解析对象
        await self.adapter.stream_text(prompt=prompt, instructions=instructions, on_token=handle_piece)

        # 兜底：若模型输出为 JSON 数组或混合文本，则在结束后整体解析一次，补齐缺失项
        if (not target_chapters) or (len(items) < (target_chapters or 0)):
            fallback = self._parse_outline_result("".join(final_text_parts))
            # 合并未出现的条目
            for it in fallback:
                if target_chapters and len(items) >= target_chapters:
                    break
                if it.index not in seen_indices:
                    seen_indices.add(it.index)
                    items.append(it)
                    # 结束后就不再做 on_outline_item 回调，避免前端顺序错乱

        # 截断到目标数量
        if target_chapters and len(items) > target_chapters:
            items = sorted(items, key=lambda x: x.index)[:target_chapters]
        else:
            items = sorted(items, key=lambda x: x.index)
        return items

    async def stream_generate_chapter_content(
        self,
        outline_items: List[ChapterOutlineItem],
        all_characters: List[Character],
        chapter_index: int,
        prev_synopsis: Optional[str],
        next_synopsis: Optional[str],
        language: Optional[str] = None,
        on_token: Optional[Callable[[str], Union[None, Awaitable[None]]]] = None,
        conversation_messages: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        流式生成单章正文。支持多轮对话：若传入 conversation_messages（严格的 messages 列表），
        则使用该 messages 发起请求并流式接收回复；否则按旧方式构造 system+user 单轮消息。
        """
        index_map = {item.index: item for item in outline_items}
        item = index_map.get(chapter_index)
        if not item:
            raise ValueError(f"chapter_index {chapter_index} not found in outline_items")

        lang_code = (language or self._detect_lang_from_characters(all_characters)).lower()
        lang_label = self._lang_label(lang_code)

        char_info = self._characters_to_compact_dicts(all_characters)
        instructions = (
            "你是一名专业小说写作代笔作者。请根据给定的章节标题、该章概述、所有人物信息，以及前后章节的概括（若有）创作本章正文。\n"
            "要求：\n"
            "1) 采用叙事文本，不要输出标题、小节标题、或任何额外标记；\n"
            "2) 内容要具体生动，描写人物行为、心理和对话，避免空泛总结；\n"
            "3) 与前后章衔接自然，不要剧透下一章但可合理埋伏笔；\n"
            "4) 文笔统一、角色人设稳定；\n"
            f"5) 最终输出语言：{lang_label}；\n"
            "6) 只输出正文内容。"
        )

        user_payload = {
            "chapter": {
                "index": item.index,
                "title": item.title,
                "synopsis": item.synopsis
            },
            "adjacent": {
                "previous_synopsis": prev_synopsis or "",
                "next_synopsis": next_synopsis or ""
            },
            "characters": char_info,
            "style": {
                "language": lang_label,
                "tone": "叙事流畅、细节充实、情感丰沛",
                "avoid": ["重复概述", "流水账", "突兀转场", "过度说明"]
            }
        }
        prompt = json.dumps(user_payload, ensure_ascii=False)

        # 如果传入 conversation_messages（多轮），则直接使用它，否则构造 system+user 单轮
        if conversation_messages:
            messages = conversation_messages
        else:
            messages = [
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt}
            ]

        # 使用 adapter 的流式接口，传入 messages
        content = await self.adapter.stream_text(on_token=on_token, messages=messages)
        return content.strip()

    async def summarize_content(
        self,
        content: str,
        target_length: int = 200,
        language: Optional[str] = None
    ) -> str:
        """
        将章节内容压缩为指定长度摘要（非流式）。
        """
        lang_code = (language or self._detect_lang_from_text(content)).lower()
        lang_label = self._lang_label(lang_code)
        unit_hint = "个汉字" if lang_code == "zh" else "characters"

        instructions = (
            f"你是一名专业的{lang_label}文本摘要助手。"
            f"请对给定的章节内容进行精准且简洁的摘要，突出关键事件、人物行为与转折。"
            f"摘要长度尽量接近 {target_length}{unit_hint}，允许±20%浮动。"
            "不要输出任何前后缀、标题、引号或JSON，仅输出摘要正文。"
        )
        prompt = content
        summary = await self.adapter.text(prompt=prompt, instructions=instructions)
        return (summary or "").strip()



# 测试代码
async def test_stream_directory(agent: ChapterAgent):
    # 模拟从 character 表读取
    characters = [
        Character(uid="c1", novel_uid="n1", name="李青麟", description="年轻道士，寡言沉稳，擅符箓捉妖。", is_main=True),
        Character(uid="c2", novel_uid="n1", name="苏晚晴", description="县衙女捕快，机敏果决，信奉理性。", is_main=True),
        Character(uid="c3", novel_uid="n1", name="白无常", description="阴差化身，冷面亦有柔肠，行事有度。", is_main=False),
    ]

    print("\n[流式结构化] 章节目录（逐条解析回调）：")
    parsed_items: List[ChapterOutlineItem] = []

    async def on_outline_item(it: ChapterOutlineItem):
        parsed_items.append(it)
        print(f'\n[on_item] 第{it.index}章 《{it.title}》：{it.synopsis}', flush=True)

    # 如需观察原始 token，可另行传入 on_token
    items = await agent.stream_generate_directory(
        novel_title="道士下山",
        genre="奇幻/志异/民俗灵异",
        description="人心善恶与因果",
        characters=characters,
        target_chapters=10,
        language=None,
        on_outline_item=on_outline_item,
        on_token=None
    )

    print("\n[解析完成] 目录前5项：")
    for it in items[:5]:
        print(f"- 第{it.index}章 《{it.title}》：{it.synopsis}")
    return items, characters


async def test_stream_contents(agent: ChapterAgent, outline_items: List[ChapterOutlineItem], characters: List[Character]):
    print("\n[流式 多轮] 生成4章内容（多轮示例）：")
    generated_contents: List[str] = []
    # 在多轮示例中，将把每次 assistant 的正文回复追加到 messages 里，以便下一轮带上下文
    messages: List[Dict[str, str]] = []

    for idx in range(1, 5):
        prev_synopsis: Optional[str] = None
        if idx > 1:
            prev_synopsis = await agent.summarize_content(generated_contents[-1], target_length=120)
            print(f"\n[上一章摘要-第{idx-1}章]: {prev_synopsis}")

        next_synopsis: Optional[str] = None
        if idx + 1 <= len(outline_items):
            next_synopsis = outline_items[idx].synopsis
            print(f"[下一章概述-第{idx+1}章]: {next_synopsis}")

        # 构造当前轮 system + user（或者在 messages 里保留之前的 messages，形成多轮）
        index_map = {item.index: item for item in outline_items}
        item = index_map.get(idx)
        if not item:
            raise ValueError(f"chapter_index {idx} not found")

        lang_label = agent._lang_label(agent._detect_lang_from_characters(characters))
        instructions = (
            "你是一名专业小说写作代笔作者。请根据给定的章节标题、该章概述、所有人物信息，以及前后章节的概括（若有）创作本章正文。\n"
            f"5) 最终输出语言：{lang_label}；\n"
            "6) 只输出正文内容。"
        )

        user_payload = {
            "chapter": {"index": item.index, "title": item.title, "synopsis": item.synopsis},
            "adjacent": {"previous_synopsis": prev_synopsis or "", "next_synopsis": next_synopsis or ""},
            "characters": agent._characters_to_compact_dicts(characters),
            "style": {"language": lang_label, "tone": "叙事流畅、细节充实、情感丰沛"}
        }
        prompt = json.dumps(user_payload, ensure_ascii=False)

        # 如果 messages 为空，则开始新会话（包含 system + user）；否则在已有 messages 后追加 user 询问以形成多轮
        if not messages:
            messages = [{"role": "system", "content": instructions}, {"role": "user", "content": prompt}]
        else:
            messages.append({"role": "user", "content": prompt})

        print(f"\n[流式输出正文-第{idx}章 开始]")

        async def on_token(piece: str):
            print(piece, end="", flush=True)

        # 多轮：将 messages 传入，stream_text 会把 assistant 的流式输出返回为字符串
        content = await agent.stream_generate_chapter_content(
            outline_items=outline_items,
            all_characters=characters,
            chapter_index=idx,
            prev_synopsis=prev_synopsis,
            next_synopsis=next_synopsis,
            language=None,
            on_token=on_token,
            conversation_messages=messages
        )
        # 将 assistant 回复追加到 messages（以便下一轮）
        messages.append({"role": "assistant", "content": content})
        generated_contents.append(content)
        print(f"\n[流式输出正文-第{idx}章 结束]\n")

    print("[完成] 已生成4章内容（多轮）。")
    return generated_contents


if __name__ == "__main__":
    async def main():
        provider = "openai"  # deepseek 或 openai
        agent = ChapterAgent(provider=provider)

        outline_items, characters = await test_stream_directory(agent)
        print("outline_items:", outline_items)
        print("characters:", characters)
        await test_stream_contents(agent, outline_items, characters)

    asyncio.run(main())