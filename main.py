from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from utils.db import init_db, add_url, get_url
import asyncio

app = FastAPI()

@app.get("/{token}", response_class=RedirectResponse, tags=["redirect"])
async def redirect(token: str) -> RedirectResponse:
    if not token:
        raise HTTPException(status_code=404, detail="Invalid token")

    url = await get_url(token)

    if not url:
        raise HTTPException(status_code=404, detail="Url not found")
    return RedirectResponse(url=url)

@app.post("/shorten", tags=["shorten"])
async def shorten(url: str) -> str:
    return await add_url(url) #returns token

async def main():
    await init_db()

if __name__ == "__main__":
    asyncio.run(main())