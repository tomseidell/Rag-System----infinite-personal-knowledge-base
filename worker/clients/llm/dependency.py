from functools import lru_cache
from shared.config import settings
from worker.clients.llm.ollama_service import OllamaService
from worker.clients.llm.openai_service import OpenaiService

@lru_cache()
def get_llm_service():
    environment = settings.ENVIRONMENT
    if environment == "development":
        return OllamaService()
    return OpenaiService()