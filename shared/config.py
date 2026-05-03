from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = Path(__file__).parent.parent / ".env" # assign path manually

class Settings(BaseSettings):
    ENVIRONMENT: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_PORT: int
    DB_NAME: str
    DB_HOST: str

    DB_POOL_SIZE:int = 16
    DB_POOL_TTL:int = 60 * 20
    DB_POOL_PRE_PING:bool = True

    S3_BUCKET_NAME: str
    S3_ENDPOINT_URL: str | None = None

    COOKIE_SECURE: bool = False

    FRONTEND_URL: str = "http://localhost:5173"

    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days in minutes

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DB_HOST}:{self.DATABASE_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_ASYNC_URL(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DB_HOST}:{self.DATABASE_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=DOTENV, extra="ignore")  # ignore all extra envs



settings = Settings() # create instance to import
