import logging
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_logging() -> None:
    """最简日志配置，避免重复处理器。"""
    root = logging.getLogger()
    if root.handlers:
        return  # 已配置
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s"))
    root.addHandler(handler)

def create_app() -> FastAPI:
    """创建 FastAPI 实例并挂载中间件。"""
    app = FastAPI(
        title="Manuscript API",
        description="简化版后端服务（可扩展路由）",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 开放跨域（起步阶段，生产建议收敛域名）
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

    # Demo 路由（用于联通性测试）
    from routers.demo.interface import router as demo_router
    app.include_router(demo_router, prefix=f"{api_base}/demo", tags=["Demo"])

# 实例化应用并注册路由
setup_logging()
app = create_app()
register_routers(app)