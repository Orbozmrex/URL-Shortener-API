from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from config import DatabaseSettings
from datetime import datetime
from typing import List
import secrets

engine = create_async_engine(DatabaseSettings.url)

session_maker = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column()
    token: Mapped[str] = mapped_column(unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    visits: Mapped[List["Visit"]] = relationship(back_populates="url", cascade="all, delete-orphan")

class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(ForeignKey("urls.id", ondelete="CASCADE"))
    url: Mapped["Url"] = relationship(back_populates="visits")

async def add_url(url):
    token = secrets.token_urlsafe(7)
    async with session_maker() as session:
        new_url = Url(token=token, url=url)
        session.add(new_url)
        await session.commit()
    return token

async def get_url(token):
    async with session_maker() as session:
        stmt = select(Url.url).where(Url.token == token)
        url = await session.scalar(stmt)
        return url

async def add_visit(token):
    async with session_maker() as session:
        stmt = select(Url).where(Url.token == token)
        url = await session.scalar(stmt)
        session.add(Visit(url_id=url.id))
        await session.commit()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
