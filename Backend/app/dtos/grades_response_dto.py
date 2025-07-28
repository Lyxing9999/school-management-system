# app/dtos/grades_response_dto.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Dict
from typing import Optional

class GradeComponents(BaseModel):
    assignment: float
    quiz: float
    midterm: float
    final: float
    project: float

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
    }

class GradesResponseDTO(BaseModel):
    id: str = Field(alias="_id")
    student_id: str
    class_id: str
    grade_components: GradeComponents
    total: float
    remark: Optional[str] = None
    created_at: int  # Unix timestamp

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": { ObjectId: str },
    }