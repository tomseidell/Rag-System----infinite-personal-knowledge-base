from fastapi import Depends
from app.clients.qdrant.dependencies import get_qdrant_service
from app.modules.document.dependencies import get_document_service
from app.clients.ollama.dependency import get_ollama_service
from app.clients.redis.dependency import get_redis_service

from app.modules.chat.service import ChatService

def get_chat_service(
    qdrant_service = Depends(get_qdrant_service),
    ollama_service = Depends(get_ollama_service),
    document_service = Depends(get_document_service),
    redis_service = Depends(get_redis_service)
    ):
    return ChatService(qdrant_service=qdrant_service, ollama_service=ollama_service, document_service=document_service, redis_service=redis_service)

