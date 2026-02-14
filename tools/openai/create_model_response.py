import yaml
import os
import asyncio
import aiohttp
from openai import OpenAI, AsyncOpenAI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Type, AsyncIterable, Any
import requests
import base64

class GPTClient:
    """OpenAI API客户端工具类"""
    
    def __init__(self, config_path: str = "config/openai/config.yaml"):
        # 从配置文件读取API密钥
        self.api_key = self._load_api_key(config_path)
        self.model = "gpt-4.1"
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
    
    def _load_api_key(self, config_path: str) -> str:
        """从YAML配置文件加载API密钥"""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                api_key = config.get('api_key')
                if not api_key:
                    raise ValueError("API密钥未在配置文件中找到")
                return api_key
        except FileNotFoundError:
            raise FileNotFoundError(f"配置文件未找到: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise RuntimeError(f"加载配置失败: {e}")
    
    def get_structured_response(self, prompt: str, instructions: str, text_format: Optional[Type[BaseModel]] = None):
        """使用 Structured Outputs 结构化生成分镜（非流式）"""
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": instructions,
                },
                {
                    "role": "user", 
                    "content": prompt,
                },
            ],
            text_format=text_format,  
        )
        return response.output_parsed
    
    async def async_get_structured_response(self, prompt: str, instructions: str, text_format: Optional[Type[BaseModel]] = None):
        """
        异步版本的结构化输出方法
        使用 AsyncOpenAI 客户端进行异步调用
        """
        try:
            response = await self.async_client.responses.parse(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": instructions,
                    },
                    {
                        "role": "user", 
                        "content": prompt,
                    },
                ],
                text_format=text_format,
            )
            return response.output_parsed
        except Exception as e:
            raise RuntimeError(f"异步结构化输出调用失败: {e}")
    
    def get_structured_stream_response(self, prompt: str, instructions: str, text_format: Type[BaseModel]):
        """结构化流式输出（官方推荐写法）"""
        stream = self.client.responses.stream(
            model=self.model,
            input=[
                {"role": "system", "content": instructions},
                {"role": "user", "content": prompt},
            ],
            text_format=text_format,
        )
        return stream
    
    async def async_get_structured_stream_response(
        self, prompt: str, instructions: str, text_format: Optional[Type[BaseModel]] = None
    ) -> AsyncIterable[Any]:
        """
        异步结构化流式输出（返回 async iterable，直接把 SDK 的事件透传）。
        使用方式（在上层）：
            async for event in client.new_get_structured_stream_response(...):
                ...
        实现：通过 async with client.responses.stream(...) as stream:
                    async for event in stream: yield event
        这样可以兼容 SDK 对流的实现（它通常以 async context manager 返回 stream manager）。
        参考：OpenAI 官方 Streaming 指南。:contentReference[oaicite:1]{index=1}
        """
        async with self.async_client.responses.stream(
                model=self.model, 
                input=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": prompt},
                ], 
                text_format=text_format,
            ) as stream:
            async for event in stream:
                yield event
    
    def get_response(self, prompt: str, instructions: str):
        """非流式调用 - 一次性获取完整回复"""
        resp = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
        )
        return resp.output_text
    
    async def async_get_response(self, prompt: str, instructions: str) -> str:
        """
        异步非流式调用 - 一次性获取完整回复
        """
        try:
            resp = await self.async_client.responses.create(
                model=self.model,
                instructions=instructions,
                input=prompt,
            )
            return resp.output_text
        except Exception as e:
            raise RuntimeError(f"异步API调用失败: {e}")
    
    def stream_response(self, prompt: str):
        """流式调用 - 返回可迭代事件流"""
        stream = self.client.responses.create(
            model=self.model,
            input=prompt,
            stream=True,
        )
        return stream

    def get_structured_image_response(
        self, 
        prompt: str, 
        image_url: str, 
        instructions: str = "你是一个专业的图像分析助手。请根据图像内容回答问题。",
        text_format: Optional[Type[BaseModel]] = None
    ):
        """
        同步版本：图像输入的结构化输出
        支持图像URL或本地文件路径
        
        Args:
            prompt: 对图像的提问或指令
            image_source: 图像URL或本地文件路径
            instructions: 系统指令
            text_format: 输出的结构化格式（Pydantic模型）
        """
        try:
            # 判断是URL还是本地路径，并转换为Base64
            if image_url.startswith(('http://', 'https://')):
                # 从URL下载图像
                response = requests.get(image_url)
                response.raise_for_status()
                image_data = base64.b64encode(response.content).decode('utf-8')
                image_url = f"data:image/jpeg;base64,{image_data}"   
            # 构建输入消息
            input_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": image_url
                        }
                    ]
                }
            ]
            
            # 调用API
            response = self.client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=input_messages,
                text_format=text_format
            )
            
            return response.output_parsed if text_format else response.output_text
            
        except Exception as e:
            raise RuntimeError(f"图像结构化响应失败: {e}")
    
    async def async_get_structured_image_response(
        self, 
        prompt: str, 
        image_url: str, 
        instructions: str = "你是一个专业的图像分析助手。请根据图像内容回答问题。",
        text_format: Optional[Type[BaseModel]] = None
    ):
        """
        异步版本：图像输入的结构化输出
        支持图像URL或本地文件路径
        
        Args:
            prompt: 对图像的提问或指令
            image_source: 图像URL或本地文件路径
            instructions: 系统指令
            text_format: 输出的结构化格式（Pydantic模型）
        """
        try:         
            # 异步处理图像源：URL或本地文件
            if image_url.startswith(('http://', 'https://')):
                # 异步下载网络图像
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        response.raise_for_status()
                        image_content = await response.read()
                        image_data = base64.b64encode(image_content).decode('utf-8')
                        processed_image_url = f"data:image/jpeg;base64,{image_data}"

            # 构建输入消息
            input_messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image", 
                            "image_url": processed_image_url
                        }
                    ]
                }
            ]
            
            # 异步调用API
            response = await self.async_client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=input_messages,
                text_format=text_format
            )
            
            return response.output_parsed if text_format else response.output_text
            
        except Exception as e:
            raise RuntimeError(f"异步图像结构化响应失败: {e}")

    


