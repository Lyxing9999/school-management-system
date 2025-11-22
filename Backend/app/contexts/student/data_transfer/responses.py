# app/contexts/student/data_transfer/responses.py
from __future__ import annotations
from typing import List
from pydantic import BaseModel

from app.contexts.school.data_transfer.responses import (
    ClassSectionDTO,
    AttendanceDTO,
    GradeDTO,
    ScheduleDTO,
)


class StudentClassListDTO(BaseModel):
    items: List[ClassSectionDTO]


class StudentAttendanceListDTO(BaseModel):
    items: List[AttendanceDTO]


class StudentGradeListDTO(BaseModel):
    items: List[GradeDTO]


class StudentScheduleListDTO(BaseModel):
    items: List[ScheduleDTO]
    