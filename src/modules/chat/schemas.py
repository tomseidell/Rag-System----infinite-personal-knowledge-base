from pydantic import BaseModel, ConfigDict


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    message : str
    reference : list[str]