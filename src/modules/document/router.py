from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response

from src.modules.document.dependencies import get_document_service
from src.modules.document.schemas import DocumentResponse, GetDocuments
from src.modules.document.service import DocumentService
from src.modules.user.dependencies import get_current_user_id
from src.modules.user.model import User


router = APIRouter()

@router.post("/", status_code=201, response_model=DocumentResponse)
async def upload(
    file:UploadFile,
    title:str | None,
    current_user: int = Depends(get_current_user_id),
    document_service:DocumentService = Depends(get_document_service)
    ):
    return await document_service.upload_document(user_id=current_user, title=title, file=file)
 

@router.get("/{document_id}/download", status_code=200)
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


@router.delete("/{document_id}", status_code=204)
async def delete(
    document_id:int,
    current_user: int = Depends(get_current_user_id),
    document_service:DocumentService = Depends(get_document_service)
    ):
    await document_service.delete_document(document_id=document_id, user_id=current_user)


@router.get("/", status_code=200, response_model=GetDocuments)
async def get_documents(
    cursor:int | None = None,
    current_user: int = Depends(get_current_user_id),
    document_service:DocumentService = Depends(get_document_service)
    ):
    documents, next_cursor = await document_service.get_documents(user_id=current_user, cursor=cursor)
    return {
        "documents": documents,
        "next_cursor": next_cursor
    }