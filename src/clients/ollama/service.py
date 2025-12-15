import ollama
import os
from src.clients.ollama.exceptions import OllamaException
import logging

logger = logging.getLogger(__name__)


class OllamaService():
    def __init__(self):
        self.client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))


    def embed_text(self, chunks:list[str]):
        try:
            response = self.client.embed(model="nomic-embed-text", input=chunks)
            return response["embeddings"]
        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="embed_text",
                detail=str(e)
            )
