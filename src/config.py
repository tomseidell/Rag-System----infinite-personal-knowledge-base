from pydantic import BaseSettings # hilft uns settings aufzusetzen, kann automatisch envs importieren und unsere class typisieren
import os #greift auf env zu 
from dotenv import load_dotenv
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
    DB_POOL_PRE_PING:bool = true #connection gets tested before connecting 


