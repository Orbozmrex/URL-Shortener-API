from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from ..config import DatabaseSettings

engine = create_async_engine(DatabaseSettings.url)

session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    session = session_maker()
    try:
        yield session
        await session.commit()
    except:
        await session.rollback()
        raise
    finally:
        await session.close()