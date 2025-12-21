from typing import Optional
from pydantic import ConfigDict

from app.contexts.iam.data_transfer.response import IAMBaseDataDTO
from app.contexts.staff.data_transfer.responses import StaffBaseDataDTO
from app.contexts.student.data_transfer.responses import StudentBaseDataDTO

from .common import BaseDTO


class AdminUserStaffDataDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)
    user: Optional[IAMBaseDataDTO] = None
    staff: Optional[StaffBaseDataDTO] = None


class AdminUserStudentDataDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)
    user: Optional[IAMBaseDataDTO] = None
    student: Optional[StudentBaseDataDTO] = None