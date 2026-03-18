from fastapi import APIRouter, Depends 
from api.modules.chat.dependencies import get_chat_service
from api.modules.chat.service import ChatService
from api.modules.user.dependencies import get_current_user_id
from fastapi.responses import StreamingResponse
from typing import Annotated


from api.modules.chat.schemas import ChatRequest

router = APIRouter()

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
CurrentUserDep = Annotated[int, Depends(get_current_user_id)]

@router.post("/",status_code=200)
async def post_message(request:ChatRequest, current_user: CurrentUserDep, chat_service:ChatServiceDep):
    async def generate():  
        async for chunk in chat_service.post_message(user_id=current_user, message=request.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n" 
    
    return StreamingResponse(content=generate(), media_type="text/event-stream") 