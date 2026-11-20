from redis.asyncio import from_url
from ..core.config import settings

async def get_redis():
    async with from_url(settings.cache.connection_url, decode_responses=True) as redis_client:
        yield redis_client