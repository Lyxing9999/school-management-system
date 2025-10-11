from pydantic import BaseModel, Field
from typing import List, Optional




# -------------------------
# Student Info Schema
# -------------------------
class StudentInfoUpdateRequestSchema(BaseModel):
    student_id: str = Field(..., description="Student ID")
    full_name: str = Field(..., description="Student Full Name")
    first_name: Optional[str] = Field(None, min_length=1, description="Student First Name")
    last_name: Optional[str] = Field(None, min_length=1, description="Student Last Name")
    nickname: Optional[str] = Field(None, min_length=1, description="Student Nickname")
    birth_date: Optional[str] = Field(None, description="Student Birth Date in YYYY-MM-DD format")
    gender: Optional[str] = Field(None, description="Student Gender")
    grade_level: Optional[int] = Field(None, description="Student Grade Level")
    classes: Optional[List[str]] = Field(None, description="Student Classes")
    enrollment_date: Optional[str] = Field(None, description="Student Enrollment Date in YYYY-MM-DD format")
    address: Optional[str] = Field(None, description="Student Address")
    photo_url: Optional[str] = Field(None, description="Student Photo URL")
    parent_number: Optional[str] = Field(None, description="Parent Phone Number")


# -------------------------
# Full Student Request Schema
# -------------------------
class StudentUpdateRequestSchema(BaseModel):
    user_id: str = Field(..., description="User ID")
    student_info: StudentInfoUpdateRequestSchema = Field(..., description="Student Info")