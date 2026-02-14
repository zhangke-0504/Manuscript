import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
import threading
import logging
from utils.config import sql_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 数据库连接
# env = os.getenv("APP_ENV", "test")
# database = os.getenv("DATABASE_URL", "postgresql+asyncpg://dev_user:Poag$epaer123!@172.22.16.16:5432/")
# dataset = "frame_forge_test" if env in ["test", "person"] else "frame_forge"

database = f"postgresql+asyncpg://{sql_config['user']}:{sql_config['password']}@{sql_config['host']}:5432/"
dataset = sql_config['database']
logger.info(f"🚀dataset={dataset},\n 🚀os.environ['APP_ENV']={os.environ['APP_ENV']}")
database_url = database + dataset
database_url_sync = database_url.replace("postgresql+asyncpg://", "postgresql://")
Base = declarative_base()

# 创建异步引擎
engine = create_async_engine(database_url, echo=False, future=True)
# 创建 session 工厂
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,         # 指定使用异步会话类
    autocommit=False,            # 通常保持 False
    autoflush=False,             # 可根据情况关闭
    expire_on_commit=False       # ⚠️ 推荐加上：防止提交后对象过期
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,         # 指定使用异步会话类
    autocommit=False,            # 通常保持 False
    autoflush=False,             # 可根据情况关闭
    expire_on_commit=False       # ⚠️ 推荐加上：防止提交后对象过期
)

thread_local = threading.local()
def get_db_session():
    """为每个线程创建独立的连接"""
    if not hasattr(thread_local, 'sessionmaker'):
        thread_local.sessionmaker = sessionmaker(
            bind=create_async_engine(database_url, echo=False, future=True),
            class_=AsyncSession,         # 指定使用异步会话类
            autocommit=False,            # 通常保持 False
            autoflush=False,             # 可根据情况关闭
            expire_on_commit=False       # ⚠️ 推荐加上：防止提交后对象过期
        )
    return thread_local.sessionmaker



# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# FastAPI 依赖：每个请求获取一个数据库会话
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# # 新增数据
# session = SessionLocal()
# article = Article(
#             title="abc",
#             content="long_content long_content long_content long_content",
#             summary="summary",
#             author="author"
#         )

# session.add(article)
# session.commit()
# session.refresh(article)

# # 查询数据
# article = session.query(Article).first()
# print(f"article={article}")

# # 修改数据
# article = session.query(Article).filter(Article.id == article.id).first()
# if article:
#     article.content = "new_content"
#     session.commit()

# article = session.query(Article).first()
# print(f"article={article}")

# # 删除数据
# article = session.query(Article).filter(Article.id == article.id).first()
# if article:
#     session.delete(article)
#     session.commit()
# article = session.query(Article).first()
# print(f"article={article}")
