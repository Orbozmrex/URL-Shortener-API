from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database.models import Url, Visit
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

        visits_stmt = select(func.count()).select_from(Visit).where(Visit.url_id == url.id)
        visits = await self.session.scalar(visits_stmt)

        days_stmt = select(
                func.date(Visit.visited_at).label("day"),
                func.count(Visit.id)).group_by(func.date(Visit.visited_at)).order_by(func.date(Visit.visited_at).asc()).where(Visit.url_id == url.id)
        days_result = await self.session.execute(days_stmt)

        days = [{str(row.day): row.count} for row in days_result.all()]

        url_model = Url_schema.model_validate(url)
        json = url_model.model_dump()
        json["visits"] = visits
        json["days"] = days
        return json