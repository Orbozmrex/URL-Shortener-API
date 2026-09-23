from dotenv import load_dotenv
import os

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


class URLSettings:
    custom_max_length: int = 15
    short_code_length: int = 4
    short_code_alphabet: str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_0123456789"

class Settings(DatabaseSettings, JWTSettings, URLSettings):
    pass