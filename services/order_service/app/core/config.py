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
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

# Create a single, reusable instance of the settings
settings = Settings()
