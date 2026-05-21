from fastapi import APIRouter
from utils.db import get_url_stats

router = APIRouter(prefix="/manage")

@router.get("/stats/{token}")
async def get_stats(token: str):
    return {'token': token, 'stats': await get_url_stats(token)}