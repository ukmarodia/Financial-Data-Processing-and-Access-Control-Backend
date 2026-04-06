import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    App-wide configuration loaded from environment variables / .env file.
    Keeps secrets out of source code and makes it easy to swap settings
    between dev and production environments.
    """

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    DATABASE_URL: str = "sqlite:////tmp/finance.db" if os.environ.get("VERCEL") else "sqlite:///./finance.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # JWT config
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
