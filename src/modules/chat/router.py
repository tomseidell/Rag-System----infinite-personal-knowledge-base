from fastapi import APIRouter, Depends, Response
from src.modules.chat.schemas import ChatMessageResponse
from src.modules.chat.dependencies import get_chat_service
from src.modules.chat.service import ChatService
from src.modules.user.dependencies import get_current_user_id

from src.modules.chat.schemas import ChatRequest

router = APIRouter()

@router.post("/",status_code=200, response_model=ChatMessageResponse)
async def postMessage(request:ChatRequest, current_user: int = Depends(get_current_user_id), chat_service:ChatService = Depends(get_chat_service)):
    answer = await chat_service.post_message(user_id=current_user, message=request.message)
    return{
        "message" : answer,
        "references" : [""]
    }