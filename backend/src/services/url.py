from ..core.utils import generate_short_code
from ..core.exceptions import ForbiddenResourceError, UrlNotFoundError, InvalidCodeError, UnauthorizedError, UrlAlreadyExistsError, UrlNotAvailableError, NoPermissionError
from ..schemas.url import UrlUpdate, Url

class UrlService:
    def __init__(self, repo):
        self.repo = repo

    async def shorten(self, url, current_user, custom_code = None, expires_at = None):
        current_user_id = None
        if current_user:
            current_user_id = current_user.id

            if not current_user.is_active:
                raise NoPermissionError("User is banned")

        if custom_code and not current_user:
            raise UnauthorizedError("Unauthorized")
        
        existing_url = await self.repo.get_by_code(custom_code)
        if existing_url is not None:
            raise UrlAlreadyExistsError("URL already exists")

        if custom_code is None:
            while True:
                custom_code = await generate_short_code()
                if await self.repo.get_by_code(custom_code) is None:
                    break

        await self.repo.create(current_user_id, url, custom_code, expires_at)
        return {"url": url, "short_code": custom_code}

    async def redirect(self, short_code):
        if not short_code:
            raise InvalidCodeError("Invalid short code")

        url = await self.repo.get_by_code(short_code)

        if not url:
            raise UrlNotFoundError("URL not found")

        if not url.is_active:
            raise UrlNotAvailableError("URL is no longer active")

        await self.repo.add_visit(short_code)
        return url.url

    async def update(self, short_code, update_data: UrlUpdate, current_user):
        url = await self.repo.get_by_code(short_code)

        if current_user is None:
            raise UnauthorizedError("Unauthorized")

        if not url:
            raise UrlNotFoundError("URL not found")

        if not url.owner_id == current_user.id:
            raise ForbiddenResourceError("Forbidden resource")

        if update_data.token:
            existing_url = await self.repo.get_by_code(update_data.token)
            if existing_url is not None:
                raise UrlAlreadyExistsError("URL already exists")


        updated = await self.repo.update(url, update_data)
        return Url.model_validate(updated)

    async def deactivate_by_code(self, short_code, current_user):
        url = await self.repo.get_by_code(short_code)

        if current_user is None:
            raise UnauthorizedError("Unauthorized")

        if not url:
            raise UrlNotFoundError("URL not found")

        if not url.owner_id == current_user.id:
            raise ForbiddenResourceError("Forbidden resource")

        if not url.is_active:
            raise UrlNotAvailableError("URL is already deactivated")

        deactivated = await self.repo.deactivate(url)
        return deactivated


    async def get_stats_by_code(self, short_code, current_user):
        url = await self.repo.get_by_code(short_code)

        if current_user is None:
            raise UnauthorizedError("Unauthorized")

        if not url:
            raise UrlNotFoundError("URL not found")
        
        if not url.owner_id == current_user.id:
            raise ForbiddenResourceError("Forbidden resource")
        
        stats = await self.repo.get_stats(url)
        return {'stats': stats}