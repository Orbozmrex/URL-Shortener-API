from fastapi import APIRouter, Depends, Query, HTTPException, Request
from fastapi.responses import RedirectResponse
from ..middlewares.jwt_handlers import get_current_user
from typing import Annotated
from pydantic import AnyHttpUrl
from ..schemas.user import UserSchema
from ..core.config import URLSettings
from ..services.url import UrlService
from ..core.exceptions import ForbiddenResourceError, UrlNotFoundError, InvalidCodeError, UnauthorizedError, UrlAlreadyExistsError
from ..core.dependencies import get_url_service
from ..core.ratelimiting import limiter

router = APIRouter(tags=["urls"])


@router.get("/{short_code}", response_class=RedirectResponse, include_in_schema=False)
@limiter.limit("3/minute")
async def redirect(request: Request, short_code: str, service: UrlService = Depends(get_url_service)) -> RedirectResponse:
    try:
        url = await service.redirect(short_code)
        return RedirectResponse(url)
    
    except InvalidCodeError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except UrlNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.post("/urls")
@limiter.limit("5/minute")
async def shorten(request: Request, 
                  url: AnyHttpUrl, 
                  current_user: Annotated[UserSchema | None, Depends(get_current_user)], 
                  custom_code: Annotated[str | None, Query(max_length=URLSettings.custom_max_length)] = None, 
                  service: UrlService = Depends(get_url_service)) -> dict:
    try:
        result = await service.shorten(url, current_user, custom_code)
        return result

    except UrlAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

    except UnauthorizedError as error:
        raise HTTPException(status_code=401, detail=str(error))


@router.get("/urls/{short_code}/stats")
@limiter.limit("10/minute")
async def get_stats(request: Request, short_code: str, current_user: Annotated[UserSchema, Depends(get_current_user)], service: UrlService = Depends(get_url_service)) -> dict:
    try:
        stats = await service.get_stats_by_code(short_code, current_user)
        return stats

    except ForbiddenResourceError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except UrlNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error))

    