from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class StudentResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    user_id: str  # Reference to users._id
    student_id: str  # Unique student ID
    year_level: int
    class_ids: List[str]  
    major: str
    birth_date: str  
    batch: str
    address: str
    phone_number: str
    email: str
    avatar_url: Optional[str] = None
    created_at: int 
    updated_at: int

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "populate_by_name": True  
    }