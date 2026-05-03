from fastapi import APIRouter, Depends, HTTPException, UploadFile, Response
from typing import Annotated
import json

from api.modules.document.dependencies import get_document_service
from api.modules.document.schemas import PaginatedDocuments, DocumentResponse
from api.modules.document.service import DocumentService
from api.modules.user.dependencies import get_current_user_id
from api.clients.redis.dependency import get_redis_service
from api.clients.redis.service import RedisService


router = APIRouter()

CurrentUserDep = Annotated[int, Depends(get_current_user_id)]
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]
RedisServiceDep = Annotated[RedisService, Depends(get_redis_service)]


@router.post("/", status_code=201, response_model=DocumentResponse)
async def upload(
    file:UploadFile,
    title:str | None,
    current_user: CurrentUserDep,
    document_service:DocumentServiceDep
    ):
    return await document_service.upload_document(user_id=current_user, title=title, file=file)
 

@router.get("/{document_id}/download", status_code=200)
async def get_document(
    document_id:int,
    current_user: CurrentUserDep,
    document_service:DocumentServiceDep
    ):
    document =  await document_service.get_document(user_id=current_user, document_id=document_id)
    return Response(
        content=document.content, # raw bytes
        media_type=document.file_type, # pdf / png
        headers={"Content-Disposition": f'attachment; filename="{document.original_filename}"'}) #asssign attachment to let the browser auto download instead of preview


@router.delete("/{document_id}", status_code=204)
async def delete(
    document_id:int,
    current_user: CurrentUserDep,
    document_service:DocumentServiceDep
    ):
    await document_service.delete_document(document_id=document_id, user_id=current_user)


@router.get("/{document_id}/status", status_code=200)
async def get_status(
    document_id: int,
    current_user: CurrentUserDep,
    redis: RedisServiceDep,
):
    raw = await redis.get(f"document:status:{document_id}")
    if not raw:
        raise HTTPException(status_code=404, detail="No status found for this document")
    return json.loads(raw)


@router.get("/", status_code=200, response_model=PaginatedDocuments)
async def get_documents(
    current_user: CurrentUserDep,
    document_service:DocumentServiceDep,
    cursor:int | None = None
    ):
    return await document_service.get_documents(user_id=current_user, cursor=cursor)
