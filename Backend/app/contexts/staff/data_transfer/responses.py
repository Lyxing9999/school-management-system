from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel

from app.contexts.shared.enum.roles import SystemRole

class LifecycleDTO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class StaffBaseDataDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        extra="ignore",
    )

    id: str
    user_id: Optional[str] = None

    staff_name: str
    staff_id: str
    role: SystemRole  
    phone_number: Optional[str] = None
    permissions: List[str] = Field(default_factory=list)
    address: Optional[str] = None
    created_by: Optional[str] = None

    lifecycle: LifecycleDTO = Field(default_factory=LifecycleDTO)


class StaffReadDataDTO(StaffBaseDataDTO):
    pass


class StaffReadDataDTOList(RootModel[List[StaffReadDataDTO]]):
    pass