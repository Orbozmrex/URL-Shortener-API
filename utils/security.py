from pwdlib import PasswordHash
from datetime import datetime, timedelta
from config import JWTSettings
import jwt

phash = PasswordHash.recommended()

async def verify_password(user, login_password):
    return phash.verify(login_password, user.hashed_password)

async def hash_password(plain_password):
    return phash.hash(plain_password)

async def create_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.now() + timedelta(days=30)})
    return jwt.encode(to_encode, JWTSettings.secret, algorithm=JWTSettings.algorithm)