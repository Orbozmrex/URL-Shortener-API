from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.models import Url, Visit
from ..utils import generate_short_code
from ..schemas.url import Url as Url_schema

class UrlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_code(self, short_code):
        stmt = select(Url).where(Url.token == short_code)
        url = await self.session.scalar(stmt)
        return url
    
    async def create(self, owner_id, url, short_code):
        new_url = Url(token=short_code, url=str(url), owner_id=owner_id)
        self.session.add(new_url)
        await self.session.commit()
        return short_code

    async def add_visit(self, short_code):
        stmt = select(Url).where(Url.token == short_code)
        url = await self.session.scalar(stmt)
        self.session.add(Visit(url_id=url.id))
        await self.session.commit()

    async def get_info_by_code(self, short_code):
        url = await self.get_by_code(short_code)
        stmt = select(func.count()).select_from(Visit).where(Visit.url_id == url.id)
        visits = await self.session.scalar(stmt)
        url_model = Url_schema.model_validate(url)
        json = url_model.model_dump()
        json["visits"] = visits
        return json