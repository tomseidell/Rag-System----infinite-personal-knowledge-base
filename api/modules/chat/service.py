from app.clients.ollama.service import OllamaServiceAsync
from app.clients.qdrant.service import AsyncQdrantService   
from app.modules.document.service import DocumentService
from app.clients.redis.service import RedisService
import hashlib
import json



class ChatService():
    def __init__(self, qdrant_service:AsyncQdrantService, ollama_service:OllamaServiceAsync, document_service:DocumentService, redis_service:RedisService):
        self.qdrant_service = qdrant_service
        self.ollama_service = ollama_service
        self.document_service = document_service
        self.redis_service = redis_service

    # when message is too long its unfitting for key
    def _create_cache_key(self, message: str, user_id: int):
        msg_hash = hashlib.md5(message.encode()).hexdigest()[:16]
        return f"message:{user_id}:{msg_hash}"
    
    async def post_message(self, message: str, user_id: int):

        cache_key = self._create_cache_key(message=message, user_id=user_id)

        # check for cached results in redis 
        cached_response = await self.redis_service.get(cache_key)

        # if cached response: return cached string and cached ressources in 2 batches
        if cached_response:
            data = json.loads(cached_response.decode()) # create python object from json byte string
            yield data["response"] # return string 
            yield json.dumps(data["ressources"]) # create json string from list
            return

        embedding = await self.ollama_service.embed_text(message)
        chunk_infos = await self.qdrant_service.get_matching_chunks(dense_vector=embedding, query_text=message, user_id=user_id)
        texts: list[str] = [chunk.payload["content"] for chunk in chunk_infos if chunk.payload]
        sources: list[int] = [chunk.payload["document_id"] for chunk in chunk_infos if chunk.payload]
        sources = list(set(sources)) # only unique sources / unique documents as sources

        ressources: list[dict] = []
        for source in sources:
            ressource = await self.document_service.get_document_name_and_id(user_id=user_id, document_id=source)
            ressources.append({"id": ressource[0], "name": ressource[1]})


        chunks = []
        async for chunk in self.ollama_service.create_message(texts=texts, user_input=message):
            chunks.append(chunk)
            yield chunk
        yield ressources

        if not cached_response:
            full_response = "".join(chunks)
            await self.redis_service.set(cache_key, json.dumps({
                "response": full_response,
                "ressources": ressources
            }), ttl=3600)

