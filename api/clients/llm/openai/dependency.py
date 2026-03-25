from functools import lru_cache
from api.clients.llm.openai.service import OpenaiService

@lru_cache()
def get_openai_service() ->OpenaiService:
    return OpenaiService()
