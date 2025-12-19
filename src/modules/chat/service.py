from src.clients.ollama.service import OllamaServiceAsync
from src.clients.qdrant.service import AsyncQdrantService   
from src.modules.document.service import DocumentService



class ChatService():
    def __init__(self, qdrant_service:AsyncQdrantService, ollama_service:OllamaServiceAsync, document_service:DocumentService):
        self.qdrant_service = qdrant_service
        self.ollama_service = ollama_service
        self.document_service = document_service

    
    async def post_message(self, message: str, user_id: int):
        embedding = await self.ollama_service.embed_text(message)
        chunk_infos = await self.qdrant_service.get_matching_chunks(dense_vector=embedding, query_text=message, user_id=user_id)
        texts: list[str] = [chunk.payload["content"] for chunk in chunk_infos if chunk.payload]
        sources: list[int] = [chunk.payload["document_id"] for chunk in chunk_infos if chunk.payload]
        sources = list(set(sources))

        ressources: list[object] = []

        for source in sources:
            ressource = await self.document_service.get_document_name_and_id(user_id=user_id, document_id=source)
            ressources.append({ressource[0], ressource[1]})

        
        async for chunk in self.ollama_service.create_message(texts=texts, user_input=message):
            yield chunk
        yield ressources

