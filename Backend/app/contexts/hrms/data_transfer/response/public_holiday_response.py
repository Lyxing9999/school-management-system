from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.contexts.shared.lifecycle.dto import LifecycleDTO
from app.contexts.admin.data_transfer.responses.common import PaginatedDTO


class PublicHolidayDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    name: str
    name_kh: Optional[str] = None
    date: date
    is_paid: bool
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    deleted_by: Optional[str] = None
    deleted_by_name: Optional[str] = None
    lifecycle: LifecycleDTO


class PublicHolidayPaginatedDTO(PaginatedDTO[PublicHolidayDTO]):
    pass




class PublicHolidayImportResultDTO(BaseModel):
    year: int
    imported_count: int
    skipped_count: int
    imported: list[PublicHolidayDTO]
    skipped_dates: list[str]
