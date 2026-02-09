from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    instagram_cookies: str | None = None
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL


@lru_cache
def get_settings() -> Settings:
    return Settings()
