from fastapi import Depends
from src.clients.qdrant.dependencies import get_qdrant_service
from src.modules.document.dependencies import get_document_service
from src.clients.ollama.dependency import get_ollama_service

from src.modules.chat.service import ChatService

def get_chat_service(
    qdrant_service = Depends(get_qdrant_service),
    ollama_service = Depends(get_ollama_service),
    document_service = Depends(get_document_service)
    ):
    return ChatService(qdrant_service=qdrant_service, ollama_service=ollama_service, document_service=document_service)

