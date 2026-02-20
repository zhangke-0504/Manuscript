# routers/model_providers/model_providers.py
import os
import sys
import logging
import asyncio
import aiofiles
import aiofiles.os
from typing import Any, Dict, Optional

import yaml
from fastapi import APIRouter
from pydantic import BaseModel

from utils.config import Model_Providers
from utils.enum import ResponseCode
from utils.error import ManuScriptValidationMsg

router = APIRouter()
logger = logging.getLogger("model_providers_router")

def _get_root_dir() -> str:
    """Return project root directory.

    When running as a PyInstaller onefile exe, __file__ points into a temporary
    extraction directory (e.g. _MEIxxxxx). In that case prefer resolving root
    relative to the executable so config files are placed next to the project
    structure (backend/config/...).
    """
    if getattr(sys, "frozen", False):
        # sys.executable -> .../backend/dist/server.exe
        # project root should be the backend folder (two levels up)
        return os.path.dirname(os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT_DIR = _get_root_dir()

class ProviderResponse(BaseModel):
    code: int
    msg: str
    data: Optional[Dict] = None


async def _provider_path(provider: str) -> str:
    rel = Model_Providers.get(provider)
    if not rel:
        raise ManuScriptValidationMsg(
            msg=f"Unsupported provider: {provider}",
            code=ResponseCode.CLIENT_ERROR.value,
        )
    
    # 构建完整的配置文件路径（确保指向文件，不是目录）
    config_path = os.path.join(ROOT_DIR, rel.replace("/", os.sep))
    
    # 创建父目录（如果不存在）
    parent_dir = os.path.dirname(config_path)
    if not await aiofiles.os.path.exists(parent_dir):
        await aiofiles.os.makedirs(parent_dir, exist_ok=True)
    
    # 如果配置文件不存在，创建一个空的
    if not await aiofiles.os.path.exists(config_path):
        async with aiofiles.open(config_path, "w", encoding="utf-8") as f:
            await f.write("api_key: xxxxxx")
    
    return config_path


async def _load_yaml(path: str) -> Dict[str, Any]:
    exists = await asyncio.to_thread(os.path.exists, path)
    if not exists:
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
    path = await _provider_path(payload.provider)
    cfg = await _load_yaml(path)
    return ProviderResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Get config successfully",
        data={"provider": payload.provider, "config": cfg, "path": path},
    )


class UpdateProviderConfigRequest(BaseModel):
    provider: str
    values: Dict[str, Any]


@router.post("/update", response_model=ProviderResponse)
async def update_provider_config_endpoint(payload: UpdateProviderConfigRequest):
    if not payload.values:
        raise ManuScriptValidationMsg(
            msg="No values to update",
            code=ResponseCode.CLIENT_ERROR.value,
        )
    path = await _provider_path(payload.provider)
    before = await _load_yaml(path)
    after = {**before, **payload.values}
    await _save_yaml(path, after)
    logger.info("Provider config updated: %s, keys=%s", payload.provider, list(payload.values.keys()))
    cfg = await _load_yaml(path)
    return ProviderResponse(
        code=ResponseCode.SUCCESS.value,
        msg="Update config successfully",
        data={"provider": payload.provider, "config": cfg, "path": path},
    )