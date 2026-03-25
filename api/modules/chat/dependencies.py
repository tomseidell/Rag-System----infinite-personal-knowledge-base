from fastapi import Depends
from api.clients.qdrant.dependencies import get_qdrant_service
from api.modules.document.dependencies import get_document_service
from api.clients.llm.dependency import get_llm_service
from api.clients.redis.dependency import get_redis_service

from api.modules.chat.service import ChatService

def get_chat_service(
    qdrant_service = Depends(get_qdrant_service),
    llm_service = Depends(get_llm_service),
    document_service = Depends(get_document_service),
    redis_service = Depends(get_redis_service)
    ):
    return ChatService(qdrant_service=qdrant_service, llm_service=llm_service, document_service=document_service, redis_service=redis_service)

