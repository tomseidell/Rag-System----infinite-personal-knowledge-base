from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.modules.document.model import Document



class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    title: str
    original_filename: str
    file_size: int
    file_type: str
    source_type: str  
    created_at: datetime  


class DocumentCreate(BaseModel):
    user_id: int
    title: str
    original_filename: str
    source_type: str
    content_hash: str
    file_size: int
    file_type: str

class GetDocuments(BaseModel):
    documents: list[DocumentResponse]
    next_cursor: int| None