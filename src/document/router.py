from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response

from src.document.dependencies import get_document_service
from src.document.schemas import DocumentResponse
from src.document.service import DocumentService
from src.user.dependencies import get_current_user_id
from src.user.model import User


router = APIRouter()

@router.post("/", status_code=201, response_model=DocumentResponse)
async def upload(
    file:UploadFile,
    title:str | None,
    current_user: int = Depends(get_current_user_id),
    document_service:DocumentService = Depends(get_document_service)
    ):
    return await document_service.upload_document(user_id=current_user, title=title, file=file)
 

@router.get("/{document_id}/download", status_code=200, response_model=bytes)
async def get_document(
    document_id:int,
    current_user: int = Depends(get_current_user_id),
    document_service:DocumentService = Depends(get_document_service)
    ):
    content, filename, content_type =  await document_service.get_document(user_id=current_user, document_id=document_id)
    return Response(
        content=content, # raw bytes
        media_type=content_type, # pdf / png
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}) #asssign attachment to let the browser auto download instead of preview