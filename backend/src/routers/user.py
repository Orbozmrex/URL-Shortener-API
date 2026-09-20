from ..schemas.user import UserRegister, UserLogin, UserSchema, UserResponse
from ..middlewares.jwt_handlers import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from ..services.user import UserService
from ..exceptions import UserAlreadyExistsError, IncorrectLoginDataError
from ..dependencies import get_user_service

router = APIRouter(tags=["user"], prefix="/users")

@router.post("/register")
async def user_register(register_data: UserRegister, service: UserService = Depends(get_user_service)) -> dict:
    try:
        token = await service.register(register_data)
        return token

    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.post("/login")
async def login(login_data: UserLogin, service: UserService = Depends(get_user_service)) -> dict:
    try:
        token = await service.login(login_data)
        return token

    except IncorrectLoginDataError as error:
        raise HTTPException(status_code=401, detail=str(error))

@router.get("/me")
async def read_me(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return UserResponse.model_validate(current_user)