from redis.asyncio import from_url
from ..core.config import CacheSettings

async def get_redis():
    async with from_url(CacheSettings.connection_url, decode_responses=True) as redis_client:
        yield redis_client