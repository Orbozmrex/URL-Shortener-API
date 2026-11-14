from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..database.models import User
from redis.asyncio import Redis
import orjson

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email) -> User | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.urls))
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def get_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id).options(selectinload(User.urls))
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def register(self, email, hashed_password) -> User:
        new_user = User(email=email, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.commit()
        return new_user

class UserCachedRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, name: str):
        data = await self.redis.get(name)
        if data is None:
            return None
        return orjson.loads(data)

    async def set(self, key: str, value: str | dict, ex: int):
        await self.redis.set(name=key, value=orjson.dumps(value), ex=ex)

    async def delete(self, key: str):
        await self.redis.delete(key)