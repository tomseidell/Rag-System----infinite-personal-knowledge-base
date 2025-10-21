from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegistration(BaseModel):
    fullname: str
    email: EmailStr
    password: str = Field(min_length=8)


class UserRegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
