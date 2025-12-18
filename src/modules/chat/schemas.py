from pydantic import BaseModel, ConfigDict, Field

class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message : str
    references : list[str]




class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)