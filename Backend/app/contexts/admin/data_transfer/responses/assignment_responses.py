from typing import List, Optional
from pydantic import BaseModel
from pydantic.config import ConfigDict
from datetime import datetime

from app.contexts.shared.lifecycle.dto import LifecycleDTO


class AdminTeachingAssignmentDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    class_id: str
    subject_id: str
    teacher_id: str
    assigned_by: Optional[str] = None
    lifecycle: LifecycleDTO


    class_name: Optional[str] = None
    subject_label: Optional[str] = None
    teacher_name: Optional[str] = None
    assigned_by_username: Optional[str] = None

class AdminTeachingAssignmentListDTO(BaseModel):
    items: List[AdminTeachingAssignmentDTO]


class AdminTeachingAssignmentWriteResultDTO(BaseModel):
    assignment_id: str
    created: bool
    modified_count: int