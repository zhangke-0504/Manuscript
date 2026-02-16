import yaml
import os
import asyncio
import aiohttp
import json
from openai import AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Type, AsyncIterable, Any
import requests
import base64

class DeepSeekClient:
    """OpenAI/DeepSeek API 客户端工具类"""

    def __init__(self, config_path: str = "config/deepseek/config.yaml"):
        self.config_info = self._load_config(config_path)
        self.api_key = self.config_info.get("api_key")
        self.model = self.config_info.get("model", "deepseek-chat")
        self.base_url = self.config_info.get("base_url")
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _load_config(self, config_path: str) -> str:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                if not config:
                    raise ValueError("配置文件为空")
                return config
        except Exception as e:
            raise RuntimeError(f"加载配置失败: {e}")

    async def async_non_stream_response(
        self,
        prompt: str,
        instructions: str,
        is_structured: bool = False  # 是否启用结构化输出
    ):
        """
        非流式返回，支持结构化
        目前deepseek只支持最基本的字典格式返回，无法支持复杂的pydantic模型解析
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ]

        # 构造可选参数
        extra_args = {}
        if is_structured:
            extra_args["response_format"] = {"type": "json_object"}

        # 发起请求
        resp = await self.async_client.chat.completions.create(
            model=self.model,
            messages=messages,
            **extra_args,
        )

        # 如果结构化，解析 JSON
        if is_structured:
            try:
                return json.loads(resp.choices[0].message.content)
            except Exception as e:
                raise RuntimeError(f"解析 JSON 失败: {resp.choices[0].message.content}") from e

        # 非结构化直接返回文本
        return resp.choices[0].message.content

    async def async_stream_response(
        self,
        prompt: str,
        instructions: str,
        is_structured: bool = False
    ) -> AsyncIterable[Any]:
        """
        流式返回，支持结构化输出
        若 is_structured=True，将尽量按 JSON Object 输出
        """
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": prompt},
        ]

        # 构造可选参数
        extra_args = {}
        if is_structured:
            extra_args["response_format"] = {"type": "json_object"}

        async with self.async_client.chat.completions.stream(
            model=self.model,
            messages=messages,
            **extra_args,
        ) as stream:
            async for event in stream:
                yield event
    
if __name__ == "__main__":
    async def test_async_non_stream_response():
        """测试异步结构化响应"""
        client = DeepSeekClient()
        
        instructions = """
        你是一名专业的动漫分镜时长设计师。你的任务是根据视频总时长 60（单位：秒）决定生成的分镜数量，每个分镜时长仅可选 4.00 、8.00和12.00，且所有分镜时长之和必须等于 60。

    # 核心指令
    1.  **输出格式**：必须严格遵循以下 JSON 格式，输出分镜总数和每个分镜的时长：
    # JSON字段定义（必须严格遵守）
    -   `total_shots`: （整数）分镜总数（s）。
    -   `duration_list`: （列表）每个分镜的时长（s），每个分镜时长仅可选 4.00 、8.00和12.00，且所有分镜时长之和必须等于 60。
    """
        
        try:
            # 使用异步方法替代同步方法
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

    async def test_async_stream_response():
        """测试异步流式响应"""
        client = DeepSeekClient()

        instructions = """
        你是一名专业的动漫分镜时长设计师。你的任务是根据视频总时长 60（单位：秒）决定生成的分镜数量，每个分镜时长仅可选 4.00 、8.00和12.00，且所有分镜时长之和必须等于 60。

    # 核心指令
    1.  **输出格式**：必须严格遵循以下 JSON 格式，输出分镜总数和每个分镜的时长：
    # JSON字段定义（必须严格遵守）
    -   `total_shots`: （整数）分镜总数（s）。
    -   `duration_list`: （列表）每个分镜的时长（s），每个分镜时长仅可选 4.00 、8.00和12.00，且所有分镜时长之和必须等于 60。
    """

        try:
            # 流式结构化设为False（文本模式）
            print("开始流式异步输出：")
            async for evt in client.async_stream_response(
                prompt="一个中国的道士下山捉妖",
                instructions=instructions,
                is_structured=True
            ):
                if hasattr(evt, "delta"):
                    print(evt.delta, end="")
        except Exception as e:
            print("流式异步调用报错：", repr(e))

    # 运行测试
    asyncio.run(test_async_non_stream_response())
    asyncio.run(test_async_stream_response())