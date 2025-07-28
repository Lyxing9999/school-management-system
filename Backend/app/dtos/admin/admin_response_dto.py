# app/dtos/admin_response_dto.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

class AdminResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    admin_id: str
    phone_number: Optional[str] = None
    created_at: int  # Unix timestamp
    updated_at: int  # Unix timestamp

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": { ObjectId: str },
    }