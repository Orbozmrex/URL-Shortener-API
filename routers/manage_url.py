from fastapi import APIRouter, HTTPException
from utils.db import get_url_stats, get_url

router = APIRouter(prefix="/manage")

@router.get("/stats/{token}")
async def get_stats(token: str):
    if not await get_url(token):
        raise HTTPException(status_code=404, detail="URL not found")
    return {'token': token, 'stats': await get_url_stats(token)}