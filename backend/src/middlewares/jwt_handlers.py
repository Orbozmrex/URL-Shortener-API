import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials 
from fastapi import Depends, HTTPException
from ..config import JWTSettings
from typing import Annotated
from ..services.user import UserService
from ..dependencies import get_user_service

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials , Depends(security_scheme)], service: UserService = Depends(get_user_service)):
    if credentials is None:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWTSettings.secret, algorithms=JWTSettings.algorithm)
        return await service.get_by_email(payload.get("email"))
    except:
        raise HTTPException(status_code=401, detail="Invalid token")