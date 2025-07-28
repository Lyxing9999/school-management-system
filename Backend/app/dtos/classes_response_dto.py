# app/dtos/class_response_dto.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional

class ClassResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    course_code: str
    course_title: str
    teacher_id: str
    schedule: List[str]  # Assuming schedule_items._id is ObjectId
    students_enrolled: List[str]  # Assuming students._id is ObjectId
    telegram_link: str
    zoom_link: Optional[str] = None
    hybrid: bool
    created_at: int  # Unix timestamp
    updated_at: int  # Unix timestamp

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,
        }
    }

class ClassListResponseDTO(BaseModel):
    classes: List[ClassResponseDTO]

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }