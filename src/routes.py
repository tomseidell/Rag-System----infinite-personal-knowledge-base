from fastapi import APIRouter
router = APIRouter()
from src.modules.document.router import router as document_router
from src.modules.user.router import router as user_router
from src.modules.chat.router import router as chat_router

router = APIRouter()


router.include_router(user_router, prefix="/user", tags= ["users"])
router.include_router(document_router, prefix="/document", tags=["document"])
router.include_router(chat_router, prefix="/chat", tags=["chat"])

@router.get("/")
async def root():
    return {"message": "Welcome to FastAPI Project testrrrr"}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}