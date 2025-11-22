from __future__ import annotations
from typing import List
from pydantic import BaseModel

from app.contexts.school.data_transfer.responses import (
    AttendanceDTO,
    GradeDTO,
    ClassSectionDTO,
)


class TeacherAttendanceListDTO(BaseModel):
    items: List[AttendanceDTO]


class TeacherGradeListDTO(BaseModel):
    items: List[GradeDTO]


class TeacherClassListDTO(BaseModel):
    items: List[ClassSectionDTO]