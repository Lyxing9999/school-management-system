from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.contexts.shared.lifecycle.dto import LifecycleDTO


class WorkLocationDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore", populate_by_name=True)

    id: str
    name: str
    address: str
    latitude: float
    longitude: float
    radius_meters: int
    is_active: bool
    location_name: Optional[str] = None
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    deleted_by: Optional[str] = None
    deleted_by_name: Optional[str] = None
    lifecycle: LifecycleDTO
