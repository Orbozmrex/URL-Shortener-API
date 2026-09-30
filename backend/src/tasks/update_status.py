from sqlalchemy import update, func
from ..database.db import session_maker
from ..database.models import Url

async def update_expired_status():
    async with session_maker() as session:
        stmt = update(Url).where(Url.expires_at < func.now()).where(Url.is_active).values(is_active=False)
        await session.execute(stmt)
        await session.commit()