import yaml
import os
import asyncio
import aiohttp
import json
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Type, AsyncIterable, Any, List
import requests
import base64

class GPTClient:
    """OpenAI / DeepSeek  API 客户端工具类（支持结构化 / 非结构化 / 流式）"""

    def __init__(self, config_path: str = "config/openai/config.yaml"):
        self.config_info = self._load_config(config_path)
        self.api_key = self.config_info.get('api_key')
        self.model = self.config_info.get('model', 'gpt-5')
        self.base_url = self.config_info.get('base_url', None)

        # 同时创建 sync 和 async 客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """从 YAML 配置文件加载 API Key 等配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                if not config:
                    raise ValueError("配置为空")
                return config
        except Exception as e:
            raise RuntimeError(f"加载配置失败: {e}")

    async def async_non_stream_response(
        self,
        prompt: str,
        instructions: str,
        text_format: Optional[Type[BaseModel]] = None
    ) -> Any:
        """
        非流式调用：
        - 如果传入 text_format，则启用结构化 JSON 输出（返回 dict 或解析后的 Pydantic 对象）
        - 否则返回普通文本
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ]

        extra_args = {}
        if text_format:
            # DeepSeek / ChatCompletion JSON Output
            extra_args["response_format"] = text_format

        # 创建请求
        resp = await self.async_client.chat.completions.parse(
            model=self.model,
            messages=messages,
            **extra_args,
        )

        content = resp.choices[0].message.content

        if text_format:
            try:
                json_dict = json.loads(content)
            except Exception as e:
                raise RuntimeError(f"解析 JSON 失败: {content}") from e
            return text_format.model_validate(json_dict)

        # 普通文本输出
        return content

    async def async_stream_response(
        self,
        prompt: str,
        instructions: str,
        text_format: Optional[Type[BaseModel]] = None
    ) -> AsyncIterable[Any]:
        """
        流式输出：
        - 如果传入 text_format，则尽量让模型输出 JSON，客户端需要自己按 JSON 组装
        - 否则实时输出纯文本
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ]

        # DeepSeek JSON Output
        kwargs = {}
        if text_format:
            kwargs["response_format"] = text_format
        async with self.async_client.chat.completions.stream(
            model=self.model,
            messages=messages,
            **kwargs
        ) as stream:
            async for event in stream:
                yield event


if __name__ == "__main__":

    class TotalShotsData(BaseModel):
        total_shots: int = Field(..., description="分镜总数")
        duration_list: List[float] = Field(..., description="每个镜头时长")

    class TotalShots(BaseModel):
        total_shots: int
        duration_list: List[float]

    async def test_async_non_stream_response():
        """测试异步结构化非流式响应"""
        client = GPTClient()

        instructions = """
        你是一名专业的动漫分镜时长设计师。
        任务：根据总时长60秒生成分镜方案，并输出 JSON。
        严格按照 JSON 输出如下格式（只输出 JSON，不要包含额外解释）：
        {
            "total_shots": 整数,
            "duration_list": [浮点数列表]
        }
        """

        result = await client.async_non_stream_response(
            prompt="一个中国的道士下山捉妖",
            instructions=instructions,
            text_format=TotalShots
        )
        print("非流式结构化结果:", result)
        # 转dict
        result_dict = result.model_dump()
        print("result_dict:", result_dict)
        print("type(result_dict):", type(result_dict))

    async def test_async_stream_response_text():
        """测试异步流式普通文本输出"""
        client = GPTClient()

        # instructions = """
        # 你是一名专业的动漫分镜时长设计师。
        # 任务：根据总时长60秒生成分镜方案，并输出 JSON。
        # 严格按照 JSON 输出如下格式（只输出 JSON，不要包含额外解释）：
        # {
        #     "total_shots": 整数,
        #     "duration_list": [浮点数列表]
        # }
        # """
        instructions = """
        你是一名专业的动漫分镜时长设计师。
        任务：根据总时长60秒生成分镜方案。
        """
        print("流式文本输出:")
        buffer: List[str] = []

        async for evt in client.async_stream_response(
            prompt="一个中国的道士下山捉妖",
            instructions=instructions,
            text_format=TotalShots
        ):
            if hasattr(evt, "delta") and evt.delta:
                piece = evt.delta if isinstance(evt.delta, str) else str(evt.delta)
                buffer.append(piece)
                print(piece, end="", flush=True)

        # 完整文本
        full_text = "".join(buffer).strip()
        print()  # 换行

        # 若传了 text_format，则将完整文本解析为模型对象再打印
        try:
            data = json.loads(full_text)
            result = TotalShots.model_validate(data)
            print("最终结构化对象:", result)
            print("result.model_dump():", result.model_dump())
        except Exception:
            # 如果不是严格 JSON，退回打印最终文本
            print("最终文本:", full_text)

    # 运行测试
    # asyncio.run(test_async_non_stream_response())
    asyncio.run(test_async_stream_response_text())

