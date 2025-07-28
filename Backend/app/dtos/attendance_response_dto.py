# app/dtos/attendance_response_dto.py
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class AttendanceRecord(BaseModel):
    date: int  # Unix timestamp for the attendance day
    status: str  # e.g., "present", "absent", "late", "excused"
    remarks: Optional[str] = None

class AttendanceResponseDTO(BaseModel):
    id: str = Field(..., alias="_id")
    student_id: str  # reference to students._id
    class_id: str  # reference to classes._id
    records: List[AttendanceRecord]  # attendance records list
    created_at: int  # Unix timestamp
    updated_at: int  # Unix timestamp

    model_config = {
        "extra": "forbid",
        "from_attributes": True,
        "json_encoders": {
            ObjectId: str,
        },
    } 