from app.clients.ollama.service import OllamaServiceAsync
from functools import lru_cache

@lru_cache()
def get_ollama_service() -> OllamaServiceAsync:
    return OllamaServiceAsync()