from ..schemas.user import UserRegister, UserLogin, UserSchema, UserResponse
from ..middlewares.jwt_handlers import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated
from ..services.user import UserService
from ..exceptions import UserAlreadyExistsError, IncorrectLoginDataError
from ..dependencies import get_user_service
from ..ratelimiting import limiter

router = APIRouter(tags=["user"], prefix="/users")

@router.post("/register")
@limiter.limit("1/15minutes")
async def user_register(request: Request, register_data: UserRegister, service: UserService = Depends(get_user_service)) -> dict:
    try:
        token = await service.register(register_data)
        return token

    except UserAlreadyExistsError as error:
        raise HTTPException(status_code=409, detail=str(error))

@router.post("/login")
@limiter.limit("1/minute")
async def login(request: Request, login_data: UserLogin, service: UserService = Depends(get_user_service)) -> dict:
    try:
        token = await service.login(login_data)
        return token

    except IncorrectLoginDataError as error:
        raise HTTPException(status_code=401, detail=str(error))

@router.get("/me")
@limiter.limit("5/minute")
async def read_me(request: Request, current_user: Annotated[UserSchema, Depends(get_current_user)]):
    if current_user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return UserResponse.model_validate(current_user)