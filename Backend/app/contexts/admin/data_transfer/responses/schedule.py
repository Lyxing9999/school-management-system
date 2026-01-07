from __future__ import annotations

from typing import Generic, TypeVar, List
from pydantic import Field

from .common import BaseDTO, OptionDTO, ItemListDTO
from app.contexts.school.data_transfer.responses import ScheduleDTO


T = TypeVar("T")


class PaginatedListDTO(BaseDTO, Generic[T]):
    items: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 10


class AdminScheduleSlotDataDTO(ScheduleDTO):
    class_name: str | None = None
    teacher_name: str | None = None
    subject_label: str | None = None


class AdminScheduleListDTO(PaginatedListDTO[AdminScheduleSlotDataDTO]):
    pass



class AdminSubjectSelectDTO(OptionDTO):
    pass


class AdminSubjectSelectListDTO(ItemListDTO[AdminSubjectSelectDTO]):
    pass