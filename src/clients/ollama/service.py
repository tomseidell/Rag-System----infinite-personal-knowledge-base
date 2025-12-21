import ollama
import os
from src.clients.ollama.exceptions import OllamaException
import logging
from ollama import ChatResponse
from typing import AsyncIterator, AsyncGenerator



logger = logging.getLogger(__name__)


class OllamaService():
    def __init__(self):
        self.client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434"))


    def embed_text(self, chunks:list[str], batch_size = 10):
        all_embeddings = []
        try:
            for i in range(0,len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                response = self.client.embed(model="nomic-embed-text", input=batch)
                all_embeddings.append(response["embeddings"])
            return all_embeddings
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

    async def create_message(self, texts:list[str], user_input)->AsyncGenerator[str , None]:
        try:
            input_string = "\n\n".join(texts)
            response= await self.client.chat(model="llama3", stream=True, messages=[
                {
                    "role": "user",
                    "content": f"Create a response and primarily focus on information from this string: {input_string}. If the string is empty or simply no relevant information to the message are given, answer the question with all your basic knowledge and do not rely on the information string. The user message or input is: {user_input}"
                }
            ])
            async for chunk in response:
                if chunk.message.content:
                    yield chunk.message.content
            
            
        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="async_create_message",
                detail=str(e)
            ) 