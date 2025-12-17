import ollama
import os
from src.clients.ollama.exceptions import OllamaException
import logging
from ollama import ChatResponse


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

class OllamaServiceAsync():
    def __init__(self):
        self.client = ollama.AsyncClient(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))
    
    async def embed_text(self, text:str)->str:
        try:
            response = await self.client.embed(model="nomic-embed-text", input=text)
            return response["embeddings"][0]
        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="async_embed_text",
                detail=str(e)
            ) 

    async def create_message(self, texts:list[str], user_input)->str:
        try:
            input_string = "\n\n".join(texts)
            response: ChatResponse = await self.client.chat(model="llama3", messages=[
                {
                    "role": "user",
                    "content": f"Create a response and primarily focus on information from this string: {input_string}"
                }
            ])
            return response['message']['content']  

        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="async_create_message",
                detail=str(e)
            ) 