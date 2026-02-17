from __future__ import annotations

import asyncio
import re
import json
from typing import List, Optional, Dict, Any, AsyncIterable, AsyncGenerator
from pydantic import BaseModel, Field, ValidationError
from db.models.character import Character

from tools.deepseek.create_model_response import DeepSeekClient
from tools.openai.create_model_response import GPTClient


class CharacterItem(BaseModel):
    name: str = Field(..., description="角色名称")
    description: str = Field(..., description="角色设定与性格、动机等，1-3句")
    is_main: bool = Field(..., description="是否主角（true/false）")

class CharacterGenerationResult(BaseModel):
    characters: List[CharacterItem]

class CharacterAgent:
    """
    角色生成 Agent，支持：
    - 非流式结构化（保留原方法）
    - 流式结构化（新增）：每解析出一个角色就 yield 给前端
    """

    def __init__(self, provider: str = "deepseek", config_path: Optional[str] = None):
        self.provider = provider.lower()
        if self.provider == "deepseek":
            self.client = DeepSeekClient(config_path or "config/deepseek/config.yaml")
            self._use_pydantic_format = False
        elif self.provider == "openai":
            self.client = GPTClient(config_path or "config/openai/config.yaml")
            self._use_pydantic_format = True
        else:
            raise ValueError("Unsupported provider. Use 'deepseek' or 'openai'.")

    def _build_instructions(self) -> str:
        # 要求严格 JSON，便于流式解析
        return (
            "你是资深的小说角色设定助手。"
            "根据给定小说的标题、题材/类型与剧情简介，推断并产出合适数量的角色设定。"
            "要求：\n"
            "1) 仅输出严格 JSON 对象，不要包含任何多余文本或注释；不要使用 Markdown。\n"
            "2) JSON 顶层结构：\n"
            "{\n"
            '  "characters": [\n'
            "    {\n"
            '      "name": "字符串，中文姓名或符合题材风格的名字",\n'
            '      "description": "字符串，1-3句，包含身份、性格、目标/冲突/秘密等",\n"'
            '      "is_main": 布尔值true或false\n'
            "    }, ...\n"
            "  ]\n"
            "}\n"
            "3) 角色数量由剧情需要自定，一般2-8个；至少包含1名主角（is_main=true）。\n"
            "4) 姓名与描述需贴合题材与世界观；语言使用中文；避免剧透式具体情节。"
        )

    def _build_prompt(self, novel: Novel) -> str:
        title = getattr(novel, "title", "") or ""
        genre = getattr(novel, "genre", "") or ""
        desc = getattr(novel, "description", "") or ""
        return (
            f"小说信息：\n"
            f"- 标题：{title}\n"
            f"- 题材/类型：{genre}\n"
            f"- 简介：{desc}\n\n"
            "请依据上述信息产出角色列表。"
        )

    async def generate_characters(self, novel: Novel) -> List[Character]:
        """
        兼容保留：非流式一次性返回。
        """
        instructions = self._build_instructions()
        prompt = self._build_prompt(novel)

        raw: Any
        if self.provider == "openai":
            raw = await self.client.async_non_stream_response(
                prompt=prompt,
                instructions=instructions,
                text_format=CharacterGenerationResult,
            )
            if isinstance(raw, BaseModel):
                data = raw.model_dump()
            else:
                try:
                    data = CharacterGenerationResult.model_validate(raw).model_dump()  # type: ignore[arg-type]
                except ValidationError as e:
                    raise RuntimeError(f"OpenAI 响应结构化解析失败: {e}") from e
        else:
            raw = await self.client.async_non_stream_response(
                prompt=prompt,
                instructions=instructions,
                is_structured=True,
            )
            try:
                data = CharacterGenerationResult.model_validate(raw).model_dump()  # type: ignore[arg-type]
            except ValidationError as e:
                raise RuntimeError(f"DeepSeek 响应结构化解析失败: {e}") from e

        return self._to_characters(data, novel_uid=getattr(novel, "uid", "") or "")

    async def generate_characters_stream(self, novel: Novel) -> AsyncGenerator[Character, None]:
        """
        流式结构化：模型以 JSON 形式流式输出，解析到一个角色对象就 yield 一个 Character。
        """
        instructions = self._build_instructions()
        prompt = self._build_prompt(novel)
        novel_uid = getattr(novel, "uid", "") or ""

        # 启动模型流
        if self.provider == "openai":
            stream = self.client.async_stream_response(
                prompt=prompt,
                instructions=instructions,
                text_format=CharacterGenerationResult,  # 提示结构化
            )
        else:
            stream = self.client.async_stream_response(
                prompt=prompt,
                instructions=instructions,
                is_structured=True,  # JSON Object
            )

        # 增量解析器：锁定 "characters": [ ... ]，逐个对象输出
        async for character in self._parse_characters_from_stream(stream, novel_uid=novel_uid):
            yield character

    @staticmethod
    def _to_characters(payload: Dict[str, Any], novel_uid: str) -> List[Character]:
        chars: List[Character] = []
        for item in payload.get("characters", []):
            name = str(item.get("name", "")).strip()
            description = str(item.get("description", "")).strip()
            is_main = bool(item.get("is_main", False))
            if not name:
                continue
            chars.append(
                Character(
                    uid=None,
                    novel_uid=novel_uid,
                    name=name,
                    description=description,
                    is_main=is_main,
                    created_at=None,
                    updated_at=None,
                )
            )
        return chars

    async def _parse_characters_from_stream(
        self,
        stream: AsyncIterable[Any],
        novel_uid: str,
    ) -> AsyncGenerator[Character, None]:
        """
        将模型的文本流增量解析为 JSON，并在 characters 数组中每完成一个对象时 yield 一个 Character。
        """
        # 用于定位 "characters": [
        key_pattern = re.compile(r'"characters"\s*:\s*\[')
        pre_buffer = ""  # 在找到数组前积累
        in_array = False
        array_ended = False

        # 对象捕获状态
        in_string = False
        escape = False
        capturing_obj = False
        brace_depth = 0
        obj_buf: List[str] = []

        async for evt in stream:
            # 统一抽取文本增量
            piece = None
            if hasattr(evt, "delta") and evt.delta:
                piece = evt.delta if isinstance(evt.delta, str) else str(evt.delta)
            elif hasattr(evt, "data") and isinstance(evt.data, str) and evt.data:
                # 兜底
                piece = evt.data
            elif isinstance(evt, str):
                piece = evt
            if not piece:
                continue

            # 阶段 1：尚未定位到 characters 数组
            if not in_array:
                pre_buffer += piece
                m = key_pattern.search(pre_buffer)
                if not m:
                    # 继续等更多数据
                    continue
                # 找到数组开始 '[' 后的内容
                start_idx = m.end()
                array_part = pre_buffer[start_idx:]
                pre_buffer = ""  # 释放内存
                in_array = True

                # 将找到的部分继续走阶段 2 的解析逻辑
                for ch in array_part:
                    # 如果数组已结束，跳过后续
                    if array_ended:
                        break
                    # 处理字符串状态
                    if capturing_obj:
                        obj_buf.append(ch)

                    if in_string:
                        if escape:
                            escape = False
                            continue
                        if ch == "\\":
                            escape = True
                            continue
                        if ch == '"':
                            in_string = False
                        continue
                    else:
                        if ch == '"':
                            in_string = True
                            continue

                    # 非字符串上下文逻辑
                    if capturing_obj:
                        if ch == "{":
                            brace_depth += 1
                        elif ch == "}":
                            brace_depth -= 1
                            if brace_depth == 0:
                                # 完整对象
                                try:
                                    obj_text = "".join(obj_buf)
                                    data = json.loads(obj_text)
                                    item = CharacterItem.model_validate(data)
                                    yield Character(
                                        uid=None,
                                        novel_uid=novel_uid,
                                        name=item.name.strip(),
                                        description=item.description.strip(),
                                        is_main=bool(item.is_main),
                                        created_at=None,
                                        updated_at=None,
                                    )
                                except Exception:
                                    # 忽略该对象解析错误，继续后续
                                    pass
                                # 重置对象捕获
                                capturing_obj = False
                                obj_buf = []
                        # 继续处理下一字符
                        continue

                    # 未在对象捕获状态
                    if ch == "{":
                        capturing_obj = True
                        brace_depth = 1
                        obj_buf = ["{"]  # 开始新对象
                        continue
                    if ch == "]":
                        array_ended = True
                        continue

                # 进入下一增量
                continue

            # 阶段 2：已在 characters 数组中，逐字符处理
            if array_ended:
                # 顶层数组已结束，无需再解析
                continue

            for ch in piece:
                if array_ended:
                    break

                if capturing_obj:
                    obj_buf.append(ch)

                if in_string:
                    if escape:
                        escape = False
                        continue
                    if ch == "\\":
                        escape = True
                        continue
                    if ch == '"':
                        in_string = False
                    continue
                else:
                    if ch == '"':
                        in_string = True
                        continue

                if capturing_obj:
                    if ch == "{":
                        brace_depth += 1
                    elif ch == "}":
                        brace_depth -= 1
                        if brace_depth == 0:
                            # 完整对象
                            try:
                                obj_text = "".join(obj_buf)
                                data = json.loads(obj_text)
                                item = CharacterItem.model_validate(data)
                                yield Character(
                                    uid=None,
                                    novel_uid=novel_uid,
                                    name=item.name.strip(),
                                    description=item.description.strip(),
                                    is_main=bool(item.is_main),
                                    created_at=None,
                                    updated_at=None,
                                )
                            except Exception:
                                pass
                            capturing_obj = False
                            obj_buf = []
                    continue

                # 未在对象捕获状态
                if ch == "{":
                    capturing_obj = True
                    brace_depth = 1
                    obj_buf = ["{"]
                    continue
                if ch == "]":
                    array_ended = True
                    continue


if __name__ == "__main__":
    from db.models.novel import Novel

    async def demo_stream(provider: str):
        print(f"\n=== Provider: {provider} (streaming) ===")
        agent = CharacterAgent(provider=provider)
        demo_novel = Novel(
            uid="novel-demo-uid-001",
            title="山海镇妖录",
            genre="东方奇幻 / 仙侠 / 悬疑",
            description="少年道士下山历练，卷入古镇连环异事，与各方势力纠葛，在斩妖捉怪中探寻身世与宿命。",
        )
        idx = 0
        try:
            async for c in agent.generate_characters_stream(demo_novel):
                idx += 1
                role = "主角" if c.is_main else "配角"
                print(f"{idx}. [{role}] {c.name} - {c.description}")
        except Exception as e:
            print(f"流式解析失败: {repr(e)}")
        finally:
            print("流式结束。")

    async def main():
        # 逐个供应商测试
        for v in ("deepseek", "openai"):
            await demo_stream(v)

    asyncio.run(main())