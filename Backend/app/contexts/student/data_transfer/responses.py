from pydantic import BaseModel
from typing import Optional, List

# -------------------------
# Student Info Response DTO
# -------------------------
class StudentInfoResponseDataDTO(BaseModel):
    student_id: str
    full_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    nickname: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    grade_level: Optional[int] = None
    classes: Optional[List[str]] = None
    enrollment_date: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    parent_number: Optional[str] = None


# -------------------------
# Full Student Response DTO
# -------------------------
class StudentResponseDataDTO(BaseModel):
    user_id: str
    student_info: StudentInfoResponseDataDTO