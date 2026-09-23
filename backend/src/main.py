from fastapi import FastAPI
import uvicorn
import asyncio

from .routers.user import router as user_router
from .routers.urls import router as urls_router

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .ratelimiting import limiter


app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(user_router)
app.include_router(urls_router)

if __name__ == "__main__":
    pass