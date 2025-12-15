from fastapi import APIRouter
router = APIRouter()
from src.modules.document.router import router as document_router
from src.modules.user.router import router as user_router

router = APIRouter()


router.include_router(user_router, prefix="/users", tags= ["users"])
router.include_router(document_router, prefix="/document", tags=["document"])


@router.get("/")
async def root():
    return {"message": "Welcome to FastAPI Project testrrrr"}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}