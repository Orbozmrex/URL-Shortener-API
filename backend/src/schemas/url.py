from pydantic import BaseModel, ConfigDict
from datetime import datetime
from pydantic import AnyHttpUrl
from typing import Annotated
from ..core.config import URLSettings
from fastapi import Query

class Url(BaseModel):
    url: str
    token: str
    created_at: datetime
    expires_at: datetime | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class UrlUpdate(BaseModel):
    url: AnyHttpUrl | None = None
    token: Annotated[str | None, Query(max_length=URLSettings.custom_max_length)] = None
    expires_at: datetime | None = None