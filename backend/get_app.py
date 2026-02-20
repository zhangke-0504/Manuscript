import logging
from contextlib import asynccontextmanager
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

def setup_logging() -> None:
    """最简日志配置，避免重复处理器。"""
    root = logging.getLogger()
    if root.handlers:
        return  # 已配置
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    root.addHandler(handler)

from db.sqlite import init_db

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # 应用启动前
    init_db()  # 数据库初始化，例如建表
    yield
    # 应用关闭后
    

def create_app() -> FastAPI:
    """创建 FastAPI 实例并挂载中间件。"""
    app = FastAPI(
        title="Manuscript API",
        description="简化版后端服务（可扩展路由）",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=app_lifespan
    )

    # 开放跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app

def register_routers(app: FastAPI) -> None:
    """集中注册路由，保持可扩展结构。"""
    env = os.getenv("APP_ENV", "dev")
    api_base = "/api"  

    # health 路由（测试服务响应）
    from routers.health.interface import router as demo_router
    app.include_router(demo_router, prefix=f"{api_base}/health", tags=["health"])

    # novel 路由
    from routers.novel.novel import router as novel_router
    app.include_router(novel_router, prefix=f"{api_base}/novel", tags=["novel"])

    # chapter 路由
    from routers.chapter.chapter import router as chapter_router
    app.include_router(chapter_router, prefix=f"{api_base}/chapter", tags=["chapter"])

    # character 路由
    from routers.character.character import router as character_router
    app.include_router(character_router, prefix=f"{api_base}/character", tags=["character"])

    # model_providers 路由
    from routers.model_providers.model_providers import router as model_providers_router
    app.include_router(model_providers_router, prefix=f"{api_base}/model_providers", tags=["model_providers"])

    # working_flow 路由
    from routers.working_flow.working_flow import router as working_flow_router
    app.include_router(working_flow_router, prefix=f"{api_base}/working_flow", tags=["working_flow"])

# 实例化应用并注册路由
setup_logging()
app = create_app()
register_routers(app)
def mount_static(app: FastAPI) -> None:
    # Serve frontend static files. When running from source, static files are
    # located at backend/dist/www; when frozen (exe in backend/dist), static
    # files are next to the exe in backend/dist/www -> sys.executable parent.
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        static_dir = os.path.join(exe_dir, "www")
    else:
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(backend_dir, "dist", "www")

    # Only mount if the directory exists
    if os.path.isdir(static_dir):
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    else:
        logging.getLogger("app").warning("Static directory not found: %s", static_dir)

mount_static(app)