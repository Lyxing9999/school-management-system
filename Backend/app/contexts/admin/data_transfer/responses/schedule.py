import datetime as dt
from typing import Optional

from pydantic import field_serializer

from .common import BaseDTO, ItemListDTO

from app.contexts.school.data_transfer.responses import ScheduleDTO

class AdminScheduleSlotDataDTO(ScheduleDTO):
    class_name: str | None = None
    teacher_name: str | None = None


class AdminScheduleListDTO(ItemListDTO[AdminScheduleSlotDataDTO]):
    pass