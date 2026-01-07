from typing import Optional
from pydantic import BaseModel


class AdminAssignSubjectTeacherRequest(BaseModel):
    subject_id: str
    teacher_id: str
    overwrite: bool = True 

class AdminUnassignSubjectTeacherRequest(BaseModel):
    subject_id: str