from fastapi import FastAPI
import uvicorn
import asyncio

from .routers.user import router as user_router
from .routers.urls import router as urls_router

app = FastAPI()

app.include_router(user_router)
app.include_router(urls_router)

if __name__ == "__main__":
    pass