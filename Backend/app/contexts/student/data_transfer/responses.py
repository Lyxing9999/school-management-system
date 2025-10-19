from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
# -------------------------
# Student Info Response DTO
# -------------------------
class StudentInfoBaseDataDTO(BaseModel):
    student_id: str
    full_name: str
    id: str | None = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    grade_level: Optional[int] = None
    classes: Optional[List[str]] = None
    enrollment_date: Optional[datetime] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    parent_number: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deleted_at: Optional[str] = None
    deleted: Optional[bool] = None
    deleted_by: Optional[str] = None
    model_config = {
        "extra": "ignore"
    }   





class StudentInfoReadDataDTO(StudentInfoBaseDataDTO):
    pass