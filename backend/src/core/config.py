from datetime import timedelta
from pydantic_settings import BaseSettings, SettingsConfigDict, JsonConfigSettingsSource
from pydantic import computed_field, BaseModel, Field
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
ROOT_DIR = Path(__file__).resolve().parents[3]

class DatabaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    name: str

    @computed_field
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class JWTSettings(BaseModel):
    algorithm: str
    secret: str
    session_ttl: timedelta


class URLSettings(BaseModel):
    custom_max_length: int
    short_code_length: int
    short_code_alphabet: str
    title_max_length: int
    domain: str


class CacheSettings(BaseModel):
    host: str
    port: int
    redis_db: int

    url_ttl: int
    url_prefix: str
    user_ttl: int
    user_prefix: str

    @computed_field
    @property
    def connection_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.redis_db}"

class RateLimitUrl(BaseModel):
    redirect: str
    shorten: str
    update: str
    deactivate: str
    get_stats: str
    generate_qr: str

class RateLimitUser(BaseModel):
    registration: str = Field(alias="register")
    login: str
    readme: str

class RateLimitSettings(BaseModel):
    urls: RateLimitUrl
    users: RateLimitUser

class Settings(BaseSettings):
    db: DatabaseSettings
    jwt: JWTSettings
    url: URLSettings
    cache: CacheSettings
    ratelimits: RateLimitSettings

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        json_file=ROOT_DIR / "config.json",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        json_file_encoding="utf-8",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, **kwargs):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            JsonConfigSettingsSource(settings_cls),
        )


settings = Settings()