
from bson import ObjectId
from pydantic import BaseModel , Field
from typing import List
class UserDBDTO(BaseModel):
    id: str = Field(alias="_id")
    username: str | None
    role: str
    email: str | None
    password: str
    model_config = {
        "orm_mode": True,
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,  
        }
    }


