from typing import Optional
from pydantic import ConfigDict

from app.contexts.student.data_transfer.responses import StudentBaseDataDTO
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO

from .common import BaseDTO, ItemListDTO


class AdminCreateStudentDataDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)
    user: Optional[IAMBaseDataDTO] = None
    student: Optional[StudentBaseDataDTO] = None


class AdminStudentNameSelectDTO(BaseDTO):
    value: str
    label: str
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None
    first_name_kh: Optional[str] = None
    last_name_kh: Optional[str] = None


class AdminStudentNameSelectListDTO(ItemListDTO[AdminStudentNameSelectDTO]):
    pass