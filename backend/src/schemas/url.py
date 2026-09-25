from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Url(BaseModel):
    url: str
    token: str
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class Stats(Url):
    visits: int