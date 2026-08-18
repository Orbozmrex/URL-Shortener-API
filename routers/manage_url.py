from fastapi import APIRouter, HTTPException, Depends
from utils.jwt_handlers import get_current_user
from utils.database import get_url, get_url_info
from typing import Annotated
from schemas.user import UserSchema

router = APIRouter(prefix="/manage", tags=["manage url"])

@router.get("/info/{token}")
async def get_info(token: str, current_user: Annotated[UserSchema, Depends(get_current_user)]) -> dict:
    url = await get_url(token)
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    if not url.owner_id == current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden resource")
    stats = await get_url_info(token)
    return {'stats': stats}