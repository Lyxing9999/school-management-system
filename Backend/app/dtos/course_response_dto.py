# app/dtos/course_response_dto.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

class CourseResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    course_code: str
    course_title: str
    description: Optional[str] = None
    credits: Optional[int] = None
    created_at: int
    updated_at: int

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": {ObjectId: str},
    }