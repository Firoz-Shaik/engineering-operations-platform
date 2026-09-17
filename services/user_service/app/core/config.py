# app/core/config.py
# Manages application-wide settings and configurations.

import os
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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

# Create a single, reusable instance of the settings
settings = Settings()
"""
print(f"[CONFIG]: Running in {APP_ENV} environment")
print("USING DATABASE_URL =", settings.DATABASE_URL)
"""