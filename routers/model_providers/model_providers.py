# routers/model_providers/model_providers.py
import os
import logging
import asyncio
from typing import Any, Dict, Optional

import yaml
from fastapi import APIRouter
from pydantic import BaseModel

from utils.config import Model_Providers
from utils.enum import ResponseCode
from utils.error import ManuScriptValidationMsg

router = APIRouter()
logger = logging.getLogger("model_providers_router")

# 项目根目录（从 routers/model_providers/ 回到项目根）
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ProviderResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Dict] = None

def _provider_path(provider: str) -> str:
    rel = Model_Providers.get(provider)
    if not rel:
        raise ManuScriptValidationMsg(
            msg=f"Unsupported provider: {provider}",
            code=ResponseCode.CLIENT_ERROR.value,
        )
    return os.path.join(ROOT_DIR, rel.replace("/", os.sep))


async def _load_yaml(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}

    def _read() -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            raise ManuScriptValidationMsg(
                msg="Config format error: expect a mapping",
                code=ResponseCode.SERVER_ERROR.value,
            )
        return data

    return await asyncio.to_thread(_read)


async def _save_yaml(path: str, data: Dict[str, Any]) -> None:
    def _write():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)

    await asyncio.to_thread(_write)

class GetProviderConfigRequest(BaseModel):
    provider: str
@router.post("/get", response_model=ProviderResponse)
async def get_provider_config_endpoint(payload: GetProviderConfigRequest):
    path = _provider_path(payload.provider)
    cfg = await _load_yaml(path)
    return ProviderResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Get config successfully",
        data={"provider": payload.provider, "config": cfg, "path": path},
    )

class UpdateProviderConfigRequest(BaseModel):
    provider: str
    values: Dict[str, Any]  # 局部更新（merge），仅覆盖传入字段
@router.post("/update", response_model=ProviderResponse)
async def update_provider_config_endpoint(payload: UpdateProviderConfigRequest):
    if not payload.values:
        raise ManuScriptValidationMsg(
            msg="No values to update",
            code=ResponseCode.CLIENT_ERROR.value,
        )
    path = _provider_path(payload.provider)
    before = await _load_yaml(path)
    # 合并更新（浅合并）
    after = {**before, **payload.values}
    await _save_yaml(path, after)
    logger.info("Provider config updated: %s, keys=%s", payload.provider, list(payload.values.keys()))
    # 返回更新后的配置
    cfg = await _load_yaml(path)
    return ProviderResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Update config successfully",
        data={"provider": payload.provider, "config": cfg, "path": path},
    )