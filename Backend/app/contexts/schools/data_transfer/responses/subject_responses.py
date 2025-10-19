



from pydantic import BaseModel
from datetime import datetime

from typing import List

class SubjectBaseDataDTO(BaseModel):
    id: str
    name: str
    teacher_ids: List[str]
    created_at: datetime
    updated_at: datetime
    created_by: str
    deleted: bool

    