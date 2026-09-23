from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import RedirectResponse
from ..middlewares.jwt_handlers import get_current_user
from typing import Annotated
from pydantic import AnyHttpUrl
from ..schemas.user import UserSchema
from ..config import URLSettings
from ..services.urls import UrlService
from ..exceptions import ForbiddenResourceError, UrlNotFoundError, InvalidCodeError, UnauthorizedError, UrlAlreadyExistsError
from ..dependencies import get_url_service

router = APIRouter(tags=["urls"])


@router.get("/{short_code}", response_class=RedirectResponse)
async def redirect(short_code: str, service: UrlService = Depends(get_url_service)) -> RedirectResponse:
    try:
        url = await service.redirect(short_code)
        return RedirectResponse(url)
    
    except InvalidCodeError as error:
        raise HTTPException(status_code=404, detail=str(error))

    except UrlNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))

@router.post("/urls")
async def shorten(url: AnyHttpUrl, 
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
async def get_stats(short_code: str, current_user: Annotated[UserSchema, Depends(get_current_user)], service: UrlService = Depends(get_url_service)) -> dict:
    try:
        stats = await service.get_stats_by_code(short_code, current_user)
        return stats

    except ForbiddenResourceError as error:
        raise HTTPException(status_code=403, detail=str(error))

    except UrlNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error))

    