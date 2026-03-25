import ollama
import os
from api.clients.llm.ollama.exceptions import OllamaException
import logging
from typing import AsyncGenerator
from api.clients.llm.base_service import BaseLLMService


logger = logging.getLogger(__name__)


class OllamaServiceAsync(BaseLLMService):
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

    async def create_message(self, texts:list[str], user_input:str)->AsyncGenerator[str , None]:
        try:
            input_string = "\n\n".join(texts)
            response= await self.client.chat(model="llama3", stream=True, messages=[
                {
                    "role": "user",
                    "content": f"Create a response and primarily focus on information from this string: {input_string}. If the string is empty or simply no relevant information to the message are given, answer the question with all your basic knowledge and do not rely on the information string. The user message or input is: {user_input}"
                }
            ])
            # return with async generator for improved performance and to allow streaming to frontend
            async for chunk in response:
                if chunk.message.content:
                    yield chunk.message.content
            
        except ollama.RequestError as e:
            logger.error(f"Ollama connection Error: {e}")
            raise OllamaException(
                operation="async_create_message",
                detail=str(e)
            ) 