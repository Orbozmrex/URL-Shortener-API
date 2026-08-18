from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from config import DatabaseSettings
from datetime import datetime
from typing import List
import secrets
from schemas.user import UserRegister
from .security import hash_password

engine = create_async_engine(DatabaseSettings.url)

session_maker = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    urls: Mapped[List["Url"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(nullable=False)
    token: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship(back_populates="urls")

    visits: Mapped[List["Visit"]] = relationship(back_populates="url", cascade="all, delete-orphan")

class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(ForeignKey("urls.id", ondelete="CASCADE"))
    url: Mapped["Url"] = relationship(back_populates="visits")

async def get_user(email):
    async with session_maker() as session:
        stmt = select(User).where(User.email == email)
        user = await session.scalars(stmt)
        return user.one_or_none()

async def add_user(data: UserRegister):
    async with session_maker() as session:
        hashed_password = await hash_password(data.password)
        new_user = User(email=data.email, hashed_password=hashed_password)
        session.add(new_user)
        await session.commit()
    
async def add_url(owner_id, url):
    token = secrets.token_urlsafe(7)
    async with session_maker() as session:
        new_url = Url(token=token, url=url, owner_id=owner_id)
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