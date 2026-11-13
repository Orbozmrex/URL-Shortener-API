from ..repositories.user import UserRepository, UserCachedRepository
from ..repositories.url import UrlRepository, UrlCachedRepository
from ..services.url import UrlService
from ..services.user import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.db import get_session
from ..cache.redis import get_redis

def get_url_service(session: AsyncSession = Depends(get_session), redis = Depends(get_redis)) -> UrlService:
    repository = UrlRepository(session)
    cache = UrlCachedRepository(redis)
    return UrlService(repository, cache)

def get_user_service(session: AsyncSession = Depends(get_session), redis = Depends(get_redis)) -> UserService:
    repository = UserRepository(session)
    cache = UserCachedRepository(redis)
    return UserService(repository, cache)