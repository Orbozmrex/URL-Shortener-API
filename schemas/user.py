from pydantic import EmailStr, BaseModel, ConfigDict

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

    model_config = ConfigDict(from_attributes = True)