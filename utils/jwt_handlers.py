import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from fastapi import Depends, HTTPException
from config import JWTSettings
from typing import Annotated
from .database import get_user

security_scheme = HTTPBearer()

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials , Depends(security_scheme)]):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWTSettings.secret, algorithms=JWTSettings.algorithm)
        return await get_user(payload.get("email"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")