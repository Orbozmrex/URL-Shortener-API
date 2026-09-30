from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .update_status import update_expired_status

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(update_expired_status, trigger=IntervalTrigger(minutes=5), id="update_expired_urls", replace_existing=True)

    scheduler.start()
    yield
    scheduler.shutdown()

scheduler_lifespan = lifespan