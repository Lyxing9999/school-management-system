

from pydantic import BaseModel
from typing import List
from datetime import datetime


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





class AcademicAddSubjectSchema(BaseModel):
    subjects: List[str]