if __name__ == "__main__":
    from typing import Optional, Dict, Any, AsyncGenerator, List, Literal
    import json

    async def main():
        """异步测试主函数"""
        
        class Character(BaseModel):
            setting: str = Field(..., alias="setting")
            appearance: str = Field(..., alias="appearance")

        # 初始化客户端
        client = GPTClient(config_path="config/openai/config.yaml")
        
        instructions = """
        你是一个专业的图像分析助手。将根据输入图像以及用户提供的简要描述来返回详细的图像内容解析文本。

        用户提供的描述：
        {description}

        要求：
            - 首先需要分析输入图像是人物、场景还是物品
            - 如果是人物，则返回的json结构中，需要生成`setting`字段的内容，该字段是人物的人设，例如："曾经是烟草世家的少爷，但家族破产之后沦落街头变成乞丐......"
            - 如果是场景或者物品，则`setting`字段为空字符串，只需要生成`appearance`字段即可，该字段是人物、物品或者场景的外观描述。
            - 场景或者物品的外观`appearance`中，不能出现任何人物的描述，错误示例如："幽静的森林小径上有一个人在散步"。正确示例为："幽静的森林小径"
            - 最终的字段值需要以{language}语种输出

        返回结构遵循一下json结构：
            - `setting`: 人物设定,场景和物品该字段值为空字符串，例如："高中生，性格内向、善良，喜欢绘画，对生活感到迷茫，希望找到属于自己的方向。"
            - `appearance`:  人物，场景或者物品的外观，例如："葱郁树荫下的旧木质长椅，周围是开满小花的草坪，阳光斑驳洒落其上，一旁有飞舞的樱花花瓣和远处的喷泉。"
    """
        
        prompt = "解析该图片内容"
        description = "流浪的中年乞丐"

        format_args = {
            "language": "zh-CN",  # 中文zh-CN, 英文en-US, 日语ja-JP
            "description": description,
        }
        instructions = instructions.format(**format_args)

        try:
            # 异步调用
            result = await client.async_get_structured_image_response(
                prompt="请分析这张图像中的内容和风格",
                image_url="https://fresource.laihua.com/2025-12-17/06ef6a134081471bb3c1239ca153012c.jpg",
                instructions=instructions,
                text_format=Character
            )
            
            # 处理结果
            result_dict = {
                "name": result.name,
                "setting": result.setting,
                "appearance": result.appearance
            }
            print("异步调用结果:", result_dict)
            
        except Exception as e:
            print(f"异步调用失败: {e}")
    asyncio.run(main())



