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


class Settings(DatabaseSettings, JWTSettings):
    pass