from pydantic_settings import BaseSettings  # neuer Importimport os #greift auf env zu 
from dotenv import load_dotenv
import os # access to system 

load_dotenv()

class Config(BaseSettings):
    ENVIRONMENT:str = os.getenv("ENVIRONMENT")

    DATABASE_USER:str = os.getenv("DB_USER")
    DATABASE_PASSWORD:str = os.getenv("DB_PASSWORD")
    DATABASE_PORT:int = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_HOST: str = os.getenv("DB_HOST")

    DB_POOL_SIZE:int = 16 # max number of connections in the pool
    DB_POOL_TTL:int = 60 * 20 #max amount of time in secs a connection can keep alive before a recycle
    DB_POOL_PRE_PING:bool = True #connection gets tested before connecting 


settings = Config()
