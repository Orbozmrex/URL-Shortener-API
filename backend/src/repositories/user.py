from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models.models import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email) -> User | None:
        stmt = select(User).where(User.email == email).options(selectinload(User.urls))
        user = await self.session.execute(stmt)
        return user.scalar_one_or_none()

    async def register(self, email, hashed_password) -> User:
        new_user = User(email=email, hashed_password=hashed_password)
        self.session.add(new_user)
        await self.session.commit()
        return new_user