
from bson import ObjectId
from pydantic import BaseModel , Field
from typing import List
class UserResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    username: str | None
    role: str
    email: str | None
    model_config = {
        "orm_mode": True,
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,  
        }
    }


class UserListResponseDTO(BaseModel):
    users: List[UserResponseDTO]

    model_config = {
        "from_attributes": True,
    }