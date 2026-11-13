import redis.asyncio as aioredis
from typing import AsyncGenerator
from app.core.config import settings

# Global connection pool
redis_client: aioredis.Redis | None = None

# Initializes the connection
async def init_redis():
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

# closes the connection on shutdown.
async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()

# FastAPI Dependency: Yields the async Redis client to endpoints.
async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    if redis_client is None:
        raise RuntimeError("Redis client is not initialized.")
    yield redis_client