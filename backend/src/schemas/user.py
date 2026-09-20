from pydantic import EmailStr, BaseModel, ConfigDict
from .url import Url
from typing import List

class UserSchema(BaseModel):
    id: int
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str

class UserLogin(UserRegister):
    pass

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    urls: List[Url]

    model_config = ConfigDict(from_attributes = True)