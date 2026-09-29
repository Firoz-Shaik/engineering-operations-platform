from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/2"
    INTERNAL_API_KEY: str
    ENVIRONMENT: str = "local"
    NOTIFICATION_MAX_RETRIES: int = 5

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()