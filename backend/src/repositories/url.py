from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..database.models import Url, Visit
from ..schemas.url import Url as Url_schema, UrlUpdate

class UrlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_code(self, short_code):
        stmt = select(Url).where(Url.token == short_code)
        url = await self.session.scalar(stmt)
        return url
    
    async def create(self, owner_id, url, short_code, expires_at):
        new_url = Url(token=short_code, url=str(url), owner_id=owner_id, expires_at=expires_at)
        self.session.add(new_url)
        await self.session.commit()
        return short_code

    async def update(self, url: Url, update_data: UrlUpdate):
        update_data = update_data.model_dump(exclude_unset=True)

        #dynamically updates model attributes
        for key, value in update_data.items():
            #converts url: AnyHttpUrl to string
            if hasattr(value, 'unicode_string'):  
                value = str(value)

            setattr(url, key, value)
        
        await self.session.commit()
        return url

    async def deactivate(self, url: Url):
        url.is_active = False
        await self.session.commit()
        return url
        
    async def add_visit(self, short_code):
        stmt = select(Url).where(Url.token == short_code)
        url = await self.session.scalar(stmt)
        self.session.add(Visit(url_id=url.id))
        await self.session.commit()

    async def get_stats(self, url: Url):
        visits_stmt = select(func.count()).select_from(Visit).where(Visit.url_id == url.id)
        visits = await self.session.scalar(visits_stmt)

        days_stmt = select(
                func.date(Visit.visited_at).label("day"),
                func.count(Visit.id)).group_by(func.date(Visit.visited_at)).order_by(func.date(Visit.visited_at).asc()).where(Visit.url_id == url.id)
        days_result = await self.session.execute(days_stmt)

        days = [{"day": str(row.day), "visits": row.count} for row in days_result.all()]

        url_model = Url_schema.model_validate(url)
        json = url_model.model_dump()
        json["visits"] = {}
        json["visits"]["total"] = visits
        json["visits"]["days"] = days
        return json