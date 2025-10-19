from pydantic import BaseModel
from typing import List




class SubjectCreateSchema(BaseModel):
    name: str
    teacher_ids: List[str] | None = None


class SubjectUpdateSchema(BaseModel):
    name: str | None = None
    teacher_ids: List[str] | None = None