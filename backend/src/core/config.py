from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

class DatabaseSettings:
    _user = os.getenv("DB_USER")
    _pass = os.getenv("DB_PASS")
    _host = os.getenv("DB_HOST")
    _port = os.getenv("DB_PORT")
    _name = os.getenv("DB_NAME")

    url = f"postgresql+asyncpg://{_user}:{_pass}@{_host}:{_port}/{_name}"

class JWTSettings:
    algorithm = os.getenv("ALGORITHM")
    secret = os.getenv("SECRET")
    session_ttl = timedelta(days=30)


class URLSettings:
    custom_max_length: int = 15
    short_code_length: int = 4
    short_code_alphabet: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789"
    title_max_length: int = 30
    domain: str = os.getenv("DOMAIN")

class CacheSettings:
    _host = os.getenv("REDIS_HOST")
    _port = os.getenv("REDIS_PORT")
    _redis_db = 0

    connection_url = f"redis://{_host}:{_port}/{_redis_db}"

    url_ttl = 600
    url_prefix = "url"

    user_ttl = 600
    user_prefix = "user"

class Settings(DatabaseSettings, JWTSettings, URLSettings, CacheSettings):
    pass