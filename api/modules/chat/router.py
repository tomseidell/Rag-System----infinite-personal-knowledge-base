from fastapi import APIRouter, Depends, Response 
from api.modules.chat.schemas import ChatMessageResponse
from api.modules.chat.dependencies import get_chat_service
from api.modules.chat.service import ChatService
from api.modules.user.dependencies import get_current_user_id
from fastapi.responses import StreamingResponse


from api.modules.chat.schemas import ChatRequest

router = APIRouter()

@router.post("/",status_code=200)
async def postMessage(request:ChatRequest, current_user: int = Depends(get_current_user_id), chat_service:ChatService = Depends(get_chat_service)):
    async def generate():  
        async for chunk in chat_service.post_message(user_id=current_user, message=request.message):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n" 
    
    return StreamingResponse(generate(), media_type="text/event-stream") 