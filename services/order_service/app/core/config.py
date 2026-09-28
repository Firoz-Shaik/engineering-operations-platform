# app/core/config.py
# Manages application-wide settings and configurations.
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

#APP_ENV = os.getenv("APP_ENV", "dev")
class Settings(BaseSettings):
    """
    Pydantic model for loading and validating environment variables.
    """
    # Database configuration
    DATABASE_URL: str
    # JWT Authentication settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    USER_SERVICE_TOKEN_URL: str = "http://127.0.0.1:8002/api/v1/auth/token"
    USER_SERVICE_URL: str = "http://127.0.0.1:8002"
    INTERNAL_API_KEY: str = "local-dev-internal-key"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

# Create a single, reusable instance of the settings
settings = Settings()
