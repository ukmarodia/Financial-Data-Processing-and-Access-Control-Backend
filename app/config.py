from pydantic_settings import BaseSettings


class Settings(BaseSettings):
   
    SECRET_KEY: str = "change_me_in_env_for_production"
    DATABASE_URL: str =  "sqlite:///./finance.db"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
