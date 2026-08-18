from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from config import DatabaseSettings
import secrets
from schemas.user import UserRegister
from schemas.url import Url as Url_schema
from .security import hash_password
from models.models import User, Url, Visit, Base
from fastapi import HTTPException

engine = create_async_engine(DatabaseSettings.url)

session_maker = async_sessionmaker(engine)

async def get_user(email):
    async with session_maker() as session:
        stmt = select(User).where(User.email == email).options(selectinload(User.urls))
        user = await session.execute(stmt)
        return user.scalar_one_or_none()


async def add_user(data: UserRegister):
    async with session_maker() as session:
        try:
            hashed_password = await hash_password(data.password)
            new_user = User(email=data.email, hashed_password=hashed_password)
            session.add(new_user)
            await session.commit()
        except IntegrityError as e:
                    await session.rollback()
                    raise HTTPException(status_code=409, detail="User already exists")
    
async def add_url(owner_id, url):
    token = secrets.token_urlsafe(7)
    async with session_maker() as session:
        new_url = Url(token=token, url=str(url), owner_id=owner_id)
        session.add(new_url)
        await session.commit()
    return token

async def get_url(token):
    async with session_maker() as session:
        stmt = select(Url).where(Url.token == token)
        url = await session.scalar(stmt)
        return url

async def add_visit(token):
    async with session_maker() as session:
        stmt = select(Url).where(Url.token == token)
        url = await session.scalar(stmt)
        session.add(Visit(url_id=url.id))
        await session.commit()

async def get_url_info(token):
    url = await get_url(token)
    async with session_maker() as session:
        stmt = select(func.count()).select_from(Visit).where(Visit.url_id == url.id)
        visits = await session.scalar(stmt)
        url_model = Url_schema.model_validate(url)
        json = url_model.model_dump()
        json["visits"] = visits
        return json

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)