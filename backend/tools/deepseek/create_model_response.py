import yaml
import os
import sys
import asyncio
import aiohttp
import json
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Type, AsyncIterable, Any, List
import requests
import base64
from utils.config import Model_Providers

class DeepSeekClient:
    """OpenAI/DeepSeek API 客户端工具类，支持多轮 messages 参数"""

    def __init__(self, config_path: Optional[str] = None):
        # Determine config path: prefer explicit, else use mapping from utils.config
        if not config_path:
            rel = Model_Providers.get("deepseek", "config/deepseek/config.yaml")
            config_path = rel

        # resolve relative path to project root (handle PyInstaller frozen exe)
        if not os.path.isabs(config_path):
            if getattr(sys, "frozen", False):
                # sys.executable is .../backend/dist/server.exe; project root should be backend (two levels up)
                project_root = os.path.dirname(os.path.dirname(sys.executable))
            else:
                # file is backend/tools/deepseek/create_model_response.py -> project root is three levels up (backend)
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(project_root, config_path)

        # Ensure parent dir exists and create placeholder if missing
        parent = os.path.dirname(config_path)
        os.makedirs(parent, exist_ok=True)
        if not os.path.exists(config_path):
            # create placeholder file with required DeepSeek defaults
            placeholder = {
                "api_key": "xxxxxx",
                "model": "deepseek-chat",
                "base_url": "https://api.deepseek.com",
            }
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.safe_dump(placeholder, f, allow_unicode=True, sort_keys=False)

        self.config_info = self._load_config(config_path)
        self.api_key = self.config_info.get("api_key")
        self.model = self.config_info.get("model", "deepseek-chat")
        self.base_url = self.config_info.get("base_url", "https://api.deepseek.com")
        # Ensure OpenAI/DeepSeek client sees API key via env if required
        if self.api_key:
            os.environ['OPENAI_API_KEY'] = str(self.api_key)
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file) or {}
                if not isinstance(config, dict):
                    raise ValueError("配置文件格式错误，期望 mapping")
                return config
        except Exception as e:
            raise RuntimeError(f"加载配置失败: {e}")

    def _ensure_json_hint(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        若 messages 中任一 content 不包含 'json'（不区分大小写），
        在 system 消息中注入一条包含 'json' 字样的提示，以满足 DeepSeek 的验证要求。
        不修改原始列表，返回新的列表。
        """
        joined = " ".join((m.get("content", "") for m in messages if m.get("content")))
        if "json" in joined.lower():
            return list(messages)
        hint = "请只输出有效的 JSON（请在说明中包含单词 json），不要附加额外解释。"
        new_messages = list(messages)
        # 尝试找到 system 消息并注入；否则插入新的 system 消息到最前
        for i, m in enumerate(new_messages):
            if m.get("role") == "system":
                new_messages[i] = {"role": "system", "content": (m.get("content", "") + "\n" + hint).strip()}
                return new_messages
        return [{"role": "system", "content": hint}] + new_messages

    async def async_non_stream_response(
        self,
        prompt: Optional[str] = None,
        instructions: Optional[str] = None,
        is_structured: bool = False,
        messages: Optional[List[Dict[str, str]]] = None
    ):
        """
        非流式返回，支持结构化和多轮 messages。
        """
        if messages is None:
            messages_payload = [
                {"role": "system", "content": instructions or ""},
                {"role": "user", "content": prompt or ""},
            ]
        else:
            messages_payload = list(messages)  # copy to avoid mutating caller

        extra_args = {}
        if is_structured:
            # DeepSeek 要求 prompt 中包含 'json' 才能使用 json_object
            messages_payload = self._ensure_json_hint(messages_payload)
            extra_args["response_format"] = {"type": "json_object"}

        resp = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages_payload,
            **extra_args,
        )

        if is_structured:
            try:
                return json.loads(resp.choices[0].message.content)
            except Exception as e:
                raise RuntimeError(f"解析 JSON 失败: {resp.choices[0].message.content}") from e

        return resp.choices[0].message.content

    async def async_stream_response(
        self,
        prompt: Optional[str] = None,
        instructions: Optional[str] = None,
        is_structured: bool = False,
        messages: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterable[Any]:
        """
        流式返回，支持结构化输出和多轮 messages。
        """
        if messages is None:
            messages_payload = [
                {"role": "system", "content": instructions or ""},
                {"role": "user", "content": prompt or ""},
            ]
        else:
            messages_payload = list(messages)

        extra_args = {}
        if is_structured:
            messages_payload = self._ensure_json_hint(messages_payload)
            extra_args["response_format"] = {"type": "json_object"}

        async with self.async_client.chat.completions.stream(
            model=self.model,
            messages=messages_payload,
            **extra_args,
        ) as stream:
            async for event in stream:
                yield event

if __name__ == "__main__":
    async def test_async_non_stream_response():
        client = DeepSeekClient()

        instructions = """
        你是一名专业的动漫分镜时长设计师。你的任务是根据视频总时长 60（单位：秒）决定生成的分镜数量...
        """

        try:
            totalshots = await client.async_non_stream_response(
                prompt="一个中国的道士下山捉妖",
                instructions=instructions,
                is_structured=True
            )
            print("异步调用结果:", totalshots)
            return totalshots
        except Exception as e:
            print("异步调用报错：", repr(e))
            return None

    async def test_multi_turn():
        """多轮对话示例（非流式）"""
        client = DeepSeekClient()
        messages = [{"role": "user", "content": "世界上最高的山是什么？"}]
        resp1 = await client.async_non_stream_response(messages=messages)
        print("Round1 assistant:", resp1)
        messages.append({"role": "assistant", "content": resp1})
        messages.append({"role": "user", "content": "那第二高的呢？"})
        resp2 = await client.async_non_stream_response(messages=messages)
        print("Round2 assistant:", resp2)

    async def test_async_stream_response():
        client = DeepSeekClient()
        print("开始流式异步输出：")
        async for evt in client.async_stream_response(
            prompt="一个中国的道士下山捉妖",
            instructions="请讲个短故事",
            is_structured=False
        ):
            if hasattr(evt, "delta"):
                print(evt.delta, end="")

    async def main():
        await test_async_non_stream_response()
        await test_multi_turn()
        await test_async_stream_response()
    asyncio.run(main())