# app/dtos/report_response_dto.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ReportResponseDTO(BaseModel):
    id: str = Field(..., alias="_id")
    report_type: str  # e.g., "attendance", "grade", "behavior"
    related_id: str  # reference id (e.g., student_id, class_id)
    data: Dict[str, Any]  # flexible field to hold report details
    generated_at: int  # Unix timestamp
    created_at: int
    updated_at: int

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": {ObjectId: str},
    }