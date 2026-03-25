from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseLLMService(ABC):
    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        pass
    
    @abstractmethod
    async def create_message(self, texts: list[str], user_input: str) -> AsyncGenerator[str, None]:
        pass
