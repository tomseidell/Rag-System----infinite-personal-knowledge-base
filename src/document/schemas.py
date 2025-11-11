from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    title: str
    original_filename: str
    file_size: int
    file_type: str
    created_at: datetime
