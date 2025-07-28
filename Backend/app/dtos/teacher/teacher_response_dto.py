from pydantic import BaseModel, Field
from typing import Optional, List

class TeacherResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    teacher_id: str
    lecturer_name: str
    phone_number: str
    subjects: List[str]
    bio: Optional[str] = None
    created_at: int
    updated_at: int

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "populate_by_name": True, 
    }