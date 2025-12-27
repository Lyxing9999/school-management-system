from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from .common import ItemListDTO

from app.contexts.student.data_transfer.responses import StudentBaseDataDTO
from app.contexts.iam.data_transfer.response import IAMBaseDataDTO

class AdminCreateStudentDataDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", use_enum_values=True)
    user: Optional[IAMBaseDataDTO] = None
    student: Optional[StudentBaseDataDTO] = None

class AdminStudentNameSelectDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    value: str
    label: str
    first_name_en: Optional[str] = None
    last_name_en: Optional[str] = None
    first_name_kh: Optional[str] = None
    last_name_kh: Optional[str] = None


class AdminStudentNameSelectListDTO(ItemListDTO[AdminStudentNameSelectDTO]):
    pass


class AdminStudentSelectDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    value: str
    label: str
    meta: dict | None = None


class PagedResultDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    items: list[AdminStudentSelectDTO] = Field(default_factory=list)
    nextCursor: str | None = None