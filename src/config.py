from dotenv import load_dotenv  # preload env variables
import os # gives us access to read env variables

load_dotenv() # preload env variables

class Config:
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")

    DB_POOL_SIZE = 16
    DB_POOL_TTL = 60 * 20
    DB_POOL_PRE_PING = True

    # GCP Bucket information
    GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    @property
    def DATABASE_URL(self):
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DB_HOST}:{self.DATABASE_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_ASYNC_URL(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DB_HOST}:{self.DATABASE_PORT}/{self.DB_NAME}"

settings = Config()
