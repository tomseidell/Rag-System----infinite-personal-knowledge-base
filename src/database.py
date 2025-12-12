from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from src.config import settings

database_url = f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DB_HOST}:{settings.DATABASE_PORT}/{settings.DB_NAME}"

engine = create_async_engine( # creates a engine / connection / postgres pool
    database_url,
    pool_size=settings.DB_POOL_SIZE,
    pool_recycle=settings.DB_POOL_TTL,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
)

AsyncSessionLocal = async_sessionmaker( # creates sessions which communicate with the engine
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base() # parent class of all db models 

sync_database_url = f"postgresql+psycopg2://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DB_HOST}:{settings.DATABASE_PORT}/{settings.DB_NAME}"

sync_engine = create_engine(sync_database_url)
SyncSessionLocal = sessionmaker(
    bind = sync_engine,
    autocommit=False,
    autoflush=False,
)

async def get_db(): # creates new sessison for each request : in each incoming request this function gets called to have the db ready and 
    async with AsyncSessionLocal() as session:
        try:
            yield session # returns session and pauses function 
        finally:
            await session.close() #closes session in the end 


def get_sync_db():
    db = SyncSessionLocal()
    try:
        yield db
    except:
        db.close