# db/redis.py
import redis
import json
import time
from typing import Tuple
from redis import Redis
from typing import Optional, Dict, Any
import logging
import threading
import redis.asyncio as aredis
import json
from contextlib import asynccontextmanager, contextmanager
from typing import Optional, AsyncGenerator
import os
import asyncio
import uuid
from utils.config import redis_config

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 使用线程本地存储来保存每个线程的Redis连接池
thread_local = threading.local()
redis_host = redis_config['host']
redis_pwd = redis_config['password']

logger.info(f"🚀redis_host={redis_host}")

def get_redis_pool():
    """为每个线程创建独立的redis连接池"""
    if not hasattr(thread_local, 'redis_pool'):
        thread_local.redis_pool = aredis.BlockingConnectionPool(
            host=redis_host,
            password=redis_pwd,
            port=6379,
            db=0,
            max_connections=20,
            timeout=5,  # 等待5秒比较合理
            retry_on_timeout=True,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info(f"Created new Redis pool for thread {threading.current_thread().name}")
    return thread_local.redis_pool

@asynccontextmanager
async def get_redis_connection() -> AsyncGenerator[aredis.Redis, None]:
    """异步上下文管理器：自动归还连接"""
    pool = get_redis_pool()
    conn = aredis.Redis(connection_pool=pool)
    try:
        yield conn
    except Exception as ex:
        logger.error(f"Redis connection error: {ex}")
        raise ex
    finally:
        await conn.aclose()



class AsyncRedisLock:
    """异步 Redis 分布式锁"""
    def __init__(self, lock_key: str, expire_time: int = 30):
        """
        初始化异步 Redis 锁
        Args:
            lock_key: 锁的键名
            expire_time: 锁的过期时间（秒）
        """
        self.lock_key = f"lock:{lock_key}"
        self.expire_time = expire_time
        self.identifier = None
    
    async def acquire(self, timeout: int = 10) -> bool:
        """
        异步获取锁
        Args:
            timeout: 获取锁的超时时间（秒）
        Returns:
            bool: 是否成功获取锁
        """
        self.identifier = str(uuid.uuid4())
        end_time = asyncio.get_event_loop().time() + timeout
        
        async with get_redis_connection() as redis:
            while asyncio.get_event_loop().time() < end_time:
                # 使用 SET NX PX 命令原子性地设置锁
                result = await redis.set(
                    self.lock_key, 
                    self.identifier, 
                    nx=True, 
                    px=self.expire_time * 1000
                )
                if result: return True
                # 异步等待一小段时间后重试
                await asyncio.sleep(0.05)
        
        logger.warning(f"获取锁超时: {self.lock_key}")
        return False
    
    async def release(self) -> bool:
        """
        异步释放锁
        Returns:
            bool: 是否成功释放锁
        """
        if not self.identifier:
            return False
            
        # 使用Lua脚本保证原子性释放
        lua_script = """
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
        """
        async with get_redis_connection() as redis:
            try:
                result = await redis.eval(lua_script, 1, self.lock_key, self.identifier)
                success = result == 1
                if not success:
                    logger.error(f"释放锁失败（可能已过期或被其他进程持有）: {self.lock_key}")
                return success
            except Exception as e:
                logger.error(f"释放锁时发生错误: {e}")
                return False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        if not await self.acquire():
            raise asyncio.TimeoutError(f"获取锁 {self.lock_key} 超时")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.release()

'''
async with AsyncRedisLock("order:2001:process", expire_time=30) as lock:
        # 在锁的保护下执行操作
        print("正在处理订单...")
        # 模拟异步业务处理
        await asyncio.sleep(2)
        print("订单处理完成")
'''



