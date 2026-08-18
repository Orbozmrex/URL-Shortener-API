from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from utils.database import add_url, get_url, init_db, add_visit, get_user, add_user
from schemas.user import UserRegister, UserLogin, UserSchema, UserResponse
from utils.jwt_handlers import get_current_user
from utils.security import verify_password, create_token
from routers.manage_url import router as management_router
import asyncio
from typing import Annotated
from pydantic import AnyHttpUrl

app = FastAPI()
app.include_router(management_router)

@app.get("/{token}", response_class=RedirectResponse, tags=["redirect"])
async def redirect(token: str) -> RedirectResponse:
    if not token:
        raise HTTPException(status_code=404, detail="Invalid token")

    url = await get_url(token)

    if not url:
        raise HTTPException(status_code=404, detail="Url not found")
    await add_visit(token)
    return RedirectResponse(url=url.url)

@app.post("/shorten", tags=["shorten"])
async def shorten(url: AnyHttpUrl, current_user: Annotated[UserSchema, Depends(get_current_user)]) -> dict:
    token = await add_url(current_user.id, url)
    return {"url": url, "token": token}

@app.post("/register", tags=["user"])
async def user_register(register_data: UserRegister) -> dict:
    await add_user(register_data)
    token = await create_token({"email": register_data.email})
    return {"token": token, "token_type": "Bearer"}

@app.post("/login", tags=["user"])
async def login(login_data: UserLogin) -> dict:
    user = await get_user(login_data.email)
    if not user or not await verify_password(user, login_data.password):
        raise HTTPException(status_code=401, detail="Incorrect login or password")
    return {"token": await create_token({"email": login_data.email}), "token_type": "Bearer"}

@app.get("/users/me", tags=["user"])
async def read_me(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    return UserResponse.model_validate(current_user)

async def main():
    await init_db()

if __name__ == "__main__":
    asyncio.run(main())