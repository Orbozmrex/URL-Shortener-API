from pwdlib import PasswordHash
from datetime import datetime
from ..core.config import settings
import jwt

phash = PasswordHash.recommended()

async def verify_password(user, login_password):
    if not user:
        return None
    
    return phash.verify(login_password, user.hashed_password)

async def hash_password(plain_password):
    return phash.hash(plain_password)

async def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + settings.jwt.session_ttl})
    return jwt.encode(to_encode, settings.jwt.secret, algorithm=settings.jwt.algorithm)