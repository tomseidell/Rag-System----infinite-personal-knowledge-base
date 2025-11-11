from fastapi import APIRouter, Depends, HTTPException, UploadFile

from document.dependencies import get_document_service
from document.schemas import DocumentResponse
from document.service import DocumentService
from user.dependencies import get_current_user_id
from user.model import User


router = APIRouter()

@router.post("/upload", status_code=201, response_model=DocumentResponse)
async def upload(
    file:UploadFile,
    title:str | None,
    current_user: User = Depends(get_current_user_id),
    document_service:DocumentService = Depends(get_document_service)
    ):
    return await document_service.upload_document(user_id=current_user.id, title=title, file=file)
 