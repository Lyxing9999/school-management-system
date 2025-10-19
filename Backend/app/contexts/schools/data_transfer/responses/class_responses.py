from datetime import datetime
from typing import List
from pydantic import BaseModel
from typing import Optional

class SchoolClassBaseDataDTO(BaseModel):
    id: str
    name: str
    grade: int
    max_students: int
    status: bool
    grade: int  
    code: Optional[str] = None
    academic_year: Optional[str] = None
    class_room: str | None = None
    homeroom_teacher: str | None = None
    students: List[str] | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted: bool = False
    deleted_at: datetime | None = None






class SchoolClassDataDTO(SchoolClassBaseDataDTO):
    pass


