

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from app.contexts.iam.data_transfer.requests import IAMUpdateSchema
from app.contexts.shared.enum.roles import SystemRole
from app.contexts.student.data_transfer.requests import StudentInfoUpdateSchema

from typing import Optional
class AcademicCreateClassSchema(BaseModel):
    name: str
    grade: int
    max_students: int = 30
    status: bool = True
    homeroom_teacher: str | None = None
    subjects: List[str] | None = None
    students: List[str] | None = None
    created_by: str | None = None  
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False
    deleted_at: datetime | None = None

    model_config = {
        "enum_values_as_str": True,
        "extra": "forbid"
    }


from typing import Literal

class AcademicCreateStudentSchema(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=3, max_length=50)
    role: Literal[SystemRole.STUDENT] = SystemRole.STUDENT
    created_by: Optional[str] = None

    model_config = {
        "enum_values_as_str": True,
        "extra": "forbid"
    }

class AcademicUpdateUserSchema(IAMUpdateSchema):
    role: Optional[SystemRole] = None

class AcademicUpdateStudentInfoSchema(StudentInfoUpdateSchema):
    pass






class AcademicAddSubjectSchema(BaseModel):
    subjects: List[str]