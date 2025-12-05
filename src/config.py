from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = Path(__file__).parent.parent / ".env"

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

    GCS_BUCKET_NAME: str
    GOOGLE_APPLICATION_CREDENTIALS: str

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DB_HOST}:{self.DATABASE_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_ASYNC_URL(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DB_HOST}:{self.DATABASE_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=DOTENV, extra="ignore")  



settings = Settings()
