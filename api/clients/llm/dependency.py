from functools import lru_cache
from api.clients.llm.ollama.service import OllamaServiceAsync
from api.clients.llm.openai.service import OpenaiService
from api.clients.llm.base_service import BaseLLMService
from shared.config import settings

@lru_cache()
def get_llm_service()-> BaseLLMService:
    environment = settings.ENVIRONMENT

    if environment == "development":
        return OllamaServiceAsync()
    elif environment == "production":
        return OpenaiService()
    else:
        raise ValueError("Wrong or Missing environment variable: ENVIRONMENT")