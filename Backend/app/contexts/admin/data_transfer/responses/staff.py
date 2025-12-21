from typing import Optional
from pydantic import ConfigDict

from app.contexts.staff.data_transfer.responses import StaffReadDataDTO, StaffBaseDataDTO
from .common import BaseDTO, ItemListDTO, NameSelectDTO


class AdminGetStaffDTO(StaffReadDataDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)


class AdminCreateStaffDTO(StaffBaseDataDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)


class AdminUpdateStaffDTO(StaffBaseDataDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)


class AdminStaffNameSelectDTO(NameSelectDTO):
    pass


class AdminTeacherSelectDTO(BaseDTO):
    """
    Keep select payload consistent for frontend:
    value/label is often easier than id/name.
    """
    value: str
    label: str


class AdminTeacherSelectListDTO(ItemListDTO[AdminTeacherSelectDTO]):
    pass