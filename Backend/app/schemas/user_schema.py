from typing import List, Dict
from pydantic import BaseModel, Field
from app.utils.objectid import ObjectId #type: ignore
from typing import Optional
from datetime import datetime, timezone, date
from app.enums.roles import Role
from app.models.classes import ClassesModel


class UserCreateSchema(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role: Role
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class UserUpdateSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class UserPatchSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[Role] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class UserResponseSchema(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[Role] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class TeacherInfoPatchSchema(BaseModel):
    teacher_id: Optional[str] = None
    teacher_name: Optional[str] = None
    subjects: Optional[List[str]] = None
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }


class TeacherPatchSchema(BaseModel):
    phone_number: Optional[str] = None
    teacher_info: Optional[TeacherInfoPatchSchema] = None
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
class StudentInfoPatchSchema(BaseModel):
    student_id: Optional[str] = Field(None, description="Unique student identifier")
    year_level: Optional[str] = Field(None, description="Year level of the student")
    class_ids: Optional[List[str]] = Field(default_factory=list)
    major: Optional[str] = None
    birth_date: Optional[date] = None
    batch: Optional[str] = None
    address: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    attendance_record: Optional[Dict[str, str]] = Field(default_factory=dict)
    courses_enrolled: Optional[List[ObjectId]] = Field(default_factory=list)
    scholarships: Optional[List[str]] = Field(default_factory=list)
    expected_graduation_year: Optional[int] = None
    current_gpa: Optional[float] = None
    remaining_credits: Optional[int] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

class StudentPatchSchema(BaseModel):
    student_info: Optional[StudentInfoPatchSchema] = None
    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }




class UserPatchUserDetailSchema(BaseModel):
    teacher: Optional[TeacherPatchSchema] = None
    student: Optional[StudentPatchSchema] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }



class UserDetailResponseSchema(BaseModel):
    teacher: Optional[TeacherPatchSchema] = None
    student: Optional[StudentPatchSchema] = None

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
    

class TeacherClassesResponseSchema(BaseModel):
    classes: Optional[List[ClassesModel]] = Field(default_factory=list)

    model_config = {
        "from_attributes": True,
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "extra": "allow",
    }