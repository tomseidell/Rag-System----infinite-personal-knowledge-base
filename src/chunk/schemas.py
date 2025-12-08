from pydantic import BaseModel, Field

class ChunkCreate(BaseModel):
    text:str = Field(min_length=1)
    document_id:int = Field(gt=0)
    user_id:int = Field(gt=0)
    chunk_index:int = Field(gt=0)
    token_count:int = Field(gt=1)