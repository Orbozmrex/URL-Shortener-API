from ..core.utils import generate_short_code
from ..core.exceptions import ForbiddenResourceError, UrlNotFoundError, InvalidCodeError, UnauthorizedError, UrlAlreadyExistsError, UrlNotAvailableError, NoPermissionError
from ..schemas.url import UrlUpdate, Url
from ..core.utils import generate_qr_code
from ..repositories.url import UrlCachedRepository, UrlRepository
from ..core.config import CacheSettings
from sqlalchemy.exc import IntegrityError

class UrlService:
    def __init__(self, repo: UrlRepository, cache: UrlCachedRepository):
        self.repo = repo
        self.cache = cache
        self.cache_prefix = CacheSettings.url_prefix
        self.cache_ttl = CacheSettings.url_ttl
        self.user_urls_prefix = CacheSettings.user_prefix

    async def invalidate_user_urls_cache(self, email: str | None) -> None:
        if email is None:
            return
        await self.cache.delete(f"{self.user_urls_prefix}:{email}")

    async def shorten(self, url, current_user, custom_code = None, expires_at = None):
        current_user_id = None
        if current_user:
            current_user_id = current_user.id

            if not current_user.is_active:
                raise NoPermissionError("User is banned")

        if custom_code and not current_user:
            raise UnauthorizedError("Unauthorized")

        if custom_code is not None:
            try:
                await self.repo.create(current_user_id, url, custom_code, expires_at)
                final_code = custom_code
            except IntegrityError:
                await self.repo.session.rollback()
                raise UrlAlreadyExistsError("URL already exists")
        else:
            while True:
                generated_code = await generate_short_code()
                try:
                    await self.repo.create(current_user_id, url, generated_code, expires_at)
                    final_code = generated_code
                    break
                except IntegrityError:
                    await self.repo.session.rollback()

        await self.cache.set(f"{self.cache_prefix}:{final_code}", str(url), self.cache_ttl)
        await self.invalidate_user_urls_cache(current_user.email)
        return {"url": url, "short_code": final_code}

    async def redirect(self, short_code):
        if not short_code:
            raise InvalidCodeError("Invalid short code")

        cached_url = await self.cache.get(f"{self.cache_prefix}:{short_code}")
        if cached_url is not None:
            await self.repo.add_visit(short_code)
            return cached_url

        url = await self.repo.get_by_code(short_code)

        if not url:
            raise UrlNotFoundError("URL not found")

        if not url.is_active:
            raise UrlNotAvailableError("URL is no longer active")

        await self.repo.add_visit(short_code, url)

        await self.cache.set(f"{self.cache_prefix}:{short_code}", url.url, self.cache_ttl)
        return url.url

    async def update(self, short_code, update_data: UrlUpdate, current_user):
        if current_user is None:
            raise UnauthorizedError("Unauthorized")

        url = await self.repo.get_by_code(short_code)
        if not url:
            raise UrlNotFoundError("URL not found")

        if not url.owner_id == current_user.id:
            raise ForbiddenResourceError("Forbidden resource")

        try:
            updated = await self.repo.update(url, update_data)
        except IntegrityError:
            await self.repo.session.rollback()
            raise UrlAlreadyExistsError("URL already exists")
        
        await self.cache.delete(f"{self.cache_prefix}:{short_code}")
        await self.invalidate_user_urls_cache(current_user.email)
        return Url.model_validate(updated)

    async def deactivate_by_code(self, short_code, current_user):
        if current_user is None:
            raise UnauthorizedError("Unauthorized")
        
        url = await self.repo.get_by_code(short_code)

        if not url:
            raise UrlNotFoundError("URL not found")

        if not url.owner_id == current_user.id:
            raise ForbiddenResourceError("Forbidden resource")

        if not url.is_active:
            raise UrlNotAvailableError("URL is already deactivated")

        try:
            deactivated = await self.repo.deactivate(url)
            return deactivated
        finally:
            await self.cache.delete(f"{self.cache_prefix}:{short_code}")
            await self.invalidate_user_urls_cache(current_user.email)

    async def get_stats_by_code(self, short_code, current_user):
        url = await self.repo.get_by_code(short_code)

        if current_user is None:
            raise UnauthorizedError("Unauthorized")

        if not url:
            raise UrlNotFoundError("URL not found")
        
        if not url.owner_id == current_user.id:
            raise ForbiddenResourceError("Forbidden resource")

        cached_stats = await self.cache.get(f"{self.cache_prefix}:{short_code}:stats")
        if cached_stats is not None:
            return {'stats': cached_stats}
        
        stats = await self.repo.get_stats(url)

        await self.cache.set(f"{self.cache_prefix}:{short_code}:stats", stats, 300)
        return {'stats': stats}

    async def qr_code(self, short_code):
        qr_code = await generate_qr_code(short_code)
        return qr_code
        