#     class Character(BaseModel):
#         name: str
#         setting: str = Field(..., alias="setting")
#         appearance: str = Field(..., alias="appearance")

#     client = GPTClient(config_path="config/openai/config.yaml")
#     instructions = """
#     你是一个专业的图像分析助手。将根据输入图像以及用户提供的简要描述来返回详细的图像内容解析文本。

#     用户提供的描述：
#     {description}

#     要求：
#         - 首先需要分析输入图像是人物、场景还是物品
#         - 如果是人物，则返回的json结构中，需要生成`setting`字段的内容，该字段是人物的人设，例如：“曾经是烟草世家的少爷，但家族破产之后沦落街头变成乞丐......”
#         - 如果是场景或者物品，则`setting`字段为空字符串，只需要生成`appearance`字段即可，该字段是人物、物品或者场景的外观描述。
#         - 场景或者物品的外观`appearance`中，不能出现任何人物的描述，错误示例如：“幽静的森林小径上有一个人在散步”。正确示例为：“幽静的森林小径”
#         - 最终的字段值需要以{language}语种输出

#     返回结构遵循一下json结构：
#         - `name`: 图像中主体（人物，场景，物品）的名字，例如“张三”， “咖啡店”， “水杯”
#         - `setting`: 人物设定，例如：“高中生，性格内向、善良，喜欢绘画，对生活感到迷茫，希望找到属于自己的方向。”
#         - `appearance`:  人物，场景或者物品的外观，例如：“葱郁树荫下的旧木质长椅，周围是开满小花的草坪，阳光斑驳洒落其上，一旁有飞舞的樱花花瓣和远处的喷泉。”
# """
#     prompt = """
#     解析该图片内容
# """

#     description = "流浪的中年乞丐"

#     format_args = {
#         "language": "zh-CN",  # 中文zh-CN, 英文en-US, 日语ja-JP
#         "description": description,
#     }
#     instructions = instructions.format(**format_args)

#     result = client.get_structured_image_response(
#         prompt="请分析这张图像中的内容和风格",
#         image_url="https://fresource.laihua.com/2025-12-17/06ef6a134081471bb3c1239ca153012c.jpg",
#         instructions=instructions,
#         text_format=Character
#     )
#     result = {
#         "name": result.name,
#         "setting": result.setting,
#         "appearance": result.appearance
#     }
#     print("同步调用结果:", result)


    # class TotalShotsData(BaseModel):
    #     """表示分镜的总数和每个分镜的时长"""
    #     total_shots: int = Field(..., description="分镜的总数")
    #     duration_list: List[float] = Field(..., description="每个分镜的时长（仅能是 4.00, 8.00, 12.00）")

    # class TotalShots(BaseModel):
    #     data: Optional[TotalShotsData]
    # client = GPTClient(config_path="config/openai/config.yaml")

    # async def test_async_structured_response():
    #     """测试异步结构化响应"""
    #     client = GPTClient(config_path="config/openai/config.yaml")
        
    #     instructions = """
    #     你是一名专业的动漫分镜时长设计师。你的任务是根据视频总时长 60（单位：秒）决定生成的分镜数量，每个分镜时长仅可选 4.00 、8.00和12.00，且所有分镜时长之和必须等于 60。

    # # 核心指令
    # 1.  **输出格式**：必须严格遵循以下 JSON 格式，输出分镜总数和每个分镜的时长：
    # # JSON字段定义（必须严格遵守）
    # -   `total_shots`: （整数）分镜总数（s）。
    # -   `duration_list`: （列表）每个分镜的时长（s），每个分镜时长仅可选 4.00 、8.00和12.00，且所有分镜时长之和必须等于 60。
    # """
        
    #     try:
    #         # 使用异步方法替代同步方法
    #         totalshots = await client.async_get_structured_response(
    #             prompt="一个中国的道士下山捉妖", 
    #             instructions=instructions,
    #             text_format=TotalShots
    #         )
    #         print("异步调用结果:", totalshots)
    #         return totalshots
    #     except Exception as e:
    #         print("异步调用报错：", repr(e))
    #         return None

    # # 运行异步测试
    # result = asyncio.run(test_async_structured_response())