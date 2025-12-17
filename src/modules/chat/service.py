from src.clients.ollama.service import OllamaServiceAsync
from src.clients.qdrant.service import AsyncQdrantService   
from src.modules.document.service import DocumentService
from qdrant_client.models import ExtendedPointId


class ChatService():
    def __init__(self, qdrant_service:AsyncQdrantService, ollama_service:OllamaServiceAsync, document_service:DocumentService):
        self.qdrant_service = qdrant_service
        self.ollama_service = ollama_service
        self.document_service = document_service

    
    async def post_message(self, message:str, user_id:int) ->str:
        embedding = await self.ollama_service.embed_text(message)
        chunk_infos = await self.qdrant_service.get_matching_chunks(vector=embedding, user_id=user_id)
        texts: list[str] = [chunk.payload["text"] for chunk in chunk_infos if chunk.payload]
        answer = await self.ollama_service.create_message(texts=texts, user_input=message)
        return answer

