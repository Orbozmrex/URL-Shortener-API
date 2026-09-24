from ..repositories.user import UserRepository
from ..repositories.url import UrlRepository
from ..services.url import UrlService
from ..services.user import UserService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.db import get_session

def get_url_service(session: AsyncSession = Depends(get_session)) -> UrlService:
    repository = UrlRepository(session)
    return UrlService(repository)

def get_user_service(session: AsyncSession = Depends(get_session)) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)