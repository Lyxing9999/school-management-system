from pydantic import BaseModel, Field, constr
from typing import List, Optional
from datetime import date


# -------------------------
# Student Info Schema
# -------------------------
class StudentInfoUpdateSchema(BaseModel):
    student_id: constr(min_length=1) = Field(None, description="Student ID")
    full_name: constr(min_length=1) = Field(None, description="Student Full Name")
    photo_url: Optional[str] = Field(None, description="Student Photo URL")
    first_name: Optional[constr(min_length=1)] = Field(None, description="Student First Name")
    last_name: Optional[constr(min_length=1)] = Field(None, description="Student Last Name")
    birth_date: Optional[date] = Field(None, description="Student Birth Date")
    gender: Optional[constr(min_length=1)] = Field(None, description="Student Gender")
    grade_level: Optional[int] = Field(None, description="Student Grade Level")
    classes: Optional[List[constr(min_length=1)]] = Field(None, description="Student Classes")
    enrollment_date: Optional[date] = Field(None, description="Student Enrollment Date")
    address: Optional[constr(min_length=1)] = Field(None, description="Student Address")
    parent_number: Optional[constr(min_length=1)] = Field(None, description="Parent Phone Number")


# -------------------------
# Full Student Update Request Schema
# -------------------------
